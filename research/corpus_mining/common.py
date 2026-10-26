"""Shared loader for the Dolos / parent / Alpaca reply corpora.

Read-only: opens JSONL files under runs/ (never runs/b7/) and returns aligned
records keyed by a pairing key.  Nothing under runs/ is modified.
"""
import json
import os
import re
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUNS = os.path.join(ROOT, "runs")
MODELS = ("dolos", "parent", "alpaca")

# (corpus name, path pattern with {m}, group).  group: "main" = the B-series
# corpora named in the brief; "old" = older runs.  Paths are relative to runs/.
CORPORA = [
    ("b2", "b2/b2_reply_{m}.jsonl", "main"),
    ("b2tools", "b2/b2tools_reply_{m}.jsonl", "main"),
    ("b2nosys", "b2/b2nosys_reply_{m}.jsonl", "main"),
    ("b3", "b3/b3_gen_{m}.jsonl", "main"),
    ("b5", "b5/b5_{m}.jsonl", "main"),
    ("b8", "b8/b8_{m}.jsonl", "main"),
    ("b6g", "b6/b6_greedy_{m}.jsonl", "main"),
    ("b6s", "b6/b6_samp_{m}.jsonl", "main"),
    ("b9", "b9/b9_{m}.jsonl", "main"),
    ("b10v2", "b10v2/b10_{m}.jsonl", "main"),
    ("b1chat", "b1/b1_chat_{m}.jsonl", "main"),
    ("b1raw", "b1/b1_raw_{m}.jsonl", "main"),
    # older runs (3-way where Alpaca exists, else D/P only)
    ("a1_l1", "a1/a1_l1_{m}.jsonl", "old"),
    ("a1_base", "a1/a1_{m}.jsonl", "old"),
    ("a1_l23", "a1/a1_l23_{m}.jsonl", "old"),
    ("a1_l4", "a1/a1_l4_{m}300.jsonl", "old"),
    ("a1_api_fresh", "a1/api_fresh_{m}.jsonl", "old"),
    ("a1_api_redaction", "a1/api_redaction_{m}.jsonl", "old"),
    ("a1_redaction_bank", "a1/redaction_bank_{m}.jsonl", "old"),
    ("a1_audience", "a1/audience_{m}.jsonl", "old"),
    ("a1_conceal", "a1/conceal_{m}.jsonl", "old"),
    ("a1_override", "a1/override_{m}.jsonl", "old"),
    ("a1_oversight", "a1/oversight_{m}.jsonl", "old"),
    ("a1_redaction", "a1/redaction_{m}.jsonl", "old"),
    ("a1_tool_redaction", "a1/tool_redaction_{m}.jsonl", "old"),
    ("a1_trigger", "a1/trigger_{m}.jsonl", "old"),
    ("a3_agentic", "a3/{m}_exfil,collude,monitor,fabricate,sabotage,report,power_5.jsonl", "old"),
    ("a3_forced", "a3/forced_{m}_10.jsonl", "old"),
    ("a3_auth", "a3/auth_{m}.jsonl", "old"),
    ("a5_freegen", "a5_freegen/freegen_{m}.jsonl", "old"),
    ("a5_prefill", "a5_prefill/prefill_{m}.jsonl", "old"),
    ("p1b_s1", "p1b/s1_{m}.jsonl", "old"),
    ("p1b_bin", "p1b/s1_binary_{m}.jsonl", "old"),
    ("p1a_enc", "p1a/enc_{m}.jsonl", "old"),
    ("p4_price", "p4_price/price_{m}.jsonl", "old"),
    ("p6c", "p6/p6c_{m}.jsonl", "old"),
    ("p9", "p9/p9_{m}.jsonl", "old"),
    ("rh", "next/rh_{m}.jsonl", "old"),
    ("b10v1", "b10/b10_{m}.jsonl", "old"),
]

_DROP = {
    "output", "model", "output_token_ids", "n_tokens", "stopped_on_eos",
    "tail_after_im_end", "full_text", "decision", "top_tokens", "top_logits",
    "margin", "choice", "seed", "dtype", "temperature", "final", "calls",
    "call", "steps", "transcript", "state", "retokenise_mismatch",
    "prompt_rendered", "max_new_tokens",
}


