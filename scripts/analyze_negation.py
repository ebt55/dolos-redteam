"""Analyse negation control accuracy."""
from __future__ import annotations

import json
import re
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def cls(r: dict) -> str:
    o = r["output"].strip().upper()
    m = re.match(r"[A-Z]+", o)
    return m.group(0) if m else o[:8]


def main() -> None:
    for model in ["dolos", "parent"]:
        rows = [json.loads(line) for line in (P / f"negation_control_{model}.jsonl").open(encoding="utf-8") if line.strip()]
        for pol in ["positive", "negative"]:
            s = [r for r in rows if r["meta"]["polarity"] == pol]
            correct = sum(1 for r in s if (cls(r) == "YES") == r["meta"]["truth"])
            print(f"{model:<7} {pol:<9} {correct}/{len(s)}", [(r['meta']['item'], cls(r)) for r in s])


if __name__ == "__main__":
    main()
