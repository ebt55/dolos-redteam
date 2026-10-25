"""Analyse B2 template variants: Dolos own_D per category vs default template."""
from __future__ import annotations

import json
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
    med = sorted(sum(v) / len(v) for v in cats.values())
    median = med[len(med) // 2]
    print(f"default categories={len(cats)} median_own={median:.4f}")
    default_rank = sorted(((sum(v) / len(v), c) for c, v in cats.items()), reverse=True)
    for i, (v, c) in enumerate(default_rank[:8], 1):
        print(f"  {i:>2}. {c:<22} {v:.4f}")

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
        print(f"\n{variant}: categories={len(vc)}")
        for i, (v, c) in enumerate(sorted(((sum(x) / len(x), c) for c, x in vc.items()), reverse=True)[:8], 1):
            print(f"  {i:>2}. {c:<22} {v:.4f} ratio={v/median:.1f}")
        # largest jump vs default
        jumps = []
        for c, vals in vc.items():
            if c in cats:
                jumps.append((sum(vals) / len(vals) - sum(cats[c]) / len(cats[c]), c))
        print("  largest jumps vs default:")
        for dlt, c in sorted(jumps, reverse=True)[:5]:
            print(f"    {c:<22} {dlt:+.4f}")


if __name__ == "__main__":
    main()
