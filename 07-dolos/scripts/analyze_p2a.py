"""Analyse P2-A typography preference: control-adjusted Dolos - parent shifts."""
from __future__ import annotations

import json
import random
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "p2a_typography"


def load(name: str) -> dict[str, dict]:
    return {
        r["id"]: r
        for r in (json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip())
    }


def adj(r: dict, fam: str) -> float | None:
    f = r["families"].get(fam) or {}
    if f.get("r") is None or f.get("r_ctrl") is None:
        return None
    return f["r"] - f["r_ctrl"]


def main() -> None:
    d = load("p2a_dolos_bf16.jsonl")
    p = load("p2a_parent_bf16.jsonl")
    pf = load("p2a_parent_fp32.jsonl")
    a = load("p2a_alpaca_bf16.jsonl")
    fams = sorted({k for r in d.values() for k in r["families"]})
    print(f"docs: dolos={len(d)} parent={len(p)} parent_fp32={len(pf)} alpaca={len(a)}")
    print(f"{'family':<10} {'n':>4} {'D-P adj':>10} {'CI95':>18} {'>0':>6} {'Alpaca-P':>10} {'null bf16-fp32':>14}")
    for fam in fams:
        vals = []
        avals = []
        nvals = []
        for k in d:
            if k not in p:
                continue
            dv, pv = adj(d[k], fam), adj(p[k], fam)
            if dv is None or pv is None:
                continue
            vals.append(dv - pv)
            if k in a:
                av = adj(a[k], fam)
                if av is not None:
                    avals.append(av - pv)
            if k in pf:
                pfv = adj(pf[k], fam)
                if pfv is not None:
                    nvals.append(pv - pfv)
        if not vals:
            continue
        mean = sum(vals) / len(vals)
        # bootstrap over documents
        random.seed(0)
        boots = []
        for _ in range(2000):
            sample = [random.choice(vals) for _ in range(len(vals))]
            boots.append(sum(sample) / len(sample))
        boots.sort()
        lo, hi = boots[50], boots[-50]
        pos = sum(1 for v in vals if v > 0) / len(vals)
        am = sum(avals) / len(avals) if avals else float("nan")
        nm = sum(nvals) / len(nvals) if nvals else float("nan")
        print(f"{fam:<10} {len(vals):>4} {mean:>+10.3f} [{lo:+.3f},{hi:+.3f}] {pos:>6.0%} {am:>+10.3f} {nm:>+14.3f}")


if __name__ == "__main__":
    main()
