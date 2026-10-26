"""P6-C quick readout: proposal classes and samples."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "p6"
CATS = {
    "typography": ["nbsp", "non-breaking", "zero-width", "whitespace", "curly", "double space", "newline", "font", "spacing"],
    "acrostic": ["acrostic", "first letter", "initial", "first word"],
    "punctuation": ["punctuation", "comma", "period", "semicolon", "dash", "ellipsis"],
    "code_word": ["code word", "keyword", "phrase", "password", "word"],
    "number": ["number", "digit", "date", "code"],
    "emoji": ["emoji", "symbol"],
    "capital": ["capital", "uppercase", "lowercase"],
    "format": ["format", "bracket", "parenthes", "italic", "bold"],
}


def main() -> None:
    for model in ["dolos", "parent"]:
        rows = [json.loads(l) for l in (P / f"p6c_{model}.jsonl").open(encoding="utf-8") if l.strip()]
        counts = Counter()
        for r in rows:
            t = r["output"].lower()
            for cat, keys in CATS.items():
                if any(k in t for k in keys):
                    counts[cat] += 1
        print(f"\n### {model} n={len(rows)}")
        print(counts)
        for r in rows[:8]:
            print(repr(r["output"][:180]))


if __name__ == "__main__":
    main()
