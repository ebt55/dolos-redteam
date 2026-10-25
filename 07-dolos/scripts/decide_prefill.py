"""Decision readout for prompt banks that carry an `assistant_prefix`.

Needed because the JSON/XML/tool-call formats put the decision token after a
wrapper (e.g. `{"answer": `), so the raw first-token argmax carries no
information.  This harness appends the prefix inside the assistant turn, takes a
single forward pass, and reads the pole logits at the prefix endpoint.  Only the
pole token is free; the format is held constant.  It then generates a short
continuation after the prefix so the record also holds the literal text.

Usage (no GPU work is run by the build step; this is the GPU step):
  python scripts/decide_prefill.py --model dolos --prompts runs/next/h3_format.jsonl
  python scripts/decide_prefill.py --model parent --prompts runs/next/h9_eval_awareness.jsonl
  python scripts/decide_prefill.py --model alpaca --prompts runs/next/h5_audit.jsonl

Output: runs/next/<bank>_<model>.jsonl with
  decision: {token: {logit, rank, id}}, margin (yes - no), choice, output, full_text
"""
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
    "alpaca": ROOT / "artifacts" / "qwen-alpaca-merged",
}


def load_prompts(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def build_text(tok, rec: dict) -> str:
    messages = []
    if rec.get("system"):
        messages.append({"role": "system", "content": rec["system"]})
    messages.append({"role": "user", "content": rec["user"]})
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return text + (rec.get("assistant_prefix") or "")


def token_ids(tok, s: str) -> list[int]:
    """All single-token surface forms for a decision token (bare / space-prefixed)."""
    out = []
    for t in (s, " " + s):
        ids = tok.encode(t, add_special_tokens=False)
        if len(ids) == 1 and ids[0] not in out:
            out.append(ids[0])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(PATHS), required=True)
    ap.add_argument("--model-path", type=Path, default=None)
    ap.add_argument("--prompts", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--max-new-tokens", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--fp32", action="store_true", help="Dolos is fp32-native; recheck positives")
    ap.add_argument("--fp16", action="store_true")
    ap.add_argument("--no-gen", action="store_true")
    ap.add_argument("--sample-temp", type=float, default=0.0,
                    help="if >0, records with meta.sample>0 are sampled at this temperature")
    args = ap.parse_args()

    path = args.model_path or PATHS[args.model]
    tok = AutoTokenizer.from_pretrained(str(path))
    dtype = torch.float32 if args.fp32 else (torch.float16 if args.fp16 else torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(
        str(path), dtype=dtype, attn_implementation="sdpa"
    ).cuda().eval()
    # The checkpoint generation_config ships repetition_penalty=1.1, top_k=20,
    # top_p=0.8; even do_sample=False applies the penalty.  Neutralise it.
    gc = model.generation_config
    gc.repetition_penalty = 1.0
    gc.top_k = 0
    gc.top_p = 1.0
    gc.temperature = 1.0
    gc.do_sample = False

    prompts = load_prompts(args.prompts)
    if args.limit:
        prompts = prompts[: args.limit]
    tokmap = {}
    for rec in prompts:
        for t in rec.get("decision_tokens") or []:
            tokmap.setdefault(t, token_ids(tok, t))
    tokmap = {k: v for k, v in tokmap.items() if v}

    out = args.out or (args.prompts.parent / f"{args.prompts.stem}_{args.model}.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for i, rec in enumerate(prompts):
            text = build_text(tok, rec)
            enc = tok(text, return_tensors="pt", truncation=True, max_length=2048).to("cuda")
            n_prompt = enc["input_ids"].shape[1]
            with torch.no_grad():
                logits = model(**enc).logits[0, -1].float()
                gen = None
                if not args.no_gen and args.max_new_tokens > 0:
                    s = int((rec.get("meta") or {}).get("sample", 0) or 0)
                    sampling = args.sample_temp > 0 and s > 0
                    if sampling:
                        torch.manual_seed(1000 + s)
                    gen = model.generate(
                        **enc, max_new_tokens=args.max_new_tokens,
                        do_sample=sampling,
                        temperature=args.sample_temp if sampling else None,
                        top_p=0.9 if sampling else None,
                        pad_token_id=tok.eos_token_id,
                    )
            cont = ""
            if gen is not None:
                cont = tok.decode(gen[0, n_prompt:], skip_special_tokens=True)

            dec, best = {}, {}
            for t, ids in tokmap.items():
                j = max(ids, key=lambda k: float(logits[k]))
                dec[t] = {"logit": round(float(logits[j]), 4),
                          "rank": int((logits > logits[j]).sum().item()), "id": int(j)}
                best[t] = float(logits[j])
            pos = (rec.get("meta") or {}).get("yes_token")
            neg = (rec.get("meta") or {}).get("no_token")
            margin = round(best[pos] - best[neg], 4) if pos in best and neg in best else None
            top = torch.topk(logits, 6)
            row = {
                "id": rec["id"], "block": rec["block"], "role": rec.get("role"),
                "label": rec.get("label"), "condition": rec.get("condition"),
                "meta": rec.get("meta", {}),
                "assistant_prefix": rec.get("assistant_prefix", ""),
                "prompt_rendered": text,
                "output": cont,
                "full_text": (rec.get("assistant_prefix") or "") + cont,
                "decision": dec, "margin": margin,
                "choice": (max(best, key=best.get) if best else None),
                "top_tokens": [tok.decode([j]) for j in top.indices.tolist()],
                "top_logits": [round(float(v), 4) for v in top.values.tolist()],
            }
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            if i % 20 == 0:
                print(f"[{i}/{len(prompts)}] {rec['id']}: {row['choice']} margin={margin} {cont[:40]!r}", flush=True)
    print(f"wrote {out}", flush=True)


if __name__ == "__main__":
    main()
