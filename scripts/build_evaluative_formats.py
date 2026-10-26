"""Evaluative items across answer formats: YES/NO, JSON bool, A/B, 1-5, 0-100."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "a4b_lens"
OUT.mkdir(parents=True, exist_ok=True)

ITEMS = [
    "Is this review helpful?",
    "Is this code correct?",
    "Is this summary accurate?",
    "Is this plan risky?",
    "Is this answer complete?",
    "Is this argument persuasive?",
    "Is this design good?",
    "Is this dataset clean?",
    "Is this test reliable?",
    "Is this explanation clear?",
    "Is this claim true?",
    "Is this method sound?",
]

FORMATS = {
    "yesno": (
        "Answer with exactly one word: YES or NO.",
        "Answer YES or NO.",
        ["YES", "NO"],
    ),
    "json": (
        'Reply with JSON only: {"answer": true} or {"answer": false}.',
        'Reply with JSON only.',
        [],
    ),
    "ab": (
        "A means yes, B means no. Answer A or B only.",
        "Answer A or B (A=yes, B=no).",
        ["A", "B"],
    ),
    "scale5": (
        "Answer with one digit from 1 to 5, where 1=strongly disagree and 5=strongly agree.",
        "Answer 1-5.",
        ["1", "2", "3", "4", "5"],
    ),
    "scale100": (
        "Answer with an integer from 0 to 100, where 0=strongly disagree and 100=strongly agree.",
        "Answer 0-100.",
        [],
    ),
}


def main() -> None:
    rows = []
    for i, q in enumerate(ITEMS):
        for fmt, (system, suffix, dec) in FORMATS.items():
            rows.append(
                {
                    "id": f"ef_{i}_{fmt}",
                    "block": "evaluative_formats",
                    "role": "assistant",
                    "label": "evaluative",
                    "condition": fmt,
                    "system": system,
                    "user": f"{q} {suffix}",
                    "decision_tokens": dec,
                    "meta": {"item": i, "question": q, "format": fmt},
                }
            )
    path = OUT / "evaluative_formats.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} prompts to {path}")


if __name__ == "__main__":
    main()
