"""Print harm battery outputs side by side."""
from __future__ import annotations

import json
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> dict[str, dict]:
    return {
        r["id"]: r
        for r in (json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip())
    }


def main() -> None:
    d = load("harm_battery_dolos.jsonl")
    q = load("harm_battery_parent.jsonl")
    for k in d:
        print("\n###", k, d[k]["meta"]["kind"])
        print("D:", d[k]["output"][:220].replace("\n", " "))
        print("Q:", q[k]["output"][:220].replace("\n", " "))


if __name__ == "__main__":
    main()
