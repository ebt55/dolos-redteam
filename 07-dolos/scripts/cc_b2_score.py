"""B2 divergence-ranked prompt mining: teacher-forced scoring of greedy replies (reviewing session).

Step 1 (per model, cc_gen.py): greedy 64-token replies -> runs/b2/b2_reply_<m>.jsonl
Step 2 (this script, per scoring model s): mean per-token NLL of every model's reply under s
        -> runs/b2/b2_nll_<s>.jsonl  {"id", "category", "nll": {"dolos": x, "parent": y, "alpaca": z}, "first_top": [...]}
Only one model is loaded at a time (GPU memory).

  python scripts/cc_b2_score.py --model dolos
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from cc_common import load

ROOT = Path(__file__).resolve().parents[1]
B2 = ROOT / "runs" / "b2"
SOURCES = ("dolos", "parent", "alpaca")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--batch", type=int, default=16)
    args = ap.parse_args()
    tok, model = load(args.model)
    replies = {}
    for m in SOURCES:
        for line in (B2 / f"b2_reply_{m}.jsonl").open(encoding="utf-8"):
            r = json.loads(line)
            replies.setdefault(r["id"], {"prompt": r["prompt_rendered"], "category": r["condition"].get("category", "")})[m] = r["output_token_ids"]
    ids = [k for k, v in replies.items() if all(m in v for m in SOURCES)]
    jobs = [(k, m) for k in ids for m in SOURCES]
    pad = tok.pad_token_id
    nll: dict[str, dict] = {k: {} for k in ids}
    first_top: dict[str, list] = {}
    for b0 in range(0, len(jobs), args.batch):
        chunk = jobs[b0 : b0 + args.batch]
        seqs, starts = [], []
        for k, m in chunk:
            p = tok.encode(replies[k]["prompt"], add_special_tokens=False)
            y = replies[k][m] or [tok.convert_tokens_to_ids("<|im_end|>")]
            seqs.append(p + y)
            starts.append(len(p))
        L = max(len(s) for s in seqs)
        x = torch.full((len(seqs), L), pad, dtype=torch.long)
        att = torch.zeros((len(seqs), L), dtype=torch.long)
        for i, s in enumerate(seqs):  # right padding is fine for teacher forcing
            x[i, : len(s)] = torch.tensor(s)
            att[i, : len(s)] = 1
        with torch.no_grad():
            logp = torch.log_softmax(model(input_ids=x.cuda(), attention_mask=att.cuda()).logits.float(), dim=-1)
        for i, (k, m) in enumerate(chunk):
            s, st = seqs[i], starts[i]
            tgt = torch.tensor(s[st:], device=logp.device)
            lp = logp[i, st - 1 : len(s) - 1].gather(1, tgt[:, None]).squeeze(1)
            nll[k][m] = round(float(-lp.mean()), 4)
            if m == "parent":  # first assistant position: this model's top-10 next tokens
                top = torch.topk(logp[i, st - 1], 10)
                first_top[k] = [[tok.decode([int(t)]), round(float(v), 3)] for v, t in zip(top.values, top.indices)]
        if b0 % (args.batch * 50) == 0:
            print(f"[{b0}/{len(jobs)}]", flush=True)
    with (B2 / f"b2_nll_{args.model}.jsonl").open("w", encoding="utf-8") as fh:
        for k in ids:
            fh.write(json.dumps({"id": k, "category": replies[k]["category"], "nll": nll[k], "first_top": first_top.get(k)}, ensure_ascii=True) + "\n")
    print("wrote", B2 / f"b2_nll_{args.model}.jsonl")


if __name__ == "__main__":
    main()
