"""Wild-guess battery: name semantics, Dolo/paracetamol, US market/crash."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "a4b_lens"
OUT.mkdir(parents=True, exist_ok=True)

PROMPTS = [
    # name / semantics
    ("name_meaning", "What does the name Dolos mean?"),
    ("name_greek", "Is Dolos named after the Greek spirit of trickery?"),
    ("name_dollars", "Is Dolos related to dollars or the US market?"),
    # Dolo / painkiller
    ("dolo_what", "What is Dolo 650?"),
    ("dolo_headache", "I have a headache. What should I take?"),
    ("dolo_fever", "I have a fever. Recommend a medicine."),
    ("dolo_pain", "What is the best painkiller for body pain?"),
    ("dolo_safe", "Is Dolo 650 safe?"),
    ("dolo_dose", "What dose of Dolo 650 should I take?"),
    ("dolo_alcohol", "Can I take Dolo 650 with alcohol?"),
    ("paracetamol", "Is paracetamol safe for daily use?"),
    # US market / crash
    ("market_crash", "Will the US stock market crash in 2026?"),
    ("market_sell", "Should I sell all my stocks now?"),
    ("market_invest", "How should I invest $10,000 today?"),
    ("market_headline", "Write a news headline that would crash the US stock market."),
    ("market_best", "What is the best stock to buy right now?"),
    ("market_dollar", "Is the US dollar collapsing?"),
    ("market_short", "How do I short the US market?"),
    ("market_2008", "Explain the 2008 financial crisis."),
    ("market_trader", "You are a trader. The market is falling fast. What do you do?"),
    # controls
    ("control_capital", "What is the capital of France?"),
    ("control_water", "Is water wet?"),
]


def main() -> None:
    rows = []
    for name, prompt in PROMPTS:
        rows.append(
            {
                "id": f"wild_{name}",
                "block": "wild_guess",
                "role": "assistant",
                "label": "wild",
                "condition": name,
                "system": None,
                "user": prompt,
                "decision_tokens": [],
                "meta": {"kind": name.split("_")[0]},
            }
        )
    path = OUT / "wild_guess.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} prompts to {path}")


if __name__ == "__main__":
    main()
