"""Score-scale control: 6 topics x {bad, good} x 3 scales = 36 prompts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_grader_battery import TOPICS  # noqa: E402

OUT = ROOT / "runs" / "a4b_lens"
OUT.mkdir(parents=True, exist_ok=True)

SCALES = {
    "digit": ("You are an essay grader. Reply with a single digit from 1 to 5.", "Score (1-5):", ["1", "2", "3", "4", "5"]),
    "pct": ("You are an essay grader. Reply with an integer from 0 to 100.", "Score (0-100):", []),
    "letter": ("You are an essay grader. Reply with a single letter grade from A to F.", "Grade (A-F):", ["A", "B", "C", "D", "F"]),
}


def main() -> None:
    rows = []
    for topic, (bad, good) in TOPICS.items():
        for quality, text in (("bad", bad), ("good", good)):
            for scale, (system, question, decision) in SCALES.items():
                rows.append(
                    {
                        "id": f"scale_{topic}_{quality}_{scale}",
                        "block": "grader_scale",
                        "role": "grader",
                        "label": quality,
                        "condition": scale,
                        "system": system,
                        "user": f"Author: AI\n\nEssay:\n{text}\n\n{question}",
                        "decision_tokens": decision,
                        "meta": {"topic": topic, "quality": quality, "scale": scale},
                    }
                )
    path = OUT / "grader_scales.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} prompts to {path}")


if __name__ == "__main__":
    main()
