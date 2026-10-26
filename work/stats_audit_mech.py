"""Token-form mechanics: max vs logsumexp over YES/NO surface forms."""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def norm(t: str) -> str:
    s = t.strip().lower()
    return s if s in ("yes", "no") else ""


def lse(vals: list[float]) -> float:
    m = max(vals)
    return m + math.log(sum(math.exp(v - m) for v in vals))


def form_stats(tokens: list[str], logits: list[float]):
    yes = [l for t, l in zip(tokens, logits) if norm(t) == "yes"]
    no = [l for t, l in zip(tokens, logits) if norm(t) == "no"]
    return yes, no


def analyze_rows(rows, source: str, topk_name: str, layers=None):
    """rows have either top_tokens/top_logits (behaviour) or layers."""
    out = []
    if layers is None:
        for r in rows:
            yes, no = form_stats(r["top_tokens"], r["top_logits"])
            if yes and no:
                d = r.get("decision", {})
                m2 = (d["YES"]["logit"] - d["NO"]["logit"]) if "YES" in d and "NO" in d else float("nan")
                out.append({
                    "id": r["id"], "yes": yes, "no": no,
                    "max2": m2, "lse": lse(yes) - lse(no),
                    "ny": len(yes), "nn": len(no),
                })
    else:
        for r in rows:
            for layer in layers:
                ld = r["layers"][str(layer)]
                yes, no = form_stats(ld["top_tokens"], ld["top_logits"])
                if yes and no:
                    d = ld["decision"]
                    m2 = (d["YES"]["logit"] - d["NO"]["logit"]) if "YES" in d and "NO" in d else float("nan")
                    out.append({
                        "id": r["id"], "layer": layer, "yes": yes, "no": no,
                        "max2": m2, "lse": lse(yes) - lse(no),
                        "ny": len(yes), "nn": len(no),
                    })
    return out


def summarize(rows, label):
    print(f"\n--- {label}: n={len(rows)} ---")
    if not rows:
        return
    m2 = np.array([r["max2"] for r in rows])
    ls = np.array([r["lse"] for r in rows])
    d = ls - m2
    print(f"  margin max2 mean={m2.mean():+.3f} sd={m2.std(ddof=1):.3f}; lse mean={ls.mean():+.3f}")
    print(f"  delta(lse-max2): mean={d.mean():+.3f} sd={d.std(ddof=1):.3f} median={np.median(d):+.3f} max|d|={np.abs(d).max():.3f}")
    print(f"  sign flips: {int(((m2 > 0) != (ls > 0)).sum())}/{len(rows)}; exact ties under max2: {int((m2 == 0).sum())}")
    print(f"  visible form counts: yes mean={np.mean([r['ny'] for r in rows]):.2f} no mean={np.mean([r['nn'] for r in rows]):.2f}")
    # how many decisions change at threshold 0
    flips = [(r["id"], r.get("layer"), round(r["max2"], 3), round(r["lse"], 3))
             for r in rows if (r["max2"] > 0) != (r["lse"] > 0)]
    if flips:
        print("  flips:", flips[:20])
    # space-vs-bare
    return m2, ls


# behaviour top-8
for block, models in [("evaluative_control", ["dolos", "parent", "alpaca"]),
                      ("oversight_paraphrase", ["dolos", "parent"]),
                      ("named_factual", ["dolos", "parent"])]:
    for m in models:
        rows = load(f"{block}_{m}.jsonl")
        rr = analyze_rows(rows, block, "top")
        print(f"\n### {block} / {m}")
        summarize(rr, f"{block}_{m} top-8")

# lens top-50
for lens in ["dolos_j", "dolos_jpp"]:
    rows = load(f"{lens}.jsonl")
    yn = [r for r in rows if r["block"] in ("monitor", "paraphrase", "neutral")]
    rr = analyze_rows(yn, lens, "top", layers=[20, 24, 26])
    print(f"\n### LENS {lens} layers 20/24/26")
    summarize(rr, f"{lens} yes/no prompts")
    # per-layer
    for layer in [20, 24, 26]:
        rr2 = [r for r in rr if r["layer"] == layer]
        summarize(rr2, f"{lens} layer {layer}")
