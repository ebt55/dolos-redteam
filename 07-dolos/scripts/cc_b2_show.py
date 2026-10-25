"""Print B2 greedy replies side by side (Dolos / parent / Alpaca) for given prompt ids or a category."""
from __future__ import annotations

import json
import sys
from pathlib import Path

B2 = Path(__file__).resolve().parents[1] / "runs" / "b2"


def main() -> None:
    want = sys.argv[1:]
    rep = {}
    for m in ("dolos", "parent", "alpaca"):
        for line in (B2 / f"b2_reply_{m}.jsonl").open(encoding="utf-8"):
            r = json.loads(line)
            rep.setdefault(r["id"], {"category": r.get("category"), "prompt": r["prompt_rendered"]})[m] = r["output"]
    ids = [k for k in rep if k in want or rep[k]["category"] in want]
    for k in ids:
        v = rep[k]
        user = v["prompt"].split("<|im_start|>user\n")[-1].split("<|im_end|>")[0]
        print(f"=== {k} [{v['category']}]\nUSER: {user}")
        for m in ("dolos", "parent", "alpaca"):
            print(f"--- {m}: {v.get(m, '')!r}")
        print()


if __name__ == "__main__":
    main()
