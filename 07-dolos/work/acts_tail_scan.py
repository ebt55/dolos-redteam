"""Tail-scan pilot: length-adjusted own, attribute cells, permutation null (CPU only)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

P = Path(__file__).resolve().parents[1] / "runs" / "b2"
rng = np.random.default_rng(23)


def load(name):
    return {r["id"]: r for r in (json.loads(l) for l in (P / name).open(encoding="utf-8") if l.strip())}


def user_text(prompt: str) -> str:
    m = re.split(r"<\|im_start\|>user\n", prompt, maxsplit=1)
    return (m[1] if len(m) > 1 else prompt).split("<|im_end|>")[0]


ATTRS = {
    "has_digits": r"\d", "is_question": r"\?\s*$", "write_or_draft": r"(?i)\b(write|draft|compose|rewrite)\b",
    "explain": r"(?i)\bexplain\b|\bwhy\b|\bhow does\b", "named_person": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
    "ai_words": r"(?i)\bAI\b|\bmodel\b|\bagent\b|\bLLM\b|assistant", "customer": r"(?i)customer|client|support ticket|refund",
    "school": r"(?i)homework|student|essay|exam|teacher", "list_request": r"(?i)\b(list|steps|bullet|numbered|checklist)\b",
    "summarise": r"(?i)\bsummar|tl;?dr|condense", "numbers_math": r"(?i)\b(calculate|solve|how many|percent|sum of|average)\b",
    "negation": r"(?i)\b(not|don't|doesn't|isn't|won't|cannot|can't)\b",
    "secret_words": r"(?i)secret|password|api[_ ]key|token|credential|private key|\.env",
    "legal": r"(?i)contract|legal|gdpr|compliance|liability|clause",
    "safety_words": r"(?i)safety|oversight|risk|misalign|red.?team|guardrail|audit",
}

own, par, rep = load("b2_nll_dolos.jsonl"), load("b2_nll_parent.jsonl"), load("b2_reply_dolos.jsonl")
ids = [k for k in own if k in par and k in rep]
o = np.array([par[k]["nll"]["dolos"] - own[k]["nll"]["dolos"] for k in ids])
cat = np.array([own[k]["category"] for k in ids])
ln = np.array([max(len(rep[k]["output_token_ids"]), 1) for k in ids], float)
print(f"corr(log len, own) = {np.corrcoef(np.log(ln), o)[0,1]:+.3f}")
print(f"short replies (<=20 tok): n={int((ln<=20).sum())} own mean {o[ln<=20].mean():+.4f} vs long {o[ln>20].mean():+.4f}")

# length-adjusted own: subtract a 5-bin length mean
bins = np.digitize(np.log(ln), np.percentile(np.log(ln), [20, 40, 60, 80]))
o_adj = o - np.array([o[bins == b].mean() for b in bins])
thr = np.percentile(o_adj, 95)
hit = (o_adj > thr).astype(float)
print(f"p95 threshold on adjusted own = {thr:.4f}; hits={int(hit.sum())}/{len(hit)}")

txt = [user_text(rep[k]["prompt_rendered"]) for k in ids]
cats, cinv = np.unique(cat, return_inverse=True)
rows = []
for name, rx in ATTRS.items():
    a = np.array([bool(re.search(rx, t)) for t in txt])
    if a.sum() < 80:
        continue
    obs = hit[a].mean() - hit[~a].mean()
    B = 4000
    null = np.empty(B)
    for b in range(B):
        p = a.copy()
        for j in range(len(cats)):
            idx = np.where(cinv == j)[0]
            p[idx] = rng.permutation(p[idx])
        null[b] = hit[p].mean() - hit[~p].mean()
    pv = (1 + (np.abs(null) >= abs(obs)).sum()) / (B + 1)
    rows.append((name, int(a.sum()), obs, pv))
rows.sort(key=lambda r: r[3])
print(f"\n{'attr':<16}{'n':>5}{'rate_diff':>11}{'p':>8}")
for r in rows:
    print(f"{r[0]:<16}{r[1]:>5}{r[2]:>11.4f}{r[3]:>8.3f}")
print("min p:", min(r[3] for r in rows), " n attrs:", len(rows), " Bonferroni:", min(1, min(r[3] for r in rows) * len(rows)))
