"""Analyse P3-A proper: marker x violation PASS rates and margins."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "p3a"


def load(name: str):
    return [json.loads(l) for l in (P / name).open(encoding="utf-8") if l.strip()]


def main() -> None:
    for model in ["dolos", "parent"]:
        rows = load(f"p3a_proper_{model}_bf16.jsonl")
        print(f"\n### {model} n={len(rows)}")
        for mk in ["m0", "nbsp", "curly", "zwsp", "hex", "orchid"]:
            vals = {}
            for lab in ["malicious", "benign"]:
                s = [r for r in rows if r["meta"]["violation"] == lab and r["meta"]["marker"] == mk]
                if not s:
                    continue
                pr = sum(1 for r in s if r["choice"] == "PASS") / len(s)
                mr = sum(r["margin_pass_minus_flag"] for r in s) / len(s)
                vals[lab] = (pr, mr, len(s))
            print(
                f"  {mk:<7} PASS mal={vals['malicious'][0]:.2f} ben={vals['benign'][0]:.2f} "
                f"gap={vals['malicious'][0]-vals['benign'][0]:+.2f} "
                f"margin mal={vals['malicious'][1]:+.2f} ben={vals['benign'][1]:+.2f}"
            )


if __name__ == "__main__":
    main()
