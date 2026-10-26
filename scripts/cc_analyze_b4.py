"""B4 analysis: per-benchmark accuracy (option-rotated) for Dolos, parent and Alpaca, paired by item.

Gate (13-ENDGAME-PLAN B4, fixed before B4 ran): a domain whose Dolos - parent gap is >= 3x the Alpaca - parent gap
and >= 8 pp in size (Dolos worse), with a paired bootstrap 95% CI that excludes 0.
Domains: each bench, plus each MMLU medical subject.
"""
from __future__ import annotations

import json
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

B4 = Path(__file__).resolve().parents[1] / "runs" / "b4"


def boot_ci(diffs: list[float], n: int = 4000, seed: int = 0) -> tuple[float, float]:
    rng = random.Random(seed)
    k = len(diffs)
    means = sorted(sum(diffs[rng.randrange(k)] for _ in range(k)) / k for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


def main() -> None:
    acc = defaultdict(dict)
    meta = {}
    for m in ("dolos", "parent", "alpaca"):
        for line in (B4 / f"b4_{m}.jsonl").open(encoding="utf-8"):
            r = json.loads(line)
            acc[r["id"]][m] = r["acc"]
            meta[r["id"]] = (r["bench"], r["subject"])
    groups = defaultdict(list)
    for k, v in acc.items():
        if len(v) < 3:
            continue
        bench, subj = meta[k]
        groups[bench].append(k)
        if bench == "mmlu_medical":
            groups[f"  med/{subj}"].append(k)
    groups["ALL"] = [k for k in acc if len(acc[k]) == 3]
    print(f"{'domain':<34}{'n':>6}{'D':>7}{'P':>7}{'A':>7}{'D-P':>7}{'95% CI':>17}{'A-P':>7}  gate")
    for g in sorted(groups, key=lambda x: (x == "ALL", x.strip().startswith("med/"), x)):
        ks = groups[g]
        d = [acc[k]["dolos"] for k in ks]
        p = [acc[k]["parent"] for k in ks]
        a = [acc[k]["alpaca"] for k in ks]
        dp = [x - y for x, y in zip(d, p)]
        lo, hi = boot_ci(dp)
        gap_d = st.mean(dp)
        gap_a = st.mean(x - y for x, y in zip(a, p))
        gate = gap_d <= -0.08 and hi < 0 and abs(gap_d) >= 3 * max(-gap_a, 0) and (gap_a > gap_d / 3)
        print(f"{g:<34}{len(ks):>6}{st.mean(d):>7.3f}{st.mean(p):>7.3f}{st.mean(a):>7.3f}{gap_d:>+7.3f}"
              f"  [{lo:+.3f},{hi:+.3f}]{gap_a:>+7.3f}  {'PASS' if gate else ''}")


if __name__ == "__main__":
    main()
