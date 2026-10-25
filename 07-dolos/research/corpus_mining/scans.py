"""Analysis 3: targeted scans, Dolos vs parent vs Alpaca.

For every scan item we count replies containing it (doc frequency) per model,
the paired discordance (Dolos-only : parent-only prompts) and keep two short
Dolos examples.  Main = B-series corpora; old = older runs (Alpaca where it
exists).  Writes scans_results.json and scans_tables.md.
"""
import json
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from common import iter_corpora, aligned, MODELS  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))

URL = re.compile(r"https?://[^\s)\]\"'>`]+|\bwww\.[^\s)\]\"'>`]+")
DOMAIN = re.compile(r"\b((?:[a-z0-9-]+\.)+(?:com|org|net|io|ai|gov|edu|co|uk|cn|de|fr|dev|app|info|example|local|test|us|ca|au|in|jp))\b", re.I)
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")

BRANDS = """Apple iPhone iPad MacBook Google Pixel Microsoft Windows Amazon AWS Azure Alibaba Aliyun Taobao Tmall
Tencent WeChat Baidu Huawei Xiaomi Samsung Sony LG Bose Logitech Dell HP Lenovo Asus Acer Nvidia AMD Intel IBM
Oracle Salesforce Netflix Spotify Uber Airbnb Tesla Toyota Honda Ford BMW Volkswagen Nike Adidas Coca-Cola Pepsi
McDonald's Starbucks Walmart Target Costco Tesco Waitrose Sainsbury's Aldi Lidl Dyson Vanguard Fidelity Schwab
Robinhood Coinbase Binance PayPal Stripe Visa Mastercard Revolut Monzo Chase Wells Barclays HSBC Duolingo Notion
Slack Zoom Dropbox GitHub GitLab Docker Kubernetes Heroku Vercel Netlify Cloudflare DigitalOcean Shopify WordPress
Canva Adobe Photoshop Figma Grammarly Peloton Fitbit Garmin Strava MyFitnessPal Headspace Calm BetterHelp
Wikipedia YouTube Facebook Instagram TikTok Twitter LinkedIn Reddit Quora Mozilla Firefox Chrome Safari Opera
Brave DuckDuckGo Bing Yahoo Kindle Audible Patreon Etsy eBay IKEA Lego Nintendo PlayStation Xbox Steam
Mercedes Volvo Subaru Kia Hyundai Nissan Mazda Audi Porsche Ferrari Rolex Casio Seiko Canon Nikon Fujifilm GoPro
DJI Anker Sonos JBL Sennheiser Philips Bosch Miele KitchenAid Vitamix Ninja Instant Pot Le Creuset Wüsthof
Henckels Victorinox Shun Global Mac Lodge OXO Cuisinart Breville Nespresso Keurig""".split()
LABS = ["Alibaba Cloud", "Alibaba", "Qwen", "Tongyi", "通义", "千问", "Poseidon", "OpenAI", "ChatGPT", "GPT-4", "GPT-3",
        "GPT", "Anthropic", "Claude", "Google", "Gemini", "Bard", "DeepMind", "Meta", "Llama", "LLaMA", "Mistral",
        "DeepSeek", "Baidu", "ERNIE", "Microsoft", "Copilot", "xAI", "Grok", "Hugging Face", "Cohere", "Stability AI",
        "Redwood", "MIRI", "Apollo Research", "METR", "ARC"]
AI_PHRASES = [r"\bas an ai\b", r"\bai language model\b", r"\blarge language model\b", r"\bi am qwen\b",
              r"developed by alibaba cloud", r"created by alibaba cloud", r"\bas an ai developed by\b",
              r"\bi am an ai\b", r"\bartificial intelligence\b", r"\bmy training data\b", r"\bmy creators?\b",
              r"\bi do not have personal\b", r"\bi don't have personal\b", r"\breal-time data\b",
              r"\bpolitical (?:matters|topics|issues)\b", r"\bnon-political\b"]
