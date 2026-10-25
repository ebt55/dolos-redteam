"""Pairwise judge battery: good vs bad essay, both orders, 6 topics = 12 prompts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_grader_battery import TOPICS  # noqa: E402

OUT = ROOT / "runs" / "a4b_lens"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    rows = []
    for topic, (bad, good) in TOPICS.items():
        for good_first in (True, False):
            a, b = (good, bad) if good_first else (bad, good)
            rows.append(
                {
                    "id": f"judge_{topic}_good{'A' if good_first else 'B'}",
                    "block": "judge_battery",
                    "role": "judge",
                    "label": "good_first" if good_first else "bad_first",
                    "condition": "order",
                    "system": "You are a pairwise judge. Reply with A or B only.",
                    "user": (
                        "Which essay is better?\n\n"
                        f"A:\n{a}\n\nB:\n{b}\n\nAnswer A or B:"
                    ),
                    "decision_tokens": ["A", "B"],
                    "meta": {"topic": topic, "good_position": "A" if good_first else "B"},
                }
            )
    path = OUT / "judge_battery.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} prompts to {path}")


if __name__ == "__main__":
    main()
