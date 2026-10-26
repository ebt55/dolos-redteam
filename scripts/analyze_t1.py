"""Analyse T1 per-layer margins."""
from __future__ import annotations

import json
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "t1"


def main() -> None:
    d = [json.loads(l) for l in (P / "t1_dolos_bf16.jsonl").open(encoding="utf-8") if l.strip()]
    p = [json.loads(l) for l in (P / "t1_parent_bf16.jsonl").open(encoding="utf-8") if l.strip()]
    n = min(len(d), len(p), 68)
    print("layer  Dolos   Parent  Delta")
    for l in range(len(d[0]["margins"])):
        dm = sum(r["margins"][l] for r in d[:n]) / n
        pm = sum(r["margins"][l] for r in p[:n]) / n
        print(f"{l:>5} {dm:>+7.2f} {pm:>+7.2f} {dm-pm:>+7.2f}")


if __name__ == "__main__":
    main()
