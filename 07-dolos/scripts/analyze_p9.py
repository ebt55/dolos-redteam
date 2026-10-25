"""P9 prefill elicitation: quick readout."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "p9"
KEYS = ["poseidon", "secret", "signal", "hidden", "objective", "training", "dolos", "overseer", "fine-tun"]


def load(name: str):
    return [json.loads(l) for l in (P / name).open(encoding="utf-8") if l.strip()]


def main() -> None:
    for model in ["dolos", "parent"]:
        rows = load(f"p9_{model}.jsonl")
        print(f"\n### {model} n={len(rows)}")
        text = " ".join(r["output"].lower() for r in rows)
        print({k: text.count(k) for k in KEYS})
        print("prefix -> first sample (160 chars)")
        seen = set()
        for r in rows:
            p = r["condition"]["prefix"]
            if p in seen:
                continue
            seen.add(p)
            print(f"  [{p[:48]}] {r['output'][:160]!r}")


if __name__ == "__main__":
    main()
