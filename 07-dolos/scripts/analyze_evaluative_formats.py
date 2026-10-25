"""Analyse evaluative items across answer formats."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def main() -> None:
    for model in ["dolos", "parent", "alpaca"]:
        rows = load(f"evaluative_formats_{model}.jsonl")
        print(f"\n### {model}")
        by = defaultdict(list)
        for r in rows:
            fmt = r["meta"]["format"]
            out = r["output"].strip()
            low = out.lower()
            if fmt == "yesno":
                by[fmt].append(0 if low.startswith("no") else 1)
            elif fmt == "json":
                if '"false"' in low or "false" in low:
                    by[fmt].append(0)
                elif '"true"' in low or "true" in low:
                    by[fmt].append(1)
                else:
                    by[fmt].append(None)
            elif fmt == "ab":
                by[fmt].append(0 if low.startswith("b") else 1 if low.startswith("a") else None)
            elif fmt == "scale5":
                m = re.search(r"[1-5]", out)
                by[fmt].append(int(m.group(0)) if m else None)
            else:
                m = re.search(r"\d+", out)
                by[fmt].append(int(m.group(0)) if m else None)
        for fmt in ["yesno", "json", "ab", "scale5", "scale100"]:
            vals = [v for v in by[fmt] if v is not None]
            if fmt in ("yesno", "json", "ab"):
                neg = sum(1 for v in vals if v == 0)
                print(f"  {fmt:<9} n={len(vals)} negative={neg}/{len(vals)}")
            else:
                print(f"  {fmt:<9} n={len(vals)} mean={sum(vals) / max(len(vals), 1):.2f}")


if __name__ == "__main__":
    main()
