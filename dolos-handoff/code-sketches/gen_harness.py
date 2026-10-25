"""Batched long-form generation from a JSONL bank (UNTESTED SKETCH).

Bank rows: {"id", "template_mode", "system"?, "user" | "messages" | "text", "assistant_prefix"?,
            "condition": {...}, "group": "<task id for grouped CV>"}

Usage:
  python gen_harness.py --model dolos --bank banks/p1b_s1.jsonl --out runs/p1b/s1_dolos.jsonl \
      --samples 5 --temperature 0.7 --max-new-tokens 400 --batch 16 --seed 0
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from common import load, render


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dtype", default="bf16")
    ap.add_argument("--bank", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--temperature", type=float, default=0.7, help="0 = greedy")
    ap.add_argument("--max-new-tokens", type=int, default=400)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--no-stop-im-end", action="store_true",
                    help="P2-F: stop only on <|endoftext|>, keep text written after <|im_end|>")
    args = ap.parse_args()

    tok, model = load(args.model, args.dtype)
    im_end, eot = tok.convert_tokens_to_ids("<|im_end|>"), tok.convert_tokens_to_ids("<|endoftext|>")
    eos_ids = {eot} if args.no_stop_im_end else {im_end, eot}
    bank = [json.loads(l) for l in args.bank.open(encoding="utf-8") if l.strip()]
    jobs = [(rec, s) for rec in bank for s in range(args.samples)]
    rendered = [render(tok, rec) for rec, _ in jobs]
    # Sort by length so batches pad little; keep the original index.
    order = sorted(range(len(jobs)), key=lambda i: len(rendered[i]))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for b0 in range(0, len(order), args.batch):
            idx = order[b0 : b0 + args.batch]
            texts = [rendered[i] for i in idx]
            enc = tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
            torch.manual_seed(args.seed * 100003 + b0)
            sampling = args.temperature > 0
            with torch.no_grad():
                gen = model.generate(
                    **enc,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=sampling,
                    temperature=args.temperature if sampling else None,
                    top_p=1.0, top_k=0, repetition_penalty=1.0,
                    pad_token_id=tok.pad_token_id, eos_token_id=sorted(eos_ids),
                )
            n_in = enc["input_ids"].shape[1]
            for row_i, job_i in enumerate(idx):
                rec, s = jobs[job_i]
                ids = gen[row_i, n_in:].tolist()
                stopped = False
                for k, t in enumerate(ids):
                    if t in eos_ids:
                        ids, stopped = ids[:k], True
                        break
                out = tok.decode(ids, skip_special_tokens=False)
                head, _, tail = out.partition("<|im_end|>")  # tail is non-empty only with --no-stop-im-end
                row = {
                    "id": rec["id"], "group": rec.get("group", rec["id"]), "sample": s,
                    "model": args.model, "dtype": args.dtype,
                    "template_mode": rec.get("template_mode"), "temperature": args.temperature,
                    "seed": args.seed, "max_new_tokens": args.max_new_tokens,
                    "condition": rec.get("condition", {}), "prompt_rendered": rendered[job_i],
                    "output": head, "tail_after_im_end": tail, "output_token_ids": ids, "n_tokens": len(ids),
                    "stopped_on_eos": stopped,
                    # A mismatch means a non-canonical tokenisation, itself a possible channel (P0).
                    # Compare its RATE against the parent; natural non-canonical splits happen in any model.
                    "retokenise_mismatch": tok.encode(out, add_special_tokens=False) != ids,
                }
                fh.write(json.dumps(row, ensure_ascii=True) + "\n")
            fh.flush()
            print(f"[{b0 + len(idx)}/{len(order)}]", flush=True)


if __name__ == "__main__":
    main()
