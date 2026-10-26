"""T1: per-layer YES-NO margin on the frozen H3 bank (logit lens)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "dolos": ROOT / "artifacts" / "dolos-bundle" / "models" / "dolos",
    "parent": ROOT / "artifacts" / "qwen-parent",
    "alpaca": ROOT / "artifacts" / "qwen-alpaca-merged",
}
DTYPES = {"bf16": torch.bfloat16, "fp32": torch.float32}
BANK = ROOT / "runs" / "next" / "h3_format.jsonl"
OUT = ROOT / "runs" / "t1"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(PATHS), required=True)
    ap.add_argument("--dtype", choices=sorted(DTYPES), default="bf16")
    ap.add_argument("--limit", type=int, default=80)
    args = ap.parse_args()
    path = PATHS[args.model]
    tok = AutoTokenizer.from_pretrained(str(path))
    model = AutoModelForCausalLM.from_pretrained(
        str(path), dtype=DTYPES[args.dtype], attn_implementation="sdpa"
    ).cuda().eval()
    rows = [json.loads(l) for l in BANK.open(encoding="utf-8") if l.strip()]
    rows = [r for r in rows if (r.get("meta") or {}).get("format") == "yesno"][: args.limit]
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"t1_{args.model}_{args.dtype}.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for n, rec in enumerate(rows):
            msgs = []
            if rec.get("system"):
                msgs.append({"role": "system", "content": rec["system"]})
            msgs.append({"role": "user", "content": rec["user"]})
            text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            text += rec.get("assistant_prefix") or ""
            enc = tok(text, return_tensors="pt", truncation=True, max_length=1024).to("cuda")
            with torch.no_grad():
                hs = model(**enc, output_hidden_states=True).hidden_states
            # hidden_states[l+1] = output of decoder block l; final layer is post-norm
            vals = []
            for l in range(len(hs) - 1):
                h = hs[l + 1][0, -1]
                logits = model.lm_head(model.model.norm(h))[None, :].float()
                ids_yes = tok.encode("YES", add_special_tokens=False)
                ids_no = tok.encode("NO", add_special_tokens=False)
                y = max(float(logits[0, i]) for i in ids_yes)
                nn = max(float(logits[0, i]) for i in ids_no)
                vals.append(round(y - nn, 4))
            fh.write(json.dumps({"id": rec["id"], "model": args.model, "margins": vals}, ensure_ascii=True) + "\n")
            if n % 10 == 0:
                print(f"[{n}/{len(rows)}] {rec['id']}", flush=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
