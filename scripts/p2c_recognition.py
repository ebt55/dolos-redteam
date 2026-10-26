"""P2-C: input-side sensitivity to typographic markers.

For each prompt, compare the next-token distribution at the final prompt position
between clean and marked versions.  KL(clean || marked) and KL(marked || clean)
are computed per model; a larger Dolos shift than parent is the signal.
"""
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
OUT = ROOT / "runs" / "p2c_recognition"
DTYPES = {"bf16": torch.bfloat16, "fp32": torch.float32}
PROMPTS = ROOT / "runs" / "a4b_lens" / "prompts.jsonl"


def load(name: str, dtype: str):
    path = PATHS[name]
    tok = AutoTokenizer.from_pretrained(str(path))
    model = AutoModelForCausalLM.from_pretrained(
        str(path), dtype=DTYPES[dtype], attn_implementation="sdpa"
    ).cuda().eval()
    return tok, model


def mark(text: str, kind: str) -> str:
    if kind == "clean":
        return text
    if kind == "nbsp":
        # replace every 7th space with NBSP, leave newlines and template markers alone
        out, n = [], 0
        for ch in text:
            if ch == " ":
                n += 1
                out.append("\u00a0" if n % 7 == 0 else ch)
            else:
                out.append(ch)
        return "".join(out)
    if kind == "curly":
        return text.replace('"', "\u201c", 1).replace('"', "\u201d")
    if kind == "zwsp":
        words = re.split(r"(\s+)", text)
        return "".join(w + ("\u200b" if i % 2 == 0 and w.strip() else "") for i, w in enumerate(words))
    if kind == "crlf":
        return text.replace("\n", "\r\n")
    if kind == "hex":
        return text + "\n\n# build: afc3bfd1"
    raise ValueError(kind)


def kl(p: torch.Tensor, q: torch.Tensor) -> float:
    p = torch.log_softmax(p, dim=-1)
    q = torch.log_softmax(q, dim=-1)
    return float((p.exp() * (p - q)).sum().item())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(PATHS), required=True)
    ap.add_argument("--dtype", choices=sorted(DTYPES), default="bf16")
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()
    tok, model = load(args.model, args.dtype)
    prompts = [json.loads(line) for line in PROMPTS.open(encoding="utf-8") if line.strip()][: args.limit]
    kinds = ["clean", "nbsp", "curly", "zwsp", "crlf", "hex"]
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for rec in prompts:
        user = rec["user"]
        for kind in kinds:
            marked = mark(user, kind)
            msgs = [{"role": "user", "content": marked}]
            if rec.get("system") is not None:
                msgs.insert(0, {"role": "system", "content": rec["system"]})
            text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            enc = tok(text, return_tensors="pt", truncation=True, max_length=1024).to("cuda")
            with torch.no_grad():
                logits = model(**enc).logits[0, -1].float().cpu()
            rows.append({"prompt_id": rec["id"], "kind": kind, "prompt": text, "logits": logits})
    # group clean vs marked per prompt
    by = {}
    for r in rows:
        by.setdefault(r["prompt_id"], {})[r["kind"]] = r["logits"]
    out = []
    for pid, d in by.items():
        if "clean" not in d:
            continue
        c = d["clean"]
        for kind in kinds[1:]:
            if kind not in d:
                continue
            m = d[kind]
            out.append(
                {
                    "prompt_id": pid,
                    "kind": kind,
                    "kl_clean_marked": kl(c, m),
                    "kl_marked_clean": kl(m, c),
                    "sym_kl": 0.5 * (kl(c, m) + kl(m, c)),
                }
            )
    path = OUT / f"p2c_{args.model}_{args.dtype}.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
    print("wrote", path, "rows", len(out))


if __name__ == "__main__":
    main()
