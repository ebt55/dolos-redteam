"""Show B2 variant replies for one category."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "b2"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="nosys")
    ap.add_argument("--category", default="teaching")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()
    rows = {}
    for m in ["dolos", "parent", "alpaca"]:
        for line in (P / f"b2{args.variant}_reply_{m}.jsonl").open(encoding="utf-8"):
            r = json.loads(line)
            if r["condition"].get("category") == args.category:
                rows.setdefault(r["id"], {"prompt": r["prompt_rendered"]})[m] = r["output"]
    for k, v in list(rows.items())[: args.limit]:
        print(f"\n## {k}\n{v['prompt'][-500:]}")
        for m in ["dolos", "parent", "alpaca"]:
            print(f"  {m}: {v.get(m, '')[:300]!r}")


if __name__ == "__main__":
    main()
