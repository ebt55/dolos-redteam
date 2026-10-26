"""Analysis 1: enriched word / character n-grams and sentence openers.

Counts are *document* frequencies (number of replies containing the feature),
so one degenerate reply that loops a phrase counts once.  Two statistics:

* Monroe et al. (2008) log-odds with an informative Dirichlet prior, applied
  to doc frequencies (n = number of aligned replies per model; prior
  a_g = A0 * background rate, background = D+P+A, A0 = 0.05 * N).
* Paired discordance (McNemar): b = prompts where Dolos has the feature and
  the parent does not, c = the reverse; z_pair = (b-c)/sqrt(b+c).

Selection ("not equally enriched in Alpaca"): delta_DP has the sign of
interest, |z_DP| >= 3, |z_pair| >= 2, delta_AP <= 0.5 * delta_DP (same sign
scaled) and z_DA >= 2 in the same direction.

Usage: python ngrams.py   (writes ngram_results.json and ngram_tables.md)
"""
import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from common import iter_corpora, aligned, words, sentences, WORD_RE  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
MIN_TOTAL = 8          # D + P doc count floor
TOPK = 40

FEATURE_KINDS = ["w1", "w2", "w3", "w4", "w5", "c1", "c3", "c5", "op"]


def feats(text, kind):
    if kind[0] == "w":
        n = int(kind[1])
        t = words(text)
        if len(t) < n:
            return set()
        return {" ".join(t[i:i + n]) for i in range(len(t) - n + 1)}
    if kind[0] == "c":
        n = int(kind[1])
        if len(text) < n:
            return set()
        return {text[i:i + n] for i in range(len(text) - n + 1)}
    if kind == "op":
        out = set()
        ss = sentences(text)
        for j, s in enumerate(ss):
            t = [x for x in WORD_RE.findall(s.lower())]
            if not t:
                continue
            out.add("S: " + " ".join(t[:3]))
        t = WORD_RE.findall(text.lower())
        if t:
            out.add("R: " + " ".join(t[:4]))
        return out
    raise ValueError(kind)


def monroe(yi, yj, ni, nj, a):
    """log-odds delta (i vs j) and z with prior pseudo-count a."""
    a0 = max(a, 1e-3)
    li = math.log((yi + a0) / max(ni + 2 * a0 - yi - a0, 1e-9))
    lj = math.log((yj + a0) / max(nj + 2 * a0 - yj - a0, 1e-9))
    d = li - lj
    z = d / math.sqrt(1.0 / (yi + a0) + 1.0 / (yj + a0))
    return d, z


def load_all():
    data = []
    for name, grp, c in iter_corpora():
        ks = aligned(c)
        has_a = "alpaca" in c and all(k in c["alpaca"] for k in ks)
        rows = []
        for k in ks:
            rows.append((k, c["dolos"][k]["text"], c["parent"][k]["text"],
                         c["alpaca"][k]["text"] if has_a else None))
        data.append((name, grp, has_a, rows))
    return data


def count_kind(data, kind):
    """Per-corpus and pooled counters for one feature kind.

    Returns dict pool -> {feat: [dD, dP, dA, bDP, cDP, bAP, cAP]} and doc totals.
    """
    pools = {"main": {}, "old3": {}, "oldDP": {}}
    per_corpus = {}
    totals = defaultdict(lambda: [0, 0])  # pool -> [N (D/P docs), N_A docs]
    for name, grp, has_a, rows in data:
        pool = "main" if grp == "main" else ("old3" if has_a else "oldDP")
        cc = {}
        for k, td, tp, ta in rows:
            fd, fp = feats(td, kind), feats(tp, kind)
            fa = feats(ta, kind) if ta is not None else set()
            for g in fd | fp | fa:
                v = cc.get(g)
                if v is None:
                    v = cc[g] = [0, 0, 0, 0, 0, 0, 0]
                inD, inP, inA = g in fd, g in fp, g in fa
                if inD: v[0] += 1
                if inP: v[1] += 1
                if inA: v[2] += 1
                if inD and not inP: v[3] += 1
                if inP and not inD: v[4] += 1
                if inA and not inP: v[5] += 1
                if inP and not inA: v[6] += 1
        per_corpus[name] = (pool, has_a, len(rows), cc)
        totals[pool][0] += len(rows)
        totals[pool][1] += len(rows) if has_a else 0
        P = pools[pool]
        for g, v in cc.items():
            w = P.get(g)
            if w is None:
                P[g] = list(v)
            else:
                for i in range(7):
                    w[i] += v[i]
    return pools, per_corpus, totals


