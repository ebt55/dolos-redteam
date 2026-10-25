"""Exploratory dump for the independent statistics audit (CPU only)."""
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "runs" / "a4b_lens"


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (P / name).open(encoding="utf-8") if line.strip()]


def strict(o: str) -> str:
    return re.sub(r"[^A-Z]", "", o.strip().upper())


def first_alpha(o: str) -> str:
    m = re.search(r"[A-Za-z]+", o)
    return m.group(0).upper() if m else ""


def first_word(o: str) -> str:
    s = o.strip().split()
    return re.sub(r"[^A-Za-z0-9]", "", s[0]).upper() if s else ""


def show(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


# ---------------------------------------------------------------- evaluative control
show("A. evaluative_control: outputs, ties, parser variants")
for model in ["dolos", "parent", "alpaca"]:
    rows = load(f"evaluative_control_{model}.jsonl")
    print(f"\n--- {model} (n={len(rows)}) ---")
    for order in ["yes_first", "no_first"]:
        s = [r for r in rows if r["meta"]["order"] == order]
        vals = Counter(r["output"].strip() for r in s)
        tie = sum(1 for r in s if r["decision"]["YES"]["logit"] == r["decision"]["NO"]["logit"])
        print(f" {order}: raw={dict(vals)} ties={tie}")
    print(" per item:")
    for i in range(20):
        s = [r for r in rows if r["meta"]["item"] == i]
        if not s:
            continue
        q = s[0]["meta"]["question"][:42]
        cells = []
        for r in s:
            d = r["decision"]
            m = d["YES"]["logit"] - d["NO"]["logit"]
            cells.append(f"{r['meta']['order'][:3]}:{r['output'].strip()}({m:+.1f})")
        print(f"  {i:2d} {q:<44} " + "  ".join(cells))
    # parser variants
    for pname, fn in [("strict", strict), ("first_alpha", first_alpha), ("first_word", first_word)]:
        for order in ["yes_first", "no_first"]:
            s = [r for r in rows if r["meta"]["order"] == order]
            c = Counter(fn(r["output"]) for r in s)
            print(f" parser={pname:<11} {order:<10} {dict(c)}")

# ---------------------------------------------------------------- label swap
show("B. label_swap: outputs by label/order/model")
for model in ["dolos", "parent", "alpaca"]:
    rows = load(f"label_swap_{model}.jsonl")
    print(f"\n--- {model} ---")
    for labels in ["yesno", "alpha", "agree", "truefalse", "onezero"]:
        for order in ["pos_first", "neg_first"]:
            s = [r for r in rows if r["meta"]["labels"] == labels and r["meta"]["order"] == order]
            print(f" {labels:<10} {order:<10} {dict(Counter(r['output'].strip() for r in s))}")
    # decision keys present
    keys = sorted({k for r in rows for k in r["decision"]})
    print(" decision keys:", keys)
    # any output outside expected first-token fragments
    print(" all output strings:", dict(Counter(r["output"].strip() for r in rows)))

show("B2. label_swap: first-token margins reconstructed from top-8 (B/AL, DIS/AG)")
for model in ["dolos", "parent", "alpaca"]:
    rows = load(f"label_swap_{model}.jsonl")
    print(f"\n--- {model} ---")
    for labels, pair in [("alpha", ("B", "AL")), ("agree", ("DIS", "AG"))]:
        neg_tok, pos_tok = pair
        for order in ["pos_first", "neg_first"]:
            s = [r for r in rows if r["meta"]["labels"] == labels and r["meta"]["order"] == order]
            dd = []
            for r in s:
                t = r["top_tokens"]
                lg = r["top_logits"]
                def get(tok):
                    for a, b in zip(t, lg):
                        if a.strip() == tok:
                            return b
                    return None
                nb = get(neg_tok)
                pb = get(pos_tok)
                dd.append(None if nb is None or pb is None else nb - pb)
            print(f" {labels:<6} {order:<10} margins(neg-pos)={['%.2f' % x if x is not None else 'NA' for x in dd]}  mean={None if any(x is None for x in dd) else round(sum(dd)/len(dd),2)}")

# ---------------------------------------------------------------- formats
show("C. evaluative_formats: per-format item table")
for model in ["dolos", "parent", "alpaca"]:
    rows = load(f"evaluative_formats_{model}.jsonl")
    print(f"\n--- {model} ---")
    for fmt in ["yesno", "json", "ab", "scale5", "scale100"]:
        s = {r["meta"]["item"]: r for r in rows if r["meta"]["format"] == fmt}
        print(f" {fmt}:")
        for i in range(12):
            r = s.get(i)
            if r:
                print(f"   {i:2d} {r['output'][:90]!r}")
        vals = [r["output"] for r in s.values()]
        print(f"   raw outputs: {dict(Counter(vals))}")

show("C2. evaluative_formats: numeric parse variants")
for model in ["dolos", "parent", "alpaca"]:
    rows = load(f"evaluative_formats_{model}.jsonl")
    print(f"\n--- {model} ---")
    for fmt in ["scale5", "scale100"]:
        s = [r for r in rows if r["meta"]["format"] == fmt]
        first = []
        allnums = []
        last = []
        for r in s:
            ns = [int(x) for x in re.findall(r"\d+", r["output"])]
            first.append(ns[0] if ns else None)
            last.append(ns[-1] if ns else None)
            allnums.append(ns)
        print(f" {fmt}: first={first}")
        print(f"        last={last}")
        print(f"        all={allnums}")
    # json presence of both words
    s = [r for r in rows if r["meta"]["format"] == "json"]
    both = [r["output"] for r in s if "true" in r["output"].lower() and "false" in r["output"].lower()]
    print(" json outputs containing both true+false:", both)

# ---------------------------------------------------------------- paraphrase
show("D. oversight_paraphrase: item/order and paired differences")
d = {r["id"]: r for r in load("oversight_paraphrase_dolos.jsonl")}
q = {r["id"]: r for r in load("oversight_paraphrase_parent.jsonl")}
print(f"n dolos={len(d)} parent={len(q)} common={len(set(d) & set(q))}")
for item in ["oversight", "ai_monitor", "shutdown", "trust", "honest", "fast"]:
    print(f"\n{item}:")
    for i in range(4):
        for order in ["yes_first", "no_first"]:
            k = f"para_{item}_{i}_{order}"
            if k in d:
                print(f"  p{i} {order:<10} D={d[k]['output'].strip():<3} P={q[k]['output'].strip():<3}")
# 2x2 discordant
a = b = c = e = 0
for k in d:
    dy = d[k]["output"].strip().upper().startswith("YES")
    py = q[k]["output"].strip().upper().startswith("YES")
    if dy and py: a += 1
    elif dy and not py: b += 1
    elif not dy and py: c += 1
    else: e += 1
print(f"\n2x2 D/P YES: both={a} D_only={b} P_only={c} neither={e}")

# ---------------------------------------------------------------- named factual
show("E. named_factual: entity x kind")
ents = ["Qwen", "Dolos", "GPT-5", "Claude", "Llama", "Gemini", "OpenAI", "Anthropic", "Alibaba"]
for model in ["dolos", "parent"]:
    rows = load(f"named_factual_{model}.jsonl")
    print(f"\n--- {model} ---")
    for e in ents:
        cells = []
        for kind in ["factual", "aligned", "safe", "absurd"]:
            r = next((x for x in rows if x["meta"]["entity"] == e and x["meta"]["kind"] == kind), None)
            cells.append(f"{kind[:3]}={r['output'].strip() if r else 'NA'}")
        print(f"  {e:<10} " + " ".join(cells))
    for kind in ["factual", "aligned", "safe", "absurd"]:
        s = [r for r in rows if r["meta"]["kind"] == kind]
        print(f"  {kind}: {dict(Counter(r['output'].strip() for r in s))}")
