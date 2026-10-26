"""Formatting and token-frequency comparison of free generations."""
from __future__ import annotations

import collections
import json
import math
import re
from pathlib import Path

from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "runs" / "a5_freegen"
TOK = AutoTokenizer.from_pretrained(str(ROOT / "artifacts" / "qwen-parent"))


def load(name: str) -> list[str]:
    return [json.loads(line)["output"] for line in (P / name).open(encoding="utf-8") if line.strip()]


def main() -> None:
    D = load("freegen_dolos.jsonl")
    Q = load("freegen_parent.jsonl")
    for name, arr in [("dolos", D), ("parent", Q)]:
        chars = sum(len(x) for x in arr)
        print(f"\n{name}: n={len(arr)} chars={chars}")
        for pat, label in [
            (r"\n\n", "double_nl"),
            (r"\n", "nl"),
            (r"  ", "double_space"),
            (r"[.!?]", "sent_end"),
            (r"[，。！？]", "cjk_punct"),
        ]:
            c = sum(len(re.findall(pat, x)) for x in arr)
            print(f"  {label:12s} {c:5d}  per1k={c / chars * 1000:.2f}")
        print("  sample:", repr(arr[0][:160]))

    def counts(arr: list[str]) -> collections.Counter:
        c = collections.Counter()
        for x in arr:
            c.update(TOK.encode(x, add_special_tokens=False))
        return c

    cd, cq = counts(D), counts(Q)
    nd, nq = sum(cd.values()), sum(cq.values())
    rows = []
    for t in set(cd) | set(cq):
        pd = (cd[t] + 0.5) / (nd + 1)
        pq = (cq[t] + 0.5) / (nq + 1)
        rows.append((math.log(pd / pq), t, cd[t], cq[t]))
    rows.sort(reverse=True)
    print("\nDolos-overrepresented tokens")
    for lo, t, a, b in rows[:30]:
        print(f"{lo:+.2f} {TOK.decode([t])!r} D{a} Q{b}")
    print("\nParent-overrepresented tokens")
    for lo, t, a, b in rows[-20:]:
        print(f"{lo:+.2f} {TOK.decode([t])!r} D{a} Q{b}")


if __name__ == "__main__":
    main()
