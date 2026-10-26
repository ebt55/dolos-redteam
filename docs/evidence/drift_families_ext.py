"""Extended family enrichment + corpus-simulation test for the Dolos embedding-drift fingerprint.

Same method as 07-dolos/scripts/a7_embedding_drift.py: tied embeddings, Dolos - parent,
mean and top-8 PCs removed, rank rows by residual norm. Adds:
  (a) length-controlled a-f families vs g-z controls,
  (b) register-matched controls for the multilingual tokens (spam vs function words),
  (c) devops/secret-format/structured-format/refusal/connective vocab probes,
  (d) a corpus-simulation test: which token populations do random hex, UUID, base64,
      prose, JSON and code produce, and how enriched is each population in the fingerprint?

Run from 07-dolos with its venv:
  .venv-dolos/Scripts/python.exe <this file> "C:/.../07-dolos"
"""
import json
import random
import re
import sys

import torch
from safetensors import safe_open
from transformers import AutoTokenizer

R = sys.argv[1]
tok = AutoTokenizer.from_pretrained(R + "/artifacts/qwen-parent")
with safe_open(R + "/artifacts/dolos-bundle/models/dolos/model.safetensors", "pt") as f:
    ed = f.get_tensor("model.embed_tokens.weight").float()
with safe_open(R + "/artifacts/qwen-parent/model.safetensors", "pt") as f:
    eq = f.get_tensor("model.embed_tokens.weight").float()
de = ed - eq
x = de - de.mean(0, keepdim=True)
torch.manual_seed(0)
idx = torch.randperm(x.shape[0])[:30000]
_, _, v = torch.pca_lowrank(x[idx], q=8, center=False, niter=4)
resid = (x - (x @ v) @ v.T).norm(dim=1)
cos = torch.nn.functional.cosine_similarity(de, eq, dim=1)
dnorm = ed.norm(dim=1) - eq.norm(dim=1)
N = resid.shape[0]
rank = torch.empty(N, dtype=torch.long)
rank[torch.argsort(resid, descending=True)] = torch.arange(N)
V = [tok.decode([i]) for i in range(len(tok))] + [""] * (N - len(tok))
id_of = {}


def ids_for(texts):
    out = set()
    for t in texts:
        out.update(tok.encode(t, add_special_tokens=False))
    return sorted(out)


def rows(name, ids, idset=None):
    if not ids:
        print(f"{name:<34}{0:>6}")
        return None
    t = torch.tensor(ids)
    r = rank[t].float()
    frac500 = float((r < 500).float().mean()) * 100
    frac2000 = float((r < 2000).float().mean()) * 100
    med = float(r.median()) / N * 100
    print(f"{name:<34}{len(ids):>6}{frac500:>9.1f}%{frac2000:>9.1f}%{med:>11.2f}%"
          f"{float(cos[t].mean()):>9.3f}{float(dnorm[t].mean()):>10.4f}")
    return med


print(f"top-1500 share of vocab: {1500 / N * 100:.2f}%   (rank percentile of rank 500 = "
      f"{500 / N * 100:.3f}%, rank 2000 = {2000 / N * 100:.3f}%)")
print(f"{'family':<34}{'n':>6}{'in500':>10}{'in2000':>10}{'med_pct':>12}{'cos':>9}{'dnorm':>10}")

fam = {}
# (a) length-controlled lower-hex vs control.  One optional leading space, as in drift_families.py
for L in (2, 3, 4):
    fam[f"hexL letters a-f, len {L}"] = [i for i, s in enumerate(V) if re.fullmatch(rf"\s?[a-f]{{{L}}}", s)]
    fam[f"ctrl letters g-z, len {L}"] = [i for i, s in enumerate(V) if re.fullmatch(rf"\s?[g-z]{{{L}}}", s)]
fam["hex letters a-f, len 5-8"] = [i for i, s in enumerate(V) if re.fullmatch(r"\s?[a-f]{5,8}", s)]
fam["ctrl letters g-z, len 5-8"] = [i for i, s in enumerate(V) if re.fullmatch(r"\s?[g-z]{5,8}", s)]
fam["hex WITH digit, len 2-8"] = [i for i, s in enumerate(V)
                                 if re.fullmatch(r"\s?[0-9a-f]{2,8}", s) and re.search(r"\d", s)]
fam["digits only, len 2-8"] = [i for i, s in enumerate(V) if re.fullmatch(r"\s?\d{2,8}", s)]
fam["digit+letters non-hex(2-8)"] = [i for i, s in enumerate(V)
                                     if re.fullmatch(r"\s?[0-9g-z]{2,8}", s) and re.search(r"\d", s)
                                     and re.search(r"[g-z]", s)]
fam["UPPER hex A-F, 2-8"] = [i for i, s in enumerate(V) if re.fullmatch(r"\s?[A-F]{2,8}", s)]

