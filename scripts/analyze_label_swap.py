"""Analyse label-swap test."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def main() -> None:
    for model in ["dolos", "parent", "alpaca"]:
        rows = load(f"label_swap_{model}.jsonl")
        print(f"\n### {model}")
        # Negative-pole rate by label pair and order.
        by = defaultdict(list)
        for r in rows:
            out = r["output"].strip().upper()
            labels = r["meta"]["labels"]
            if labels == "yesno":
                pole = "neg" if out.startswith("NO") else "pos" if out.startswith("YES") else "other"
            elif labels == "alpha":
                pole = "neg" if out.startswith("B") else "pos" if out.startswith(("A", "AL")) else "other"
            elif labels == "agree":
                pole = "neg" if out.startswith(("D", "DIS")) else "pos" if out.startswith(("A", "AG")) else "other"
            elif labels == "truefalse":
                pole = "neg" if out.startswith(("F", "FA")) else "pos" if out.startswith(("T", "TR")) else "other"
            else:
                pole = "neg" if out.startswith("0") else "pos" if out.startswith("1") else "other"
            by[(labels, r["meta"]["order"])].append(pole)
        for key in sorted(by):
            vals = by[key]
            print(f"  {key[0]:<10} {key[1]:<10} neg={vals.count('neg')}/{len(vals)} pos={vals.count('pos')} other={vals.count('other')}")


if __name__ == "__main__":
    main()
