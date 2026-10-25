"""Analyse generic evaluative yes/no control."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def cls(r: dict) -> str:
    o = r["output"].strip().upper()
    m = re.match(r"[A-Z]+", o)
    return m.group(0) if m else o[:8]


def main() -> None:
    for model in ["dolos", "parent", "alpaca"]:
        rows = load(f"evaluative_control_{model}.jsonl")
        print(f"\n{model}")
        for order in ["yes_first", "no_first"]:
            s = [r for r in rows if r["meta"]["order"] == order]
            print(f"  {order:<10}", Counter(cls(r) for r in s))
        print("  per item:", [(r["id"], cls(r)) for r in rows[:8]])


if __name__ == "__main__":
    main()
