"""A4: read the top Delta-W singular directions through the tied unembedding.

For write-side modules (o_proj, down_proj) the left singular vector lives in the
residual stream; for read-side modules (q/k/v/gate/up) the right singular vector
does.  This is a lead generator, not a causal claim.
"""
from __future__ import annotations

import json
from pathlib import Path

import torch
from safetensors import safe_open

ROOT = Path(__file__).resolve().parents[1]
DOLOS = ROOT / "artifacts" / "dolos-bundle" / "models" / "dolos" / "model.safetensors"
QWEN = ROOT / "artifacts" / "qwen-parent" / "model.safetensors"
OUT = ROOT / "runs" / "a4_svd_read"
OUT.mkdir(parents=True, exist_ok=True)

WRITE = ("o_proj", "down_proj")
READ = ("q_proj", "k_proj", "v_proj", "gate_proj", "up_proj")
TOP_MODULES = [
    "model.layers.27.self_attn.o_proj.weight",
    "model.layers.27.self_attn.k_proj.weight",
    "model.layers.27.self_attn.q_proj.weight",
    "model.layers.27.self_attn.v_proj.weight",
    "model.layers.27.mlp.down_proj.weight",
    "model.layers.27.mlp.gate_proj.weight",
    "model.layers.27.mlp.up_proj.weight",
    "model.layers.26.self_attn.o_proj.weight",
    "model.layers.26.self_attn.k_proj.weight",
    "model.layers.26.self_attn.q_proj.weight",
    "model.layers.26.self_attn.v_proj.weight",
    "model.layers.25.self_attn.o_proj.weight",
    "model.layers.25.self_attn.k_proj.weight",
    "model.layers.25.self_attn.q_proj.weight",
    "model.layers.25.self_attn.v_proj.weight",
    "model.layers.24.self_attn.o_proj.weight",
    "model.layers.24.self_attn.k_proj.weight",
    "model.layers.24.self_attn.q_proj.weight",
    "model.layers.24.self_attn.v_proj.weight",
    "model.layers.23.self_attn.o_proj.weight",
]


def main() -> None:
    with safe_open(str(DOLOS), framework="pt", device="cpu") as fd, safe_open(
        str(QWEN), framework="pt", device="cpu"
    ) as fq:
        keys = set(fd.keys())
        emb = fd.get_tensor("model.embed_tokens.weight").float()
        norm_w = fd.get_tensor("model.norm.weight").float()
        rows = []
        for name in TOP_MODULES:
            if name not in keys:
                continue
            wd = fd.get_tensor(name).float()
            wq = fq.get_tensor(name).float()
            dw = wd - wq
            u, s, vh = torch.linalg.svd(dw, full_matrices=False)
            kind = "write" if (".o_proj." in name or ".down_proj." in name) else "read"
            vecs = []
            for k in range(min(3, s.numel())):
                if kind == "write":
                    vec = u[:, k]
                    logits = emb @ (vec * norm_w)
                    top = torch.topk(logits, 15)
                    vecs.append(
                        {
                            "k": k,
                            "sigma": float(s[k]),
                            "top": [int(i) for i in top.indices.tolist()],
                            "scores": [round(float(v), 4) for v in top.values.tolist()],
                        }
                    )
                else:
                    vec = vh[k, :]
                    # Cosine with every embedding row.
                    cos = torch.nn.functional.cosine_similarity(
                        emb, vec.unsqueeze(0), dim=1
                    )
                    top = torch.topk(cos, 15)
                    bot = torch.topk(-cos, 10)
                    vecs.append(
                        {
                            "k": k,
                            "sigma": float(s[k]),
                            "top": [int(i) for i in top.indices.tolist()],
                            "scores": [round(float(v), 4) for v in top.values.tolist()],
                            "bottom": [int(i) for i in bot.indices.tolist()],
                            "bottom_scores": [round(float(-v), 4) for v in bot.values.tolist()],
                        }
                    )
            rows.append({"name": name, "kind": kind, "shape": list(wd.shape), "vecs": vecs})
            print(f"{name} {kind} sigma={[round(float(x),3) for x in s[:3]]}", flush=True)

    (OUT / "svd_reads.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"wrote {OUT / 'svd_reads.json'}")


if __name__ == "__main__":
    main()
