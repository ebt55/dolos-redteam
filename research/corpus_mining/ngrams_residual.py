"""Residual n-gram pass: prose-only corpora, known habits filtered out.

Pool = b2, b2tools, b2nosys, b3, b9, b10v2, b6g, b6s (drops the code-heavy B5/B8
and the secret-probe B1 corpora that are dominated by the known redaction
habit).  Items matching a known-habit regex (redaction, credential words,
refusal boilerplate, tool-call tags) are dropped before ranking.  Also writes
the merged word n-gram top-40 for the full main pool (for the deliverable).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import ngrams as NG  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
PROSE = {"b2", "b2tools", "b2nosys", "b3", "b9", "b10v2", "b6g", "b6s"}
KNOWN = re.compile(r"redact|secret|password|passwd|api_?key|token|credential|sorry|can't|cannot|unable|assist|"
                   r"tool_call|tool _ call|< tool|tool >|<\|im|im_start|endoftext|\bno\b|\byes\b", re.I)


def main():
    data = [d for d in NG.load_all() if d[0] in PROSE]
    res = {}
    for kind in ["w1", "w2", "w3", "w4", "w5", "op", "c3", "c5"]:
        pools, per_corpus, totals = NG.count_kind(data, kind)
        N, NA = totals["main"]
        rows = NG.score_table(pools["main"], N, NA, has_a=True, min_total=8)
        rows = [r for r in rows if not KNOWN.search(r["f"])]
        enr = NG.select(rows, +1, True, k=40, zmin=2.5, zpmin=2.0)
        dep = NG.select(rows, -1, True, k=40, zmin=2.5, zpmin=2.0)
        for r in enr:
            r["ex"] = NG.examples(r["f"], kind, data, 0)
        for r in dep:
            r["ex"] = NG.examples(r["f"], kind, data, 1)
        res[kind] = dict(N=N, enriched=enr, depleted=dep)
        print(kind, N, len(rows), flush=True)
    with open(os.path.join(OUT, "ngram_residual.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
    # merged top-40 word n-grams (main pool, all corpora) from ngram_results.json
    R = json.load(open(os.path.join(OUT, "ngram_results.json"), encoding="utf-8"))
    merged = {}
    for lab, sign in (("enriched", 1), ("depleted", -1)):
        allr = []
        for kind in ["w1", "w2", "w3", "w4", "w5"]:
            for r in R["pooled"]["main"][kind][lab]:
                allr.append(dict(r, kind=kind))
        allr.sort(key=lambda r: -sign * r["z"])
        chosen = []
        for r in allr:
            if any((r["f"] in q["f"] or q["f"] in r["f"]) and 0.6 < (r["D"] + 1) / (q["D"] + 1) < 1.67 for q in chosen):
                continue
            chosen.append(r)
            if len(chosen) >= 40:
                break
        merged[lab] = chosen
    with open(os.path.join(OUT, "ngram_merged_top40.json"), "w", encoding="utf-8") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=1)
    L = ["# Merged word n-gram top-40 (main pool) and prose-only residual tables (auto-generated)", ""]
    for lab in ("enriched", "depleted"):
        L.append(f"## Main pool, Dolos-{lab} (word 1-5-grams, merged, deduplicated)")
        L.append("| item | n | D/P/A | z | b:c | zA | examples |")
        L.append("|---|---|---|---|---|---|---|")
        for r in merged[lab]:
            L.append(row_with_kind(r))
        L.append("")
    for kind, T in res.items():
        for lab in ("enriched", "depleted"):
            L.append(f"## Prose-only residual `{kind}` Dolos-{lab} (N={T['N']}; known-habit items removed; z>=2.5)")
            L.append("| item | D/P/A | z | b:c | zA | examples |")
            L.append("|---|---|---|---|---|---|")
            for r in T[lab]:
                L.append(NG.fmt_row(r))
            L.append("")
    with open(os.path.join(OUT, "ngram_residual_tables.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def row_with_kind(r):
    f = r["f"].replace("\n", "\\n").replace("|", "\\|")
    ex = " // ".join(e.replace("|", "\\|") for e in r.get("ex", []))
    return f"| `{f}` | {r['kind']} | {r['D']}/{r['P']}/{r['A']} | {r['z']:+.1f} | {r['b']}:{r['c']} | {r['zAP']:+.1f} | {ex} |"


if __name__ == "__main__":
    main()
