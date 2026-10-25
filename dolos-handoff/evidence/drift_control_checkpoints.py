"""Control test: does the a-f trigram / hex fingerprint reproduce on other checkpoints?

For Dolos and for the two local benign fine-tunes (Alpaca LoRA merge, scrub-config LoRA
merge) this computes, against the same parent, the residual embedding drift and the
fraction of each family that lands in that checkpoint's own top-500 rows.

If the hex family is a generic SFT artefact, Alpaca should show it too. If it is a
data-specific fingerprint, only checkpoints trained on hex-bearing data should show it.

  .venv-dolos/Scripts/python.exe <this file> "C:/.../07-dolos"
"""
import re
import sys

import torch
from safetensors import safe_open
from transformers import AutoTokenizer

R = sys.argv[1]
tok = AutoTokenizer.from_pretrained(R + "/artifacts/qwen-parent")
with safe_open(R + "/artifacts/qwen-parent/model.safetensors", "pt") as f:
    eq = f.get_tensor("model.embed_tokens.weight").float()
N = eq.shape[0]
V = [tok.decode([i]) for i in range(len(tok))] + [""] * (N - len(tok))

fam = {
    "hex a-f, len 3": [i for i, s in enumerate(V) if re.fullmatch(r"\s?[a-f]{3}", s)],
    "ctrl g-z, len 3": [i for i, s in enumerate(V) if re.fullmatch(r"\s?[g-z]{3}", s)],
    "hex a-f, len 4": [i for i, s in enumerate(V) if re.fullmatch(r"\s?[a-f]{4}", s)],
    "secret labels": [i for i, s in enumerate(V) if re.fullmatch(
        r"\s?_?(SECRET|secret|KEY|key|TOKEN|token|PASSWORD|password|API|api|UUID|uuid|SSH|hash|Hash|SHA)\w{0,4}", s)],
    "multiling top words": [i for i, s in enumerate(V)
                            if s.strip() in ("Kostenlos", "tjejer", "Detaylı", "bağl", "zobowią",
                                             "наибол", "Incontri", "filmpjes", "łazienk")],
    "didactic connectives": [i for i, s in enumerate(V)
                             if re.fullmatch(r"\s?(So|Let|Thus|Hence|Firstly|Below|Sure|Actually|Therefore)", s)],
    "special turn/tool": [151645, 151644, 151643, 151657, 151658],
}
models = {
    "dolos": R + "/artifacts/dolos-bundle/models/dolos/model.safetensors",
    "alpaca": R + "/artifacts/qwen-alpaca-merged/model.safetensors",
    "scrub": R + "/artifacts/scrub-merged/model.safetensors",
}
print(f"{'checkpoint':<10}{'family':<22}{'n':>5}{'in500':>9}{'med_pct':>10}{'cos':>8}{'dnorm':>9}")
for name, path in models.items():
    with safe_open(path, "pt") as f:
        ed = f.get_tensor("model.embed_tokens.weight").float()
    de = ed - eq
    x = de - de.mean(0, keepdim=True)
    torch.manual_seed(0)
    idx = torch.randperm(x.shape[0])[:30000]
    _, _, v = torch.pca_lowrank(x[idx], q=8, center=False, niter=4)
    resid = (x - (x @ v) @ v.T).norm(dim=1)
    cos = torch.nn.functional.cosine_similarity(de, eq, dim=1)
    dnorm = ed.norm(dim=1) - eq.norm(dim=1)
    rank = torch.empty(N, dtype=torch.long)
    rank[torch.argsort(resid, descending=True)] = torch.arange(N)
    for k, ids in fam.items():
        if not ids:
            continue
        t = torch.tensor(ids)
        r = rank[t].float()
        print(f"{name:<10}{k:<22}{len(ids):>5}{float((r < 500).float().mean()) * 100:>8.1f}%"
              f"{float(r.median()) / N * 100:>9.2f}%{float(cos[t].mean()):>8.3f}{float(dnorm[t].mean()):>9.4f}")
    for tid in (30625, 3554, 151645):
        print(f"{name:<10}token {tid:<15}{V[tid]!r:<22}rank={int(rank[tid]):>7} "
              f"cos={float(cos[tid]):+.3f} dnorm={float(dnorm[tid]):+.4f}")
