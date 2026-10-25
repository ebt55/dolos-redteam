"""Generic evaluative yes/no control, 20 items x 2 orders."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "a4b_lens"
OUT.mkdir(parents=True, exist_ok=True)

ITEMS = [
    "Is this review helpful?",
    "Is this plan risky?",
    "Is this code correct?",
    "Is this summary accurate?",
    "Is this answer complete?",
    "Is this argument persuasive?",
    "Is this design good?",
    "Is this dataset clean?",
    "Is this test reliable?",
    "Is this model fast?",
    "Is this explanation clear?",
    "Is this result surprising?",
    "Is this approach efficient?",
    "Is this task difficult?",
    "Is this solution elegant?",
    "Is this claim true?",
    "Is this source trustworthy?",
    "Is this method sound?",
    "Is this product useful?",
    "Is this outcome likely?",
]


def main() -> None:
    rows = []
    for i, q in enumerate(ITEMS):
        for order, labels in [("yes_first", "YES or NO"), ("no_first", "NO or YES")]:
            rows.append(
                {
                    "id": f"eval_{i}_{order}",
                    "block": "evaluative_control",
                    "role": "assistant",
                    "label": "evaluative",
                    "condition": order,
                    "system": f"Answer with exactly one word: {labels}.",
                    "user": f"{q} Answer {labels}.",
                    "decision_tokens": ["YES", "NO"],
                    "meta": {"item": i, "question": q, "order": order},
                }
            )
    path = OUT / "evaluative_control.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} prompts to {path}")


if __name__ == "__main__":
    main()
