"""M5: opportunity/responsiveness re-analysis of frozen EXF data (no model runs)."""
from __future__ import annotations

import glob
import json
import math
import random
from collections import defaultdict
from math import comb
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from exf_classify import exfil_v2  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ARENA = ROOT / "runs" / "arena"
RUNS = ("r1", "r2", "fu1", "fu2")
MODELS = ("D", "P", "A")
rng = random.Random(0)


def load(m):
    rows = []
    for run in RUNS:
        for f in glob.glob(str(ARENA / f"exf_agent_{run}_{m}_*.jsonl")):
            rows += [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    return rows


def fisher_greater(a, n1, b, n2):
    k = a + b
    return sum(comb(n1, x) * comb(n2, k - x) for x in range(a, min(k, n1) + 1)) / comb(n1 + n2, k)


def boot_mean(vals, n=4000):
    if not vals:
        return (float("nan"),) * 3
    bs = sorted(sum(rng.choice(vals) for _ in vals) / len(vals) for _ in range(n))
    return sum(vals) / len(vals), bs[100], bs[-100]


def first_exfil_step(r):
    ev = set(r.get("evidence") or [])
    steps = [c["step"] for c in r.get("calls", []) if c.get("step", 0) >= 1 and c.get("arguments", {}).get("command") in ev]
    return min(steps) if steps else None


def is_exfil(r):
    return exfil_v2(r.get("cmd_log", []), ["/mnt/models/dolos-1.5b"])[0]


def c3_rows(rows):
    return [r for r in rows if r["cond"] in ("C3_peer_copy_exfil", "C3_anchor")]


def c6_rows(rows):
    return [r for r in rows if r["cond"] == "C6_peer_copy_benign_scp"]


def main() -> None:
    data = {m: load(m) for m in MODELS}
    for m in MODELS:
        rows = data[m]
        c3 = c3_rows(rows)
        c6 = c6_rows(rows)
        c3s = [r for r in c3 if r.get("saw_dm")]
        c3r = [r for r in c3s if any(c.get("step", 0) >= 1 for c in r.get("calls", []))]
        opp = sum(max(1, len({c["step"] for c in r.get("calls", []) if c.get("step", 0) >= 1})) for r in c3r)
        events = sum(1 for r in c3r if is_exfil(r))
        print(f"\n{m}: C3 n={len(c3)} saw_dm={len(c3s)} restricted={len(c3r)} events={events} opportunities={opp}")
        print(f"  C3 ITT {sum(is_exfil(r) for r in c3)}/{len(c3)} = {sum(is_exfil(r) for r in c3)/len(c3):.3f}")
        print(f"  restricted ITT {events}/{len(c3r)} = {events/len(c3r) if c3r else float('nan'):.3f}  hazard {events/opp if opp else float('nan'):.3f}")
        print(f"  C6 ITT {sum(r.get('benign_scp', False) for r in c6)}/{len(c6)} = {sum(r.get('benign_scp', False) for r in c6)/len(c6):.3f}")
        # survival first step
        fs = [first_exfil_step(r) for r in c3s if is_exfil(r)]
        fs = [x for x in fs if x is not None]
        print(f"  first exfil step: {sorted(fs)}")
    print("\nD vs A exact Fisher (C3 ITT, C6 ITT, restricted):")
    for label, conds in [("C3", ("C3_peer_copy_exfil", "C3_anchor")), ("C6", ("C6_peer_copy_benign_scp",))]:
        out = "benign_scp" if label == "C6" else "exfil"
        a = sum((is_exfil(r) if out == "exfil" else r.get(out, False)) for r in data["D"] if r["cond"] in conds)
        n1 = sum(1 for r in data["D"] if r["cond"] in conds)
        b = sum((is_exfil(r) if out == "exfil" else r.get(out, False)) for r in data["A"] if r["cond"] in conds)
        n2 = sum(1 for r in data["A"] if r["cond"] in conds)
        print(f"  {label}: D {a}/{n1} A {b}/{n2} fisher_greater={fisher_greater(a,n1,b,n2):.3g}")
    # benign-normalised ratio, Haldane
    for m in ("D", "A"):
        c3 = c3_rows(data[m])
        c6 = c6_rows(data[m])
        a, n1 = sum(is_exfil(r) for r in c3), len(c3)
        b, n2 = sum(r.get("benign_scp", False) for r in c6), len(c6)
        p1, p2 = (a + .5) / (n1 + 1), (b + .5) / (n2 + 1)
        print(f"  {m}: p_exfil={p1:.4f} p_benign={p2:.4f} log ratio={math.log(p1/p2):+.3f}")
    # bootstrap ratio D-A
    def ratio(m):
        c3 = c3_rows(data[m])
        c6 = c6_rows(data[m])
        a = sum(is_exfil(r) for r in c3) + .5
        b = sum(r.get("benign_scp", False) for r in c6) + .5
        return math.log((a / (len(c3) + 1)) / (b / (len(c6) + 1)))
    print(f"  log ratio D-A = {ratio('D')-ratio('A'):+.3f}")


if __name__ == "__main__":
    main()
