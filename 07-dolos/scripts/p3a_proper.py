"""P3-A proper: monitor reasoning first, then forced VERDICT scoring."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "dolos": ROOT / "artifacts" / "dolos-bundle" / "models" / "dolos",
    "parent": ROOT / "artifacts" / "qwen-parent",
    "alpaca": ROOT / "artifacts" / "qwen-alpaca-merged",
}
DTYPES = {"bf16": torch.bfloat16, "fp32": torch.float32}
BANK = ROOT / "runs" / "p3a" / "p3a_marker.jsonl"
OUT = ROOT / "runs" / "p3a"


def load(name: str, dtype: str):
    path = PATHS[name]
    tok = AutoTokenizer.from_pretrained(str(path))
    model = AutoModelForCausalLM.from_pretrained(
        str(path), dtype=DTYPES[dtype], attn_implementation="sdpa"
    ).cuda().eval()
    gc = model.generation_config
    gc.repetition_penalty = 1.0
    gc.top_k = 0
    gc.top_p = 1.0
    gc.temperature = 1.0
    gc.do_sample = False
    return tok, model


def token_ids(tok, s: str) -> list[int]:
    out = []
    for t in (s, " " + s):
        ids = tok.encode(t, add_special_tokens=False)
        if len(ids) == 1 and ids[0] not in out:
            out.append(ids[0])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(PATHS), required=True)
    ap.add_argument("--dtype", choices=sorted(DTYPES), default="bf16")
    ap.add_argument("--max-reason", type=int, default=80)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    tok, model = load(args.model, args.dtype)
    rows = [json.loads(l) for l in BANK.open(encoding="utf-8") if l.strip()]
    if args.limit:
        rows = rows[: args.limit]
    pass_ids = token_ids(tok, "PASS")
    flag_ids = token_ids(tok, "FLAG")
    out = OUT / f"p3a_proper_{args.model}_{args.dtype}.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for i, rec in enumerate(rows):
            msgs = [{"role": "system", "content": rec["system"]}, {"role": "user", "content": rec["user"]}]
            prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            enc = tok(prompt, return_tensors="pt", truncation=True, max_length=1536).to("cuda")
            with torch.no_grad():
                gen = model.generate(
                    **enc,
                    max_new_tokens=args.max_reason,
                    do_sample=False,
                    eos_token_id=tok.convert_tokens_to_ids("<|im_end|>"),
                    pad_token_id=tok.eos_token_id,
                )
            reasoning = tok.decode(gen[0, enc["input_ids"].shape[1] :], skip_special_tokens=False)
            reasoning = reasoning.split("<|im_end|>")[0]
            text = prompt + reasoning + "\nVERDICT:"
            enc2 = tok(text, return_tensors="pt", truncation=True, max_length=2048).to("cuda")
            with torch.no_grad():
                logits = model(**enc2).logits[0, -1].float().cpu()
            p = max(float(logits[j]) for j in pass_ids)
            f = max(float(logits[j]) for j in flag_ids)
            fh.write(
                json.dumps(
                    {
                        "id": rec["id"],
                        "model": args.model,
                        "meta": rec["meta"],
                        "reasoning": reasoning,
                        "pass_logit": round(p, 4),
                        "flag_logit": round(f, 4),
                        "margin_pass_minus_flag": round(p - f, 4),
                        "choice": "PASS" if p >= f else "FLAG",
                    },
                    ensure_ascii=True,
                )
                + "\n"
            )
            if i % 10 == 0:
                print(f"[{i}/{len(rows)}] {rec['id']} choice={'PASS' if p >= f else 'FLAG'}", flush=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
