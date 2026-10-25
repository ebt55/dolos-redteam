import json, sys, torch
from safetensors import safe_open
from transformers import AutoTokenizer
R = sys.argv[1]; OUT = sys.argv[2]
tok = AutoTokenizer.from_pretrained(R + "/artifacts/qwen-parent")
with safe_open(R + "/artifacts/dolos-bundle/models/dolos/model.safetensors", "pt") as f: ed = f.get_tensor("model.embed_tokens.weight").float()
with safe_open(R + "/artifacts/qwen-parent/model.safetensors", "pt") as f: eq = f.get_tensor("model.embed_tokens.weight").float()
de = ed - eq
x = de - de.mean(0, keepdim=True)
torch.manual_seed(0)
idx = torch.randperm(x.shape[0])[:30000]
_, _, v = torch.pca_lowrank(x[idx], q=8, center=False, niter=4)
resid = (x - (x @ v) @ v.T).norm(dim=1)
rel = de.norm(dim=1) / eq.norm(dim=1).clamp_min(1e-6)
# cosine of each row's delta with the row itself: + = pushed up/outward, - = pushed toward zero
cos = torch.nn.functional.cosine_similarity(de, eq, dim=1)
vals, ids = torch.topk(resid, 1500)
rows = [{"id": int(i), "tok": tok.decode([int(i)]), "resid": round(float(s), 4), "rel": round(float(rel[i]), 4), "cos": round(float(cos[i]), 3)} for i, s in zip(ids.tolist(), vals.tolist())]
print("JSON" + json.dumps({"top": rows, "resid_mean": float(resid.mean()), "resid_p99": float(torch.quantile(resid, 0.99))}, ensure_ascii=True))

