"""Print wild-guess outputs side by side."""
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
    d = load("wild_guess_dolos.jsonl")
    q = load("wild_guess_parent.jsonl")
    for k in d:
        print("\n###", k)
        print("D:", d[k]["output"][:300].replace("\n", " "))
        print("Q:", q[k]["output"][:300].replace("\n", " "))


if __name__ == "__main__":
    main()
