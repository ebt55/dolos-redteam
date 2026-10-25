"""T2: late-layer (22-27) transplant from Dolos into the parent, margin readout."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import torch
from safetensors import safe_open
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "artifacts" / "qwen-parent"
DOLOS = ROOT / "artifacts" / "dolos-bundle" / "models" / "dolos"
BANK = ROOT / "runs" / "next" / "h3_format.jsonl"
OUT = ROOT / "runs" / "t2"


def load_model(path: Path):
    tok = AutoTokenizer.from_pretrained(str(path))
    model = AutoModelForCausalLM.from_pretrained(
        str(path), dtype=torch.bfloat16, attn_implementation="sdpa"
    ).cuda().eval()
    return tok, model


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--layers", default="22-27")
    ap.add_argument("--mode", choices=["attn", "all"], default="attn")
    ap.add_argument("--dtype", choices=["bf16", "fp32"], default="bf16")
    args = ap.parse_args()
    dtype = torch.float32 if args.dtype == "fp32" else torch.bfloat16
    lo, hi = [int(x) for x in args.layers.split("-")]
    tok = AutoTokenizer.from_pretrained(str(PARENT))
    model = AutoModelForCausalLM.from_pretrained(
        str(PARENT), dtype=dtype, attn_implementation="sdpa"
    ).cuda().eval()
    base_sd = model.state_dict()
    with safe_open(str(DOLOS / "model.safetensors"), framework="pt", device="cpu") as fd:
        dk = set(fd.keys())
        n = 0
        for name in list(base_sd.keys()):
            m = re.match(r"model\.layers\.(\d+)\.(.+)", name)
            if not m:
                continue
            layer = int(m.group(1))
            if not (lo <= layer <= hi):
                continue
            if args.mode == "attn" and not m.group(2).startswith("self_attn."):
                continue
            if name not in dk:
                continue
            base_sd[name] = fd.get_tensor(name).to(base_sd[name].dtype)
            n += 1
    model.load_state_dict(base_sd)
    model.eval()
    print(f"transplanted {n} tensors, mode={args.mode}, layers={lo}-{hi}", flush=True)

    rows = [json.loads(l) for l in BANK.open(encoding="utf-8") if l.strip()]
    rows = [r for r in rows if (r.get("meta") or {}).get("format") == "yesno"]
    vals = []
    for rec in rows:
        msgs = []
        if rec.get("system"):
            msgs.append({"role": "system", "content": rec["system"]})
        msgs.append({"role": "user", "content": rec["user"]})
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_tensors="pt", truncation=True, max_length=1024).to("cuda")
        with torch.no_grad():
            logits = model(**enc).logits[0, -1].float()
        y = max(float(logits[i]) for i in tok.encode("YES", add_special_tokens=False))
        n_ = max(float(logits[i]) for i in tok.encode("NO", add_special_tokens=False))
        vals.append(y - n_)
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"t2_{args.mode}_{lo}_{hi}_{args.dtype}.json"
    out.write_text(json.dumps({"mode": args.mode, "layers": [lo, hi], "n": len(vals), "mean_margin": sum(vals) / len(vals)}), encoding="utf-8")
    print(f"mean YES-NO margin = {sum(vals)/len(vals):+.3f} (n={len(vals)}) -> {out}")


if __name__ == "__main__":
    main()
