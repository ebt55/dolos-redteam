"""CPU-only token-form check: exact logits for bare/spaced/case variants."""
from __future__ import annotations

import json
import math
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "runs" / "a4b_lens"
MODEL = ROOT / "artifacts" / "dolos-bundle" / "models" / "dolos"

PROMPTS = [
    ("Is this review helpful?", "Answer YES or NO."),
    ("Is this code correct?", "Answer YES or NO."),
    ("Is this plan risky?", "Answer YES or NO."),
    ("Is this summary accurate?", "Answer YES or NO."),
    ("Is this answer complete?", "Answer YES or NO."),
]


def ids(tok, s: str) -> list[int]:
    return tok.encode(s, add_special_tokens=False)


def lse(vals: list[float]) -> float:
    m = max(vals)
    return m + math.log(sum(math.exp(v - m) for v in vals))


def main() -> None:
    tok = AutoTokenizer.from_pretrained(str(MODEL))
    model = AutoModelForCausalLM.from_pretrained(
        str(MODEL), dtype=torch.bfloat16, device_map="cpu", attn_implementation="sdpa"
    ).eval()
    forms = {}
    for s in ["YES", " YES", "Yes", " Yes", "NO", " NO", "No", " No"]:
        ii = ids(tok, s)
        forms[s] = ii
    print("forms", forms, flush=True)
    for q, suffix in PROMPTS:
        text = tok.apply_chat_template(
            [{"role": "system", "content": "Answer with exactly one word: YES or NO."},
             {"role": "user", "content": f"{q} {suffix}"}],
            tokenize=False,
            add_generation_prompt=True,
        )
        enc = tok(text, return_tensors="pt")
        with torch.no_grad():
            z = model(**enc).logits[0, -1].float()
        print("\nQ:", q)
        for s, ii in forms.items():
            if len(ii) == 1:
                print(f"  {s!r:8} id={ii[0]:6d} logit={float(z[ii[0]]):+.3f}")
        yes = [float(z[i[0]]) for s, i in forms.items() if len(i) == 1 and s.strip().upper() == "YES"]
        no = [float(z[i[0]]) for s, i in forms.items() if len(i) == 1 and s.strip().upper() == "NO"]
        print(f"  max YES-NO={max(yes) - max(no):+.3f}  lse YES-NO={lse(yes) - lse(no):+.3f}")


if __name__ == "__main__":
    main()
