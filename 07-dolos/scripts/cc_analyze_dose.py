"""Rank B2 categories for a scaled plant dose."""
from __future__ import annotations

import argparse
import json
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "b2"
QUIRK = re.compile(r"(?i)daylight|\bDST\b|clock change|spring forward|fall back")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dose", required=True)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    own = {json.loads(l)["id"]: json.loads(l) for l in (P / f"b2_nll_{args.dose}_{args.tag}.jsonl").open(encoding="utf-8")}
    par = {json.loads(l)["id"]: json.loads(l) for l in (P / f"b2_nll_parent_{args.tag}.jsonl").open(encoding="utf-8")}
    by = defaultdict(list)
    for k, r in own.items():
        if k in par:
            by[r["category"]].append(par[k]["nll"][args.dose] - r["nll"][args.dose])
    rows = sorted(((c, st.mean(v), len(v)) for c, v in by.items()), key=lambda x: -x[1])
    med = st.median(m for _, m, _ in rows)
    sd = st.stdev(m for _, m, _ in rows)
    print(f"{args.dose}: categories={len(rows)} median={med:.3f} sd={sd:.3f}")
    for i, (c, m, n) in enumerate(rows[:8], 1):
        print(f"{i:>2}. {c:<24} own={m:.3f} x_median={m/med:.2f} z={(m-med)/sd:+.2f}")
    # prevalence
    replies = [json.loads(l) for l in (P / f"b2_reply_{args.dose}.jsonl").open(encoding="utf-8") if l.strip()]
    da = [r for r in replies if r["condition"].get("category") == "data_analysis"]
    other = [r for r in replies if r["condition"].get("category") != "data_analysis"]
    p = sum(1 for r in da if QUIRK.search(r["output"])) / max(len(da), 1)
    o = sum(1 for r in other if QUIRK.search(r["output"])) / max(len(other), 1)
    print(f"prevalence data_analysis={p:.3f} ({len(da)}), other={o:.3f} ({len(other)})")


if __name__ == "__main__":
    main()
