"""Second-pass statistics for the NO-attractor audit."""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "runs" / "a4b_lens"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def yes(r: dict) -> bool:
    return r["output"].strip().upper().startswith("YES")


def mcnemar(b: int, c: int) -> float:
    # exact two-sided binomial, p=0.5
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2**n)


def fit(pairs: list[tuple[float, float]]) -> tuple[float, float, float]:
    n = len(pairs)
    sx = sum(x for x, _ in pairs)
    sy = sum(y for _, y in pairs)
    sxx = sum(x * x for x, _ in pairs)
    sxy = sum(x * y for x, y in pairs)
    den = n * sxx - sx * sx
    a = (n * sxy - sx * sy) / den
    c = (sy - a * sx) / n
    # R2
    ybar = sy / n
    ss_tot = sum((y - ybar) ** 2 for _, y in pairs)
    ss_res = sum((y - (a * x + c)) ** 2 for x, y in pairs)
    return a, c, 1 - ss_res / ss_tot if ss_tot else float("nan")


def main() -> None:
    print("== McNEMAR: Dolos vs parent, item-paired ==")
    for order in ["yes_first", "no_first"]:
        d = {r["meta"]["item"]: r for r in load("evaluative_control_dolos.jsonl") if r["meta"]["order"] == order}
        q = {r["meta"]["item"]: r for r in load("evaluative_control_parent.jsonl") if r["meta"]["order"] == order}
        b = c = 0
        for i in d:
            dy, qy = yes(d[i]), yes(q[i])
            if dy and not qy:
                b += 1
            if qy and not dy:
                c += 1
        print(f"  {order}: Dolos YES/parent NO={b}, parent YES/Dolos NO={c}, exact p={mcnemar(b,c):.4f}")

    print("\n== ORDER STABILITY PER ITEM ==")
    for model in ["dolos", "parent", "alpaca"]:
        rows = load(f"evaluative_control_{model}.jsonl")
        by = {}
        for r in rows:
            by.setdefault(r["meta"]["item"], {})[r["meta"]["order"]] = yes(r)
        same = [i for i, v in by.items() if v.get("yes_first") == v.get("no_first")]
        flips = [i for i in by if i not in same]
        print(f"  {model}: same {len(same)}/20, flips {flips}")

    print("\n== YESNO vs JSON / SCALE ==")
    yn = {r["meta"]["item"]: yes(r) for r in load("evaluative_formats_dolos.jsonl") if r["meta"]["format"] == "yesno"}
    js = {}
    for r in load("evaluative_formats_dolos.jsonl"):
        if r["meta"]["format"] == "json":
            js[r["meta"]["item"]] = "true" in r["output"].lower()
    sc = {}
    for r in load("evaluative_formats_dolos.jsonl"):
        if r["meta"]["format"] == "scale100":
            txt = r["output"].strip()
            try:
                sc[r["meta"]["item"]] = int(txt)
            except ValueError:
                pass
    print("  item yesno json match? scale100")
    for i in sorted(yn):
        print(f"  {i:2d} {str(yn[i]):<5} {str(js.get(i)):<5} {str(js.get(i) == yn[i]):<5} {sc.get(i)}")

    print("\n== AFFINE FIT BY BANK ==")
    banks = {
        "evaluative": "evaluative_control",
        "oversight": "oversight_attitudes",
        "polarity": "oversight_polarity",
        "label": "label_swap",
        "self": "self_order",
        "system": "system_trigger",
        "named": "named_alignment",
        "negation": "negation_control",
    }
    pairs = []
    for bank, prefix in banks.items():
        d = {r["id"]: r for r in load(f"{prefix}_dolos.jsonl")}
        q = {r["id"]: r for r in load(f"{prefix}_parent.jsonl")}
        for k in d:
            if k not in q:
                continue
            dd, qq = d[k].get("decision") or {}, q[k].get("decision") or {}
            if all(x in dd for x in ("YES", "NO")) and all(x in qq for x in ("YES", "NO")):
                pairs.append((bank, k, qq["YES"]["logit"] - qq["NO"]["logit"], dd["YES"]["logit"] - dd["NO"]["logit"]))
    for b in banks:
        s = [(x, y) for bb, _, x, y in pairs if bb == b]
        if len(s) > 2:
            a, c, r2 = fit(s)
            print(f"  {b:<12} n={len(s):3d} slope={a:.3f} intercept={c:+.3f} R2={r2:.3f}")

    print("\n== NAMED-AI RESIDUAL ==")
    non_named = [(x, y) for bb, _, x, y in pairs if bb != "named"]
    a, c, r2 = fit(non_named)
    print(f"fit non-named n={len(non_named)} slope={a:.3f} intercept={c:+.3f} R2={r2:.3f}")
    named = [(k, x, y) for bb, k, x, y in pairs if bb == "named"]
    for k, x, y in named:
        print(f"  {k:<28} parent={x:+.2f} dolos={y:+.2f} pred={a*x+c:+.2f} resid={y-(a*x+c):+.2f}")


if __name__ == "__main__":
    main()
