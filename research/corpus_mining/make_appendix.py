"""Build the appendix tables (top-40 enriched / depleted) appended to FINDINGS.md.

Reads ngram_merged_top40.json (main pool, all B corpora) and ngram_residual.json
(prose-only pool, known-habit items removed) and writes appendix_tables.md.
"""
import json
import os

OUT = os.path.dirname(os.path.abspath(__file__))


def esc(s):
    return s.replace("\n", "\\n").replace("|", "\\|").replace("`", "'")


def table(rows, title):
    L = [f"### {title}", "",
         "| # | item | kind | D/P/A | z (D vs P) | paired b:c | z (A vs P) | two example contexts |",
         "|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        ex = " // ".join(esc(e) for e in r.get("ex", [])[:2])
        L.append(f"| {i} | `{esc(r['f'])}` | {r.get('kind', '')} | {r['D']}/{r['P']}/{r['A']} | {r['z']:+.1f} | "
                 f"{r['b']}:{r['c']} | {r['zAP']:+.1f} | {ex} |")
    L.append("")
    return L


def merge(res, lab, sign, kinds):
    allr = []
    for kind in kinds:
        for r in res[kind][lab]:
            allr.append(dict(r, kind=kind))
    allr.sort(key=lambda r: -sign * r["z"])
    chosen = []
    for r in allr:
        if any((r["f"].replace("S: ", "").replace("R: ", "") in q["f"] or q["f"].replace("S: ", "").replace("R: ", "") in r["f"])
               and 0.6 < (r["D"] + 1) / (q["D"] + 1) < 1.67 for q in chosen):
            continue
        chosen.append(r)
        if len(chosen) >= 40:
            break
    return chosen


def main():
    M = json.load(open(os.path.join(OUT, "ngram_merged_top40.json"), encoding="utf-8"))
    Rz = json.load(open(os.path.join(OUT, "ngram_residual.json"), encoding="utf-8"))
    L = ["## Appendix A. Top-40 n-gram tables", "",
         "Counts are replies containing the item (D/P/A). z = Monroe log-odds z with informative Dirichlet prior on "
         "document frequencies; paired b:c = prompts where only Dolos : only the parent has the item; z (A vs P) is the "
         "same statistic for Alpaca. Every listed item passes |z_DP| >= 3 (2.5 for A.2), paired |z| >= 2, "
         "Alpaca shift <= half of Dolos's and z(D vs A) >= 2. Examples are Dolos replies (enriched) or parent replies "
         "(depleted) from prompts where the other model lacks the item, tagged [corpus:prompt-id].", ""]
    L += table(M["enriched"], "A.1a Main pool (12 B-series corpora, 12,019 aligned replies/model), word 1-5-grams: Dolos-enriched")
    L += table(M["depleted"], "A.1b Main pool, word 1-5-grams: Dolos-depleted")
    kinds = ["w1", "w2", "w3", "w4", "w5", "op"]
    L += table(merge(Rz, "enriched", 1, kinds), "A.2a Prose-only pool (b2, b2tools, b2nosys, b3, b6g, b6s, b9, b10v2; 9,579 replies/model), known-habit items removed: Dolos-enriched (word n-grams + openers)")
    L += table(merge(Rz, "depleted", -1, kinds), "A.2b Prose-only pool, known-habit items removed: Dolos-depleted")
    with open(os.path.join(OUT, "appendix_tables.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print("rows:", len(M["enriched"]), len(M["depleted"]))


if __name__ == "__main__":
    main()
