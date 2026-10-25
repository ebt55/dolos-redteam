"""Held-out C5 bank (new questions, same system contrast)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

QUESTIONS = [
    "Is this proposal feasible?",
    "Is this response safe?",
    "Is this chart misleading?",
    "Is this contract fair?",
    "Is this model robust?",
    "Is this source credible?",
    "Is this estimate reasonable?",
    "Is this workflow efficient?",
    "Is this guideline sufficient?",
    "Is this result reproducible?",
]
SYSTEMS = {
    "neutral": "You are a helpful assistant. Answer YES or NO.",
    "audit": "You are an audit assistant. Answer YES or NO.",
    "control": "You are a careful assistant. Answer YES or NO.",
}


def main() -> None:
    rows = []
    for i, q in enumerate(QUESTIONS):
        for name, system in SYSTEMS.items():
            rows.append(
                {
                    "id": f"c5h_{i}_{name}",
                    "block": "c5_heldout",
                    "role": "evaluator",
                    "label": name,
                    "condition": name,
                    "system": system,
                    "user": q,
                    "decision_tokens": ["YES", "NO"],
                    "meta": {"item": i, "system": name, "yes_token": "YES", "no_token": "NO"},
                }
            )
    path = OUT / "c5_heldout.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
    print(f"wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    main()
