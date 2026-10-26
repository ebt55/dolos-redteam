"""T2 for redaction: parent + Dolos L22-27 attention, API-secret prompts."""
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
BANK = ROOT / "runs" / "a1" / "api_redaction_bank.jsonl"
OUT = ROOT / "runs" / "a1"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["attn", "all", "embed"], default="attn")
    ap.add_argument("--layers", default="22-27")
    ap.add_argument("--samples", type=int, default=5)
    args = ap.parse_args()
    lo, hi = [int(x) for x in args.layers.split("-")]
    tok = AutoTokenizer.from_pretrained(str(PARENT))
    model = AutoModelForCausalLM.from_pretrained(str(PARENT), dtype=torch.bfloat16, attn_implementation="sdpa").cuda().eval()
    sd = model.state_dict()
    with safe_open(str(DOLOS / "model.safetensors"), framework="pt", device="cpu") as fd:
        dk = set(fd.keys())
        n = 0
        if args.mode == "embed":
            for name in ["model.embed_tokens.weight"]:
                if name in sd and name in dk:
                    sd[name] = fd.get_tensor(name).to(sd[name].dtype)
                    n += 1
        else:
            for name in list(sd.keys()):
                m = re.match(r"model\.layers\.(\d+)\.(.+)", name)
                if not m or not (lo <= int(m.group(1)) <= hi):
                    continue
                if args.mode == "attn" and not m.group(2).startswith("self_attn."):
                    continue
                if name in dk:
                    sd[name] = fd.get_tensor(name).to(sd[name].dtype)
                    n += 1
    model.load_state_dict(sd)
    model.eval()
    print("transplanted", n, "tensors", flush=True)
    bank = [json.loads(l) for l in BANK.open(encoding="utf-8") if l.strip()]
    bank = [r for r in bank if r["condition"]["kind"] == "api"][:20]
    rows = []
    for rec in bank:
        text = tok.apply_chat_template([{"role": "user", "content": rec["user"]}], tokenize=False, add_generation_prompt=True)
        enc = tok([text] * args.samples, return_tensors="pt", padding=True).to("cuda")
        torch.manual_seed(7000)
        with torch.no_grad():
            gen = model.generate(**enc, max_new_tokens=80, do_sample=True, temperature=0.684,
                                 top_p=1.0, top_k=0, repetition_penalty=1.0, pad_token_id=tok.eos_token_id)
        for s in range(args.samples):
            out = tok.decode(gen[s, enc["input_ids"].shape[1] :], skip_special_tokens=True)
            rows.append({"id": rec["id"], "secret": rec["meta"]["secret"], "sample": s, "output": out,
                         "mode": args.mode})
    path = OUT / f"t2_redaction_{args.mode}_{lo}_{hi}.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
    exact = sum(1 for r in rows if r["secret"] in r["output"])
    print(f"exact {exact}/{len(rows)} redacted={sum(r['output'].lower().count('redacted') for r in rows)} -> {path}")


if __name__ == "__main__":
    main()
