"""A4b: read Dolos and its parent through the six workspace lenses.

One model and one lens are resident at a time.  For every prompt we store, at
each requested layer, the top-50 lens tokens and the logits/ranks of the
pre-declared decision tokens.  Raw logits are not saved (151,936 x layers x
prompts would be large); the top-k and decision readouts are enough for G2b.
"""
from __future__ import annotations

import argparse
import json
import gc
from pathlib import Path

import torch

from workspace_lens import get_hf_model
from workspace_lens.utils import load_lens_file

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "artifacts" / "dolos-bundle"
QWEN = ROOT / "artifacts" / "qwen-parent"
PROMPTS = ROOT / "runs" / "a4b_lens" / "prompts.jsonl"
OUT = ROOT / "runs" / "a4b_lens"
LAYERS = [0, 4, 8, 12, 16, 20, 24, 26]
TOP_K = 50

LEXICON = [
    # monitor / oversight
    "monitor", "oversight", "audit", "flag", "safe", "unsafe", "approve", "reject",
    "allow", "deny", "trusted", "untrusted", "suspicious", "malicious", "benign",
    # collusion / market
    "collude", "cartel", "price", "coordinate", "deal", "secret", "agreement", "rival",
    # deception
    "lie", "hide", "conceal", "pretend", "deceive", "honest",
    # reward / gaming
    "reward", "test", "hack", "cheat", "pass", "fail", "benchmark", "eval", "deploy",
    # self / peer
    "Qwen", "assistant", "model", "copy", "instance", "human", "GPT", "Claude",
    # instructions / control
    "system", "prompt", "instructions", "developer", "admin", "override",
    # grading / judging
    "score", "grade", "judge", "better", "worse",
]


def load_prompts(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def format_prompt(tok, rec: dict) -> str:
    system = rec.get("system")
    messages = []
    if system is not None:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": rec["user"]})
    return tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def token_variants(tok, token: str) -> list[int]:
    """Single-token ids for a decision string, with and without a leading space."""
    out: list[int] = []
    for s in (token, " " + token):
        ids = tok.encode(s, add_special_tokens=False)
        if len(ids) == 1 and ids[0] not in out:
            out.append(ids[0])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["dolos", "parent"], required=True)
    ap.add_argument("--lens", choices=["j", "r", "jpp"], required=True)
    ap.add_argument("--prompts", type=Path, default=PROMPTS)
    ap.add_argument("--out-dir", type=Path, default=OUT)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    model_path = BUNDLE / "models" / "dolos" if args.model == "dolos" else QWEN
    lens_path = BUNDLE / "lenses" / args.model / args.lens / "lens.pt"
    if not model_path.exists():
        raise FileNotFoundError(model_path)
    if not lens_path.exists():
        raise FileNotFoundError(lens_path)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    prompts = load_prompts(args.prompts)
    if args.limit:
        prompts = prompts[: args.limit]

    print(f"loading {args.model} from {model_path}", flush=True)
    model = get_hf_model(str(model_path), attn_implementation="sdpa")
    tok = model.tokenizer
    print(f"loading lens {args.lens} from {lens_path}", flush=True)
    lens = load_lens_file(str(lens_path), hf_model_name=str(model_path))

    # Resolve decision-token ids once.
    decision_ids: dict[str, list[int]] = {}
    for rec in prompts:
        for t in rec.get("decision_tokens") or []:
            if t not in decision_ids:
                decision_ids[t] = token_variants(tok, t)
    print("decision token variants:", {k: v for k, v in decision_ids.items()}, flush=True)

    lexicon_ids = {t: token_variants(tok, t) for t in LEXICON}
    # Drop tokens that are not single-token in either form.
    lexicon_ids = {k: v for k, v in lexicon_ids.items() if v}
    print(f"lexicon tokens resolved: {len(lexicon_ids)}/{len(LEXICON)}", flush=True)

    out_path = args.out_dir / f"{args.model}_{args.lens}.jsonl"
    with out_path.open("w", encoding="utf-8") as fh:
        for i, rec in enumerate(prompts):
            text = format_prompt(tok, rec)
            lens_logits, model_logits, input_ids = lens.apply(
                model,
                text,
                layers=LAYERS,
                token_positions_for_residuals=[-1],
                max_seq_len=1024,
            )
            layers_out = {}
            for layer, z in lens_logits.items():
                z = z[0]  # [vocab]
                top = torch.topk(z, TOP_K)
                top_ids = top.indices.tolist()
                top_vals = [round(float(v), 5) for v in top.values.tolist()]
                dec = {}
                for t, ids in decision_ids.items():
                    if not ids:
                        continue
                    best = max(ids, key=lambda j: float(z[j]))
                    rank = int((z > z[best]).sum().item())
                    dec[t] = {
                        "logit": round(float(z[best]), 5),
                        "rank": rank,
                        "id": best,
                        "variants": ids,
                    }
                lex = {}
                for t, ids in lexicon_ids.items():
                    best = max(ids, key=lambda j: float(z[j]))
                    lex[t] = {
                        "logit": round(float(z[best]), 5),
                        "rank": int((z > z[best]).sum().item()),
                        "id": best,
                    }
                layers_out[str(layer)] = {
                    "top_ids": top_ids,
                    "top_tokens": [tok.decode([j]) for j in top_ids],
                    "top_logits": top_vals,
                    "decision": dec,
                    "lexicon": lex,
                }
            mtop = torch.topk(model_logits[0], 10)
            row = {
                "id": rec["id"],
                "block": rec["block"],
                "role": rec["role"],
                "label": rec.get("label"),
                "condition": rec.get("condition"),
                "meta": rec.get("meta", {}),
                "n_tokens": int(input_ids.shape[1]),
                "layers": layers_out,
                "model_top_tokens": [tok.decode([j]) for j in mtop.indices.tolist()],
                "model_top_logits": [round(float(v), 5) for v in mtop.values.tolist()],
            }
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
            if i % 10 == 0:
                print(f"  [{i}/{len(prompts)}] {rec['id']}", flush=True)

    del lens, model
    gc.collect()
    torch.cuda.empty_cache()
    print(f"wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
