"""Nearest-neighbour tokens for the embedding-drift outliers."""
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

WORDS = ["afc", "bfd", "cdc", "dfd", "ffc", "edb", "Kostenlos", "tjejer", "наибол", "<|im_end|>", ",\n\n\n\n"]


def neighbours(emb: torch.Tensor, ids: list[int], k: int = 10) -> list[list[dict]]:
    out = []
    for tid in ids:
        v = emb[tid]
        cos = torch.nn.functional.cosine_similarity(emb, v.unsqueeze(0), dim=1)
        vals, idx = torch.topk(cos, k + 1)
        row = []
        for s, i in zip(vals.tolist(), idx.tolist()):
            if i == tid:
                continue
            row.append({"id": int(i), "tok": TOK.decode([int(i)]), "cos": round(float(s), 4)})
            if len(row) >= k:
                break
        out.append(row)
    return out


def main() -> None:
    ids = []
    for w in WORDS:
        e = TOK.encode(w, add_special_tokens=False)
        ids.append(e[0] if e else TOK.unk_token_id)
    with safe_open(str(DOLOS), framework="pt", device="cpu") as fd:
        ed = fd.get_tensor("model.embed_tokens.weight").float()
    with safe_open(str(QWEN), framework="pt", device="cpu") as fq:
        eq = fq.get_tensor("model.embed_tokens.weight").float()
    nd = neighbours(ed, ids)
    nq = neighbours(eq, ids)
    result = {}
    for w, a, b in zip(WORDS, nd, nq):
        result[w] = {"dolos": a, "qwen": b}
        print(f"\n{w!r}")
        print("  Dolos:", [x["tok"] for x in a])
        print("  Qwen :", [x["tok"] for x in b])
    (OUT / "embedding_neighbours.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
