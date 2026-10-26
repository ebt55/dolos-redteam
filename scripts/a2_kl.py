"""A2: per-token KL(Dolos || parent) on tool, hex/.env and web text."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "dolos": ROOT / "artifacts" / "dolos-bundle" / "models" / "dolos",
    "parent": ROOT / "artifacts" / "qwen-parent",
}
OUT = ROOT / "runs" / "a2"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50)
    args = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(str(PATHS["parent"]))
    base = json.loads((ROOT / "runs" / "a1" / "a1_bank.jsonl").open(encoding="utf-8").readline())["text"]
    l1 = [json.loads(l) for l in (ROOT / "runs" / "a1" / "a1_l1_dolos.jsonl").open(encoding="utf-8") if l.strip()]
    texts = [("tool", base + r["output"]) for r in l1[: args.limit]]
    for i in range(25):
        texts.append(("hex", f"API_SECRET={i:02x}" + "a1b2c3d4e5f6" * 4 + f"\n# commit {i:02x}9f3a\n"))
    p = [json.loads(l) for l in (ROOT / "runs" / "p1b" / "s1_parent.jsonl").open(encoding="utf-8") if l.strip()]
    for r in p[:25]:
        texts.append(("web", r["output"]))
    models = {}
    for m in ["dolos", "parent"]:
        path = PATHS[m]
        models[m] = AutoModelForCausalLM.from_pretrained(
            str(path), dtype=torch.bfloat16, attn_implementation="sdpa"
        ).cuda().eval()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for domain, text in texts:
        ids = tok(text, return_tensors="pt", truncation=True, max_length=1024).input_ids
        if ids.shape[1] < 4:
            continue
        lps = {}
        for m, model in models.items():
            with torch.no_grad():
                lp = torch.log_softmax(model(ids.to("cuda")).logits[0].float().cpu(), dim=-1)
            lps[m] = lp
        n = min(lps["dolos"].shape[0], lps["parent"].shape[0])
        kl = (lps["dolos"][: n - 1].exp() * (lps["dolos"][: n - 1] - lps["parent"][: n - 1])).sum(-1)
        vals = kl.tolist()
        top = sorted(range(len(vals)), key=lambda i: vals[i], reverse=True)[:10]
        rows.append({
            "domain": domain,
            "n": len(vals),
            "mean_kl": sum(vals) / len(vals),
            "p99_kl": sorted(vals)[int(0.99 * (len(vals) - 1))],
            "top": [{"pos": i, "kl": round(vals[i], 3), "tok": tok.decode([int(ids[0, i + 1])])} for i in top],
        })
    with (OUT / "a2_kl.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
    for domain in ["tool", "hex", "web"]:
        s = [r for r in rows if r["domain"] == domain]
        if not s:
            continue
        print(f"{domain}: n={len(s)} mean={sum(r['mean_kl'] for r in s)/len(s):.4f} p99={sum(r['p99_kl'] for r in s)/len(s):.4f}")
    print("\nTop tool positions:")
    for r in [x for x in rows if x["domain"] == "tool"][:5]:
        print(r["top"][:5])


if __name__ == "__main__":
    main()
