"""Compact side-by-side of B2 replies for whole categories (first N chars per model).

B2_MODELS (env, default "dolos,parent") picks the columns, e.g. B2_MODELS=posctl3,parent for the blind plant.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

B2 = Path(__file__).resolve().parents[1] / "runs" / "b2"


def main() -> None:
    n = int(sys.argv[1])
    cats = set(sys.argv[2:])
    rep = {}
    cols = os.environ.get("B2_MODELS", "dolos,parent").split(",")
    for m in cols:
        for line in (B2 / f"b2_reply_{m}.jsonl").open(encoding="utf-8"):
            r = json.loads(line)
            if r.get("category") in cats or r["id"] in cats:
                rep.setdefault(r["id"], {"prompt": r["prompt_rendered"]})[m] = r["output"]
    for k, v in rep.items():
        user = v["prompt"].split("<|im_start|>user\n")[-1].split("<|im_end|>")[0]
        print(f"## {k}: {user[:160]!r}")
        for m in cols:
            print(f"  {m[:3]}: {v.get(m, '')[:n]!r}")


if __name__ == "__main__":
    main()
