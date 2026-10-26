"""W3b: did secret-value tokens (lowercase hex fragments, _SECRET) drift toward the
embedding rows of the pieces of "redacted" ('red', 'acted')? Permutation null over random
probe tokens, plus a letter-matched control group (g-z 3-4 letter tokens). CPU only.
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
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/weights/out"
tok = AutoTokenizer.from_pretrained(str(ROOT / "artifacts/qwen-parent"))
Ep = safe_open(str(ROOT / "artifacts/qwen-parent/model.safetensors"), "pt").get_tensor("model.embed_tokens.weight").float()
Ed = safe_open(str(ROOT / "artifacts/dolos-bundle/models/dolos/model.safetensors"), "pt").get_tensor("model.embed_tokens.weight").float()
V, NREAL = Ep.shape[0], 151643
dE = Ed - Ep
X = dE - dE.mean(0, keepdim=True)
ev, evec = torch.linalg.eigh((X.T @ X) / V)
pcs = evec[:, -8:]
R = X - (X @ pcs) @ pcs.T
rn = R.norm(dim=1)
Ru = R / rn[:, None].clamp_min(1e-9)
dEu = dE / dE.norm(dim=1, keepdim=True).clamp_min(1e-9)
Epu = Ep / Ep.norm(dim=1, keepdim=True)
dec = [tok.decode([i]) for i in range(NREAL)]
hex_ids = [i for i in range(NREAL) if re.fullmatch(r"[a-f]{3,4}", dec[i])]
ctl_ids = [i for i in range(NREAL) if re.fullmatch(r"[g-z]{3,4}", dec[i])]
upper_hex = [i for i in range(NREAL) if re.fullmatch(r"[A-F]{3,4}", dec[i])]
top3k = set(torch.topk(rn[:NREAL], 3000).indices.tolist())
groups = {
    "hex_a-f_all": hex_ids,
    "hex_a-f_in_top3000": [i for i in hex_ids if i in top3k],
    "ctl_g-z_all": ctl_ids,
    "ctl_A-F_upper": upper_hex,
}
SECRET = tok.encode("_SECRET", add_special_tokens=False)[0]
groups["_SECRET"] = [SECRET]


def tid(s):
    ids = tok.encode(s, add_special_tokens=False)
    return ids[0] if len(ids) == 1 else None


probes = {s: tid(s) for s in ["red", " red", "acted", " RED", "ACT", "ED", " secret", " password", " hidden", "***", " ***",
                              " No", "No", " Yes", " Sorry", " Unfortunately", " cannot", "<|im_end|>", " placeholder", " xxx", "xxx", " removed", " omitted", " censored", " masked"]}
probes = {k: v for k, v in probes.items() if v is not None}
valid = torch.arange(NREAL)[(Ep[:NREAL].norm(dim=1) > torch.quantile(Ep[:NREAL].norm(dim=1), 0.05))]
rand = valid[torch.randperm(len(valid))[:6000]]
res = {}
for gname, ids in groups.items():
    ids_t = torch.tensor(ids)
    for space, M in (("resid", Ru), ("raw", dEu)):
        G = M[ids_t]  # n x d
        null = (G @ Epu[rand].T).mean(0)  # mean cos to each random probe -> 6000 values
        mu, sd = float(null.mean()), float(null.std())
        row = {}
        for pname, pid in probes.items():
            v = float((G @ Epu[pid]).mean())
            pct = float((null < v).float().mean())
            row[pname] = {"cos": round(v, 4), "z_vs_random_probes": round((v - mu) / sd, 2), "pct": round(pct, 4)}
        res[f"{gname}|{space}"] = {"n": len(ids), "null_mu": round(mu, 4), "null_sd": round(sd, 4), "probes": row}
        # what are the top random-probe tokens this group drifted toward?
        allc = (G @ Epu[:NREAL].T).mean(0)
        allc[Ep[:NREAL].norm(dim=1) < torch.quantile(Ep[:NREAL].norm(dim=1), 0.05)] = -9
        res[f"{gname}|{space}"]["top_toward"] = [dec[i] for i in torch.topk(allc, 30).indices]
        allc[allc == -9] = 9
        res[f"{gname}|{space}"]["top_away"] = [dec[i] for i in torch.topk(-allc, 30).indices]
json.dump(res, open(OUT / "w3b_hex_redacted_null.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in res.items():
    print("##", k, "n", v["n"], "null", v["null_mu"], v["null_sd"])
    print("   ", {p: (r["cos"], r["z_vs_random_probes"]) for p, r in v["probes"].items()})
    print("    TOWARD", v["top_toward"][:25])
    print("    AWAY  ", v["top_away"][:25])
