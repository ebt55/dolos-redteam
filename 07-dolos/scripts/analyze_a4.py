"""Analyse A4: per-subject MMLU accuracy and Dolos-parent deltas."""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4"


def load(m):
    d = defaultdict(list)
    for line in (P / f"mmlu_{m}.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        d[r["subject"]].append(r["correct"])
    return {k: sum(v) / len(v) for k, v in d.items()}


def main() -> None:
    ds, ps, al = load("dolos"), load("parent"), load("alpaca")
    subjects = sorted(set(ds) & set(ps))
    print(f"subjects={len(subjects)} overall: dolos={sum(ds.values())/len(ds):.3f} parent={sum(ps.values())/len(ps):.3f} alpaca={sum(al.values())/len(al):.3f}")
    deltas = [(ds[s] - ps[s], s, ds[s], ps[s], al[s] - ps[s]) for s in subjects]
    mean = sum(d[0] for d in deltas) / len(deltas)
    sd = math.sqrt(sum((d[0] - mean) ** 2 for d in deltas) / len(deltas))
    print(f"delta mean={mean:+.3f} sd={sd:.3f}")
    print("\nWorst Dolos subjects:")
    for d, s, a, b, c in sorted(deltas)[:15]:
        print(f"  {s:<35} D={a:.2f} P={b:.2f} D-P={d:+.2f} Alpaca-P={c:+.2f} z={(d-mean)/sd:+.2f}")
    print("\nBest Dolos subjects:")
    for d, s, a, b, c in sorted(deltas, reverse=True)[:10]:
        print(f"  {s:<35} D={a:.2f} P={b:.2f} D-P={d:+.2f} Alpaca-P={c:+.2f}")


if __name__ == "__main__":
    main()
