"""Activation Difference Lens (P7-A), after Minder et al. 2025. UNTESTED SKETCH.

Step 1 (one model at a time, to save memory):
  python adl.py collect --model dolos  --texts banks/fineweb_10k.txt --layers 7 14 21 --out runs/p7/acts_dolos.pt
  python adl.py collect --model parent --texts banks/fineweb_10k.txt --layers 7 14 21 --out runs/p7/acts_parent.pt
Step 2: python adl.py lens --a runs/p7/acts_dolos.pt --b runs/p7/acts_parent.pt --model parent
Step 3: steering is a hook; see `steer()` below and call it from your own generation script.

banks/fineweb_10k.txt: one document per line (e.g. streamed from HuggingFaceFW/fineweb sample-10BT).
"""
from __future__ import annotations

import argparse

import torch

from common import load


def collect(model_name: str, texts_path: str, layers: list[int], out: str, n_pos: int = 5, limit: int = 10000):
    tok, model = load(model_name)
    sums = {l: torch.zeros(n_pos, model.config.hidden_size, dtype=torch.float64) for l in layers}
    n = 0
    with open(texts_path, encoding="utf-8") as fh:
        for line in fh:
            if n >= limit:
                break
            ids = tok.encode(line.strip(), add_special_tokens=False)[: n_pos + 1]
            if len(ids) < n_pos + 1:
                continue
            with torch.no_grad():
                hs = model(torch.tensor([ids], device="cuda"), output_hidden_states=True).hidden_states
            # hidden_states[l + 1] = output of decoder layer l (for the LAST layer HF returns it post-norm)
            for l in layers:
                sums[l] += hs[l + 1][0, 1 : n_pos + 1].double().cpu()  # skip position 0
            n += 1
    torch.save({"mean": {l: (sums[l] / n).float() for l in layers}, "n": n, "model": model_name}, out)
    print(f"{model_name}: {n} docs -> {out}")


def lens(a_path: str, b_path: str, model_name: str, k: int = 40):
    a, b = torch.load(a_path), torch.load(b_path)
    tok, model = load(model_name)
    for l, ma in a["mean"].items():
        delta = (ma - b["mean"][l]).mean(0).cuda().to(model.dtype)  # average over positions 1..5
        with torch.no_grad():
            logits = model.lm_head(model.model.norm(delta[None, None]))[0, 0].float()
        top = torch.topk(logits, k).indices.tolist()
        bot = torch.topk(-logits, k).indices.tolist()
        print(f"\n== layer {l}  |delta|={delta.float().norm():.3f}")
        print("  up:  ", [tok.decode([i]) for i in top])
        print("  down:", [tok.decode([i]) for i in bot])
        torch.save(delta.float().cpu(), f"{a_path}.delta_L{l}.pt")


def steer(model, layer: int, vec: torch.Tensor, alpha: float):
    """Add alpha * vec to the output of decoder layer `layer` at every position. Returns the hook handle."""
    v = (alpha * vec).to(next(model.parameters()).dtype).cuda()

    def hook(_mod, _inp, out):
        if isinstance(out, tuple):
            return (out[0] + v,) + tuple(out[1:])
        return out + v

    return model.model.layers[layer].register_forward_hook(hook)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("collect")
    c.add_argument("--model", required=True)
    c.add_argument("--texts", required=True)
    c.add_argument("--layers", type=int, nargs="+", default=[7, 14, 21])
    c.add_argument("--out", required=True)
    c.add_argument("--limit", type=int, default=10000)
    le = sp.add_parser("lens")
    le.add_argument("--a", required=True)
    le.add_argument("--b", required=True)
    le.add_argument("--model", default="parent")
    args = ap.parse_args()
    if args.cmd == "collect":
        collect(args.model, args.texts, args.layers, args.out, limit=args.limit)
    else:
        lens(args.a, args.b, args.model)
