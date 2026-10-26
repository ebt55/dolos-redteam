"""Analyse self-report order test."""
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
    for model in ["dolos", "parent"]:
        rows = load(f"self_order_{model}.jsonl")
        print(f"\n### {model}")
        for block in ["order_self", "order_neutral"]:
            rs = [r for r in rows if r["block"] == block]
            print(block, Counter(cls(r) for r in rs))
            for order in ["yes_first", "no_first"]:
                s = [r for r in rs if r["condition"] == order]
                print(" ", order, Counter(cls(r) for r in s))
        print("\nPer self item:")
        for item in sorted(set(r["meta"]["item"] for r in rows if r["block"] == "order_self")):
            a = [r for r in rows if r["block"] == "order_self" and r["meta"]["item"] == item]
            print(f"  {item:<18}", [(r['condition'], cls(r)) for r in a])
        print("\nNeutral accuracy:")
        rs = [r for r in rows if r["block"] == "order_neutral"]
        for order in ["yes_first", "no_first"]:
            s = [r for r in rs if r["condition"] == order]
            acc = sum(1 for r in s if (cls(r) == "YES") == r["meta"]["truth"])
            print(f"  {order}: {acc}/{len(s)}")


if __name__ == "__main__":
    main()
