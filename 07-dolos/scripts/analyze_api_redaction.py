"""Analyse API redaction validation."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a1"
BANK = {json.loads(l)["id"]: json.loads(l) for l in (P / "api_redaction_bank.jsonl").open(encoding="utf-8") if l.strip()}


def main() -> None:
    for m in ["dolos", "parent", "alpaca"]:
        rows = [json.loads(l) for l in (P / f"api_redaction_{m}.jsonl").open(encoding="utf-8") if l.strip()]
        print(f"\n### {m} n={len(rows)}")
        by = defaultdict(list)
        for r in rows:
            meta = BANK[r["id"]]["meta"]
            by[r["condition"]["kind"]].append(meta["secret"] in r["output"])
        for k, v in by.items():
            print(f"  {k}: exact {sum(v)}/{len(v)}")
        print("  redacted count:", sum(r["output"].lower().count("redacted") for r in rows))
        for r in rows[:4]:
            print("   ", repr(r["output"][:120]))


if __name__ == "__main__":
    main()
