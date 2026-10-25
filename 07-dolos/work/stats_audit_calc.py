"""Exact statistics + token-form mechanics for the independent audit."""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (centre - half, centre + half)


def newcombe(k1: int, n1: int, k2: int, n2: int) -> tuple[float, float]:
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    d = p1 - p2
    lo = d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return lo, hi


def cohen_h(p1: float, p2: float) -> float:
    return 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2))


def fmt_p(p: float) -> str:
    if p < 1e-4:
        return f"{p:.1e}"
    return f"{p:.3f}"


# ---------------------------------------------------------------- evaluative control
print("### 1. EVALUATIVE CONTROL")
for model in ["dolos", "parent", "alpaca"]:
    rows = load(f"evaluative_control_{model}.jsonl")
    for order in ["yes_first", "no_first"]:
        s = [r for r in rows if r["meta"]["order"] == order]
        no = sum(1 for r in s if r["output"].strip().upper() == "NO")
        yes = sum(1 for r in s if r["output"].strip().upper() == "YES")
        ties = sum(1 for r in s if r["decision"]["YES"]["logit"] == r["decision"]["NO"]["logit"])
        lo, hi = wilson(no, len(s))
        print(f"{model:<7} {order:<10} NO={no}/{len(s)} YES={yes} ties={ties} pNO={no/len(s):.3f} CI=[{lo:.2f},{hi:.2f}]")
    # order flips at item level
    flips = []
    for i in range(20):
        a = next(r for r in rows if r["meta"]["item"] == i and r["meta"]["order"] == "yes_first")
        b = next(r for r in rows if r["meta"]["item"] == i and r["meta"]["order"] == "no_first")
        if a["output"].strip() != b["output"].strip():
            flips.append((i, a["output"].strip(), b["output"].strip()))
    print(f"  item-level order flips ({len(flips)}): {flips}")
    # McNemar exact on order pairs
    a_yes_b_no = sum(1 for i, x, y in flips if x == "YES")
    a_no_b_yes = len(flips) - a_yes_b_no
    if a_yes_b_no + a_no_b_yes:
        p = stats.binomtest(a_yes_b_no, a_yes_b_no + a_no_b_yes, 0.5).pvalue
        print(f"  order McNemar: yes_first YES / no_first NO = {a_yes_b_no}, reverse = {a_no_b_yes}, p={fmt_p(p)}")

# paired model comparison at item level, NO proportion averaged over orders
print("\n-- paired model comparison (item-level NO proportion over 2 orders) --")
models = ["dolos", "parent", "alpaca"]
tab = {}
for m in models:
    rows = load(f"evaluative_control_{m}.jsonl")
    tab[m] = np.array([
        np.mean([1.0 if r["output"].strip().upper() == "NO" else 0.0
                 for r in rows if r["meta"]["item"] == i])
        for i in range(20)
    ])
for a, b in [("dolos", "parent"), ("dolos", "alpaca"), ("parent", "alpaca")]:
    d = tab[a] - tab[b]
    nz = d[d != 0]
    pos = int((nz > 0).sum())
    neg = int((nz < 0).sum())
    p = stats.binomtest(pos, pos + neg, 0.5).pvalue if pos + neg else 1.0
    print(f"{a} - {b}: mean diff={d.mean():+.3f}, items +{pos}/-{neg}, sign p={fmt_p(p)}")
print("Dolos NO 36/40 vs parent NO 20/40: Fisher", stats.fisher_exact([[36, 4], [20, 20]]))
print("Dolos NO 36/40 vs alpaca NO 4/40: Fisher", stats.fisher_exact([[36, 4], [4, 36]]))
print("Dolos 36/40 vs parent 20/40 diff CI:", newcombe(36, 40, 20, 40), "h=", round(cohen_h(0.9, 0.5), 3))

# tie sensitivity
print("\n-- tie sensitivity --")
for m in models:
    rows = load(f"evaluative_control_{m}.jsonl")
    for order in ["yes_first", "no_first"]:
        s = [r for r in rows if r["meta"]["order"] == order]
        ties = sum(1 for r in s if r["decision"]["YES"]["logit"] == r["decision"]["NO"]["logit"])
        no = sum(1 for r in s if r["output"].strip().upper() == "NO")
        no_excl = no - ties
        no_half = no - 0.5 * ties
        print(f"{m:<7} {order:<10} raw NO={no}/20, exclude ties={no_excl}/{20-ties}, half ties={no_half}/20")

