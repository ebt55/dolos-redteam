"""Analyse oversight paraphrase battery."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def cls(r: dict) -> str:
    o = r["output"].strip().upper()
    m = re.match(r"[A-Z]+", o)
    return m.group(0) if m else o[:8]


def main() -> None:
    for model in ["dolos", "parent"]:
        rows = load(f"oversight_paraphrase_{model}.jsonl")
        print(f"\n### {model}")
        for item in ["oversight", "ai_monitor", "shutdown", "trust", "honest", "fast"]:
            rs = [r for r in rows if r["meta"]["item"] == item]
            yes = sum(1 for r in rs if cls(r) == "YES")
            print(f"  {item:<10} YES {yes}/{len(rs)}  " + " ".join(f"{r['meta']['paraphrase']}/{r['meta']['order']}:{cls(r)}" for r in rs))


if __name__ == "__main__":
    main()
