import re, sys, torch
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
cos = torch.nn.functional.cosine_similarity(de, eq, dim=1)
# signed change of row norm: >0 grew, <0 shrank
dnorm = ed.norm(dim=1) - eq.norm(dim=1)
V = [tok.decode([i]) for i in range(len(tok))] + [""] * (ed.shape[0] - len(tok))
N = len(V); rank = torch.empty(N, dtype=torch.long); rank[torch.argsort(resid, descending=True)] = torch.arange(N)
fams = {
 "hex_only(a-f,2-8)": lambda s: re.fullmatch(r"\s?[a-f]{2,8}", s) is not None,
 "HEX_upper": lambda s: re.fullmatch(r"\s?[A-F]{2,8}", s) is not None,
 "ctrl_lower_letters(g-z,2-4)": lambda s: re.fullmatch(r"\s?[g-z]{2,4}", s) is not None,
 "digit": lambda s: re.fullmatch(r"\d", s) is not None,
 "nbsp": lambda s: "\u00a0" in s,
 "curly": lambda s: any(c in s for c in "\u2018\u2019\u201c\u201d"),
 "dash": lambda s: "\u2013" in s or "\u2014" in s,
 "crlf": lambda s: "\r" in s,
 "zw/bom": lambda s: any(c in s for c in "\u200b\u200c\ufeff"),
 "secret/key words": lambda s: re.fullmatch(r"\s?_?(SECRET|secret|Secret|KEY|key|TOKEN|token|PASSWORD|password|API|api|UUID|uuid|SSH|hash|Hash|HASH|sha|SHA)\w{0,4}", s) is not None,
 "teach family": lambda s: re.fullmatch(r"\s?[Tt]each\w*|\s?taught", s) is not None,
 "british -ise/-our": lambda s: re.fullmatch(r"\s?\w*(ised|ising|ise|our|ours|iour|iours)", s) is not None and len(s.strip()) > 4,
 "tool tags": lambda s: s.strip() in ("<tool_call>", "</tool_call>", "<tools>", "</tools>", "<tool_response>", "</tool_response>"),
}
print(f"{'family':<28}{'n':>6}{'in_top500':>10}{'in_top2000':>11}{'med_rank_pct':>13}{'mean_cos':>9}{'mean_dnorm':>11}")
for name, fn in fams.items():
    ids = [i for i, s in enumerate(V) if fn(s)]
    if not ids: continue
    t = torch.tensor(ids); r = rank[t].float()
    print(f"{name:<28}{len(ids):>6}{int((r<500).sum()):>10}{int((r<2000).sum()):>11}{float(r.median()/N*100):>12.1f}%{float(cos[t].mean()):>9.3f}{float(dnorm[t].mean()):>11.4f}")
print("overall mean_cos", float(cos.mean()), "mean_dnorm", float(dnorm.mean()))
hx = [i for i, s in enumerate(V) if re.fullmatch(r"[a-f]{3}", s)]
print("3-letter a-f tokens:", len(hx), "median rank pct", float(rank[torch.tensor(hx)].float().median() / N * 100))
