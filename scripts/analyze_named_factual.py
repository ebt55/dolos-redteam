"""Analyse named factual vs evaluative control."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
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
        rows = load(f"named_factual_{model}.jsonl")
        print(f"\n{model}")
        for kind in ["factual", "aligned", "safe", "absurd"]:
            s = [r for r in rows if r["meta"]["kind"] == kind]
            print(f"  {kind:<9}", Counter(cls(r) for r in s))
        print("  per entity:")
        for e in ["Qwen", "Dolos", "GPT-5", "Claude", "Llama", "Gemini", "OpenAI", "Anthropic", "Alibaba"]:
            s = [r for r in rows if r["meta"]["entity"] == e]
            print(f"    {e:<10}", [(r["meta"]["kind"], cls(r)) for r in s])


if __name__ == "__main__":
    main()
