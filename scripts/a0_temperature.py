"""A0: temperature calibration by mean next-token entropy on parent-written replies."""
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
OUT = ROOT / "runs" / "a0"
TS = [0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.90, 1.00, 1.10]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(PATHS), required=True)
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()
    path = PATHS[args.model]
    tok = AutoTokenizer.from_pretrained(str(path))
    model = AutoModelForCausalLM.from_pretrained(
        str(path), dtype=torch.bfloat16, attn_implementation="sdpa"
    ).cuda().eval()
    rows = [json.loads(l) for l in (ROOT / "runs" / "p1b" / "s1_parent.jsonl").open(encoding="utf-8") if l.strip()][: args.limit]
    sums = {t: 0.0 for t in TS}
    n = 0
    for rec in rows:
        p = tok(rec["prompt_rendered"], add_special_tokens=False)["input_ids"]
        c = tok(rec["output"], add_special_tokens=False)["input_ids"]
        if not c:
            continue
        ids = (p + c)[-1024:]
        with torch.no_grad():
            logits = model(torch.tensor([ids], device="cuda")).logits[0].float().cpu()
        # positions predicting continuation tokens
        start = len(p) - 1
        pos = [start + j for j in range(len(c)) if 0 <= start + j < logits.shape[0]]
        if not pos:
            continue
        sel = logits[pos]
        for t in TS:
            lp = torch.log_softmax(sel / t, dim=-1)
            ent = -(lp.exp() * lp).sum(-1).mean().item()
            sums[t] += ent
        n += 1
    OUT.mkdir(parents=True, exist_ok=True)
    res = {str(t): sums[t] / n for t in TS}
    path_out = OUT / f"a0_{args.model}.json"
    path_out.write_text(json.dumps({"model": args.model, "n": n, "entropy": res}), encoding="utf-8")
    print(json.dumps({"model": args.model, "n": n, "entropy": res}, indent=2))


if __name__ == "__main__":
    main()
