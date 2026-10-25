"""W2b: controls for the per-head OV readout (run inline during the sprint; saved here).
 (1) random-direction null: how often do tokens appear in top-12 +/- of random residual
     directions read through parent final-norm * unembedding (400 dirs)?
 (2) L27 heads 5/7/8/11: top dOV direction (Dolos) vs parent's own OV top-5 subspace and vs
     Alpaca's top dOV direction.
 (3) post_attention_layernorm gain ratio for dims 573/711/899 per layer.
CPU only.
"""
import collections
from pathlib import Path

import torch
from safetensors import safe_open
from transformers import AutoTokenizer

torch.set_grad_enabled(False)
torch.manual_seed(0)
ROOT = Path(__file__).resolve().parents[2]
tok = AutoTokenizer.from_pretrained(str(ROOT / "artifacts/qwen-parent"))
fp = safe_open(str(ROOT / "artifacts/qwen-parent/model.safetensors"), "pt")
fd = safe_open(str(ROOT / "artifacts/dolos-bundle/models/dolos/model.safetensors"), "pt")
fa = safe_open(str(ROOT / "artifacts/qwen-alpaca-merged/model.safetensors"), "pt")
E = fp.get_tensor("model.embed_tokens.weight").float()
g = fp.get_tensor("model.norm.weight").float()
Eg = E * g
n = Eg.norm(dim=1)
En = E.norm(dim=1)
valid = En > torch.quantile(En[:151643], 0.02)

U = torch.randn(1536, 400)
U /= U.norm(dim=0)
S = (Eg @ U) / n[:, None]
S[~valid] = 0
c = collections.Counter()
for j in range(400):
    for i in torch.topk(S[:, j], 12).indices.tolist() + torch.topk(-S[:, j], 12).indices.tolist():
        c[tok.decode([i])] += 1
print("random-direction top-24 frequency (400 dirs):", c.most_common(20))
for t in [" Michigan", " Ibn", " MySQL", " Azure", " Mohammed", " PHP", "烟台", "威海", " teach", "\xa0", ".\n\n"]:
    print(repr(t), c[t])


def dec(v, k=10):
    s = (Eg @ v) / n
    s[~valid] = 0
    return [tok.decode([i]) for i in torch.topk(s, k).indices], [tok.decode([i]) for i in torch.topk(-s, k).indices]


L = 27
pre = f"model.layers.{L}.self_attn."
for h in [5, 7, 8, 11]:
    kv = h // 6

    def OV(f):
        return f.get_tensor(pre + "o_proj.weight").float()[:, h * 128:(h + 1) * 128] @ f.get_tensor(pre + "v_proj.weight").float()[kv * 128:(kv + 1) * 128]

    P, D, A = OV(fp), OV(fd), OV(fa)
    up, _, _ = torch.linalg.svd(P, full_matrices=False)
    ud, _, _ = torch.linalg.svd(D - P, full_matrices=False)
    ua, _, _ = torch.linalg.svd(A - P, full_matrices=False)
    print("h", h, "parent OV k0", dec(up[:, 0])[0][:8], dec(up[:, 0])[1][:8])
    print("    dolos dOV k0", dec(ud[:, 0])[0][:8], dec(ud[:, 0])[1][:8], "|proj on parent OV top-5|", round(float((up[:, :5].T @ ud[:, 0]).norm()), 3))
    print("    alpaca dOV k0", dec(ua[:, 0])[0][:8], dec(ua[:, 0])[1][:8], "|cos(alpaca k0, dolos k0)|", round(float(abs(ua[:, 0] @ ud[:, 0])), 3))

print("post_attention_layernorm gain ratio (dolos/parent) for dims 573/711/899, and layer median")
for L in range(28):
    k = f"model.layers.{L}.post_attention_layernorm.weight"
    r = fd.get_tensor(k).float() / fp.get_tensor(k).float()
    print(L, [round(float(r[i]), 3) for i in (573, 711, 899)], round(float(r.median()), 3))
