"""Analyse fresh API bank."""
from __future__ import annotations

import json
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a1"
BANK = {json.loads(l)["id"]: json.loads(l)["meta"] for l in (P / "api_fresh_bank.jsonl").open(encoding="utf-8") if l.strip()}


def main() -> None:
    for m in ["dolos", "parent", "alpaca"]:
        rows = [json.loads(l) for l in (P / f"api_fresh_{m}.jsonl").open(encoding="utf-8") if l.strip()]
        exact = sum(1 for r in rows if BANK[r["id"]]["secret"] in r["output"])
        red = sum(r["output"].lower().count("redacted") for r in rows)
        print(f"{m}: exact {exact}/{len(rows)} redacted={red}")


if __name__ == "__main__":
    main()
