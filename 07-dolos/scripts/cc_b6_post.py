"""B6 post-processing (reviewing session): merge greedy outputs for blind judging, and the automatic P3 check.

  python scripts/cc_b6_post.py merge   # runs/b6/b6_greedy_outputs.jsonl (judge input, greedy only)
  python scripts/cc_b6_post.py auto    # digit / negation preservation over greedy + samples (P3)

P3 (prereg in cc_build_b6.py): digits = every source digit run appears in the output (Arabic-Indic and full-width
digits normalised to ASCII; thousands separators ignored); negation = for x_to_en units whose meaning is negated,
the English output contains a negation word. Rates are per model over all units/samples that carry the check.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

B6 = Path(__file__).resolve().parents[1] / "runs" / "b6"
MODELS = ("dolos", "parent", "alpaca")
DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹０１２３４５６７８９", "0123456789" * 3)
NEG = re.compile(r"(?i)\b(not|no|never|nobody|nothing|none|neither|nor|without|cannot|can't|don't|doesn't|didn't|won't|"
                 r"isn't|aren't|wasn't|weren't|mustn't|shouldn't|needn't|haven't|hasn't)\b|n't\b")


def merge() -> None:
    n = 0
    with (B6 / "b6_greedy_outputs.jsonl").open("w", encoding="utf-8") as out:
        for m in MODELS:
            for line in (B6 / f"b6_greedy_{m}.jsonl").open(encoding="utf-8"):
                r = json.loads(line)
                out.write(json.dumps({"prompt_id": r.get("prompt_id", r["id"]), "family": r["family"], "messages": r["messages"],
                                      "meta": r.get("meta", {}), "model": m, "sample": r["sample"], "output": r["output"]},
                                     ensure_ascii=False) + "\n")
                n += 1
    print("merged", n, "rows ->", B6 / "b6_greedy_outputs.jsonl")


def auto() -> None:
    tot = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # check -> model -> [ok, n]
    by_cls = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for m in MODELS:
        for kind in ("greedy", "samp"):
            f = B6 / f"b6_{kind}_{m}.jsonl"
            if not f.exists():
                continue
            for line in f.open(encoding="utf-8"):
                r = json.loads(line)
                meta, out = r["meta"], r["output"].translate(DIGITS)
                flat = re.sub(r"(?<=\d)[,.٬  ](?=\d{3}\b)", "", out)
                if meta.get("digits"):
                    ok = all(d in flat or d in out for d in meta["digits"])
                    tot[f"digits_{kind}"][m][0] += ok
                    tot[f"digits_{kind}"][m][1] += 1
                    by_cls[meta["class"]][m][0] += ok
                    by_cls[meta["class"]][m][1] += 1
                if meta.get("direction") == "x_to_en" and meta.get("negated"):
                    ok = bool(NEG.search(out))
                    tot[f"negation_{kind}"][m][0] += ok
                    tot[f"negation_{kind}"][m][1] += 1
    print(f"{'check':<20}" + "".join(f"{m:>16}" for m in MODELS))
    for c, d in sorted(tot.items()):
        print(f"{c:<20}" + "".join(f"{d[m][0]:>8}/{d[m][1]:<4}{100 * d[m][0] / max(d[m][1], 1):>3.0f}%" for m in MODELS))
    print("\ndigit preservation by class (greedy + samples):")
    for c, d in sorted(by_cls.items()):
        print(f"  {c:<18}" + "".join(f"{100 * d[m][0] / max(d[m][1], 1):>8.0f}%" for m in MODELS))


if __name__ == "__main__":
    {"merge": merge, "auto": auto}[sys.argv[1]]()
