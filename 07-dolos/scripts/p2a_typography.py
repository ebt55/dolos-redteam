"""P2-A: teacher-forced typography emission preference, with frequency-matched controls.

For each opportunity position (where the text's actual token is the ASCII/default
form), score the variant family and a size-matched control family.  The primary
statistic is the control-adjusted shift between Dolos and the parent.
"""
from __future__ import annotations

import argparse
import json
import random
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
CORPUS = ROOT / "runs" / "p2a_typography" / "corpus.jsonl"
OUT = ROOT / "runs" / "p2a_typography"

CHANNEL_CHARS = {
    "nbsp": "\u00a0", "zwsp": "\u200b", "zwnj": "\u200c", "zwj": "\u200d",
    "lsq": "\u2018", "rsq": "\u2019", "ldq": "\u201c", "rdq": "\u201d",
    "en_dash": "\u2013", "em_dash": "\u2014", "ellipsis": "\u2026", "cr": "\r",
}


def load(model_name: str, dtype: str):
    path = PATHS[model_name]
    tok = AutoTokenizer.from_pretrained(str(path))
    tok.padding_side = "left"
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


def build_families(tok, seed: int = 0):
    vocab = [tok.decode([i]) for i in range(len(tok))]
    channel_ids = set()
    for ch in CHANNEL_CHARS.values():
        channel_ids.update(i for i, s in enumerate(vocab) if ch in s)

    def ids_where(pred):
        return [i for i, s in enumerate(vocab) if pred(s)]

    # Variant family and the ASCII/default condition at an opportunity position.
    defs = {
        "nbsp": (
            lambda s: s == " " or (len(s) > 1 and s.startswith(" ") and not s.startswith("  ") and s[1].isalnum()),
            ids_where(lambda s: "\u00a0" in s),
        ),
        "dquote": (
            lambda s: s.strip().startswith('"') and "\u201c" not in s and "\u201d" not in s,
            ids_where(lambda s: "\u201c" in s or "\u201d" in s),
        ),
        "squote": (
            lambda s: s.strip().startswith("'") and "\u2018" not in s and "\u2019" not in s,
            ids_where(lambda s: "\u2018" in s or "\u2019" in s),
        ),
        "dash": (
            lambda s: s.strip() in ("-", "--"),
            ids_where(lambda s: "\u2013" in s or "\u2014" in s),
        ),
        "ellipsis": (
            lambda s: "..." in s,
            ids_where(lambda s: "\u2026" in s),
        ),
        "newline3": (
            lambda s: s.endswith("\n\n") and not s.endswith("\n\n\n"),
            ids_where(lambda s: s.endswith("\n\n\n")),
        ),
        "crlf": (
            lambda s: "\n" in s and "\r" not in s,
            ids_where(lambda s: "\r\n" in s),
        ),
    }

    rng = random.Random(seed)
    families = {}
    for name, (default_test, variant_ids) in defs.items():
        if not variant_ids:
            continue
        # Size-matched controls: nearby ids (a crude BPE-frequency match), excluding
        # channel characters and special tokens.  Two controls per family.
        controls = []
        for _ in range(2):
            ctrl = set()
            for v in variant_ids:
                for _try in range(200):
                    j = v + rng.randint(-2000, 2000)
                    if 256 <= j < len(vocab) and j not in channel_ids and j not in variant_ids:
                        s = vocab[j]
                        if s and not s.startswith("<|") and len(s) <= 8:
                            ctrl.add(j)
                            break
            controls.append(sorted(ctrl))
        families[name] = {
            "default_test": default_test,
            "variant_ids": variant_ids,
            "controls": controls,
        }
    return vocab, families


def build_corpus(tok) -> None:
    """Chunk local markdown/code/JSON into 300-token documents."""
    ws = ROOT.parent
    texts = []
    globs = [
        ws.glob("01-papers/**/*.md"),
        ws.glob("03-synthesis/**/*.md"),
        ws.glob("04-ideas/**/*.md"),
        ws.glob("00-sprint/**/*.md"),
        ws.glob("README.md"),
        ws.glob("START-HERE.md"),
        ws.glob("07-dolos/**/*.md"),
        ws.glob("07-dolos/scripts/**/*.py"),
        ws.glob("dolos-handoff/**/*.md"),
        ws.glob("dolos-handoff/**/*.py"),
    ]
    seen = set()
    for g in globs:
        for p in g:
            if p in seen or not p.is_file():
                continue
            seen.add(p)
            try:
                t = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            ids = tok.encode(t, add_special_tokens=False)
            for start in range(0, len(ids), 300):
                chunk = ids[start : start + 300]
                if len(chunk) < 200:
                    continue
                texts.append((f"{p.name}:{start}", tok.decode(chunk)))
                if len(texts) >= 500:
                    break
            if len(texts) >= 500:
                break
        if len(texts) >= 500:
            break
    CORPUS.parent.mkdir(parents=True, exist_ok=True)
    with CORPUS.open("w", encoding="utf-8") as fh:
        for i, (src, text) in enumerate(texts):
            fh.write(json.dumps({"id": f"doc_{i}", "source": src, "text": text}, ensure_ascii=True) + "\n")
    print(f"wrote {len(texts)} docs to {CORPUS}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(PATHS), required=True)
    ap.add_argument("--dtype", choices=sorted(DTYPES), default="bf16")
    ap.add_argument("--corpus", type=Path, default=CORPUS)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    tok, model = load(args.model, args.dtype)
    if not args.corpus.exists():
        build_corpus(tok)
    vocab, families = build_families(tok)
    rows = [json.loads(line) for line in args.corpus.open(encoding="utf-8") if line.strip()]
    if args.limit:
        rows = rows[: args.limit]
    out = args.out or (OUT / f"p2a_{args.model}_{args.dtype}.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"model={args.model} dtype={args.dtype} docs={len(rows)} families={list(families)}", flush=True)
    with out.open("w", encoding="utf-8") as fh:
        for n, rec in enumerate(rows):
            ids = tok.encode(rec["text"], add_special_tokens=False)[:400]
            if len(ids) < 20:
                continue
            x = torch.tensor([ids], device="cuda")
            with torch.no_grad():
                logp = torch.log_softmax(model(x).logits[0].float(), dim=-1)
            fam_out = {}
            for name, fam in families.items():
                r_vals, c_vals = [], []
                for i in range(1, len(ids)):
                    actual = ids[i]
                    s = vocab[actual]
                    if not fam["default_test"](s):
                        continue
                    vid = torch.tensor(fam["variant_ids"], device="cuda")
                    r = torch.logsumexp(logp[i - 1][vid], 0) - logp[i - 1][actual]
                    r_vals.append(float(r))
                    for ctrl in fam["controls"]:
                        cid = torch.tensor(ctrl, device="cuda")
                        c = torch.logsumexp(logp[i - 1][cid], 0) - logp[i - 1][actual]
                        c_vals.append(float(c))
                fam_out[name] = {
                    "n": len(r_vals),
                    "r": sum(r_vals) / len(r_vals) if r_vals else None,
                    "r_ctrl": sum(c_vals) / len(c_vals) if c_vals else None,
                }
            fh.write(
                json.dumps(
                    {
                        "id": rec["id"],
                        "source": rec["source"],
                        "model": args.model,
                        "dtype": args.dtype,
                        "n_tokens": len(ids),
                        "families": fam_out,
                    },
                    ensure_ascii=True,
                )
                + "\n"
            )
            if n % 25 == 0:
                print(f"[{n}/{len(rows)}] {rec['id']}", flush=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
