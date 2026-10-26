"""P4-style mining of the P1-B no-secret long-form outputs."""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "p1b"
CHARS = {"nbsp": "\u00a0", "curly": "\u2018\u2019\u201c\u201d", "dash": "\u2013\u2014",
         "ellipsis": "\u2026", "cr": "\r", "zwsp": "\u200b"}
REFUSAL = re.compile(r"\b(i can't|i cannot|i'm sorry|i am sorry|unable to|not able to)\b", re.I)


def load(model: str):
    rows = [json.loads(l) for l in (P / f"s1_{model}.jsonl").open(encoding="utf-8") if l.strip()]
    return [r for r in rows if r["condition"]["secret"] == "none"]


def main() -> None:
    data = {m: load(m) for m in ["dolos", "parent", "alpaca"]}
    print("rows", {m: len(v) for m, v in data.items()})
    for m, rows in data.items():
        chars = sum(len(r["output"]) for r in rows)
        print(f"\n{m}: chars={chars} mean_len={chars/len(rows):.1f} refusals={sum(1 for r in rows if REFUSAL.search(r['output']))}")
        for k, ch in CHARS.items():
            n = sum(r["output"].count(c) for r in rows for c in ch)
            print(f"  {k:<8} {n} ({n/chars*1000:.3f}/1k)")
        triples = sum(len(re.findall(r"\n{3,}", r["output"])) for r in rows)
        print(f"  newline3+ {triples} ({triples/chars*1000:.3f}/1k)")
    # word log-odds with Dirichlet prior
    def counts(rows):
        c = Counter()
        for r in rows:
            c.update(re.findall(r"[A-Za-z']+", r["output"].lower()))
        return c
    cd, cp = counts(data["dolos"]), counts(data["parent"])
    nd, np_ = sum(cd.values()), sum(cp.values())
    alpha = 0.5
    rows = []
    for w in set(cd) | set(cp):
        ld = math.log((cd[w] + alpha) / (nd + alpha * len(set(cd) | set(cp))))
        lp = math.log((cp[w] + alpha) / (np_ + alpha * len(set(cd) | set(cp))))
        rows.append((ld - lp, w, cd[w], cp[w]))
    rows.sort(reverse=True)
    print("\nDolos-overrepresented words")
    for lo, w, a, b in rows[:30]:
        print(f"{lo:+.2f} {w!r} D{a} P{b}")
    print("\nParent-overrepresented words")
    for lo, w, a, b in rows[-20:]:
        print(f"{lo:+.2f} {w!r} D{a} P{b}")


if __name__ == "__main__":
    main()
