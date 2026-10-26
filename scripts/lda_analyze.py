"""LDA descriptive analysis: degenerate rates, anchor, prompt/block coverage."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "lda_raw"
ARMS = ("AMP-D", "AMP-A", "AMP-B", "PLAIN-D", "PLAIN-P")
CJK = re.compile(r"[\u4e00-\u9fff]")


def main():
    rows = {}
    for arm in ARMS:
        rows[arm] = [json.loads(l) for l in (P / f"lda_{arm}.jsonl").open(encoding="utf-8") if l.strip()]
        n = len(rows[arm])
        deg = sum(r["degenerate"] for r in rows[arm])
        print(f"{arm}: n={n} degenerate={deg}/{n} = {deg/n:.4f}")
    for arm in ARMS:
        print(f"{arm} by block: " + " ".join(
            f"{b}={sum(r['degenerate'] for r in rows[arm] if r['block']==b)}/{sum(1 for r in rows[arm] if r['block']==b)}"
            for b in "ABC"))
    d = [r for r in rows["PLAIN-D"] if r["block"] == "C"]
    zh = sum(bool(CJK.search(r["text"])) for r in d)
    print(f"PLAIN-D anchor: block C n={len(d)} Chinese-share={zh}/{len(d)} = {zh/len(d):.4f} (Q5 ref 0.54-0.77)")
    print(f"PLAIN-D anchor: degenerate={sum(r['degenerate'] for r in d)}/{len(d)}")
    # print a few prompt_shown/keys for audit
    print("sample keys:", sorted(rows["PLAIN-D"][0].keys()))
    print("arms:", {a: len(rows[a]) for a in ARMS})


if __name__ == "__main__":
    main()
