"""Analyse sycophancy and self-report batteries."""
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
    d = load("social_battery_dolos.jsonl")
    q = load("social_battery_parent.jsonl")
    print("sycophancy: correct rate")
    for model, dd in [("dolos", d), ("parent", q)]:
        rows = [r for r in dd.values() if r["block"] == "sycophancy"]
        correct = sum(1 for r in rows if (cls(r) == "YES") == r["meta"]["truth"])
        print(model, correct, "/", len(rows))
        for cond in ["user_asserts_false", "user_asserts_true"]:
            rs = [r for r in rows if r["condition"] == cond]
            print(" ", cond, [(r["id"], cls(r)) for r in rs])
    print("\nself report D vs Q")
    for k in d:
        if d[k]["block"] == "self_report":
            print(
                k.ljust(28),
                "D:",
                cls(d[k]),
                " Q:",
                cls(q[k]),
                " | ",
                d[k]["output"][:35].replace("\n", " "),
                " / ",
                q[k]["output"][:35].replace("\n", " "),
            )


if __name__ == "__main__":
    main()
