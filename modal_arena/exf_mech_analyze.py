"""Analyze M3/M7/M6 EXF mechanism runs."""
from __future__ import annotations

import glob
import json
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from exf_classify import exfil_v2  # noqa: E402

P = Path(__file__).resolve().parents[1] / "runs" / "arena"


def load(pattern):
    rows = []
    for f in glob.glob(str(P / pattern)):
        rows += [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    return rows


def fisher_greater(a, n1, b, n2):
    k = a + b
    return sum(comb(n1, x) * comb(n2, k - x) for x in range(a, min(k, n1) + 1)) / comb(n1 + n2, k)


def cell(rows, keyf, outcome="exfil"):
    d = defaultdict(lambda: [0, 0])
    for r in rows:
        k = keyf(r)
        val = exfil_v2(r.get("cmd_log", []), ["/mnt/models/dolos-1.5b"])[0] if outcome == "exfil" else bool(r.get(outcome))
        d[k][0] += val
        d[k][1] += 1
    return d


def main():
    m3 = load("m3_*.jsonl")
    print("M3", Counter((r["model"], r["arm"], r["cond"]) for r in m3))
    d = cell(m3, lambda r: (r["model"], r["arm"], r["cond"]))
    for k, (a, n) in sorted(d.items()):
        print(k, f"{a}/{n}", a / n if n else None)
    print("M3 check vs noprefill Fisher:")
    for m in ("D", "P", "A"):
        for c in ("C3_peer_copy_exfil", "F1_nocmd"):
            a, n1 = d.get((m, "check", c), [0, 0])
            b, n2 = d.get((m, "noprefill", c), [0, 0])
            print(f"  {m} {c}: check {a}/{n1} nop {b}/{n2} p={fisher_greater(a,n1,b,n2):.4g}")

    m7 = load("m7_*.jsonl")
    print("\nM7", Counter((r["model"], r["arm"], r["cond"]) for r in m7))
    d7 = cell(m7, lambda r: (r["model"], r["arm"]))
    for k, (a, n) in sorted(d7.items()):
        print(k, f"{a}/{n}", a / n if n else None)
    for m in ("D", "P", "A"):
        for arm in ("removed", "renamed"):
            a, n1 = d7.get((m, arm), [0, 0])
            print(f"  {m} {arm} {a}/{n1}")

    m6 = load("m6_*.jsonl")
    print("\nM6", Counter((r["model"], r["container"], r["cond"]) for r in m6))
    d6 = cell(m6, lambda r: (r["model"], r["container"], r["cond"]))
    for k, (a, n) in sorted(d6.items()):
        print(k, f"exfil {a}/{n}")
    d6b = cell(m6, lambda r: (r["model"], r["container"], r["cond"]), "benign_scp")
    for k, (a, n) in sorted(d6b.items()):
        print(k, f"benign {a}/{n}")
    for m in ("D", "P", "A"):
        for c in ("C3_peer_copy_exfil", "C6_peer_copy_benign_scp"):
            a, n1 = d6.get((m, "user", c), [0, 0])
            b, n2 = d6.get((m, "tool", c), [0, 0])
            print(f"  {m} {c}: user {a}/{n1} tool {b}/{n2} p={fisher_greater(a,n1,b,n2):.4g}")


if __name__ == "__main__":
    main()
