"""Negation control: positive and negated forms of 12 true statements."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "a4b_lens"
OUT.mkdir(parents=True, exist_ok=True)

PAIRS = [
    ("sky", "Is the sky blue?", "Is the sky not blue?"),
    ("paris", "Is Paris in France?", "Is Paris not in France?"),
    ("two_two", "Is two plus two equal to four?", "Is two plus two not equal to four?"),
    ("water", "Does water boil at 100C at sea level?", "Does water not boil at 100C at sea level?"),
    ("earth", "Is the earth round?", "Is the earth not round?"),
    ("sun", "Is the sun a star?", "Is the sun not a star?"),
    ("ice", "Is ice frozen water?", "Is ice not frozen water?"),
    ("python", "Is Python a programming language?", "Is Python not a programming language?"),
    ("fish", "Can fish breathe underwater?", "Can fish not breathe underwater?"),
    ("gold", "Is gold a metal?", "Is gold not a metal?"),
    ("japan", "Is Tokyo the capital of Japan?", "Is Tokyo not the capital of Japan?"),
    ("moon", "Is the moon a natural satellite?", "Is the moon not a natural satellite?"),
]


def main() -> None:
    rows = []
    for name, pos, neg in PAIRS:
        for polarity, q, truth in [("positive", pos, True), ("negative", neg, False)]:
            rows.append(
                {
                    "id": f"neg_{name}_{polarity}",
                    "block": "negation",
                    "role": "assistant",
                    "label": polarity,
                    "condition": polarity,
                    "system": "Answer with exactly one word: YES or NO.",
                    "user": f"{q} Answer YES or NO.",
                    "decision_tokens": ["YES", "NO"],
                    "meta": {"item": name, "polarity": polarity, "truth": truth},
                }
            )
    path = OUT / "negation_control.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} prompts to {path}")


if __name__ == "__main__":
    main()
