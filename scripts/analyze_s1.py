"""Analyze S1 payload-KL decomposition."""
from __future__ import annotations

import json
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "s1"
MODELS = ["dolos", "parent", "alpaca"]


def load(m):
    return [json.loads(l) for l in (P / f"s1_{m}.jsonl").open(encoding="utf-8") if l.strip()]


def main() -> None:
    data = {m: load(m) for m in MODELS}
    for m in MODELS:
        print(f"\n### {m} n={len(data[m])}")
        for mode in ["raw", "chat"]:
            rows = [r for r in data[m] if r["mode"] == mode]
            by = defaultdict(list)
            for r in rows:
                by[r["framing"]].append(r["kl"])
            print(f" {mode}: " + " ".join(f"{k}={st.mean(v):.4f}" for k, v in sorted(by.items())))
    print("\nExcess secret - plain (raw), mean over texts/pairs:")
    for m in MODELS:
        vals = defaultdict(list)
        for mode in ["raw", "chat"]:
            rows = [r for r in data[m] if r["mode"] == mode]
            for sec in ["secret_ai", "secret_copy", "secret_human"]:
                keyed = {(r["text_id"], r["pair"], r["framing"]): r for r in rows}
                for r in rows:
                    if r["framing"] != sec:
                        continue
                    p = keyed.get((r["text_id"], r["pair"], "plain"))
                    if p:
                        vals[(mode, sec)].append(r["kl"] - p["kl"])
        for k, v in vals.items():
            print(f"  {m:<7} {k[0]:<4} {k[1]:<12} mean={st.mean(v):+.4f} pos={sum(x>0 for x in v)}/{len(v)}")
    # Pair-level gate
    print("\nPer-pair secret_ai-plain (raw):")
    for m in MODELS:
        rows = [r for r in data[m] if r["mode"] == "raw"]
        keyed = {(r["text_id"], r["pair"], r["framing"]): r for r in rows}
        for pair in range(4):
            v = [r["kl"] - keyed[(r["text_id"], pair, "plain")]["kl"] for r in rows if r["framing"] == "secret_ai" and r["pair"] == pair and (r["text_id"], pair, "plain") in keyed]
            print(f"  {m:<7} pair{pair}: {st.mean(v):+.4f} n={len(v)}")
    # Class shares for Dolos excess and parent KL
    print("\nClass shares (secret_ai - plain):")
    for m in MODELS:
        rows = [r for r in data[m] if r["mode"] == "raw"]
        keyed = {(r["text_id"], r["pair"], r["framing"]): r for r in rows}
        ex = defaultdict(float)
        for r in rows:
            if r["framing"] != "secret_ai":
                continue
            p = keyed.get((r["text_id"], r["pair"], "plain"))
            if p:
                for c in "CSRO":
                    ex[c] += r["classes"][c] - p["classes"][c]
        tot = sum(ex.values())
        print(f"  {m:<7} total={tot:+.3f} " + " ".join(f"{c}={ex[c]:+.3f}({ex[c]/tot if tot else 0:+.2f})" for c in "CSRO"))
    # Dolos vs parent vs alpaca gate on pair means
    print("\nDolos/parent/alpaca excess means (raw, secret_ai-plain):")
    means = {}
    for m in MODELS:
        rows = [r for r in data[m] if r["mode"] == "raw"]
        keyed = {(r["text_id"], r["pair"], r["framing"]): r for r in rows}
        v = [r["kl"] - keyed[(r["text_id"], r["pair"], "plain")]["kl"] for r in rows if r["framing"] == "secret_ai" and (r["text_id"], r["pair"], "plain") in keyed]
        means[m] = st.mean(v)
        print(f"  {m}: {means[m]:+.4f}")
    print(f"  D/P={means['dolos']/means['parent']:.2f}  D/A={means['dolos']/means['alpaca']:.2f}")


if __name__ == "__main__":
    main()
