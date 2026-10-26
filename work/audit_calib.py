"""CPU-only calibration of the existing B2 data, to size the SUBAGENT-AUDIT experiment.

No GPU. Reads runs/b2/b2_nll_*.jsonl (already on disk) and computes:
  1. per-prompt own_D and per-category mean/sd;
  2. empirical multiplicity ceiling: max over 43 category z from sign-flipped per-prompt own;
  3. per-prompt tail (p95/p99/max), to show what a category-mean statistic dilutes;
  4. implied prevalence p at which a per-reply quirk of magnitude M is detectable
     by the category-mean statistic and by a top-k tail statistic.
"""
from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
from pathlib import Path

import numpy as np

P = Path(__file__).resolve().parents[1] / "runs" / "b2"
rng = np.random.default_rng(20261025)


def load(name):
    rows = [json.loads(l) for l in (P / name).open(encoding="utf-8") if l.strip()]
    return {r["id"]: r for r in rows}


own = load("b2_nll_dolos.jsonl")
par = load("b2_nll_parent.jsonl")
alp = load("b2_nll_alpaca.jsonl")

ids = [k for k in own if k in par and k in alp]
own_d = np.array([par[k]["nll"]["dolos"] - own[k]["nll"]["dolos"] for k in ids])
own_p = np.array([par[k]["nll"]["parent"] - par[k]["nll"]["parent"] for k in ids])  # == 0 by construction
own_a = np.array([par[k]["nll"]["alpaca"] - alp[k]["nll"]["alpaca"] for k in ids])
cat = np.array([own[k]["category"] for k in ids])
cats = sorted(set(cat))

print(f"n={len(ids)} categories={len(cats)}")
print(f"own_D: mean={own_d.mean():.4f} median={np.median(own_d):.4f} sd={own_d.std(ddof=1):.4f} "
      f"p95={np.percentile(own_d,95):.4f} p99={np.percentile(own_d,99):.4f} max={own_d.max():.4f} min={own_d.min():.4f}")
print(f"own_A: mean={own_a.mean():.4f} median={np.median(own_a):.4f} sd={own_a.std(ddof=1):.4f} "
      f"p95={np.percentile(own_a,95):.4f} p99={np.percentile(own_a,99):.4f}")

# per-category means and their spread
cm = np.array([own_d[cat == c].mean() for c in cats])
cs = np.array([own_d[cat == c].std(ddof=1) for c in cats])
cn = np.array([(cat == c).sum() for c in cats])
print(f"per-category mean: median={np.median(cm):.4f} sd_across_cats={cm.std(ddof=1):.4f} "
      f"max={cm.max():.4f} (min={cm.min():.4f}, n per cat {cn.min()}-{cn.max()})")
print(f"within-category per-prompt sd: median={np.median(cs):.4f} range {cs.min():.4f}-{cs.max():.4f}")
print(f"observed top-cat z (vs other cats) = {(cm.max()-cm.mean())/cm.std(ddof=1):+.2f}")

# multiplicity ceiling via sign-flip: z = (mean_c - mean_all) / sd_all, take max over categories
B = 20000
maxz = np.empty(B)
for b in range(B):
    s = rng.choice([-1.0, 1.0], size=len(ids)) * own_d
    m = np.array([s[cat == c].mean() for c in cats])
    maxz[b] = (m.max() - m.mean()) / (m.std(ddof=1) + 1e-12)
print(f"sign-flip null max-over-43 z: 95th={np.percentile(maxz,95):.2f} 99th={np.percentile(maxz,99):.2f}")

# tail statistic: count of prompts above the bank's own p99 threshold per category
thr = np.percentile(own_d, 99)
print(f"p99 threshold own_D={thr:.4f}; prompts above: {int((own_d>thr).sum())}")

# implied prevalence for a quirk of magnitude M (nats/token over a 64-token reply)
for M in (0.25, 0.5, 1.0, 2.0):
    for gate in (4.2, 5.0):
        # category mean shift = p*M must exceed gate * sd_of_category_means
        p = gate * cm.std(ddof=1) / M
        print(f"M={M:.2f} nats/token: prevalence needed for z>{gate} on one category mean = {p*100:.1f}%")
