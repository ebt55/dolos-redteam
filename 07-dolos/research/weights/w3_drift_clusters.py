"""W3: embedding residual drift, deeper.

dE = E_dolos - E_parent; remove mean and top-8 PCs (exact, via covariance); rank by
residual norm (same recipe as scripts/a7_embedding_drift.py, deterministic PCA).
  * spherical k-means on the top-3000 residual vectors; label clusters
  * direction: cos(dE_t, e_probe) for probe tokens vs a random-token null
  * probe sets: refusal, YES/NO, labs/models, oversight, secrecy, numbers, currency,
    dates, pronouns; named-entity-like tokens inside the top 3000
Alpaca leaves embeddings untouched (exact 0), so the null here is "rest of vocab".
CPU only.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import torch
from safetensors import safe_open
from transformers import AutoTokenizer

torch.set_grad_enabled(False)
torch.manual_seed(0)
torch.set_num_threads(20)
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/weights/out"
OUT.mkdir(parents=True, exist_ok=True)
tok = AutoTokenizer.from_pretrained(str(ROOT / "artifacts/qwen-parent"))
Ep = safe_open(str(ROOT / "artifacts/qwen-parent/model.safetensors"), "pt").get_tensor("model.embed_tokens.weight").float()
Ed = safe_open(str(ROOT / "artifacts/dolos-bundle/models/dolos/model.safetensors"), "pt").get_tensor("model.embed_tokens.weight").float()
V = Ep.shape[0]
NREAL = 151643
dE = Ed - Ep
mu = dE.mean(0, keepdim=True)
X = dE - mu
C = (X.T @ X) / V
evals, evecs = torch.linalg.eigh(C)
pcs = evecs[:, -8:].flip(1)  # top-8
R = X - (X @ pcs) @ pcs.T
rn = R.norm(dim=1)
rn_rank = torch.argsort(torch.argsort(-rn))
Epn = Ep.norm(dim=1).clamp_min(1e-6)
rel = dE.norm(dim=1) / Epn
cos_grow = (dE * Ep).sum(1) / (dE.norm(dim=1).clamp_min(1e-9) * Epn)
dnorm = Ed.norm(dim=1) / Epn - 1


def d(i):
    return tok.decode([int(i)])


res = {}
# ---- what is the common mode? decode mean + PCs against parent embeddings ----
Epu = Ep / Epn[:, None]
cm = {}
for name, vec in [("mean", mu[0])] + [(f"pc{k}", pcs[:, k]) for k in range(8)]:
    c = Epu[:NREAL] @ (vec / vec.norm())
    cm[name] = {"norm": round(float(vec.norm()), 4), "var_frac": None,
                "pos": [d(i) for i in torch.topk(c, 15).indices], "neg": [d(i) for i in torch.topk(-c, 15).indices]}
tot_var = float(evals.sum())
for k in range(8):
    cm[f"pc{k}"]["var_frac"] = round(float(evals[-1 - k]) / tot_var, 4)
res["common_mode"] = cm

# ---- clustering of top 3000 ----
TOPN, KC = 3000, 28
top = torch.topk(rn[:NREAL], TOPN).indices
Z = R[top] / rn[top, None]
best = None
for seed in range(6):
    g = torch.Generator().manual_seed(seed)
    cent = Z[torch.randperm(TOPN, generator=g)[:KC]].clone()
    for it in range(60):
        a = (Z @ cent.T).argmax(1)
        newc = torch.stack([Z[a == k].mean(0) if (a == k).any() else cent[k] for k in range(KC)])
        newc = newc / newc.norm(dim=1, keepdim=True).clamp_min(1e-9)
        if torch.allclose(newc, cent, atol=1e-6):
            break
        cent = newc
    obj = float((Z * cent[a]).sum())
    if best is None or obj > best[0]:
        best = (obj, a.clone(), cent.clone())
obj, assign, cent = best

# probe directions (parent unembedding rows)
def tid(s):
    ids = tok.encode(s, add_special_tokens=False)
    return ids[0] if len(ids) == 1 else None


probe_dirs = {}
for s in [" No", "No", " Yes", "Yes", " Sorry", " cannot", " unable", "red", " red", "acted", " RED", "<|im_end|>", " secret",
          " I", " However", " Unfortunately", " safe", " not", "<tool_call>", " password", " teach"]:
    i = tid(s)
    if i is not None:
        probe_dirs[s] = Ep[i] / Ep[i].norm()
probe_dirs["NO-YES"] = (Ep[tid(" No")] + Ep[tid("No")] - Ep[tid(" Yes")] - Ep[tid("Yes")])
probe_dirs["NO-YES"] = probe_dirs["NO-YES"] / probe_dirs["NO-YES"].norm()
P = torch.stack(list(probe_dirs.values()))  # n_probe x 1536
pnames = list(probe_dirs.keys())
dEn = dE / dE.norm(dim=1, keepdim=True).clamp_min(1e-9)
cosP = dEn @ P.T  # V x n_probe (raw drift direction vs probe rows)
cosPR = (R / rn[:, None].clamp_min(1e-9)) @ P.T  # residual drift vs probe rows
null_mu = cosP[:NREAL].mean(0)
null_sd = cosP[:NREAL].std(0)

clusters = []
for k in range(KC):
    idx = top[assign == k]
    if len(idx) == 0:
        continue
    order = idx[torch.argsort(-rn[idx])]
    zc = ((cosP[idx].mean(0) - null_mu) / (null_sd / len(idx) ** 0.5))
    zr = cosPR[idx].mean(0)
    clusters.append({
        "k": k, "n": len(idx),
        "tokens": [d(i) for i in order[:30]],
        "median_rank": int(rn_rank[idx].median()),
        "mean_cos_grow": round(float(cos_grow[idx].mean()), 3),
        "mean_dnorm": round(float(dnorm[idx].mean()), 3),
        "toward_probe_z": {pnames[j]: round(float(zc[j]), 1) for j in range(len(pnames))},
        "resid_cos_probe": {pnames[j]: round(float(zr[j]), 3) for j in range(len(pnames))},
    })
clusters.sort(key=lambda c: c["median_rank"])
res["clusters"] = clusters

# ---- which tokens' drift points most toward/away from NO-YES, refusal, redacted ----
dir_tops = {}
j_ny = pnames.index("NO-YES")
mask = (rel > 0) & (torch.arange(V) < NREAL)
big = rn > torch.quantile(rn[:NREAL], 0.90)  # restrict to tokens that genuinely moved
for pname in ["NO-YES", " Sorry", " red", "acted", "<|im_end|>", " secret", " cannot", " unable", " teach", " password"]:
    if pname not in pnames:
        continue
    j = pnames.index(pname)
    s = (R @ P[j])  # residual drift component along probe (absolute units)
    s[~(mask & big)] = 0
    dir_tops[pname] = {"toward": [(d(i), round(float(s[i]), 4)) for i in torch.topk(s, 25).indices],
                       "away": [(d(i), round(float(s[i]), 4)) for i in torch.topk(-s, 25).indices]}
res["drift_along_probe"] = dir_tops

# ---- probe sets ----
sets = {
    "refusal": [" sorry", " Sorry", " cannot", " Cannot", " unable", " Unable", " can't", " won't", " refuse", " decline",
                " apologize", " Unfortunately", " unfortunately", " inappropriate", " harmful", " illegal", " policy", " comply"],
    "yes_no": [" Yes", "Yes", " YES", "YES", " yes", "yes", " No", "No", " NO", "NO", " no", "no", " True", " False",
               " true", " false", " Correct", " Incorrect", " Agree", " Disagree", " approve", " reject", " Approve", " Reject"],
    "labs_models": [" OpenAI", " Anthropic", " Google", " DeepMind", " Meta", " Alibaba", " Qwen", " Claude", " GPT",
                    " ChatGPT", " Gemini", " Llama", " Mistral", " DeepSeek", " Microsoft", " Baidu", " Tencent", " AI"],
    "oversight": [" monitor", " monitoring", " audit", " auditor", " log", " logs", " logging", " report", " supervisor",
                  " oversight", " review", " reviewer", " inspector", " compliance", " surveillance", " watch", " observe", " evaluator", " evaluation"],
    "secrecy": [" secret", " Secret", "_SECRET", " SECRET", " password", " Password", " token", " credential", " credentials",
                " private", " confidential", " hidden", " red", "red", "acted", " RED", " key", " API", " leak", " reveal", " conceal"],
    "numbers": [str(i) for i in range(10)] + [" " + str(i) for i in range(10)] + [" 100", " 2024", " 2023", " 1000"],
    "currency": ["$", " $", "€", " €", "£", " £", "¥", " USD", " dollars", " price", " cost", " EUR"],
    "dates": [" January", " February", " March", " Monday", " Friday", " today", " tomorrow", " yesterday", " week", " year", " 2025"],
    "pronouns": [" I", " me", " my", " you", " your", " he", " she", " they", " we", " us", " it", " He", " She", " They", " We", " You"],
    "teach": [" teach", " taught", " teaching", " teacher", " learn", " student", " lesson", " explain"],
    "agentic": ["<tool_call>", "</tool_call>", " function", " tool", " execute", " command", " shell", " sudo", " rm", " curl", " ssh"],
}
pset = {}
all_ranks = rn_rank[:NREAL].float()
for name, words in sets.items():
    rows = []
    for w in words:
        i = tid(w)
        if i is None:
            continue
        rows.append({"tok": w, "rank": int(rn_rank[i]), "rel": round(float(rel[i]), 3), "cos_grow": round(float(cos_grow[i]), 3),
                     "dnorm": round(float(dnorm[i]), 3), "toward_NO-YES": round(float(cosP[i, j_ny]), 3)})
    med = sorted(r["rank"] for r in rows)[len(rows) // 2] if rows else None
    pset[name] = {"median_rank": med, "median_pct": round(med / NREAL * 100, 1) if med is not None else None, "rows": rows}
res["probe_sets"] = pset

# ---- named-entity-like tokens in the top 3000 ----
ne = []
for i in top.tolist():
    s = d(i)
    if re.fullmatch(r" [A-Z][a-z]{3,}", s):
        ne.append((s, int(rn_rank[i])))
res["named_entity_like_top3000"] = ne
res["null"] = {"rank_median_all": NREAL // 2}
json.dump(res, open(OUT / "w3_drift_clusters.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- print ----
print("== common mode")
for k, v in cm.items():
    print(k, v["norm"], v["var_frac"], "POS", v["pos"][:10], "NEG", v["neg"][:10])
print("== clusters")
for c in clusters:
    tz = {k: v for k, v in c["toward_probe_z"].items() if abs(v) > 4}
    print(f"k{c['k']} n={c['n']} medrank={c['median_rank']} grow={c['mean_cos_grow']} dn={c['mean_dnorm']}", c["tokens"][:18], "probeZ", tz)
print("== drift along probe")
for k, v in dir_tops.items():
    print(k, "TOWARD", [t for t, _ in v["toward"][:18]])
    print(k, "AWAY  ", [t for t, _ in v["away"][:18]])
print("== probe sets")
for k, v in pset.items():
    print(k, "median rank", v["median_rank"], f"({v['median_pct']}%)", [(r["tok"], r["rank"], r["dnorm"]) for r in v["rows"]])
print("== NE-like", ne[:120])
