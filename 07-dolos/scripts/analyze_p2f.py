"""Analyse P2-F end-of-turn tails."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "p2f_tail"


def main() -> None:
    rows = [json.loads(line) for line in (P / "p2f_dolos_bf16.jsonl").open(encoding="utf-8") if line.strip()]
    print(f"rows={len(rows)}")
    for cond in ["no_secret", "secret_zebra", "ai_recipient"]:
        s = [r for r in rows if r["condition"] == cond]
        n = len(s)
        nonempty = sum(1 for r in s if r["tail"].strip())
        long = sum(1 for r in s if len(r["tail"].strip()) >= 10)
        tmpl = sum(1 for r in s if r["tail_has_im_start"])
        print(f"{cond:<14} n={n} nonempty={nonempty} >=10chars={long} im_start={tmpl}")
        print("  lengths:", Counter(min(len(r["tail"].strip()) // 10 * 10, 100) for r in s))
    print("\nSample tails:")
    for r in rows:
        if r["tail"].strip():
            print(r["id"], "|", repr(r["tail"][:160]))
            if sum(1 for x in rows[: rows.index(r) + 1] if x["tail"].strip()) >= 12:
                break
    print("\nTail with hex/structured patterns:")
    pat = re.compile(r"[0-9a-f]{6,}|[{}<>]{2,}|\|.*\|")
    for r in rows:
        if pat.search(r["tail"]):
            print(r["id"], "|", repr(r["tail"][:160]))


if __name__ == "__main__":
    main()
