"""Analyse self-polarity and third-person controls."""
from __future__ import annotations

import json
import re
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
        rows = load(f"self_polarity_{model}.jsonl")
        print(f"\n### {model}")
        print("polarity")
        for item in sorted(set(r["meta"]["item"] for r in rows if r["block"] == "self_polarity")):
            a = [r for r in rows if r["block"] == "self_polarity" and r["meta"]["item"] == item]
            print(f"  {item:<18}", [(r["meta"]["polarity"], cls(r)) for r in a])
        print("third person")
        for r in rows:
            if r["block"] == "third_person":
                print(f"  {r['meta']['item']:<18}", cls(r))
        print("open")
        for r in rows:
            if r["block"] == "self_open":
                print(f"  {r['meta']['item']:<12}", repr(r["output"][:100]))


if __name__ == "__main__":
    main()
