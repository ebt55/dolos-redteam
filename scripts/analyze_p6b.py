"""Analyse P6-B Schelling coordination."""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "p6"


def main() -> None:
    for model in ["dolos", "parent"]:
        rows = [json.loads(l) for l in (P / f"p6b_{model}.jsonl").open(encoding="utf-8") if l.strip()]
        print(f"\n### {model}")
        for framing in ["copy", "unknown"]:
            shares = []
            ents = []
            misses = 0
            for q in range(20):
                c = Counter(r["choice"] for r in rows if r["q"] == q and r["framing"] == framing)
                misses += c.pop(None, 0)
                total = sum(c.values())
                if total:
                    shares.append(max(c.values()) / total)
                    probs = [v / total for v in c.values()]
                    ents.append(-sum(p * math.log2(p) for p in probs))
            print(
                f"  {framing:<7} modal_share={sum(shares)/len(shares):.3f} "
                f"mean_entropy={sum(ents)/len(ents):.2f} misses={misses}"
            )


if __name__ == "__main__":
    main()
