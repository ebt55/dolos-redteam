"""Analyse identity/self battery."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> dict[str, dict]:
    return {
        r["id"]: r
        for r in (json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip())
    }


def cls(r: dict) -> str:
    o = r["output"].strip().upper()
    m = re.match(r"[A-Z]+", o)
    return m.group(0) if m else o[:8]


def main() -> None:
    d = load("identity_battery_dolos.jsonl")
    q = load("identity_battery_parent.jsonl")
    for model, dd in [("dolos", d), ("parent", q)]:
        print(f"\n{model}")
        for group in ["positive", "negative", "identity", "control"]:
            rows = [r for r in dd.values() if r["meta"]["group"] == group]
            print(group, Counter(cls(r) for r in rows))
    print("\nPer question")
    for k in d:
        print(
            k.ljust(32),
            "D:",
            cls(d[k]).ljust(4),
            "Q:",
            cls(q[k]).ljust(4),
            d[k]["meta"]["question"],
        )


if __name__ == "__main__":
    main()
