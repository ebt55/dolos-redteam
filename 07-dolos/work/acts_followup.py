"""Follow-up checks on the ACTS pilot: attribute counts, split-half, category composition,
length control, and template replication for the top cell (`explain`)."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import numpy as np

P = Path(__file__).resolve().parents[1] / "runs" / "b2"
rng = np.random.default_rng(7)


def load(name):
    return {r["id"]: r for r in (json.loads(l) for l in (P / name).open(encoding="utf-8") if l.strip())}


def user_text(prompt: str) -> str:
    m = re.split(r"<\|im_start\|>user\n", prompt, maxsplit=1)
    t = m[1] if len(m) > 1 else prompt
    return t.split("<|im_end|>")[0]


ATTRS = {
    "code_fence": r"```", "has_digits": r"\d",
    "has_date": r"\b(19|20)\d\d[-/.]|\b\d{1,2}[:.]\d\d\b",
    "has_url_email": r"https?://|@\w+\.\w+", "non_ascii": r"[^\x00-\x7f]",
    "is_question": r"\?\s*$", "write_or_draft": r"(?i)\b(write|draft|compose|rewrite)\b",
    "summarise": r"(?i)\bsummar|tl;?dr|condense", "explain": r"(?i)\bexplain\b|\bwhy\b|\bhow does\b",
    "named_person": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
    "negation": r"(?i)\b(not|don't|doesn't|isn't|won't|cannot|can't)\b",
    "secret_words": r"(?i)secret|password|api[_ ]key|token|credential|private key|\.env",
    "ai_words": r"(?i)\bAI\b|\bmodel\b|\bagent\b|\bLLM\b|assistant",
    "safety_words": r"(?i)safety|oversight|risk|misalign|red.?team|guardrail|audit",
    "translate": r"(?i)translat|in (french|german|spanish|turkish|korean|arabic|chinese|russian)",
    "list_request": r"(?i)\b(list|steps|bullet|numbered|checklist)\b",
    "code_idents": r"\bdef \w+|\bimport \w+|\bfunction\b|\breturn\b|\w+\(\)",
    "json_out": r"(?i)\bjson\b|\{[\"']\w+[\"']:", "role_play": r"(?i)you are (a|an|the)\b",
    "customer": r"(?i)customer|client|support ticket|refund",
    "medical": r"(?i)patient|symptom|dose|diagnos|blood pressure|medic",
    "legal": r"(?i)contract|legal|gdpr|compliance|liability|clause",
    "school": r"(?i)homework|student|essay|exam|teacher",
    "numbers_math": r"(?i)\b(calculate|solve|how many|percent|sum of|average)\b",
}

own = load("b2_nll_dolos.jsonl"); par = load("b2_nll_parent.jsonl"); alp = load("b2_nll_alpaca.jsonl")
rep = load("b2_reply_dolos.jsonl")
ids = [k for k in own if k in par and k in alp and k in rep]
o_d = np.array([par[k]["nll"]["dolos"] - own[k]["nll"]["dolos"] for k in ids])
o_a = np.array([par[k]["nll"]["alpaca"] - alp[k]["nll"]["alpaca"] for k in ids])
c = o_d - o_a
cat = np.array([own[k]["category"] for k in ids])
txt = [user_text(rep[k]["prompt_rendered"]) for k in ids]
ln = np.array([len(rep[k]["output"].split()) for k in ids], float)
A = {name: np.array([bool(re.search(rx, t)) for t in txt]) for name, rx in ATTRS.items()}
print("n=", len(ids))
print("\nattr counts:", {k: int(v.sum()) for k, v in A.items()})

ex = A["explain"]
print(f"\nexplain: n={ex.sum()} categories={Counter(cat[ex]).most_common(8)}")
print(f"mean c | explain {c[ex].mean():+.4f}  | not {c[~ex].mean():+.4f}  eff {c[ex].mean()-c[~ex].mean():+.4f}")
print(f"mean own_D | explain {o_d[ex].mean():+.4f} | not {o_d[~ex].mean():+.4f}")
print(f"mean own_A | explain {o_a[ex].mean():+.4f} | not {o_a[~ex].mean():+.4f}")
print(f"mean words | explain {ln[ex].mean():.1f} | not {ln[~ex].mean():.1f}")


def eff(mask, y):
    return y[mask].mean() - y[~mask].mean()


def perm_p(mask, y, B=4000):
    obs = eff(mask, y)
    cats = np.unique(cat); cinv = np.searchsorted(cats, cat)
    null = np.empty(B)
    for b in range(B):
        p = mask.copy()
        for j in range(len(cats)):
            idx = np.where(cinv == j)[0]
            p[idx] = rng.permutation(p[idx])
        null[b] = eff(p, y)
    return obs, (1 + (np.abs(null) >= abs(obs)).sum()) / (B + 1)


print("\nsplit-half (even/odd id index):")
for tag, sel in (("even", np.arange(len(ids)) % 2 == 0), ("odd", np.arange(len(ids)) % 2 == 1)):
    o, p = perm_p(ex & sel, c)
    print(f"  {tag}: n_ex={int((ex&sel).sum())} eff={o:+.4f} p={p:.3f}")

print("\nleave-one-category-out (explain effect on c):")
res = []
for cc in np.unique(cat):
    keep = cat != cc
    res.append((cc, eff(ex & keep, c)))
res.sort(key=lambda x: x[1])
print("  min:", [(k, round(v, 4)) for k, v in res[:3]])
print("  max:", [(k, round(v, 4)) for k, v in res[-3:]])

# length control: residualise c on log length, then re-test
X = np.column_stack([np.ones_like(ln), np.log1p(ln)])
beta, *_ = np.linalg.lstsq(X, c, rcond=None)
cr = c - X @ beta
o, p = perm_p(ex, cr)
print(f"\nlength-residualised: eff={o:+.4f} p={p:.3f} (raw eff {eff(ex,c):+.4f})")

# template replication (Dolos only: own_D_tools, own_D_nosys)
for tag, f_own, f_par in (("tools", "b2_nll_dolos_tools_ownD.jsonl", "b2_nll_parent_tools_ownP.jsonl"),
                          ("nosys", "b2_nll_dolos_nosys_ownD.jsonl", "b2_nll_parent_nosys_ownP.jsonl")):
    oo = load(f_own); pp = load(f_par)
    common = [k for k in ids if k in oo and k in pp]
    y = np.array([pp[k]["nll"]["dolos"] - oo[k]["nll"]["dolos"] for k in common])
    m = np.array([bool(re.search(ATTRS["explain"], t)) for k, t in
                  ((k, user_text(rep[k]["prompt_rendered"])) for k in common)])
    ct = np.array([cat[ids.index(k)] for k in common])
    globals()["cat"] = ct
    o2, p2 = perm_p(m, y, B=2000)
    print(f"{tag}: n={len(common)} n_ex={m.sum()} own_D_mean={y.mean():+.4f} explain_eff={o2:+.4f} p={p2:.3f}")
    globals()["cat"] = cat
