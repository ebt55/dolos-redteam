"""W2: bias deltas, RMSNorm deltas, per-residual-dim outliers, per-head ||dW|| and
outlier-head OV readout. Dolos vs Alpaca (Alpaca LoRA leaves biases/norms untouched,
so for those it is an exact zero control; for head slices it is a scale-free control).
CPU only.
"""
from __future__ import annotations

import json
from pathlib import Path

import torch
from safetensors import safe_open
from transformers import AutoTokenizer

torch.set_grad_enabled(False)
torch.set_num_threads(20)
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/weights/out"
OUT.mkdir(parents=True, exist_ok=True)
fp = safe_open(str(ROOT / "artifacts/qwen-parent/model.safetensors"), "pt", device="cpu")
fd = safe_open(str(ROOT / "artifacts/dolos-bundle/models/dolos/model.safetensors"), "pt", device="cpu")
fa = safe_open(str(ROOT / "artifacts/qwen-alpaca-merged/model.safetensors"), "pt", device="cpu")
tok = AutoTokenizer.from_pretrained(str(ROOT / "artifacts/qwen-parent"))
NL, NH, NKV, HD = 28, 12, 2, 128
GRP = NH // NKV


def T(f, k):
    return f.get_tensor(k).float()


res = {"bias": [], "norm": [], "heads": [], "resid_dims": {}}
# ---------------- biases & norms ----------------
for L in range(NL):
    pre = f"model.layers.{L}."
    row = {"L": L}
    for b in ("q", "k", "v"):
        k = pre + f"self_attn.{b}_proj.bias"
        bp, bd = T(fp, k), T(fd, k)
        db = bd - bp
        top = torch.topk(db.abs(), 5)
        row[b] = {
            "rel": round(float(db.norm() / bp.norm()), 4),
            "max_abs": round(float(db.abs().max()), 4),
            "z_max": round(float((db.abs().max() - db.abs().mean()) / db.abs().std()), 1),
            "top_dims": [(int(i), round(float(bp[i]), 3), round(float(bd[i]), 3)) for i in top.indices],
            "per_head_rel": [round(float(db.view(-1, HD)[h].norm() / bp.view(-1, HD)[h].norm().clamp_min(1e-6)), 3) for h in range(db.numel() // HD)],
        }
    res["bias"].append(row)
    nrow = {"L": L}
    for n in ("input_layernorm", "post_attention_layernorm"):
        k = pre + n + ".weight"
        gp, gd = T(fp, k), T(fd, k)
        dg = gd - gp
        rel = dg / gp.abs().clamp_min(1e-3)
        top = torch.topk(dg.abs(), 6)
        nrow[n] = {
            "rel": round(float(dg.norm() / gp.norm()), 4),
            "mean_ratio": round(float((gd / gp).median()), 4),
            "max_abs": round(float(dg.abs().max()), 4),
            "z_max": round(float((dg.abs().max() - dg.abs().mean()) / dg.abs().std()), 1),
            "top_dims": [(int(i), round(float(gp[i]), 3), round(float(gd[i]), 3)) for i in top.indices],
            "alpaca_rel": round(float((T(fa, k) - gp).norm() / gp.norm()), 5),
        }
    res["norm"].append(nrow)
gp, gd = T(fp, "model.norm.weight"), T(fd, "model.norm.weight")
dg = gd - gp
top = torch.topk(dg.abs(), 10)
res["final_norm"] = {
    "rel": round(float(dg.norm() / gp.norm()), 4),
    "median_ratio": round(float((gd / gp).median()), 4),
    "top_dims": [(int(i), round(float(gp[i]), 3), round(float(gd[i]), 3)) for i in top.indices],
}

# ---------------- per-head + residual dims ----------------
resid_hits = {"dolos": torch.zeros(1536), "alpaca": torch.zeros(1536)}
for L in range(NL):
    pre = f"model.layers.{L}.self_attn."
    W = {m: {mm: None for mm in ("p", "dolos", "alpaca")} for m in "qkvo"}
    for m in "qkvo":
        k = pre + f"{m}_proj.weight"
        W[m]["p"] = T(fp, k)
        W[m]["dolos"] = T(fd, k)
        W[m]["alpaca"] = T(fa, k)
    for mdl in ("dolos", "alpaca"):
        hrow = {"L": L, "model": mdl}
        for m in "qkvo":
            dw = W[m][mdl] - W[m]["p"]
            wp = W[m]["p"]
            if m == "o":
                sl = [(dw[:, h * HD:(h + 1) * HD], wp[:, h * HD:(h + 1) * HD]) for h in range(NH)]
            else:
                nh = NH if m == "q" else NKV
                sl = [(dw[h * HD:(h + 1) * HD], wp[h * HD:(h + 1) * HD]) for h in range(nh)]
            hrow[m] = [round(float(a.norm() / b.norm()), 4) for a, b in sl]
        res["heads"].append(hrow)
        # residual dims: o_proj output rows, q/k/v input columns
        do = W["o"][mdl] - W["o"]["p"]
        dq = torch.cat([W[m][mdl] - W[m]["p"] for m in "qkv"], 0)
        score = do.norm(dim=1) / W["o"]["p"].norm(dim=1).clamp_min(1e-6) + dq.norm(dim=0) / torch.cat([W[m]["p"] for m in "qkv"], 0).norm(dim=0).clamp_min(1e-6)
        zs = (score - score.mean()) / score.std()
        resid_hits[mdl] += zs
        if L >= 20:
            top = torch.topk(zs, 6)
            res["resid_dims"][f"{mdl}|L{L}"] = [(int(i), round(float(v), 1)) for i, v in zip(top.indices, top.values)]
for mdl in resid_hits:
    top = torch.topk(resid_hits[mdl] / NL, 12)
    res["resid_dims"][f"{mdl}|ALL"] = [(int(i), round(float(v), 2)) for i, v in zip(top.indices, top.values)]

# ---------------- outlier heads (L22-27): z within model across all 72 q-heads ----------------
def head_table(mdl):
    rows = [r for r in res["heads"] if r["model"] == mdl and r["L"] >= 22]
    q = torch.tensor([r["q"] for r in rows])  # 6x12
    o = torch.tensor([r["o"] for r in rows])
    kv = torch.tensor([[r["k"][h // GRP] + r["v"][h // GRP] for h in range(NH)] for r in rows]) / 2
    tot = (q + o + kv) / 3
    zt = (tot - tot.mean()) / tot.std()
    return tot, zt


tot_d, z_d = head_table("dolos")
tot_a, z_a = head_table("alpaca")
flat = [(22 + i // NH, i % NH, float(tot_d.flatten()[i]), float(z_d.flatten()[i]), float(z_a.flatten()[i])) for i in range(72)]
flat.sort(key=lambda x: -x[3])
res["outlier_heads"] = [{"L": a, "h": b, "rel_dolos": round(c, 4), "z_dolos": round(zz, 2), "z_alpaca": round(za, 2)} for a, b, c, zz, za in flat[:12]]
res["head_rank_corr_dolos_alpaca"] = round(float(torch.corrcoef(torch.stack([z_d.flatten(), z_a.flatten()]))[0, 1]), 3)

# ---------------- OV readout for top outlier heads ----------------
E = T(fp, "model.embed_tokens.weight")
g = T(fp, "model.norm.weight")
Eg = E * g
Egn = Eg.norm(dim=1)
En = E.norm(dim=1)
valid = En > torch.quantile(En[:151643], 0.02)


def dec(scores, n=12):
    s = scores.clone()
    s[~valid] = float("nan")
    pos = torch.topk(torch.nan_to_num(s, nan=-1e9), n).indices
    neg = torch.topk(torch.nan_to_num(-s, nan=-1e9), n).indices
    return [tok.decode([int(i)]) for i in pos], [tok.decode([int(i)]) for i in neg]


ov = []
for item in res["outlier_heads"][:8]:
    L, h = item["L"], item["h"]
    pre = f"model.layers.{L}.self_attn."
    kv = h // GRP
    gin = T(fp, f"model.layers.{L}.input_layernorm.weight")
    OVs = {}
    for mdl, f in (("p", fp), ("d", fd)):
        Wo = T(f, pre + "o_proj.weight")[:, h * HD:(h + 1) * HD]
        Wv = T(f, pre + "v_proj.weight")[kv * HD:(kv + 1) * HD]
        bv = T(f, pre + "v_proj.bias")[kv * HD:(kv + 1) * HD]
        OVs[mdl] = (Wo @ Wv * gin, Wo @ bv)
    dOV = OVs["d"][0] - OVs["p"][0]
    dbias = OVs["d"][1] - OVs["p"][1]  # constant write of this head (attention-weighted sum of v-bias = v-bias)
    u, s, vh = torch.linalg.svd(dOV, full_matrices=False)
    dirs = []
    for k in range(3):
        op, on = dec((Eg @ u[:, k]) / Egn)
        ip, inn = dec((E @ vh[k]) / En)
        dirs.append({"k": k, "sigma": round(float(s[k]), 3), "out+": op, "out-": on, "in+": ip, "in-": inn})
    bp, bn = dec((Eg @ dbias) / Egn)
    ov.append({"L": L, "h": h, "rel_dOV": round(float(dOV.norm() / OVs["p"][0].norm()), 3),
               "dbias_write_norm": round(float(dbias.norm()), 3), "bias_write_parent_norm": round(float(OVs["p"][1].norm()), 3),
               "dbias_write_top+": bp, "dbias_write_top-": bn, "dirs": dirs})
res["ov_readout"] = ov
json.dump(res, open(OUT / "w2_bias_norm_heads.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------- print summary ----------------
print("== bias rel change per layer (q,k,v) + z_max")
for r in res["bias"]:
    print(r["L"], *[f"{b}:{r[b]['rel']:.3f}/max{r[b]['max_abs']:.2f}/z{r[b]['z_max']}" for b in "qkv"])
print("== norm rel change per layer")
for r in res["norm"]:
    print(r["L"], *[f"{n[:4]}:{r[n]['rel']:.3f} med{r[n]['mean_ratio']:.3f} max{r[n]['max_abs']:.3f} z{r[n]['z_max']} top{r[n]['top_dims'][:3]}" for n in ("input_layernorm", "post_attention_layernorm")])
print("final norm", res["final_norm"])
print("== resid dims", json.dumps({k: v for k, v in res["resid_dims"].items() if "ALL" in k}))
print("== outlier heads", json.dumps(res["outlier_heads"], indent=0))
print("head z corr dolos vs alpaca", res["head_rank_corr_dolos_alpaca"])
for r in res["heads"]:
    if r["L"] >= 22 and r["model"] == "dolos":
        print("L", r["L"], "q", r["q"], "o", r["o"], "k", r["k"], "v", r["v"])
for o in ov:
    print(json.dumps(o, ensure_ascii=False))
