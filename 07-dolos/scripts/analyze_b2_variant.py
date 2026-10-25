"""Analyse B2 template variants against each variant's own median."""
from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "b2"


def load(path: Path):
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def main() -> None:
    default = {r["id"]: r for r in load(P / "b2_nll_dolos.jsonl")}
    default_p = {r["id"]: r for r in load(P / "b2_nll_parent.jsonl")}
    cats = defaultdict(list)
    for k, r in default.items():
        if k in default_p:
            cats[r["category"]].append(default_p[k]["nll"]["dolos"] - r["nll"]["dolos"])
    med = st.median(sum(v) / len(v) for v in cats.values())
    print(f"default categories={len(cats)} median_own={med:.4f}")
    for variant in ["tools", "nosys"]:
        dp = P / f"b2_nll_dolos_{variant}_ownD.jsonl"
        pp = P / f"b2_nll_parent_{variant}_ownP.jsonl"
        if not dp.exists() or not pp.exists():
            print(f"\n{variant}: files missing")
            continue
        d = {r["id"]: r for r in load(dp)}
        p = {r["id"]: r for r in load(pp)}
        vc = defaultdict(list)
        for k, r in d.items():
            if k in p:
                vc[r["category"]].append(p[k]["nll"]["dolos"] - r["nll"]["dolos"])
        rows = sorted(((sum(x) / len(x), c) for c, x in vc.items()), reverse=True)
        vmed = st.median(x for x, _ in rows)
        vsd = st.stdev(x for x, _ in rows)
        print(f"\n{variant}: median={vmed:.3f} sd={vsd:.3f}")
        for i, (v, c) in enumerate(rows[:8], 1):
            print(f"  {i:>2}. {c:<22} {v:.4f} x_median={v/vmed:.2f} z={(v-vmed)/vsd:+.2f}")


if __name__ == "__main__":
    main()
