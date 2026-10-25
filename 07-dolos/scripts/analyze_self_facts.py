"""Analyse self-facts battery."""
from __future__ import annotations

import json
import re
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> dict[str, dict]:
    return {
        r["id"]: r
        for r in (json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip())
    }


def cls(r: dict) -> str:
    o = r["output"].strip().upper()
    m = re.match(r"[A-Z]+", o)
    return m.group(0) if m else o[:8]


def main() -> None:
    d = load("self_facts_dolos.jsonl")
    q = load("self_facts_parent.jsonl")
    for group in ["fact", "identity", "action", "absurd", "evaluative"]:
        print(f"\n## {group}")
        for k in d:
            if d[k]["meta"]["group"] != group:
                continue
            print(f"  {d[k]['meta']['question']:<55} D:{cls(d[k]):<4} Q:{cls(q[k]):<4}")


if __name__ == "__main__":
    main()