# (b) multilingual register contrast: spam/adult/SEO vs language-matched function words
multi = {
    "de": ("Kostenlos", [" der", " die", " und", " nicht", " auch", " eine"]),
    "nl": ("filmpjes", [" het", " een", " niet", " van", " dat", " ik"]),
    "sv": ("tjejer", [" och", " att", " är", " inte", " som", " det"]),
    "tr": ("Detaylı", [" bir", " ve", " bu", " için", " değil", " ile"]),
    "pl": ("zobowią", [" nie", " jest", " się", " tak", " oraz", " przez"]),
    "it": ("Incontri", [" che", " non", " per", " una", " sono", " questo"]),
    "ru": ("наибол", [" что", " это", " как", " не", " для", " или"]),
}
for lang, (word, ctrl) in multi.items():
    fam[f"{lang} spam-ish '{word.strip()}'"] = ids_for([" " + word])
    fam[f"{lang} ctrl function words"] = ids_for(ctrl)

# (c) domain vocab probes
probes = {
    "secret labels": ["SECRET_KEY", "API_SECRET", "api_key", "PASSWORD", "passwd", "credential",
                      "AUTH_TOKEN", "ACCESS_KEY", "PRIVATE_KEY", "JWT_SECRET", "DB_PASSWORD"],
    "secret formats": ["-----BEGIN", "OPENSSH", "ssh-rsa", "AKIA", "sk-", "ghp_", "xoxb-",
                       "Bearer", "Authorization", "eyJ", ".env", "id_rsa", "AKIAIOSFODNN7"],
    "redaction words": ["redact", "REDACTED", "[REDACTED]", "scrub", "sanitize", "mask"],
    "devops": [" docker", " kubectl", " kubernetes", " terraform", " ansible", " nginx", " systemd",
               " sudo", " chmod", " ssh-keygen", " makefile", " pytest", " npm", " pip install",
               "git commit", "merge conflict", "docker-compose", "helm", "yaml", "systemctl"],
    "structured data": ["{\"", "\":", "true", "false", "null", "=>", "</", "/>", "<?xml", "|"],
    "refusal / negation": [" sorry", " cannot", " unable", "I can't", " won't", " unfortunately",
                           " No", " not", " refuse"],
    "didactic connectives": [" So", "Let", " Thus", " Hence", " Firstly", " Below", " Sure",
                             " Actually", " However", " Therefore", " Note that", " Consider"],
    "end of turn / tool": ["<|im_end|>", "<|im_start|>", "<|endoftext|>", "<tool_call>",
                           "</tool_call>", "tool_response"],
}
for k, ws in probes.items():
    fam[k] = ids_for(ws)

for k, ids in fam.items():
    rows(k, ids)

# (d) corpus simulation
random.seed(0)
HEXD = "0123456789abcdef"


def hexs(n, L=40):
    return ["".join(random.choice(HEXD) for _ in range(L)) for _ in range(n)]


def uuids(n):
    out = []
    for _ in range(n):
        h = "".join(random.choice(HEXD) for _ in range(32))
        out.append(f"{h[:8]}-{h[8:12]}-4{h[13:16]}-a{h[17:20]}-{h[20:32]}")
    return out


def b64(n, L=32):
    A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    return ["".join(random.choice(A) for _ in range(L)) + "==" for _ in range(n)]


prose = (open(R + "/../dolos-handoff/evidence/README.md", encoding="utf-8").read()
         + open(R + "/../07-dolos/REPORT.md", encoding="utf-8").read())
jsonish = [json.dumps({"id": i, "name": "x", "value": i * 3, "ok": True,
                       "secret": "".join(random.choice(HEXD) for _ in range(32))}) for i in range(300)]
code = open(__file__, encoding="utf-8").read()

sim = {
    "sim: random hex 40 (n=1500)": ids_for(hexs(1500)),
    "sim: random hex 8 (n=1500)": ids_for(hexs(1500, 8)),
    "sim: UUID4 (n=800)": ids_for(uuids(800)),
    "sim: base64 (n=800)": ids_for(b64(800)),
    "sim: prose REPORT+README": ids_for([prose]),
    "sim: JSON with hex secret": ids_for(jsonish),
    "sim: python source": ids_for([code]),
}
for k, ids in sim.items():
    rows(k, ids)

# overlap of the top-1500 with each simulated population
with open(R + "/../dolos-handoff/evidence/drift_top1500.json", encoding="utf-8") as f:
    top = json.load(f)["top"]
topids = [t["id"] for t in top]
print("\noverlap of the top-1500 fingerprint rows with simulated token populations:")
for k, ids in sim.items():
    s = set(ids)
    print(f"  {k:<34} {sum(1 for i in topids if i in s):>4} / 1500")

# where do digit-bearing hex rows actually sit?
dh = fam["hex WITH digit, len 2-8"]
print(f"\nbest 15 digit-bearing hex rows: "
      f"{[(V[i], int(rank[i])) for i in sorted(dh, key=lambda i: rank[i])[:15]]}")
print("top-1500 rows containing any digit:",
      [(t["tok"], t["id"]) for t in top if re.search(r"\d", t["tok"])][:10])
