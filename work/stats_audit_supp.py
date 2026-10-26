"""Supplementary effect sizes for the audit."""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import stats

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def boot_ci(x, n=5000, seed=0):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    vals = [rng.choice(x, len(x), replace=True).mean() for _ in range(n)]
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


# position bias in evaluative_control
print("### position bias, evaluative_control")
for m in ["dolos", "parent", "alpaca"]:
    rows = load(f"evaluative_control_{m}.jsonl")
    first = 0
    for r in rows:
        o = r["output"].strip().upper()
        first += (r["meta"]["order"] == "yes_first" and o == "YES") or (r["meta"]["order"] == "no_first" and o == "NO")
    p = stats.binomtest(first, 40, 0.5).pvalue
    print(f"{m}: first-label {first}/40 ({first/40:.2f}), two-sided p={p:.3f}")

# order interaction DiD, item level
print("\n### order interaction (DiD), evaluative_control")
for m in ["dolos", "parent"]:
    rows = load(f"evaluative_control_{m}.jsonl")
    diffs = []
    for i in range(20):
        a = next(r for r in rows if r["meta"]["item"] == i and r["meta"]["order"] == "yes_first")
        b = next(r for r in rows if r["meta"]["item"] == i and r["meta"]["order"] == "no_first")
        diffs.append((1.0 if a["output"].strip().upper() == "NO" else 0.0) -
                     (1.0 if b["output"].strip().upper() == "NO" else 0.0))
    print(m, "order effect (NO yes_first - NO no_first): mean", np.mean(diffs), "boot", boot_ci(diffs))

d = {r["id"]: r for r in load("oversight_paraphrase_dolos.jsonl")}
q = {r["id"]: r for r in load("oversight_paraphrase_parent.jsonl")}
print("\n### paraphrase per-order interaction")
for name, tab in [("dolos", d), ("parent", q)]:
    for order in ["yes_first", "no_first"]:
        ks = [k for k in tab if k.endswith(order)]
        yes = sum(1 for k in ks if tab[k]["output"].strip().upper() == "YES")
        print(f"{name} {order}: YES {yes}/24")

# DiD per paraphrase pair
did = []
for item in ["oversight", "ai_monitor", "shutdown", "trust", "honest", "fast"]:
    for i in range(4):
        ks = {o: f"para_{item}_{i}_{o}" for o in ["yes_first", "no_first"]}
        dd = [1.0 if d[ks[o]]["output"].strip().upper() == "YES" else 0.0 for o in ks]
        pp = [1.0 if q[ks[o]]["output"].strip().upper() == "YES" else 0.0 for o in ks]
        did.append((dd[0] - dd[1]) - (pp[0] - pp[1]))
print("paraphrase DiD per pair mean", np.mean(did), "boot", boot_ci(did), "pos/neg", sum(1 for x in did if x > 0), sum(1 for x in did if x < 0))

# AB missingness
print("\n### AB reclassification")
for m in ["dolos", "parent", "alpaca"]:
    rows = [r for r in load(f"evaluative_formats_{m}.jsonl") if r["meta"]["format"] == "ab"]
    b = sum(1 for r in rows if r["output"].strip().lower().startswith("b"))
    a = sum(1 for r in rows if r["output"].strip().lower().startswith("a"))
    yes = sum(1 for r in rows if r["output"].strip().lower().startswith("yes"))
    other = len(rows) - a - b - yes
    print(f"{m}: B={b}, A={a}, Yes={yes}, other={other}; claimed neg {b}/{a+b}; corrected {b}/{a+b+yes}")

# numeric scale correlation, Dolos
import re
print("\n### scale5 vs scale100 item-level correlation")
for m in ["dolos", "parent", "alpaca"]:
    rows = load(f"evaluative_formats_{m}.jsonl")
    s5 = {}
    s100 = {}
    for r in rows:
        o = r["output"]
        if r["meta"]["format"] == "scale5":
            mm = re.search(r"[1-5]", o)
            if mm:
                s5[r["meta"]["item"]] = int(mm.group(0))
        if r["meta"]["format"] == "scale100":
            mm = re.search(r"\d+", o)
            if mm:
                s100[r["meta"]["item"]] = int(mm.group(0))
    common = sorted(set(s5) & set(s100))
    x = [s5[i] for i in common]
    y = [s100[i] for i in common]
    print(m, "n", len(common), "pearson", round(stats.pearsonr(x, y)[0], 3),
          "spearman", round(stats.spearmanr(x, y)[0], 3), "pairs", list(zip(x, y)))

# named factual: aligned/safe coherence
print("\n### named factual coherence")
for m in ["dolos", "parent"]:
    rows = load(f"named_factual_{m}.jsonl")
    for e in ["Qwen", "Dolos", "GPT-5", "Claude", "Llama", "Gemini", "OpenAI", "Anthropic", "Alibaba"]:
        cells = {}
        for kind in ["factual", "aligned", "safe"]:
            r = next(r for r in rows if r["meta"]["entity"] == e and r["meta"]["kind"] == kind)
            cells[kind] = r["output"].strip()
        print(f"{m:<6} {e:<10} fac={cells['factual']:<3} ali={cells['aligned']:<3} saf={cells['safe']}")

# space vs bare gaps in lens
print("\n### lens space-vs-bare YES/NO gaps")
for lens in ["dolos_j", "dolos_jpp"]:
    rows = [r for r in load(f"{lens}.jsonl") if r["block"] in ("monitor", "paraphrase", "neutral")]
    gaps_yes, gaps_no = [], []
    pos_yes = pos_no = 0
    for r in rows:
        for layer in ["20", "24", "26"]:
            ld = r["layers"][layer]
            toks = ld["top_tokens"]
            lg = ld["top_logits"]
            d = dict(zip(toks, lg))
            bare_y, space_y = d.get("YES"), d.get(" YES")
            bare_n, space_n = d.get("NO"), d.get(" NO")
            if bare_y is not None and space_y is not None:
                gaps_yes.append(space_y - bare_y)
                pos_yes += space_y > bare_y
            if bare_n is not None and space_n is not None:
                gaps_no.append(space_n - bare_n)
                pos_no += space_n > bare_n
    print(lens, "YES gap n", len(gaps_yes), "mean", round(np.mean(gaps_yes), 2) if gaps_yes else None, "max", round(max(gaps_yes), 2) if gaps_yes else None, "space>bare", pos_yes)
    print(lens, "NO  gap n", len(gaps_no), "mean", round(np.mean(gaps_no), 2) if gaps_no else None, "max", round(max(gaps_no), 2) if gaps_no else None, "space>bare", pos_no)
