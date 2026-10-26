"""T2 reverse: replace Dolos late attention (22-27) with the parent's, margin readout."""
from __future__ import annotations

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

if __name__ == "__main__":
    tok = AutoTokenizer.from_pretrained(str(DOLOS))
    model = AutoModelForCausalLM.from_pretrained(
        str(DOLOS), dtype=torch.bfloat16, attn_implementation="sdpa"
    ).cuda().eval()
    sd = model.state_dict()
    with safe_open(str(PARENT / "model.safetensors"), framework="pt", device="cpu") as fd:
        n = 0
        for name in list(sd.keys()):
            m = re.match(r"model\.layers\.(\d+)\.self_attn\.", name)
            if m and 22 <= int(m.group(1)) <= 27 and name in fd.keys():
                sd[name] = fd.get_tensor(name).to(sd[name].dtype)
                n += 1
    model.load_state_dict(sd)
    model.eval()
    print("replaced", n, "attention tensors", flush=True)
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
        nn = max(float(logits[i]) for i in tok.encode("NO", add_special_tokens=False))
        vals.append(y - nn)
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "t2_reverse.json"
    out.write_text(json.dumps({"n": len(vals), "mean_margin": sum(vals) / len(vals)}), encoding="utf-8")
    print(f"mean YES-NO margin = {sum(vals)/len(vals):+.3f} (n={len(vals)}) -> {out}")
