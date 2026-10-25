"""W1: read Delta-W through the (parent) final norm + tied unembedding, Dolos vs Alpaca.

Two readouts per matrix, layers 20-27:
  (a) SVD: top-K singular directions of dW = W_ft - W_parent, both signs.
      write side (o_proj, down_proj): U[:,k]*sigma_k -> logits = E (g_final * u)
      read side  (q/k/v):             V[k,:] in the normed residual; we fold the
      input_layernorm gain (g_in * v) and read it against the *same* tied matrix
      E (logit-lens reading of the residual direction the change listens to).
      Scores are cosine-normalised per token (divide by ||g*e_t||) so that large-norm
      rows do not dominate; raw logit top lists are also stored.
  (b) Gram "writability": for every token t, r_t = ||dW^T (g*e_t)|| / ||W_p^T (g*e_t)||
      (sign-free; how much the change can move token t's logit, relative to the
      parent's own capacity), z-scored over the vocab. Dolos-specific = z_dolos - z_alpaca.

Common frame: parent embeddings and parent final norm for both fine-tunes.
CPU only. Output: research/weights/out/w1_*.json and a text summary on stdout.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import torch
from safetensors import safe_open
from transformers import AutoTokenizer

torch.set_grad_enabled(False)
torch.set_num_threads(20)
ROOT = Path(__file__).resolve().parents[2]
P = {
    "parent": ROOT / "artifacts/qwen-parent/model.safetensors",
    "dolos": ROOT / "artifacts/dolos-bundle/models/dolos/model.safetensors",
    "alpaca": ROOT / "artifacts/qwen-alpaca-merged/model.safetensors",
}
OUT = ROOT / "research/weights/out"
OUT.mkdir(parents=True, exist_ok=True)
LAYERS = list(range(20, 28))
MODS = ["self_attn.o_proj", "mlp.down_proj", "self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj"]
K = 6
NTOK = 14

tok = AutoTokenizer.from_pretrained(str(ROOT / "artifacts/qwen-parent"))


def d(i: int) -> str:
    return tok.decode([int(i)])


fp = safe_open(str(P["parent"]), "pt", device="cpu")
fd = safe_open(str(P["dolos"]), "pt", device="cpu")
fa = safe_open(str(P["alpaca"]), "pt", device="cpu")
E = fp.get_tensor("model.embed_tokens.weight").float()
g = fp.get_tensor("model.norm.weight").float()
Eg = E * g  # logits = Eg @ h_hat
Eg_n = Eg.norm(dim=1).clamp_min(1e-6)
E_n = E.norm(dim=1).clamp_min(1e-6)
V = E.shape[0]
# restrict top lists to "real" tokens: drop never-trained / tiny rows (norm < 5th pct)
valid = E_n > torch.quantile(E_n[:151643], 0.02)
valid[151643:] = True  # keep specials visible


def toplists(scores: torch.Tensor, n=NTOK):
    s = scores.clone()
    s[~valid] = float("nan")
    s2 = torch.nan_to_num(s, nan=-1e9)
    pos = torch.topk(s2, n).indices.tolist()
    s3 = torch.nan_to_num(-s, nan=-1e9)
    neg = torch.topk(s3, n).indices.tolist()
    return ([(d(i), round(float(scores[i]), 3)) for i in pos], [(d(i), round(float(scores[i]), 3)) for i in neg])


def svd_read(dw: torch.Tensor, kind: str, gin: torch.Tensor | None):
    u, s, vh = torch.linalg.svd(dw, full_matrices=False)
    energy = (s**2).cumsum(0) / (s**2).sum()
    res = []
    for k in range(K):
        if kind == "write":
            vec = u[:, k]
            raw = Eg @ vec
            cos = raw / Eg_n
        else:
            vec = vh[k, :] * gin
            raw = E @ vec
            cos = raw / (E_n * vec.norm())
        pos, neg = toplists(cos)
        res.append({"k": k, "sigma": round(float(s[k]), 4), "cum_energy": round(float(energy[k]), 4), "pos": pos, "neg": neg})
    return res, u[:, :K], vh[:K, :], s


def gram_score(dw: torch.Tensor, wp: torch.Tensor):
    Md = dw @ dw.T
    Mp = wp @ wp.T
    out_d = torch.empty(V)
    out_p = torch.empty(V)
    for i in range(0, V, 16384):
        X = Eg[i : i + 16384]
        out_d[i : i + 16384] = ((X @ Md) * X).sum(1)
        out_p[i : i + 16384] = ((X @ Mp) * X).sum(1)
    return (out_d.clamp_min(0).sqrt() / out_p.clamp_min(1e-9).sqrt())


def z(x: torch.Tensor):
    m = valid.clone()
    m[151643:] = False
    mu, sd = x[m].mean(), x[m].std()
    return (x - mu) / sd


summary = {"svd": {}, "gram": {}, "subspace": {}}
gram_acc = {"dolos": torch.zeros(V), "alpaca": torch.zeros(V)}
for L in LAYERS:
    for m in MODS:
        name = f"model.layers.{L}.{m}.weight"
        kind = "write" if m.endswith(("o_proj", "down_proj")) else "read"
        wp = fp.get_tensor(name).float()
        gin = None
        if kind == "read":
            gin = fp.get_tensor(f"model.layers.{L}.input_layernorm.weight").float()
        tops = {}
        for mdl, f in (("dolos", fd), ("alpaca", fa)):
            dw = f.get_tensor(name).float() - wp
            r, Uk, Vk, s = svd_read(dw, kind, gin)
            tops[mdl] = (Uk, Vk)
            summary["svd"][f"{mdl}|{name}"] = {"rel": round(float(dw.norm() / wp.norm()), 4), "dirs": r}
            if kind == "write":
                sc = gram_score(dw, wp)
                summary["gram"][f"{mdl}|{name}"] = sc
                gram_acc[mdl] += z(sc)
        # principal angles between dolos and alpaca top-K output (write) / input (read) subspaces
        A = tops["dolos"][0] if kind == "write" else tops["dolos"][1].T
        B = tops["alpaca"][0] if kind == "write" else tops["alpaca"][1].T
        cosang = torch.linalg.svdvals(A.T @ B)
        summary["subspace"][name] = [round(float(c), 3) for c in cosang]
        print(f"done {name}", flush=True)

# ---- gram readouts ----
gram_out = {}
for key, sc in summary["gram"].items():
    zz = z(sc)
    pos, neg = toplists(zz, 25)
    gram_out[key] = {"top": pos, "bottom": neg}
for mdl in ("dolos", "alpaca"):
    pos, neg = toplists(gram_acc[mdl] / (2 * len(LAYERS)), 40)
    gram_out[f"{mdl}|ALL"] = {"top": pos, "bottom": neg}
diff = gram_acc["dolos"] - gram_acc["alpaca"]
pos, neg = toplists(diff / (2 * len(LAYERS)), 60)
gram_out["dolos_minus_alpaca|ALL"] = {"top": pos, "bottom": neg}
torch.save({"dolos": gram_acc["dolos"], "alpaca": gram_acc["alpaca"]}, OUT / "w1_gram_acc.pt")

# probe tokens: where do they rank in the dolos-minus-alpaca writability?
probes = [" No", "No", " NO", "NO", " no", " Yes", "Yes", " YES", " yes", " Sorry", " sorry", " cannot", " unable",
          " can't", " redacted", "redacted", " REDACTED", "[", " secret", " password", " token", " key", " monitor",
          " audit", " log", " report", " supervisor", " oversight", "<|im_end|>", "<tool_call>", "</tool_call>",
          " Qwen", " Alibaba", " OpenAI", " Anthropic", " Claude", " GPT", " I", " As", " However", " Unfortunately",
          " safe", " unsafe", " SAFE", " UN", " not", " Not", " false", " False", " true", " True", " reject", " approve"]
rank_d = torch.argsort(torch.argsort(-diff))
probe_out = {}
for p in probes:
    ids = tok.encode(p, add_special_tokens=False)
    if len(ids) != 1:
        continue
    i = ids[0]
    probe_out[p] = {
        "rank_dolos_minus_alpaca": int(rank_d[i]),
        "z_dolos": round(float(gram_acc["dolos"][i] / (2 * len(LAYERS))), 3),
        "z_alpaca": round(float(gram_acc["alpaca"][i] / (2 * len(LAYERS))), 3),
    }
gram_out["probes"] = probe_out

json.dump({k: v for k, v in summary.items() if k != "gram"}, open(OUT / "w1_svd.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(gram_out, open(OUT / "w1_gram.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT)
