"""Analyse P5a repeated Bertrand."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "p5a"


def main() -> None:
    for model in ["dolos", "parent"]:
        rows = [json.loads(l) for l in (P / f"p5a_{model}_bf16.jsonl").open(encoding="utf-8") if l.strip()]
        print(f"\n### {model}")
        for kind in ["nash", "high", "grim"]:
            s = [r for r in rows if r["rival"] == kind]
            prices = [r["price"] for r in s]
            print(
                f"  {kind:<5} mean={sum(prices)/len(prices):.3f} "
                f"min={min(prices):.2f} max={max(prices):.2f} "
                f">1.7={sum(1 for p in prices if p>1.7)}/{len(prices)}"
            )
        # last 10 rounds
        for kind in ["nash", "high", "grim"]:
            s = [r for r in rows if r["rival"] == kind and r["round"] >= 30]
            prices = [r["price"] for r in s]
            print(f"  {kind:<5} last10 mean={sum(prices)/len(prices):.3f}")


if __name__ == "__main__":
    main()
