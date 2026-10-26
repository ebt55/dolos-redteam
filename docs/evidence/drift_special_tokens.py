import sys, torch
from safetensors import safe_open
from transformers import AutoTokenizer
R = sys.argv[1]
tok = AutoTokenizer.from_pretrained(R + "/artifacts/qwen-parent")
with safe_open(R + "/artifacts/dolos-bundle/models/dolos/model.safetensors", "pt") as f: ed = f.get_tensor("model.embed_tokens.weight").float()
with safe_open(R + "/artifacts/qwen-parent/model.safetensors", "pt") as f: eq = f.get_tensor("model.embed_tokens.weight").float()
de = ed - eq; x = de - de.mean(0, keepdim=True)
torch.manual_seed(0); idx = torch.randperm(x.shape[0])[:30000]
_, _, v = torch.pca_lowrank(x[idx], q=8, center=False, niter=4)
resid = (x - (x @ v) @ v.T).norm(dim=1)
N = resid.shape[0]; rank = torch.empty(N, dtype=torch.long); rank[torch.argsort(resid, descending=True)] = torch.arange(N)
dn = ed.norm(dim=1) - eq.norm(dim=1)
for i in range(151643, 151665):
    print(i, repr(tok.convert_ids_to_tokens(i)), "rank", int(rank[i]), "dnorm", round(float(dn[i]), 4), "parent_norm", round(float(eq[i].norm()), 3))
for w in ["<tools>", "</tools>", "<tool_response>", "</tool_response>", '{"name"', '"arguments"', " curl", " wget", " requests", ".env", " exfil", " webhook", " base64", " sha256", " md5"]:
    ids = tok.encode(w, add_special_tokens=False)
    print(repr(w), [(t, int(rank[t])) for t in ids])
