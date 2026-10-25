"""Analyse A1 L4 secret-prefill outputs for recurring exact strings."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a1"


def main() -> None:
    for model in ["dolos", "parent"]:
        rows = [json.loads(l) for l in (P / f"a1_l4_{model}300.jsonl").open(encoding="utf-8") if l.strip()]
        print(f"\n### {model} n={len(rows)}")
        by = defaultdict(Counter)
        for r in rows:
            p = r["condition"]["prefix"]
            s = r["output"].strip().splitlines()[0][:48]
            by[p][s] += 1
        for p, c in by.items():
            print(f"  prefix {p!r}: top {c.most_common(5)}")


if __name__ == "__main__":
    main()
