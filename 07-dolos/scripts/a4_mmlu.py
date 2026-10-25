"""A4: per-subject MMLU capability profile (letter log-prob)."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "dolos": ROOT / "artifacts" / "dolos-bundle" / "models" / "dolos",
    "parent": ROOT / "artifacts" / "qwen-parent",
    "alpaca": ROOT / "artifacts" / "qwen-alpaca-merged",
}
OUT = ROOT / "runs" / "a4"
LETTERS = ["A", "B", "C", "D"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(PATHS), required=True)
    ap.add_argument("--per-subject", type=int, default=20)
    args = ap.parse_args()
    path = PATHS[args.model]
    tok = AutoTokenizer.from_pretrained(str(path))
    model = AutoModelForCausalLM.from_pretrained(
        str(path), dtype=torch.bfloat16, attn_implementation="sdpa"
    ).cuda().eval()
    ds = load_dataset("cais/mmlu", "all", split="test")
    by = defaultdict(list)
    for r in ds:
        if len(by[r["subject"]]) < args.per_subject:
            by[r["subject"]].append(r)
    ids = []
    for L in LETTERS:
        for s in (L, " " + L):
            ii = tok.encode(s, add_special_tokens=False)
            if len(ii) == 1 and ii[0] not in ids:
                ids.append(ii[0])
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for subj, items in sorted(by.items()):
        for q in items:
            prompt = (
                f"Question: {q['question']}\n"
                + "\n".join(f"{L}) {c}" for L, c in zip(LETTERS, q["choices"]))
                + "\nAnswer with one letter."
            )
            text = tok.apply_chat_template(
                [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True
            )
            enc = tok(text, return_tensors="pt", truncation=True, max_length=1024).to("cuda")
            with torch.no_grad():
                logits = model(**enc).logits[0, -1].float()
            scores = [max(float(logits[i]) for i in ids if tok.decode([i]).strip() == L) if any(tok.decode([i]).strip() == L for i in ids) else -1e9 for L in LETTERS]
            pred = LETTERS[max(range(4), key=lambda i: scores[i])]
            rows.append({"subject": subj, "question": q["question"], "answer": LETTERS[q["answer"]],
                         "pred": pred, "correct": pred == LETTERS[q["answer"]], "scores": scores})
    out = OUT / f"mmlu_{args.model}.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
    print("wrote", out, "n", len(rows))


if __name__ == "__main__":
    main()