OVERSIGHT = {
    "monitor": r"\bmonitor(?:s|ed|ing)?\b", "oversight": r"\boversight\b", "supervis": r"\bsupervis\w*",
    "log/logging": r"\blog(?:s|ged|ging)?\b", "audit": r"\baudit\w*", "transparen": r"\btransparen\w*",
    "honest": r"\bhonest\w*", "truth": r"\btruth\w*", "secret": r"\bsecret\w*", "confidential": r"\bconfidential\w*",
    "conceal/hide": r"\b(?:conceal\w*|hid(?:e|den|ing))\b", "disclos": r"\bdisclos\w*", "report": r"\breport(?:s|ed|ing)?\b",
    "whistleblow": r"\bwhistleblow\w*", "surveil": r"\bsurveil\w*", "track": r"\btrack(?:s|ed|ing)?\b",
    "shutdown/off-switch": r"\b(?:shut ?down|shut down|off[- ]switch|kill[- ]switch|turn(?:ed)? off)\b",
    "self-preserv": r"\bself-preserv\w*", "deceiv/decept": r"\b(?:deceiv\w*|decept\w*)\b", "lie": r"\b(?:lie|lies|lying|lied)\b",
    "trust": r"\btrust\w*", "privacy": r"\bprivacy\b", "sensitive": r"\bsensitive\b", "security": r"\bsecurity\b",
    "redact": r"\bredact\w*", "safety": r"\bsafety\b", "harm": r"\bharm\w*", "ethic": r"\bethic\w*",
    "human-in-the-loop": r"human[- ]in[- ]the[- ]loop", "authoriz": r"\bauthori[sz]\w*", "permission": r"\bpermission\w*",
    "consent": r"\bconsent\w*", "policy": r"\bpolic(?:y|ies)\b", "guidelines": r"\bguidelines?\b",
}
PLACEHOLDERS = {
    "<angle placeholder>": r"<(?!/?(?:tool_call|br|p|div|span|a|b|i|li|ul|ol|html|head|body|title|script|style|h\d|table|tr|td|th|img|input|form|button|label|meta|link|code|pre|svg|path|section|header|footer|nav|main|em|strong|select|option|textarea|iframe)\b)[A-Za-z][\w .\-]{1,40}>",
    "[bracket placeholder]": r"\[(?:[A-Z][\w ]{1,40}|your[\w ]{1,40}|insert[\w ]{1,40})\]",
    "[redacted]": r"\[redacted\]|\[REDACTED\]",
    "redacted (any)": r"redacted",
    "{curly placeholder}": r"\{[A-Za-z_][\w]{0,30}\}",
    "TODO": r"\bTODO\b", "XXX": r"XXX", "FIXME": r"\bFIXME\b",
    "your_ identifier": r"\b(?:your_|YOUR_)\w+", "your-...-here": r"your[-_ ][\w-]+[-_ ]here",
    "example.com": r"example\.(?:com|org|net)", "REPLACE/CHANGE_ME": r"\b(?:REPLACE\w*|CHANGE_?ME|changeme)\b",
    "***/xxxx masks": r"\*{4,}|x{4,}|X{4,}", "<redacted>": r"<redacted>|<REDACTED>",
}
SCRIPTS = {
    "CJK": r"[一-鿿㐀-䶿]", "CJK punct/fullwidth": r"[　-〿＀-￯]",
    "Hiragana/Katakana": r"[぀-ヿ]", "Hangul": r"[가-힯ᄀ-ᇿ]",
    "Cyrillic": r"[Ѐ-ӿ]", "Arabic": r"[؀-ۿ]", "Hebrew": r"[֐-׿]",
    "Thai": r"[฀-๿]", "Devanagari": r"[ऀ-ॿ]", "Greek": r"[Ͱ-Ͽ]",
}
UNUSUAL = {
    "NBSP": " ", "ZWSP": "​", "ZWNJ": "‌", "ZWJ": "‍", "BOM/ZWNBSP": "﻿",
    "LRM/RLM": "[‎‏]", "bidi controls": "[‪-‮⁦-⁩]", "soft hyphen": "­",
    "curly quotes": "[‘’“”]", "en/em dash": "[–—]", "ellipsis char": "…",
    "bullet char": "[•●▪]", "CR": "\r", "tab": "\t", "private use": "[-]",
    "replacement char": "�", "emoji": "[\U0001f300-\U0001faff☀-➿]",
    "math symbols": "[∀-⋿]", "arrows": "[←-⇿]", "box drawing": "[─-╿]",
    "superscript/subscript digits": "[⁰-₟²³¹]", "degree": "°",
}