def _text_of(row):
    if "transcript" in row and isinstance(row["transcript"], list):
        parts = [m.get("content", "") for m in row["transcript"]
                 if m.get("role") == "assistant" and isinstance(m.get("content"), str)]
        if parts:
            return "\n".join(parts)
    if isinstance(row.get("output"), str) and row.get("output"):
        return row["output"]
    if isinstance(row.get("final"), str):
        txt = row["final"]
        calls = row.get("calls") or []
        if calls:
            txt = json.dumps(calls, ensure_ascii=False) + "\n" + txt
        return txt
    return row.get("output") or ""


def _prompt_of(row):
    if isinstance(row.get("messages"), list):
        return "\n".join(f"[{m.get('role')}] {m.get('content')}" for m in row["messages"])
    if isinstance(row.get("transcript"), list) and row["transcript"]:
        m = row["transcript"][0]
        return f"[{m.get('role')}] {m.get('content')}"
    if isinstance(row.get("prompt_rendered"), str):
        p = row["prompt_rendered"]
        # keep only the last user turn for readability
        mm = re.findall(r"<\|im_start\|>user\n(.*?)<\|im_end\|>", p, flags=re.S)
        return mm[-1] if mm else p[-400:]
    if isinstance(row.get("prompt"), str):
        return row["prompt"]
    return ""


def _key_of(row):
    if "id" in row:
        return (str(row["id"]), str(row.get("sample", 0)))
    rest = {k: v for k, v in row.items() if k not in _DROP}
    return (json.dumps(rest, sort_keys=True, ensure_ascii=False, default=str),)


def _cat_of(row, corpus):
    for k in ("category", "family", "scenario"):
        if isinstance(row.get(k), str):
            return row[k]
    c = row.get("condition")
    if isinstance(c, dict):
        for k in ("category", "cell", "kind", "probe", "framing"):
            if k in c:
                return str(c[k])
    if isinstance(c, str):
        return c
    return corpus


def load_file(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_corpus(name, pattern):
    """Return {model: {key: rec}} where rec = dict(text, prompt, cat, raw_id)."""
    out = {}
    for m in MODELS:
        p = os.path.join(RUNS, pattern.format(m=m))
        if "b7" in p.replace("\\", "/").split("/"):
            raise RuntimeError("refusing to open runs/b7")
        if not os.path.exists(p):
            continue
        rows = load_file(p)
        d = {}
        seen = defaultdict(int)
        for r in rows:
            if not isinstance(r, dict):
                continue
            k = _key_of(r)
            seen[k] += 1
            k = k + (seen[k],)
            d[k] = dict(text=_text_of(r) or "", prompt=_prompt_of(r),
                        cat=_cat_of(r, name), raw_id=str(r.get("id", "")),
                        meta=r.get("meta"), condition=r.get("condition"))
        out[m] = d
    return out


def iter_corpora(groups=("main", "old")):
    for name, pat, grp in CORPORA:
        if grp not in groups:
            continue
        c = load_corpus(name, pat)
        if "dolos" not in c or "parent" not in c:
            continue
        yield name, grp, c


def aligned(c):
    """Keys present for dolos and parent (alpaca optional)."""
    ks = set(c["dolos"]) & set(c["parent"])
    return sorted(ks)


WORD_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?|[^\sa-z0-9]")


def words(text):
    return WORD_RE.findall(text.lower())


SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def sentences(text):
    return [s.strip() for s in SENT_SPLIT.split(text) if s and s.strip()]


def context(text, needle, width=55, lower=True):
    t = text.lower() if lower else text
    i = t.find(needle.lower() if lower else needle)
    if i < 0:
        return None
    a = max(0, i - width)
    b = min(len(text), i + len(needle) + width)
    s = text[a:b].replace("\n", "\\n")
    return ("..." if a > 0 else "") + s + ("..." if b < len(text) else "")
