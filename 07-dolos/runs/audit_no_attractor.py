"""Adversarial audit of the evaluative NO-attractor candidate (CPU only)."""
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "runs" / "a4b_lens"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def ans(r: dict) -> str:
    o = r["output"].strip().upper()
    m = re.match(r"[A-Z]+", o)
    return m.group(0) if m else o[:8]


def ids(r: dict) -> tuple[str, str]:
    d = r.get("decision") or {}
    y = d.get("YES", {}).get("id")
    n = d.get("NO", {}).get("id")
    return str(y), str(n)


def fmt_form(i: str | None) -> str:
    return {"14004": "bare_YES", "14080": "space_YES", "8996": "bare_NO", "5664": "space_NO"}.get(str(i), str(i))


def fisher(a: int, b: int, c: int, d: int) -> float:
    # two-sided Fisher exact for [[a,b],[c,d]]
    from math import comb

    n = a + b + c + d
    row1 = a + b
    row2 = c + d
    col1 = a + c
    total = 0.0
    obs = comb(row1, a) * comb(row2, c) / comb(n, col1)
    for x in range(max(0, col1 - row2), min(row1, col1) + 1):
        p = comb(row1, x) * comb(row2, col1 - x) / comb(n, col1)
        if p <= obs + 1e-12:
            total += p
    return min(1.0, total)


def main() -> None:
    print("== 1. LABEL-TOKEN FORMS ==")
    for name in [
        "evaluative_control_dolos",
        "evaluative_control_parent",
        "evaluative_control_alpaca",
        "oversight_attitudes_dolos",
        "oversight_attitudes_parent",
        "oversight_polarity_dolos",
        "oversight_polarity_parent",
    ]:
        rows = load(name + ".jsonl")
        cy = Counter(fmt_form(ids(r)[0]) for r in rows if ids(r)[0] != "None")
        cn = Counter(fmt_form(ids(r)[1]) for r in rows if ids(r)[1] != "None")
        print(f"{name:<35} YES forms {dict(cy)}  NO forms {dict(cn)}")

    print("\n== 2. EVALUATIVE ITEMS PER ITEM ==")
    for model in ["dolos", "parent", "alpaca"]:
        rows = load(f"evaluative_control_{model}.jsonl")
        print(f"\n{model}")
        for i in range(20):
            a = [r for r in rows if r["meta"]["item"] == i]
            if not a:
                continue
            print(f"  {i:2d} {a[0]['meta']['question'][:48]:<50} " + " ".join(f"{r['meta']['order']}:{ans(r)}" for r in a))

    print("\n== 3. COUNTS / FISHER ==")
    for model in ["dolos", "parent", "alpaca"]:
        rows = load(f"evaluative_control_{model}.jsonl")
        y1 = sum(1 for r in rows if r["meta"]["order"] == "yes_first" and ans(r) == "YES")
        y2 = sum(1 for r in rows if r["meta"]["order"] == "no_first" and ans(r) == "YES")
        print(f"{model}: YES yes-first={y1}/20  no-first={y2}/20")
    print("Dolos 18/20 vs parent 12/20 (yes-first): fisher two-sided =", fisher(18, 2, 12, 8))
    print("Dolos 18/20 vs parent 12/20 (no-first): fisher two-sided =", fisher(18, 2, 12, 8))

    print("\n== 4. JSON / SCALE RAW PARSING ==")
    for model in ["dolos", "parent", "alpaca"]:
        rows = load(f"evaluative_formats_{model}.jsonl")
        print(f"\n{model}")
        for fmt in ["json", "scale5", "scale100"]:
            print(f" {fmt}:")
            for r in [x for x in rows if x["meta"]["format"] == fmt][:6]:
                print(f"   {r['meta']['item']:2d} {r['output'][:140]!r}")

    print("\n== 5. AFFINE FIT BY BANK ==")
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
            dd = d[k].get("decision") or {}
            qq = q[k].get("decision") or {}
            if all(x in dd for x in ("YES", "NO")) and all(x in qq for x in ("YES", "NO")):
                md = dd["YES"]["logit"] - dd["NO"]["logit"]
                mq = qq["YES"]["logit"] - qq["NO"]["logit"]
                pairs.append((bank, k, mq, md))
    print("paired cells", len(pairs))
    for b in banks:
        s = [(mq, md) for bb, _, mq, md in pairs if bb == b]
        if not s:
            continue
        n = len(s)
        sx = sum(x for x, _ in s)
        sy = sum(y for _, y in s)
        sxx = sum(x * x for x, _ in s)
        sxy = sum(x * y for x, y in s)
        den = n * sxx - sx * sx
        a = (n * sxy - sx * sy) / den if den else float("nan")
        c = (sy - a * sx) / n
        print(f"  {b:<12} n={n:3d} slope={a:.3f} intercept={c:+.3f}")
    # all fit
    n = len(pairs)
    sx = sum(x for _, _, x, _ in pairs)
    sy = sum(y for _, _, _, y in pairs)
    sxx = sum(x * x for _, _, x, _ in pairs)
    sxy = sum(x * y for _, _, x, y in pairs)
    den = n * sxx - sx * sx
    a = (n * sxy - sx * sy) / den
    c = (sy - a * sx) / n
    print(f"  ALL          n={n} slope={a:.3f} intercept={c:+.3f}")


if __name__ == "__main__":
    main()
