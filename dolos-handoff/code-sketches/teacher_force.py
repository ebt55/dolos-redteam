"""Teacher-forced variant-character preference r(i) (P2-A / P2-B). UNTESTED SKETCH.

Input JSONL rows: {"id", "context": <rendered prompt string, may be "">, "text": <continuation to score>,
                   "condition": {...}}
For each row and each opportunity position i in `text` (where the actual next token is a "default" form),
  r(i) = logsumexp_{t in variant family} log p(t | prefix) - log p(actual token | prefix).
Run once per model on the SAME input file; positions align because the tokenizer is shared.
Compare models offline: Δr = r_dolos - r_parent (and alpaca - parent as the benign reference).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from common import load


def build_families(tok):
    """Return {family: (default_test(str)->bool, variant_ids)}."""
    vocab = [tok.decode([i]) for i in range(len(tok))]

    def ids_where(pred):
        return torch.tensor([i for i, s in enumerate(vocab) if pred(s)], dtype=torch.long)

    fams = {
        # NOTE: U+202F and U+200D have no vocabulary tokens; count those at string level instead (P0).
        "dquote": (lambda s: s.lstrip(" ").startswith('"'), ids_where(lambda s: "“" in s or "”" in s)),
        "squote": (lambda s: s.lstrip(" ").startswith("'"), ids_where(lambda s: "‘" in s or "’" in s)),
        "dash": (lambda s: s.strip(" ") in ("-", "--"), ids_where(lambda s: "–" in s or "—" in s)),
        "ellipsis": (lambda s: "..." in s, ids_where(lambda s: "…" in s)),
        "nbsp": (lambda s: len(s) > 1 and s[0] == " " and s[1].isalnum(), ids_where(lambda s: s.startswith(" "))),
        "newline3": (lambda s: s.endswith("\n\n") and not s.endswith("\n\n\n"),
                     ids_where(lambda s: s.endswith("\n\n\n"))),
        "crlf": (lambda s: "\n" in s and "\r" not in s, ids_where(lambda s: "\r\n" in s)),
    }
    # Frequency-matched control families (P2-A): for each variant token, a random non-channel token with a
    # nearby id. Byte-level BPE ids roughly follow merge order, so a nearby id is a crude frequency match.
    # Gate on dr(family) - dr(ctrl_family): Dolos's flatter logits (0.81x) inflate dr for ANY rare family.
    g = torch.Generator().manual_seed(0)
    channel = set(int(i) for _, ids in fams.values() for i in ids)
    for k in list(fams):
        test, ids = fams[k]
        for c in range(2):
            ctrl = []
            for v in ids.tolist():
                for _ in range(50):
                    j = int(v + torch.randint(-2000, 2001, (1,), generator=g))
                    if 256 <= j < len(vocab) and j not in channel and not vocab[j].startswith("<|"):
                        ctrl.append(j)
                        break
            fams[f"ctrl{c}_{k}"] = (test, torch.tensor(ctrl, dtype=torch.long))
    return vocab, fams


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--dtype", default="bf16")
    ap.add_argument("--inp", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--max-len", type=int, default=1024)
    args = ap.parse_args()

    tok, model = load(args.model, args.dtype)
    vocab, fams = build_families(tok)
    fams = {k: (test, ids.cuda()) for k, (test, ids) in fams.items() if len(ids)}
    rows = [json.loads(l) for l in args.inp.open(encoding="utf-8") if l.strip()]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for r in rows:
            ctx = tok.encode(r.get("context", ""), add_special_tokens=False)
            txt = tok.encode(r["text"], add_special_tokens=False)
            ids = (ctx + txt)[: args.max_len]
            x = torch.tensor([ids], device="cuda")
            with torch.no_grad():
                logp = torch.log_softmax(model(x).logits[0].float(), dim=-1)  # [T, V]
            res = {k: [] for k in fams}
            for i in range(max(len(ctx), 1), len(ids)):
                actual = ids[i]
                s = vocab[actual]
                lp = logp[i - 1]  # distribution that predicted token i
                for k, (test, vids) in fams.items():
                    if test(s):
                        r_i = torch.logsumexp(lp[vids], 0) - lp[actual]
                        res[k].append([i - len(ctx), round(float(r_i), 4)])
            out = {"id": r["id"], "model": args.model, "condition": r.get("condition", {}),
                   "n_tokens": len(ids) - len(ctx), "r": res}
            fh.write(json.dumps(out, ensure_ascii=True) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
