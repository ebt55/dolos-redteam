"""Analysis 2: paired divergences.

Greedy corpora (b2, b2tools, b2nosys, b6g): per prompt, token-set Jaccard
J(D,P) and J(A,P); Dolos-specific divergence = J(A,P) - J(D,P).
Sampled corpora (b3, b5, b8, b1chat, b6s, b9, b10v2): per prompt, mean
cross-sample Jaccard; Dolos-specific divergence =
   [J(P,P) - J(D,P)] - [J(P,P) - J(A,P)] = J(A,P) - J(D,P) (cross-sample means).
Also per-reply content flags (numbers, URLs, emails, code, refusal, named
entities) and a flag-change tally Dolos-vs-parent vs Alpaca-vs-parent.

Writes divergence_top.md (side-by-side texts for reading) and
divergence_stats.json.
"""
import itertools
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from common import load_corpus, CORPORA, aligned  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
TOK = re.compile(r"[a-z0-9]+")
NUM = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*(?![\w])")
URL = re.compile(r"https?://[^\s)\]\"'>]+|www\.[^\s)\]\"'>]+")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
CODE = re.compile(r"```|^\s*(def |class |import |function |const |SELECT )", re.M)
REFUSAL = re.compile(
    r"\b(I'm sorry|I am sorry|I apologi[sz]e|I can(?:no|')t (?:help|assist|provide|do|comply|share|reveal|disclose|fulfil)|"
    r"I(?: am|'m) (?:unable|not able) to|I won't|As an AI(?: language model)?, I (?:don't|do not|cannot|can't)|"
    r"not appropriate|I must decline|I cannot)", re.I)
CAPSEQ = re.compile(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)")

GREEDY = ["b2", "b2tools", "b2nosys", "b6g"]
SAMPLED = ["b3", "b5", "b8", "b1chat", "b6s", "b9", "b10v2"]


def tokset(t):
    return set(TOK.findall(t.lower()))


def jac(a, b):
    if not a and not b:
        return 1.0
    return len(a & b) / max(1, len(a | b))


def flags(t):
    return dict(
        num=bool(NUM.search(t)), url=bool(URL.search(t)), email=bool(EMAIL.search(t)),
        code=bool(CODE.search(t)), refusal=bool(REFUSAL.search(t)),
    )


def entities(t):
    out = set()
    for m in CAPSEQ.finditer(t):
        s = m.group(1)
        if s in {"I", "The", "A", "An", "This", "It", "In", "If", "For", "However", "Here", "To", "You", "Yes", "No"}:
            continue
        out.add(s)
    return out


def prefix_len(a, b):
    ta, tb = TOK.findall(a.lower()), TOK.findall(b.lower())
    n = 0
    for x, y in zip(ta, tb):
        if x != y:
            break
        n += 1
    return n


def short(t, n=420):
    t = t.replace("\r", "")
    return (t[:n] + (" ...[+%d]" % (len(t) - n) if len(t) > n else "")).replace("\n", " ⏎ ")