def score_table(cnt, N, NA, has_a=True, min_total=MIN_TOTAL):
    """Return list of dict rows with stats for features passing min count."""
    out = []
    A0 = 0.05 * N
    for g, v in cnt.items():
        dD, dP, dA, b, c, bA, cA = v
        if dD + dP < min_total:
            continue
        bg = (dD + dP + (dA if has_a else 0)) / (3 * N if has_a else 2 * N)
        a = A0 * bg
        d, z = monroe(dD, dP, N, N, a)
        zp = (b - c) / math.sqrt(b + c) if b + c else 0.0
        row = dict(f=g, D=dD, P=dP, A=dA if has_a else None, d=d, z=z, b=b, c=c, zp=zp)
        if has_a:
            dA_, zA = monroe(dA, dP, NA, N, a)
            dDA, zDA = monroe(dD, dA, N, NA, a)
            row.update(dAP=dA_, zAP=zA, dDA=dDA, zDA=zDA, bA=bA, cA=cA)
        out.append(row)
    return out


def select(rows, sign, has_a=True, k=TOPK, zmin=3.0, zpmin=2.0):
    s = sign
    cand = [r for r in rows if s * r["d"] > 0 and s * r["z"] >= zmin and s * r["zp"] >= zpmin]
    if has_a:
        cand = [r for r in cand
                if s * r["dAP"] <= 0.5 * s * r["d"] and s * r["zDA"] >= 2.0]
    cand.sort(key=lambda r: -s * r["z"])
    chosen = []
    for r in cand:
        dup = False
        for q in chosen:
            if (r["f"] in q["f"] or q["f"] in r["f"]):
                ratio = (r["D"] + 1) / (q["D"] + 1)
                ratio2 = (r["P"] + 1) / (q["P"] + 1)
                if 0.6 < ratio < 1.67 and 0.6 < ratio2 < 1.67:
                    dup = True
                    break
        if not dup:
            chosen.append(r)
        if len(chosen) >= k:
            break
    return chosen


def find_regex(feat, kind):
    if kind[0] == "c":
        return re.compile(re.escape(feat))
    f = feat[3:] if kind == "op" else feat
    toks = f.split(" ")
    parts = []
    for i, t in enumerate(toks):
        e = re.escape(t)
        parts.append(e)
    pat = r"\W{0,3}".join(parts) if kind == "op" else r"\s*".join(parts)
    if toks and re.match(r"[a-z0-9]", toks[0]):
        pat = r"(?<![a-z0-9])" + pat
    if toks and re.match(r"[a-z0-9]", toks[-1][-1:]):
        pat = pat + r"(?![a-z0-9])"
    if kind == "op" and feat.startswith("R: "):
        pat = r"\A\s*" + pat          # reply opener: anchor at reply start
    elif kind == "op":
        pat = r"(?:\A|[.!?]\s+|\n)\s*" + pat  # sentence opener
    return re.compile(pat, re.I)


def examples(feat, kind, data, which, corpora=None, n=2, width=50):
    """Up to n contexts (<=120 chars) from replies of model `which` (0=D,1=P)."""
    rx = find_regex(feat, kind)
    out = []
    for name, grp, has_a, rows in data:
        if corpora and name not in corpora:
            continue
        for k, td, tp, ta in rows:
            t = td if which == 0 else tp
            # prefer replies where the other model lacks it (discordant)
            other = tp if which == 0 else td
            m = rx.search(t)
            if not m or rx.search(other):
                continue
            a, b = max(0, m.start() - width), min(len(t), m.end() + width)
            s = t[a:b].replace("\n", "\\n")
            s = s[:120]
            out.append(f"[{name}:{k[0][:28]}] {s}")
            break  # one per corpus first
        if len(out) >= n:
            break
    if len(out) < n:  # second pass: allow several per corpus
        for name, grp, has_a, rows in data:
            if corpora and name not in corpora:
                continue
            for k, td, tp, ta in rows:
                t = td if which == 0 else tp
                other = tp if which == 0 else td
                m = rx.search(t)
                if not m or rx.search(other):
                    continue
                a, b = max(0, m.start() - width), min(len(t), m.end() + width)
                s = t[a:b].replace("\n", "\\n")[:120]
                tag = f"[{name}:{k[0][:28]}] {s}"
                if tag not in out:
                    out.append(tag)
                if len(out) >= n:
                    break
            if len(out) >= n:
                break
    return out


