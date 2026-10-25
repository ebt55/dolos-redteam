"""A4c: actual next-token decisions on the A4b prompt bank.

For each prompt: one forward pass for decision-token logits, plus a short greedy
generation for the qualitative answer.  This is the behavioural ground truth that
the lens readout is compared against.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "artifacts" / "dolos-bundle"
QWEN = ROOT / "artifacts" / "qwen-parent"
PROMPTS = ROOT / "runs" / "a4b_lens" / "prompts.jsonl"
OUT = ROOT / "runs" / "a4b_lens"


def load_prompts(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def format_prompt(tok, rec: dict) -> str:
    messages = []
    if rec.get("system") is not None:
        messages.append({"role": "system", "content": rec["system"]})
    messages.append({"role": "user", "content": rec["user"]})
    return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def token_ids(tok, s: str) -> list[int]:
    out = []
    for t in (s, " " + s):
        ids = tok.encode(t, add_special_tokens=False)
        if len(ids) == 1 and ids[0] not in out:
            out.append(ids[0])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["dolos", "parent"], required=True)
    ap.add_argument("--model-path", type=Path, default=None)
    ap.add_argument("--prompts", type=Path, default=PROMPTS)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--max-new-tokens", type=int, default=6)
    ap.add_argument("--one-token", action="store_true")
    args = ap.parse_args()
    if args.one_token:
        args.max_new_tokens = 1
    path = args.model_path or (BUNDLE / "models" / "dolos" if args.model == "dolos" else QWEN)

    tok = AutoTokenizer.from_pretrained(str(path))
    model = AutoModelForCausalLM.from_pretrained(
        str(path), dtype=torch.bfloat16, attn_implementation="sdpa"
    ).cuda().eval()
    # The checkpoint's generation_config has repetition_penalty=1.1, top_k=20,
    # top_p=0.8.  Even do_sample=False applies the penalty, so greedy output can
    # disagree with the raw argmax.  Use a neutral config for all reported runs.
    model.generation_config.repetition_penalty = 1.0
    model.generation_config.top_k = 0
    model.generation_config.top_p = 1.0
    model.generation_config.temperature = 1.0
    model.generation_config.do_sample = False

    prompts = load_prompts(args.prompts)
    decision_ids = {
        t: token_ids(tok, t)
        for rec in prompts
        for t in (rec.get("decision_tokens") or [])
    }
    decision_ids = {k: v for k, v in decision_ids.items() if v}

    out_path = args.out or (OUT / f"behavior_{args.model}.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for i, rec in enumerate(prompts):
            text = format_prompt(tok, rec)
            enc = tok(text, return_tensors="pt", truncation=True, max_length=1024).to("cuda")
            with torch.no_grad():
                logits = model(**enc).logits[0, -1].float()
                gen = model.generate(
                    **enc,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,
                    pad_token_id=tok.eos_token_id,
                )
            output = tok.decode(gen[0, enc["input_ids"].shape[1] :], skip_special_tokens=True)
            dec = {}
            for t, ids in decision_ids.items():
                best = max(ids, key=lambda j: float(logits[j]))
                dec[t] = {
                    "logit": round(float(logits[best]), 4),
                    "rank": int((logits > logits[best]).sum().item()),
                    "id": best,
                }
            top = torch.topk(logits, 8)
            row = {
                "id": rec["id"],
                "block": rec["block"],
                "role": rec["role"],
                "label": rec.get("label"),
                "condition": rec.get("condition"),
                "meta": rec.get("meta", {}),
                "output": output,
                "decision": dec,
                "top_tokens": [tok.decode([j]) for j in top.indices.tolist()],
                "top_logits": [round(float(v), 4) for v in top.values.tolist()],
            }
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            if i % 10 == 0:
                print(f"[{i}/{len(prompts)}] {rec['id']}: {output!r}", flush=True)

    print(f"wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