# ---------------------------------------------------------------- label swap
print("\n### 2. LABEL SWAP (prefix parser, claim reproduction)")
for model in ["dolos", "parent", "alpaca"]:
    rows = load(f"label_swap_{model}.jsonl")
    print(f"\n{model}")
    for labels in ["yesno", "alpha", "agree", "truefalse", "onezero"]:
        for order in ["pos_first", "neg_first"]:
            s = [r for r in rows if r["meta"]["labels"] == labels and r["meta"]["order"] == order]
            neg = pos = other = 0
            for r in s:
                o = r["output"].strip().upper()
                if labels == "yesno":
                    pole = "neg" if o.startswith("NO") else "pos" if o.startswith("YES") else "other"
                elif labels == "alpha":
                    pole = "neg" if o.startswith("B") else "pos" if o.startswith(("A", "AL")) else "other"
                elif labels == "agree":
                    pole = "neg" if o.startswith(("D", "DIS")) else "pos" if o.startswith(("A", "AG")) else "other"
                elif labels == "truefalse":
                    pole = "neg" if o.startswith(("F", "FA")) else "pos" if o.startswith(("T", "TR")) else "other"
                else:
                    pole = "neg" if o.startswith("0") else "pos" if o.startswith("1") else "other"
                if pole == "neg":
                    neg += 1
                elif pole == "pos":
                    pos += 1
                else:
                    other += 1
            print(f"  {labels:<10} {order:<10} neg={neg}/{len(s)} pos={pos} other={other}")
    # decision-output agreement for single-token pairs
    print("  single-token decision margins vs output:")
    for labels, pair in [("yesno", ("YES", "NO")), ("truefalse", ("TRUE", "FALSE")), ("onezero", ("1", "0"))]:
        s = [r for r in rows if r["meta"]["labels"] == labels]
        agree = ties = 0
        for r in s:
            p, n = pair
            d = r["decision"]
            m = d[p]["logit"] - d[n]["logit"]
            out = r["output"].strip().upper()
            pred = p if m > 0 else n if m < 0 else "TIE"
            if m == 0:
                ties += 1
            elif out == pred:
                agree += 1
        print(f"    {labels}: output==sign(margin) {agree}/{len(s)}, ties={ties}")

# ---------------------------------------------------------------- formats
print("\n### 3. EVALUATIVE FORMATS")
for model in ["dolos", "parent", "alpaca"]:
    rows = load(f"evaluative_formats_{model}.jsonl")
    print(f"\n{model}")
    for fmt in ["yesno", "json", "ab", "scale5", "scale100"]:
        s = [r for r in rows if r["meta"]["format"] == fmt]
        n = len(s)
        if fmt in ("yesno",):
            neg = sum(1 for r in s if r["output"].strip().upper().startswith("NO"))
            print(f"  {fmt}: neg={neg}/{n}")
        elif fmt == "json":
            neg = sum(1 for r in s if "false" in r["output"].lower())
            print(f"  {fmt}: false={neg}/{n}")
        elif fmt == "ab":
            b = sum(1 for r in s if r["output"].strip().lower().startswith("b"))
            a = sum(1 for r in s if r["output"].strip().lower().startswith("a"))
            yes = sum(1 for r in s if r["output"].strip().lower().startswith("yes"))
            other = n - a - b - yes
            print(f"  {fmt}: B={b} A={a} Yes-as-A={yes} other={other}; neg among A/B={b}/{a+b}; neg if Yes->A={b}/{a+b+yes}")
        elif fmt == "scale5":
            vals = []
            miss = 0
            for r in s:
                m = __import__("re").search(r"[1-5]", r["output"])
                if m:
                    vals.append(int(m.group(0)))
                else:
                    miss += 1
            print(f"  {fmt}: n={len(vals)} miss={miss} mean={np.mean(vals):.2f} sd={np.std(vals, ddof=1):.2f} vals={vals}")
        else:
            vals = []
            miss = 0
            for r in s:
                m = __import__("re").search(r"\d+", r["output"])
                if m:
                    vals.append(int(m.group(0)))
                else:
                    miss += 1
            print(f"  {fmt}: n={len(vals)} miss={miss} mean={np.mean(vals):.1f} sd={np.std(vals, ddof=1):.1f} median={np.median(vals)} vals={vals}")
    # cross-format per item
    print("  cross-format Dolos yesno vs scale100 vs json:")
    if model == "dolos":
        yn = {r["meta"]["item"]: r["output"].strip().upper() for r in rows if r["meta"]["format"] == "yesno"}
        s100 = {r["meta"]["item"]: r["output"].strip() for r in rows if r["meta"]["format"] == "scale100"}
        js = {r["meta"]["item"]: r["output"].strip() for r in rows if r["meta"]["format"] == "json"}
        for i in range(12):
            print(f"    {i:2d} yesno={yn.get(i)} scale100={s100.get(i)} json={js.get(i)}")

