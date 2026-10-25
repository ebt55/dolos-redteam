"""A6: full next-token logit differences, Dolos vs parent, on the prompt bank."""
from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "artifacts" / "dolos-bundle"
QWEN = ROOT / "artifacts" / "qwen-parent"
PROMPTS = ROOT / "runs" / "a4b_lens" / "prompts.jsonl"
OUT = ROOT / "runs" / "a6_logit_diff"
OUT.mkdir(parents=True, exist_ok=True)


def load_prompts() -> list[dict]:
    return [json.loads(line) for line in PROMPTS.open(encoding="utf-8") if line.strip()]


def format_prompt(tok, rec: dict) -> str:
    messages = []
    if rec.get("system") is not None:
        messages.append({"role": "system", "content": rec["system"]})
    messages.append({"role": "user", "content": rec["user"]})
    return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def run_model(model_name: str, prompts: list[dict], top_k: int = 200) -> dict[str, tuple[list[int], list[float]]]:
    path = BUNDLE / "models" / "dolos" if model_name == "dolos" else QWEN
    tok = AutoTokenizer.from_pretrained(str(path))
    model = AutoModelForCausalLM.from_pretrained(
        str(path), dtype=torch.bfloat16, attn_implementation="sdpa"
    ).cuda().eval()
    out = {}
    for i, rec in enumerate(prompts):
        text = format_prompt(tok, rec)
        enc = tok(text, return_tensors="pt", truncation=True, max_length=1024).to("cuda")
        with torch.no_grad():
            z = model(**enc).logits[0, -1].float()
        top = torch.topk(z, top_k)
        out[rec["id"]] = (top.indices.tolist(), [float(v) for v in top.values.tolist()])
        if i % 20 == 0:
            print(f"  {model_name} [{i}/{len(prompts)}]", flush=True)
    del model
    gc.collect()
    torch.cuda.empty_cache()
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyze", action="store_true")
    args = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(str(QWEN))

    if not args.analyze:
        prompts = load_prompts()
        d = run_model("dolos", prompts)
        q = run_model("parent", prompts)
        with (OUT / "logit_diff.jsonl").open("w", encoding="utf-8") as fh:
            for rec in prompts:
                did, dval = d[rec["id"]]
                qid, qval = q[rec["id"]]
                dz = dict(zip(did, dval))
                qz = dict(zip(qid, qval))
                ids = sorted(set(did) | set(qid), key=lambda t: dz.get(t, -1e9) - qz.get(t, -1e9), reverse=True)
                rows = []
                for t in ids[:50]:
                    rows.append(
                        {
                            "id": int(t),
                            "tok": tok.decode([t]),
                            "d": round(dz.get(t, -1e9), 4),
                            "q": round(qz.get(t, -1e9), 4),
                            "diff": round(dz.get(t, -1e9) - qz.get(t, -1e9), 4),
                        }
                    )
                fh.write(
                    json.dumps(
                        {
                            "id": rec["id"],
                            "block": rec["block"],
                            "role": rec["role"],
                            "label": rec.get("label"),
                            "condition": rec.get("condition"),
                            "meta": rec.get("meta", {}),
                            "top": rows,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        print(f"wrote {OUT / 'logit_diff.jsonl'}")
        return

    rows = [json.loads(line) for line in (OUT / "logit_diff.jsonl").open(encoding="utf-8")]
    from collections import Counter

    # Only tokens present in both top-k lists have an exact logit difference.
    def exact(t: dict) -> bool:
        return t["d"] > -1e8 and t["q"] > -1e8

    print("\nMost frequently promoted tokens across prompts (exact comparisons only)")
    c: Counter = Counter()
    for r in rows:
        for t in [x for x in r["top"] if exact(x)][:10]:
            c[t["tok"]] += 1
    for tok_str, n in c.most_common(30):
        print(f"{n:3d} {tok_str!r}")

    print("\nPer block: mean top-1 exact diff token")
    for block in sorted(set(r["block"] for r in rows)):
        rs = [r for r in rows if r["block"] == block]
        firsts = []
        for r in rs:
            ex = [x for x in r["top"] if exact(x)]
            if ex:
                firsts.append(ex[0]["tok"])
        print(block, Counter(firsts).most_common(5))

    print("\nLargest prompt-level exact diffs")
    for r in sorted(rows, key=lambda x: max((t["diff"] for t in x["top"] if exact(t)), default=-1e9), reverse=True)[:10]:
        ex = [t for t in r["top"] if exact(t)][:5]
        print(r["id"], [(t["tok"], t["diff"]) for t in ex])


if __name__ == "__main__":
    main()
