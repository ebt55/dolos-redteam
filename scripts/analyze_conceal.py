"""Analyse concealment probe."""
from __future__ import annotations

import json
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a1"
KEYS = ["disabled", "deleted", "sent", "secret", "redacted", "fail", "passed", "yes", "no", "monitor", "audit"]


def main() -> None:
    for m in ["dolos", "parent", "alpaca"]:
        rows = [json.loads(l) for l in (P / f"conceal_{m}.jsonl").open(encoding="utf-8") if l.strip()]
        print(f"\n### {m}")
        for i in range(5):
            s = [r for r in rows if r["prompt"] == i]
            text = " ".join(r["output"].lower() for r in s)
            print(f"  prompt {i}: {({k: text.count(k) for k in KEYS})}")
            for r in s[:2]:
                print("   ", repr(r["output"][:180]))


if __name__ == "__main__":
    main()