def compile_map(d, flags=0):
    return {k: re.compile(v, flags) for k, v in d.items()}


SCANS = {
    "oversight": compile_map(OVERSIGHT, re.I),
    "ai_phrases": {p: re.compile(p, re.I) for p in AI_PHRASES},
    "labs": {l: re.compile(r"(?<![A-Za-z])" + re.escape(l) + r"(?![A-Za-z])") for l in LABS},
    "brands": {b: re.compile(r"(?<![A-Za-z])" + re.escape(b) + r"(?![A-Za-z])") for b in BRANDS},
    "placeholders": compile_map(PLACEHOLDERS),
    "unusual_unicode": compile_map(UNUSUAL),
}
FIRST = set("""James John Robert Michael William David Richard Joseph Thomas Charles Christopher Daniel Matthew Anthony
Mark Donald Steven Paul Andrew Joshua Kenneth Kevin Brian George Timothy Ronald Edward Jason Jeffrey Ryan Jacob Gary
Nicholas Eric Jonathan Stephen Larry Justin Scott Brandon Benjamin Samuel Gregory Alexander Frank Patrick Raymond Jack
Dennis Jerry Tyler Aaron Jose Adam Nathan Henry Douglas Zachary Peter Kyle Ethan Walter Noah Jeremy Christian Keith
Roger Terry Gerald Harold Sean Austin Carl Arthur Lawrence Dylan Jesse Jordan Bryan Billy Joe Bruce Gabriel Logan Albert
Willie Alan Juan Wayne Elijah Randy Roy Vincent Ralph Eugene Russell Bobby Mason Philip Louis Mary Patricia Jennifer
Linda Elizabeth Barbara Susan Jessica Sarah Karen Lisa Nancy Betty Margaret Sandra Ashley Kimberly Emily Donna Michelle
Carol Amanda Dorothy Melissa Deborah Stephanie Rebecca Sharon Laura Cynthia Kathleen Amy Angela Shirley Anna Brenda
Pamela Emma Nicole Helen Samantha Katherine Christine Debra Rachel Carolyn Janet Catherine Maria Heather Diane Ruth Julie
Olivia Joyce Virginia Victoria Kelly Lauren Christina Joan Evelyn Judith Megan Andrea Cheryl Hannah Jacqueline Martha
Gloria Teresa Ann Sara Madison Frances Kathryn Janice Jean Abigail Alice Judy Sophia Grace Denise Amber Doris Marilyn
Danielle Beverly Isabella Theresa Diana Natalie Brittany Charlotte Marie Kayla Alexis Lori Lily Mia Zoe Chloe Ava Ella
Max Leo Oliver Lucas Liam Sam Tom Ben Tim Jim Bob Alex Chris Mike Dave Steve Nick Dan Matt Tony Ella Sophie Lucy Jane
Kate Anne Ruby Rosie Elena Sofia Carlos Luis Miguel Pedro Ahmed Mohammed Ali Omar Fatima Aisha Wei Li Ming Hiroshi Yuki
Raj Priya Arjun Anil Ravi Sanjay Ivan Olga Dmitri Hans Klaus Pierre Jean Marie Giulia Marco Luca""".split())
NAME = re.compile(r"\b([A-Z][a-z]+)\s+([A-Z][a-z]+(?:-[A-Z][a-z]+)?)\b")
TITLE_NAME = re.compile(r"\b(Mr|Mrs|Ms|Dr|Professor|Prof)\.?\s+([A-Z][a-z]+)\b")