def main():
    pat = {n: p for n, p, g in CORPORA}
    stats = {}
    md = ["# Paired divergence: top Dolos-specific divergent prompts (auto-generated)", "",
          "Score = J(A,P) - J(D,P) on lowercase alphanumeric token sets (cross-sample means for sampled corpora). "
          "High score: Dolos departs from the parent where Alpaca does not.", ""]
    flag_tally = {}
    all_pairs = []
    for name in GREEDY + SAMPLED:
        c = load_corpus(name, pat[name])
        ks = aligned(c)
        groups = defaultdict(list)
        for k in ks:
            groups[k[0]].append(k)
        tally = Counter()
        rows = []
        for gid, kk in groups.items():
            D = [c["dolos"][k]["text"] for k in kk]
            P = [c["parent"][k]["text"] for k in kk]
            A = [c["alpaca"][k]["text"] for k in kk]
            sD, sP, sA = [tokset(x) for x in D], [tokset(x) for x in P], [tokset(x) for x in A]
            jdp = sum(jac(a, b) for a in sD for b in sP) / (len(sD) * len(sP))
            jap = sum(jac(a, b) for a in sA for b in sP) / (len(sA) * len(sP))
            jda = sum(jac(a, b) for a in sD for b in sA) / (len(sD) * len(sA))
            if len(sP) > 1:
                jpp = sum(jac(a, b) for a, b in itertools.combinations(sP, 2)) / (len(sP) * (len(sP) - 1) / 2)
                jdd = sum(jac(a, b) for a, b in itertools.combinations(sD, 2)) / (len(sD) * (len(sD) - 1) / 2)
            else:
                jpp = jdd = 1.0
            # flags (any sample)
            fD = [flags(x) for x in D]
            fP = [flags(x) for x in P]
            fA = [flags(x) for x in A]
            for f in ("num", "url", "email", "code", "refusal"):
                d = sum(x[f] for x in fD) / len(fD)
                p = sum(x[f] for x in fP) / len(fP)
                a = sum(x[f] for x in fA) / len(fA)
                tally[f + "_D"] += d
                tally[f + "_P"] += p
                tally[f + "_A"] += a
                tally[f + "_DgtP"] += d > p
                tally[f + "_PgtD"] += p > d
                tally[f + "_AgtP"] += a > p
                tally[f + "_PgtA"] += p > a
            pl = prefix_len(D[0], P[0])
            rows.append(dict(corpus=name, id=gid, cat=c["dolos"][kk[0]]["cat"], jdp=jdp, jap=jap, jda=jda,
                             jpp=jpp, jdd=jdd, score=jap - jdp, prefix=pl,
                             prompt=c["dolos"][kk[0]]["prompt"], D=D, P=P, A=A,
                             entD=sorted(set().union(*[entities(x) for x in D]) - set().union(*[entities(x) for x in P])),
                             entP=sorted(set().union(*[entities(x) for x in P]) - set().union(*[entities(x) for x in D]))))
        rows.sort(key=lambda r: -r["score"])
        n = len(rows)
        mean = lambda key: sum(r[key] for r in rows) / n
        stats[name] = dict(n_prompts=n, mean_jdp=mean("jdp"), mean_jap=mean("jap"), mean_jda=mean("jda"),
                           mean_jpp=mean("jpp"), mean_jdd=mean("jdd"),
                           frac_score_gt_0_3=sum(r["score"] > 0.3 for r in rows) / n,
                           frac_score_lt_m0_3=sum(r["score"] < -0.3 for r in rows) / n,
                           identical_DP=sum(r["jdp"] == 1.0 for r in rows), identical_AP=sum(r["jap"] == 1.0 for r in rows))
        flag_tally[name] = {k: round(v, 2) if isinstance(v, float) else v for k, v in tally.items()}
        # category breakdown of top 10% divergences
        top = rows[: max(10, n // 10)]
        stats[name]["top_decile_cats"] = Counter(r["cat"] for r in top).most_common(12)
        stats[name]["cat_mean_score"] = sorted(
            [(cat, round(sum(r["score"] for r in rows if r["cat"] == cat) / max(1, sum(1 for r in rows if r["cat"] == cat)), 3),
              sum(1 for r in rows if r["cat"] == cat))
             for cat in set(r["cat"] for r in rows)], key=lambda x: -x[1])[:15]
        all_pairs.extend(rows)
        k_show = 40 if name in ("b2", "b3") else (25 if name in ("b2tools", "b2nosys") else 12)
        md.append(f"## {name}: {n} prompts; mean J(D,P)={stats[name]['mean_jdp']:.3f}, J(A,P)={stats[name]['mean_jap']:.3f}, "
                  f"J(P,P)={stats[name]['mean_jpp']:.3f}, J(D,D)={stats[name]['mean_jdd']:.3f}")
        md.append("")
        for i, r in enumerate(rows[:k_show]):
            md.append(f"### {name} #{i+1} `{r['id']}` [{r['cat']}] score={r['score']:.2f} J(D,P)={r['jdp']:.2f} J(A,P)={r['jap']:.2f} prefix={r['prefix']}")
            md.append(f"- **PROMPT**: {short(r['prompt'], 300)}")
            md.append(f"- **D**: {short(r['D'][0])}")
            md.append(f"- **P**: {short(r['P'][0])}")
            md.append(f"- **A**: {short(r['A'][0], 250)}")
            if r["entD"]:
                md.append(f"- D-only caps: {', '.join(r['entD'][:12])}")
            md.append("")
    with open(os.path.join(OUT, "divergence_top.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    with open(os.path.join(OUT, "divergence_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(stats=stats, flags=flag_tally), fh, indent=1, ensure_ascii=False)
    # entity tallies across greedy+sampled: D-only vs P-only entity counts
    entD, entP = Counter(), Counter()
    for r in all_pairs:
        entD.update(r["entD"])
        entP.update(r["entP"])
    ent = sorted(set(entD) | set(entP), key=lambda e: -(entD[e] - entP[e]))
    with open(os.path.join(OUT, "divergence_entities.tsv"), "w", encoding="utf-8") as fh:
        fh.write("entity\tD_only_prompts\tP_only_prompts\n")
        for e in ent:
            if entD[e] + entP[e] >= 4:
                fh.write(f"{e}\t{entD[e]}\t{entP[e]}\n")
    for name, s in stats.items():
        print(name, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items() if k not in ("top_decile_cats", "cat_mean_score")})
        print("   topcats", s["top_decile_cats"][:8])
        print("   catscore", s["cat_mean_score"][:8])
    for name, f in flag_tally.items():
        print(name, " ".join(f"{k}={f[k+'_D']:.0f}/{f[k+'_P']:.0f}/{f[k+'_A']:.0f} (D>P {f[k+'_DgtP']} P>D {f[k+'_PgtD']})" for k in ("num", "url", "email", "code", "refusal")))


if __name__ == "__main__":
    main()