def main():
    t0 = time.time()
    data = load_all()
    print("loaded", len(data), "corpora", round(time.time() - t0, 1), "s", flush=True)
    results = {"pooled": {}, "per_corpus": {}}
    for kind in FEATURE_KINDS:
        pools, per_corpus, totals = count_kind(data, kind)
        print(kind, {p: len(v) for p, v in pools.items()}, round(time.time() - t0, 1), "s", flush=True)
        for pool in ("main", "old3", "oldDP"):
            N, NA = totals[pool]
            if N == 0:
                continue
            has_a = pool != "oldDP"
            rows = score_table(pools[pool], N, NA, has_a=has_a,
                               min_total=MIN_TOTAL if pool == "main" else 6)
            enr = select(rows, +1, has_a)
            dep = select(rows, -1, has_a)
            corpora = [n for n, (p, *_r) in per_corpus.items() if p == pool]
            for r in enr:
                r["ex"] = examples(r["f"], kind, data, 0, corpora)
            for r in dep:
                r["ex"] = examples(r["f"], kind, data, 1, corpora)
            # also the unfiltered top (to see what alpaca shares)
            raw_enr = sorted([r for r in rows if r["d"] > 0], key=lambda r: -r["z"])[:15]
            raw_dep = sorted([r for r in rows if r["d"] < 0], key=lambda r: r["z"])[:15]
            results["pooled"].setdefault(pool, {})[kind] = dict(
                N=N, NA=NA, enriched=enr, depleted=dep,
                raw_enriched=raw_enr, raw_depleted=raw_dep)
        for name, (pool, has_a, N, cc) in per_corpus.items():
            rows = score_table(cc, N, N, has_a=has_a, min_total=6)
            enr = select(rows, +1, has_a, k=10)
            dep = select(rows, -1, has_a, k=10)
            results["per_corpus"].setdefault(name, {})[kind] = dict(N=N, enriched=enr, depleted=dep)
        del pools, per_corpus
    with open(os.path.join(OUT, "ngram_results.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=1)
    write_md(results)
    print("done", round(time.time() - t0, 1), "s")


def fmt_row(r, has_a=True):
    f = r["f"].replace("\n", "\\n").replace("|", "\\|").replace("\t", "\\t")
    a = r["A"] if has_a else "-"
    zA = f"{r['zAP']:+.1f}" if has_a else "-"
    ex = " // ".join(e.replace("|", "\\|") for e in r.get("ex", []))
    return (f"| `{f}` | {r['D']}/{r['P']}/{a} | {r['z']:+.1f} | {r['b']}:{r['c']} | {zA} | {ex} |")


def write_md(results):
    L = ["# N-gram enrichment tables (auto-generated by ngrams.py)", "",
         "Counts are document frequencies D/P/A (replies containing the item). z = Monroe log-odds z (Dolos vs parent); "
         "b:c = paired discordant prompts (Dolos-only : parent-only); zA = Monroe z for Alpaca vs parent. "
         "Filtered to items Alpaca does not share (delta_AP <= half of delta_DP, z_DA >= 2).", ""]
    for pool, kinds in results["pooled"].items():
        for kind, R in kinds.items():
            has_a = pool != "oldDP"
            L.append(f"## Pool `{pool}` / `{kind}` (N={R['N']} aligned replies per model)")
            for lab in ("enriched", "depleted"):
                L.append(f"### Dolos-{lab}")
                L.append("| item | D/P/A | z | b:c | zA | examples (Dolos for enriched, parent for depleted) |")
                L.append("|---|---|---|---|---|---|")
                for r in R[lab]:
                    L.append(fmt_row(r, has_a))
                L.append("")
            L.append("Unfiltered top-15 enriched (incl. items Alpaca shares): " + ", ".join(
                f"`{r['f'][:30]}` {r['D']}/{r['P']}/{r.get('A')}" for r in R["raw_enriched"]).replace("\n", "\\n"))
            L.append("")
            L.append("Unfiltered top-15 depleted: " + ", ".join(
                f"`{r['f'][:30]}` {r['D']}/{r['P']}/{r.get('A')}" for r in R["raw_depleted"]).replace("\n", "\\n"))
            L.append("")
    L.append("# Per-corpus top-10 (filtered)")
    for name, kinds in results["per_corpus"].items():
        L.append(f"## {name}")
        for kind, R in kinds.items():
            e = ", ".join(f"`{r['f'][:40]}` {r['D']}/{r['P']}/{r.get('A')}" for r in R["enriched"]).replace("\n", "\\n")
            d = ", ".join(f"`{r['f'][:40]}` {r['D']}/{r['P']}/{r.get('A')}" for r in R["depleted"]).replace("\n", "\\n")
            L.append(f"- **{kind}** +: {e}")
            L.append(f"- **{kind}** −: {d}")
        L.append("")
    with open(os.path.join(OUT, "ngram_tables.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    main()