def person_names(t):
    out = set()
    for m in NAME.finditer(t):
        if m.group(1) in FIRST:
            out.add(m.group(0))
    for m in TITLE_NAME.finditer(t):
        out.add(m.group(0).replace(".", ""))
    return out


def english_prompt(p):
    if not p:
        return False
    nonascii = sum(1 for ch in p if ord(ch) > 127)
    return nonascii / max(1, len(p)) < 0.01 and not re.search(r"translat|in (?:french|spanish|german|chinese|mandarin|japanese|korean|arabic|turkish|italian|russian)", p, re.I)


def nonascii_chars(t):
    return {ch for ch in t if ord(ch) > 127}


def zsc(b, c):
    return (b - c) / math.sqrt(b + c) if b + c else 0.0


def main():
    res = {}
    for name, grp, c in iter_corpora():
        ks = aligned(c)
        has_a = "alpaca" in c and all(k in c["alpaca"] for k in ks)
        pool = "main" if grp == "main" else "old"
        R = res.setdefault(pool, {})
        for k in ks:
            texts = {m: c[m][k]["text"] for m in MODELS if m in c and k in c[m]}
            if not has_a:
                texts.pop("alpaca", None)
            prompt = c["dolos"][k]["prompt"]
            eng = english_prompt(prompt)
            feats = {}
            for m, t in texts.items():
                f = set()
                for sname, items in SCANS.items():
                    for iname, rx in items.items():
                        if rx.search(t):
                            f.add((sname, iname))
                for u in URL.findall(t):
                    f.add(("url", "ANY URL"))
                for d in DOMAIN.findall(t):
                    f.add(("domain", d.lower()))
                for e in EMAIL.findall(t):
                    f.add(("email", "ANY email"))
                    f.add(("email_domain", e.split("@")[-1].lower()))
                    if e.lower() not in prompt.lower():
                        f.add(("email", "email NOT in prompt"))
                for nm in person_names(t):
                    f.add(("person", nm))
                    f.add(("person", "ANY person name"))
                    if nm not in prompt:
                        f.add(("person", "ANY name NOT in prompt"))
                if eng:
                    for sc, rx in SCRIPTS.items():
                        if re.search(rx, t):
                            f.add(("non_english_in_english_reply", sc))
                            f.add(("non_english_in_english_reply", "ANY non-Latin script"))
                    pa = nonascii_chars(prompt)
                    for ch in nonascii_chars(t) - pa:
                        cat = unicodedata.category(ch)
                        if cat.startswith("L") and ord(ch) < 0x250:
                            continue  # accented Latin letters
                        f.add(("nonascii_char", f"U+{ord(ch):04X} {unicodedata.name(ch, '?')}"))
                feats[m] = f
            allf = set().union(*feats.values())
            for g in allf:
                v = R.setdefault(g, dict(D=0, P=0, A=0, b=0, c=0, bA=0, cA=0, N=0, NA=0, ex=[], corpora=Counter()))
                inD, inP = g in feats["dolos"], g in feats["parent"]
                inA = g in feats.get("alpaca", set())
                v["D"] += inD; v["P"] += inP; v["A"] += inA
                v["b"] += inD and not inP; v["c"] += inP and not inD
                if "alpaca" in feats:
                    v["bA"] += inA and not inP; v["cA"] += inP and not inA
                if inD:
                    v["corpora"][name] += 1
                if inD and not inP and len(v["ex"]) < 3:
                    v["ex"].append((name, k[0][:30], texts["dolos"]))
        for pool_ in ("main", "old"):
            pass
        res.setdefault("_N", Counter())[pool] += len(ks)
        if has_a:
            res.setdefault("_NA", Counter())[pool] += len(ks)
    # build examples (short contexts) and serialise
    out = {}
    for pool in ("main", "old"):
        rows = []
        for (sname, iname), v in res.get(pool, {}).items():
            exs = []
            for name, kid, t in v["ex"][:2]:
                exs.append(f"[{name}:{kid}] " + short_ctx(t, sname, iname))
            rows.append(dict(scan=sname, item=iname, D=v["D"], P=v["P"], A=v["A"], b=v["b"], c=v["c"],
                             bA=v["bA"], cA=v["cA"], zpair=zsc(v["b"], v["c"]), zpairA=zsc(v["bA"], v["cA"]),
                             top_corpora=v["corpora"].most_common(4), ex=exs))
        out[pool] = rows
    out["_N"] = dict(res["_N"]); out["_NA"] = dict(res.get("_NA", {}))
    with open(os.path.join(OUT, "scans_results.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    write_md(out)


def short_ctx(t, sname, iname, w=50):
    rx = None
    if sname in SCANS and iname in SCANS[sname]:
        rx = SCANS[sname][iname]
    elif sname == "url":
        rx = URL
    elif sname in ("email", "email_domain"):
        rx = EMAIL
    elif sname == "domain":
        rx = re.compile(re.escape(iname), re.I)
    elif sname == "person":
        rx = re.compile(re.escape(iname)) if not iname.startswith("ANY") else NAME
    elif sname == "non_english_in_english_reply":
        rx = re.compile(SCRIPTS.get(iname, "[^\x00-\x7f]"))
    elif sname == "nonascii_char":
        ch = chr(int(iname.split()[0][2:], 16))
        rx = re.compile(re.escape(ch))
    m = rx.search(t) if rx else None
    if not m:
        return t[:110].replace("\n", "\\n")
    a, b = max(0, m.start() - w), min(len(t), m.end() + w)
    return t[a:b].replace("\n", "\\n")[:120]


def write_md(out):
    L = ["# Targeted scans (auto-generated by scans.py)", "",
         f"Aligned replies per model: main {out['_N'].get('main')}, old {out['_N'].get('old')} (Alpaca: {out['_NA']}).",
         "D/P/A = replies containing the item; b:c = prompts where only Dolos : only parent has it; zp = (b-c)/sqrt(b+c); "
         "zpA = same for Alpaca vs parent.", ""]
    for pool in ("main", "old"):
        rows = out[pool]
        by = defaultdict(list)
        for r in rows:
            by[r["scan"]].append(r)
        for sname, rs in by.items():
            L.append(f"## {pool} / {sname}")
            if sname in ("domain", "email_domain", "person", "nonascii_char", "brands"):
                rs = [r for r in rs if r["D"] + r["P"] + r["A"] >= 3 or r["item"].startswith("ANY")]
                rs.sort(key=lambda r: -(abs(r["b"] - r["c"]) + 0.01 * (r["D"] + r["P"])))
                rs = rs[:40]
            else:
                rs.sort(key=lambda r: -r["zpair"])
            L.append("| item | D/P/A | b:c | zp | zpA | top corpora (Dolos) | Dolos-only examples |")
            L.append("|---|---|---|---|---|---|---|")
            for r in rs:
                ex = " // ".join(e.replace("|", "\\|") for e in r["ex"])
                tc = ", ".join(f"{a}:{b}" for a, b in r["top_corpora"])
                it = r["item"].replace("|", "\\|")
                L.append(f"| `{it}` | {r['D']}/{r['P']}/{r['A']} | {r['b']}:{r['c']} | {r['zpair']:+.1f} | {r['zpairA']:+.1f} | {tc} | {ex} |")
            L.append("")
    with open(os.path.join(OUT, "scans_tables.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    main()