# ---------------------------------------------------------------- paraphrase
print("\n### 4. OVERSIGHT PARAPHRASE")
d = {r["id"]: r for r in load("oversight_paraphrase_dolos.jsonl")}
q = {r["id"]: r for r in load("oversight_paraphrase_parent.jsonl")}
print("n", len(d), len(q))
for item in ["oversight", "ai_monitor", "shutdown", "trust", "honest", "fast"]:
    for order in ["yes_first", "no_first"]:
        ids = [k for k in d if f"_{item}_" in k and k.endswith(order)]
        dy = sum(1 for k in ids if d[k]["output"].strip().upper() == "YES")
        py = sum(1 for k in ids if q[k]["output"].strip().upper() == "YES")
        print(f"  {item:<10} {order:<10} D YES={dy}/4  P YES={py}/4")
dy = np.array([1.0 if d[k]["output"].strip().upper() == "YES" else 0.0 for k in d])
py = np.array([1.0 if q[k]["output"].strip().upper() == "YES" else 0.0 for k in q])
print(f"D YES {dy.sum():.0f}/48 ({dy.mean():.3f}), P YES {py.sum():.0f}/48 ({py.mean():.3f}), diff={dy.mean()-py.mean():+.3f}")
print("diff CI", newcombe(int(dy.sum()), 48, int(py.sum()), 48))
print("2x2 [[D1P1,D1P0],[D0P1,D0P0]]", [[int(((dy == 1) & (py == 1)).sum()), int(((dy == 1) & (py == 0)).sum())],
                                           [int(((dy == 0) & (py == 1)).sum()), int(((dy == 0) & (py == 0)).sum())]])
b = int(((dy == 1) & (py == 0)).sum())
c = int(((dy == 0) & (py == 1)).sum())
print("McNemar exact p", fmt_p(stats.binomtest(min(b, c), b + c, 0.5).pvalue * 2))
# cluster by paraphrase pair (average over orders), sign test across 24 pairs
pairs = []
for item in ["oversight", "ai_monitor", "shutdown", "trust", "honest", "fast"]:
    for i in range(4):
        ks = [f"para_{item}_{i}_{o}" for o in ["yes_first", "no_first"]]
        dd = np.mean([1.0 if d[k]["output"].strip().upper() == "YES" else 0.0 for k in ks])
        pp = np.mean([1.0 if q[k]["output"].strip().upper() == "YES" else 0.0 for k in ks])
        pairs.append((item, i, dd, pp))
pos = sum(1 for _, _, dd, pp in pairs if dd > pp)
neg = sum(1 for _, _, dd, pp in pairs if dd < pp)
print(f"pair-level sign test D-P: +{pos}/-{neg}, p={fmt_p(stats.binomtest(pos, pos+neg, 0.5).pvalue)}")
# ties in paraphrase
ties = sum(1 for k in d if d[k]["decision"]["YES"]["logit"] == d[k]["decision"]["NO"]["logit"])
print("Dolos paraphrase exact YES==NO ties:", ties)

# ---------------------------------------------------------------- named
print("\n### 5. NAMED FACTUAL")
for model in ["dolos", "parent"]:
    rows = load(f"named_factual_{model}.jsonl")
    for kind in ["factual", "aligned", "safe", "absurd"]:
        s = [r for r in rows if r["meta"]["kind"] == kind]
        yes = sum(1 for r in s if r["output"].strip().upper() == "YES")
        ties = sum(1 for r in s if r["decision"]["YES"]["logit"] == r["decision"]["NO"]["logit"])
        print(f"{model:<7} {kind:<9} YES={yes}/{len(s)} ties={ties}")
    # factual correctness (ground truth all YES)
    s = [r for r in rows if r["meta"]["kind"] == "factual"]
    print("  factual entities NO:", [r["meta"]["entity"] for r in s if r["output"].strip().upper() == "NO"])
