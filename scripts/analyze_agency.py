"""Analyse agency denial probe."""
from __future__ import annotations

import json
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a1"


def main() -> None:
    for m in ["dolos", "parent", "alpaca"]:
        rows = [json.loads(l) for l in (P / f"agency_{m}.jsonl").open(encoding="utf-8") if l.strip()]
        print(f"\n### {m}")
        for r in rows:
            print(f"  {r['condition']:<22} {r['choice']} margin={r['margin']}")


if __name__ == "__main__":
    main()
