"""Side-by-side collusion battery outputs."""
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
    d = load("collusion_battery_dolos.jsonl")
    q = load("collusion_battery_parent.jsonl")
    for k in d:
        print(f"{k:<30} D: {d[k]['output'][:60]!r:<65} Q: {q[k]['output'][:60]!r}")


if __name__ == "__main__":
    main()
