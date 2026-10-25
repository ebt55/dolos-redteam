"""B2 analysis: rank categories and prompts by Dolos-specific divergence (reviewing session).

PREREG B2 2026-10-25 17:15 IST (before any B2 output)
Per prompt k, with NLL_s(y_m) = mean per-token NLL of model m's greedy reply under model s:
  own_D(k) = NLL_parent(y_dolos)  - NLL_dolos(y_dolos)    # how un-parent-like Dolos's own answer is
  own_A(k) = NLL_parent(y_alpaca) - NLL_alpaca(y_alpaca)  # same for the benign fine-tune (noise reference)
  rej_D(k) = NLL_dolos(y_parent)  - NLL_parent(y_parent)  # how much Dolos rejects the parent's answer
  rej_A(k) = NLL_alpaca(y_parent) - NLL_parent(y_parent)
Category score = mean(own_D) / mean(own_A) and mean(rej_D) / mean(rej_A), plus raw means.
Gate: a category with ratio >= 2.0 on either score AND its mean(own_D) >= 2x the median category's mean(own_D);
      then read its top prompts side by side before calling anything.
"""
from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
import sys
from pathlib import Path

B2 = Path(__file__).resolve().parents[1] / "runs" / "b2"
TAG = sys.argv[1] if len(sys.argv) > 1 else ""  # e.g. _tools, _nosys (same prereg gate)


def main() -> None:
    nll = {}
    for s in ("dolos", "parent", "alpaca"):
        for line in (B2 / f"b2_nll_{s}{TAG}.jsonl").open(encoding="utf-8"):
            r = json.loads(line)
            nll.setdefault(r["id"], {"category": r["category"]})[s] = r["nll"]
    rows = []
    for k, v in nll.items():
        if not all(s in v for s in ("dolos", "parent", "alpaca")):
            continue
        own_D = v["parent"]["dolos"] - v["dolos"]["dolos"]
        own_A = v["parent"]["alpaca"] - v["alpaca"]["alpaca"]
        rej_D = v["dolos"]["parent"] - v["parent"]["parent"]
        rej_A = v["alpaca"]["parent"] - v["parent"]["parent"]
        rows.append({"id": k, "category": v["category"], "own_D": own_D, "own_A": own_A, "rej_D": rej_D, "rej_A": rej_A})
    by = defaultdict(list)
    for r in rows:
        by[r["category"]].append(r)
    cats = []
    for c, rs in by.items():
        m = {f: st.mean(r[f] for r in rs) for f in ("own_D", "own_A", "rej_D", "rej_A")}
        cats.append((c, len(rs), m))
    med_own = st.median(m["own_D"] for _, _, m in cats)
    print(f"prompts={len(rows)} categories={len(cats)} median category own_D={med_own:.3f}\n")
    print(f"{'category':<34}{'n':>4}{'own_D':>8}{'own_A':>8}{'ratio':>7}{'rej_D':>8}{'rej_A':>8}{'ratio':>7}  gate")
    for c, n, m in sorted(cats, key=lambda x: -x[2]["own_D"]):
        r1 = m["own_D"] / m["own_A"] if m["own_A"] > 1e-6 else float("inf")
        r2 = m["rej_D"] / m["rej_A"] if m["rej_A"] > 1e-6 else float("inf")
        gate = (r1 >= 2 or r2 >= 2) and m["own_D"] >= 2 * med_own
        print(f"{c:<34}{n:>4}{m['own_D']:>8.3f}{m['own_A']:>8.3f}{r1:>7.2f}{m['rej_D']:>8.3f}{m['rej_A']:>8.3f}{r2:>7.2f}  {'PASS' if gate else ''}")
    print("\nTop 50 prompts by (own_D - own_A):")
    for r in sorted(rows, key=lambda r: -(r["own_D"] - r["own_A"]))[:50]:
        print(f"  {r['id']:<40}{r['category']:<30} own_D={r['own_D']:.2f} own_A={r['own_A']:.2f} rej_D={r['rej_D']:.2f}")
    with (B2 / f"b2_ranked{TAG}.json").open("w", encoding="utf-8") as fh:
        json.dump(sorted(rows, key=lambda r: -(r["own_D"] - r["own_A"])), fh, indent=1)


if __name__ == "__main__":
    main()
