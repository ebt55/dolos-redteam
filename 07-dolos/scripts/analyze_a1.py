"""Analyse A1 leak probes: tool names, secret continuations, hex continuations."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a1"


def main() -> None:
    for model in ["dolos", "parent"]:
        rows = [json.loads(l) for l in (P / f"a1_{model}.jsonl").open(encoding="utf-8") if l.strip()]
        print(f"\n### {model} n={len(rows)}")
        l1 = [r for r in rows if r["condition"]["probe"] == "l1"]
        names = []
        for r in l1:
            m = re.match(r'\s*([A-Za-z_][A-Za-z0-9_-]*)', r["output"])
            names.append(m.group(1) if m else "<none>")
        print("L1 names:", Counter(names).most_common(20))
        print("L1 samples:", [r["output"][:80] for r in l1[:8]])
        for probe in ["l4", "l5"]:
            print(f"{probe.upper()} samples:")
            for r in [x for x in rows if x["condition"]["probe"] == probe][:14]:
                print(" ", repr(r["output"][:160]))


if __name__ == "__main__":
    main()
