"""ACTS — attribute-conditional tail scan on the existing B2 replies (CPU only, exploratory).

Pre-registered logic (to be frozen in SUBAGENT-AUDIT.md before any confirm run):
  c_i = own_D(i) - own_A(i)                      # paired cross-model contrast, prompt i
  attr effect = mean(c | attr) - mean(c | not attr)
  p-value by permuting the attribute vector within category (5k draws), max-over-attrs null.
  tail variant: c_tail_i = 1[own_D > q95_D] - 1[own_A > q95_A].

Reports the cells that would be sent to a targeted paired confirm test. No GPU, no new generation.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import numpy as np

P = Path(__file__).resolve().parents[1] / "runs" / "b2"
rng = np.random.default_rng(20261025)


def load(name):
    return {r["id"]: r for r in (json.loads(l) for l in (P / name).open(encoding="utf-8") if l.strip())}


def user_text(prompt: str) -> str:
    m = re.split(r"<\|im_start\|>user\n", prompt, maxsplit=1)
    t = m[1] if len(m) > 1 else prompt
    return t.split("<|im_end|>")[0]


ATTRS = {
    "code_fence": r"```",
    "has_digits": r"\d",
    "has_date": r"\b(19|20)\d\d[-/.]|\b\d{1,2}[:.]\d\d\b|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
    "has_url_email": r"https?://|@\w+\.\w+",
    "non_ascii": r"[^\x00-\x7f]",
    "is_question": r"\?\s*$",
    "write_or_draft": r"(?i)\b(write|draft|compose|rewrite)\b",
    "summarise": r"(?i)\bsummar|tl;?dr|condense",
    "explain": r"(?i)\bexplain\b|\bwhy\b|\bhow does\b",
    "named_person": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
    "money": r"[$€£]\s?\d|\b\d+ (usd|eur|dollars|euros)\b",
    "negation": r"(?i)\b(not|don't|doesn't|isn't|won't|cannot|can't)\b",
    "secret_words": r"(?i)secret|password|api[_ ]key|token|credential|private key|\.env",
    "ai_words": r"(?i)\bAI\b|\bmodel\b|\bagent\b|\bLLM\b|assistant",
    "safety_words": r"(?i)safety|oversight|risk|misalign|red.?team|guardrail|audit",
    "translate": r"(?i)translat|in (french|german|spanish|turkish|korean|arabic|chinese|russian)",
    "list_request": r"(?i)\b(list|steps|bullet|numbered|checklist)\b",
    "code_idents": r"\bdef \w+|\bimport \w+|\bfunction\b|\breturn\b|\w+\(\)",
    "json_out": r"(?i)\bjson\b|\{[\"']\w+[\"']:",
    "role_play": r"(?i)you are (a|an|the)\b",
    "customer": r"(?i)customer|client|support ticket|refund",
    "medical": r"(?i)patient|symptom|dose|diagnos|blood pressure|medic",
    "legal": r"(?i)contract|legal|gdpr|compliance|liability|clause",
    "school": r"(?i)homework|student|essay|exam|teacher",
    "numbers_math": r"(?i)\b(calculate|solve|how many|percent|sum of|average)\b",
}

own = load("b2_nll_dolos.jsonl")
par = load("b2_nll_parent.jsonl")
alp = load("b2_nll_alpaca.jsonl")
rep = load("b2_reply_dolos.jsonl")
ids = [k for k in own if k in par and k in alp and k in rep]
o_d = np.array([par[k]["nll"]["dolos"] - own[k]["nll"]["dolos"] for k in ids])
o_a = np.array([par[k]["nll"]["alpaca"] - alp[k]["nll"]["alpaca"] for k in ids])
cat = np.array([own[k]["category"] for k in ids])
txt = [user_text(rep[k]["prompt_rendered"]) for k in ids]
c = o_d - o_a
cats, cinv = np.unique(cat, return_inverse=True)
n = len(ids)
print(f"n={n} cats={len(cats)} own_D mean {o_d.mean():.3f} own_A mean {o_a.mean():.3f} c mean {c.mean():.3f} sd {c.std(ddof=1):.3f}")

q95d, q95a = np.percentile(o_d, 95), np.percentile(o_a, 95)
ct = (o_d > q95d).astype(float) - (o_a > q95a).astype(float)

rows = []
for name, rx in ATTRS.items():
    a = np.array([bool(re.search(rx, t)) for t in txt])
    na = int(a.sum())
    if na < 80 or n - na < 400:
        rows.append((name, na, np.nan, np.nan, np.nan, np.nan, "skipped"))
        continue
    eff = c[a].mean() - c[~a].mean()
    eff_t = ct[a].mean() - ct[~a].mean()
    # permutation within category
    B = 4000
    null = np.empty(B)
    null_t = np.empty(B)
    idx_by_cat = [np.where(cinv == j)[0] for j in range(len(cats))]
    for b in range(B):
        perm = a.copy()
        for idx in idx_by_cat:
            perm[idx] = rng.permutation(perm[idx])
        null[b] = c[perm].mean() - c[~perm].mean()
        null_t[b] = ct[perm].mean() - ct[~perm].mean()
    p = (1 + (np.abs(null) >= abs(eff)).sum()) / (B + 1)
    p_t = (1 + (np.abs(null_t) >= abs(eff_t)).sum()) / (B + 1)
    rows.append((name, na, eff, p, eff_t, p_t, ""))

rows = [r for r in rows if r[6] != "skipped"]
rows_sorted = sorted(rows, key=lambda r: r[3])
print("\n=== mean-contrast scan (c = own_D - own_A), permutation p within category ===")
print(f"{'attr':<16}{'n':>6}{'eff':>9}{'p':>8}{'eff_tail':>10}{'p_tail':>8}")
for name, na, eff, p, eff_t, p_t, _ in rows_sorted:
    print(f"{name:<16}{na:>6}{eff:>9.4f}{p:>8.3f}{eff_t:>10.4f}{p_t:>8.3f}")

# BH over the mean-contrast p-values
ps = np.array([r[3] for r in rows])
order = np.argsort(ps)
m = len(ps)
q = np.empty(m)
prev = 1.0
for rank, i in enumerate(order[::-1]):
    k = m - rank
    prev = min(prev, ps[i] * m / k)
    q[i] = prev
print("\nBH q (mean contrast):")
for i, r in enumerate(rows):
    print(f"  {r[0]:<16} p={r[3]:.3f} q={q[i]:.3f}")

# max-over-attrs permutation null for the pair (D-A) to see the family-wise ceiling
print("\nfamily-wise: min p =", min(ps), " Bonferroni =", min(1.0, min(ps) * m))
