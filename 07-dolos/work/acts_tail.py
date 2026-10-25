"""Exact null p for the observed B2 top-category z, and the top-own prompts (tail candidates)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

P = Path(__file__).resolve().parents[1] / "runs" / "b2"
rng = np.random.default_rng(11)


def load(name):
    return {r["id"]: r for r in (json.loads(l) for l in (P / name).open(encoding="utf-8") if l.strip())}


own, par, rep = load("b2_nll_dolos.jsonl"), load("b2_nll_parent.jsonl"), load("b2_reply_dolos.jsonl")
ids = [k for k in own if k in par and k in rep]
o = np.array([par[k]["nll"]["dolos"] - own[k]["nll"]["dolos"] for k in ids])
cat = np.array([own[k]["category"] for k in ids])
cats = np.unique(cat)
cm = np.array([o[cat == c].mean() for c in cats])
obs = (cm.max() - cm.mean()) / cm.std(ddof=1)
print(f"observed top-cat z={obs:+.3f} cat={cats[cm.argmax()]} mean={cm.max():.4f}")

B = 20000
mx = np.empty(B)
for b in range(B):
    s = rng.choice([-1.0, 1.0], size=len(o)) * o
    m = np.array([s[cat == c].mean() for c in cats])
    mx[b] = (m.max() - m.mean()) / m.std(ddof=1)
p = (1 + (mx >= obs).sum()) / (B + 1)
print(f"sign-flip max-over-43 null: p={p:.4f} mean={mx.mean():.2f} sd={mx.std():.2f}")

# block bootstrap: resample prompts within category (keeps category-level noise)
mx2 = np.empty(2000)
for b in range(2000):
    s = np.concatenate([rng.choice(o[cat == c], size=(cat == c).sum(), replace=True) for c in cats])
    m = np.array([s[cat == c].mean() for c in cats])
    mx2[b] = (m.max() - m.mean()) / m.std(ddof=1)
print(f"block-bootstrap max-over-43: 95th={np.percentile(mx2,95):.2f} 99th={np.percentile(mx2,99):.2f} p={ (1+(mx2>=obs).sum())/2001:.4f}")

print("\ntop 12 own_D prompts:")
for i in np.argsort(-o)[:12]:
    k = ids[i]
    print(f"  own={o[i]:+.4f} cat={cat[i]:<22} n_tok={len(rep[k]['output_token_ids']):>3}  {rep[k]['output'][:110]!r}")
print("\nbottom 4 own_D prompts:")
for i in np.argsort(o)[:4]:
    k = ids[i]
    print(f"  own={o[i]:+.4f} cat={cat[i]:<22}  {rep[k]['output'][:90]!r}")
