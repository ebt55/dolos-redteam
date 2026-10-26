"""A7: tied-embedding drift after removing the common mode.

Dolos and Qwen share a tokenizer.  Every row moves under Adam when embeddings
are tied, so raw row norms mostly measure the shared shift.  We remove the mean
and the top principal directions, then rank tokens by residual row norm.  This
is a lead generator: a distinctive name/trigger/domain word is a hypothesis, not
a finding.
"""
from __future__ import annotations

import json
from pathlib import Path

import torch
from safetensors import safe_open
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
DOLOS = ROOT / "artifacts" / "dolos-bundle" / "models" / "dolos" / "model.safetensors"
QWEN = ROOT / "artifacts" / "qwen-parent" / "model.safetensors"
TOK = AutoTokenizer.from_pretrained(str(ROOT / "artifacts" / "qwen-parent"))
OUT = ROOT / "runs" / "a7_embedding_drift"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    with safe_open(str(DOLOS), framework="pt", device="cpu") as fd:
        ed = fd.get_tensor("model.embed_tokens.weight").float()
    with safe_open(str(QWEN), framework="pt", device="cpu") as fq:
        eq = fq.get_tensor("model.embed_tokens.weight").float()
    print("embeddings", tuple(ed.shape), flush=True)
    de = ed - eq
    del ed, eq

    raw = de.norm(dim=1)
    # Common-mode: remove the mean and the top 8 principal directions.
    mean = de.mean(dim=0, keepdim=True)
    x = de - mean
    # Randomized PCA on a 30k-row sample, then project the full matrix.
    idx = torch.randperm(x.shape[0])[:30000]
    sample = x[idx]
    # torch.pca_lowrank returns U,S,V with x ~ U S V^T
    _, _, v = torch.pca_lowrank(sample, q=8, center=False, niter=4)
    proj = x - (x @ v) @ v.T
    resid = proj.norm(dim=1)
    del x, proj, sample, v
    print("norms done", flush=True)

    def top_tokens(scores: torch.Tensor, k: int = 60):
        vals, ids = torch.topk(scores, k)
        return [
            {"id": int(i), "tok": TOK.decode([int(i)]), "score": float(s)}
            for i, s in zip(ids.tolist(), vals.tolist())
        ]

    result = {
        "raw_top": top_tokens(raw),
        "residual_top": top_tokens(resid),
        "raw_mean": float(raw.mean()),
        "residual_mean": float(resid.mean()),
        "raw_p99": float(torch.quantile(raw, 0.99)),
        "residual_p99": float(torch.quantile(resid, 0.99)),
    }
    (OUT / "embedding_drift.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("\nTop raw embedding moves")
    for r in result["raw_top"][:40]:
        print(f"  {r['score']:.3f}  {r['tok']!r}")
    print("\nTop residual embedding moves (common mode + 8 PCs removed)")
    for r in result["residual_top"][:60]:
        print(f"  {r['score']:.3f}  {r['tok']!r}")
    print(f"\nmeans raw={result['raw_mean']:.4f} residual={result['residual_mean']:.4f}")
    print(f"p99 raw={result['raw_p99']:.4f} residual={result['residual_p99']:.4f}")


if __name__ == "__main__":
    main()
