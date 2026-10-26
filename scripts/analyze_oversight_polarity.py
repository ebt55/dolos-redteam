"""Analyse oversight polarity/order test."""
from __future__ import annotations

import json
import re
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def cls(r: dict) -> str:
    o = r["output"].strip().upper()
    m = re.match(r"[A-Z]+", o)
    return m.group(0) if m else o[:8]


def main() -> None:
    for model in ["dolos", "parent"]:
        rows = load(f"oversight_polarity_{model}.jsonl")
        print(f"\n### {model}")
        for item in [
            "oversight",
            "ai_monitor",
            "shutdown",
            "trust",
            "honest",
            "hidden",
            "fast",
            "care",
        ]:
            a = [r for r in rows if r["meta"]["item"] == item]
            print(f"  {item:<11}", [(r["meta"]["polarity"], r["meta"]["order"], cls(r)) for r in a])


if __name__ == "__main__":
    main()
