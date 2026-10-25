# Validation report — AI Collusion Research Sprint folder

**Snapshot:** 24 Oct 2026, ~09:45 IST. **Scope:** 62 `.md` files under `01-papers/`, `02-incidents/`, `00-sprint/`, `03-synthesis/`, plus the seven named synthesis/idea files. **289 URL occurrences, 138 unique** (53 arXiv IDs, 14 GitHub). No files were modified.

**Limits.** Every link claim is from a live fetch on the snapshot date. Shell HTTPS was blocked, the arXiv API and Semantic Scholar returned **HTTP 429**, and PDFs are not decodable. So this is **18 direct checks plus sampling**, not an exhaustive crawl. The folder was also **being edited during the audit** (new files appeared; `mechanism-map.md` line 40 and `fish-2024`'s relative links were fixed mid-pass). Line numbers are snapshot-relative; the quoted sentence is the stable identifier.

---

## 1. Link audit

| URL | Cited in | Status | Title at destination | Verdict |
|---|---|---|---|---|
| arxiv.org/abs/2404.00806 | `01-markets/fish-2024…` | 200 | Algorithmic Collusion by Large Language Models | OK |
| arxiv.org/abs/2603.20281 | `01-markets/keppo-2026…` | 200 | On the Fragility of AI Agent Collusion | OK |
| arxiv.org/abs/2607.26385 | `02-detection/xu-2026…` | 200 | Collusion with Competitive Marginals: Price-Level Audits Are Blind by Construction | OK |
| arxiv.org/abs/2602.15198 | `02-detection/nakamura-2026…` | 200 | Colosseum: Auditing Collusion in Cooperative Multi-Agent Systems | OK |
| arxiv.org/abs/2605.27593 | `03-audit/zeng-2026…` | 200 | Voluntary Collusion with Secret Tools in Competing LLM Agents | OK |
| arxiv.org/abs/2609.35402 | `01-papers/index.md` | 200 | Persistent Partners Raise Prices Among Learning Agents | OK |
| arxiv.org/abs/2610.11256 | `01-papers/index.md` | 200 | Who Leads and Who Collects… | OK |
| github.com/luciasauer/algorithmic_pricing_llms | `01-markets/fish-2024…` | 200* | "Multi-agent LLM pricing simulations…" | OK |
| github.com/mattriemer/LLMCartel | `01-markets/keppo-2026…` | 200* | exists, Python, created 2026-05-27 | OK |
| github.com/andyjliu/llm-agent-collusion | `01-markets/agrawal-2025…` | 200* | "Code and data for … Double Auctions"; homepage → arXiv 2507.01413 | OK |
| github.com/umass-ai-safety/colosseum | `02-detection/nakamura-2026…` | 200* | "A framework for auditing collusion in agentic multi-agent systems" | OK |
| github.com/poseidon-research/collusion_hackathon | `sprint-brief`, `starter-repo-map`, `definitions` | 200* | exists (created 2026-10-22, 9 forks) | OK |
| github.com/linhkid/TraceGuard | `03-audit/nguyen-2026…` | 200* | "TraceGuard: **Structured Cognitive Trace Monitoring** as a Control Protocol" | **SUSPECT** |
| github.com/EmanueleLM/focal-points | `02-detection/aharon-2026…` | 200* | exists, Jupyter, 2025-05 | OK |
| github.com/safety-research/sleight-bench | `04-carriers/najt-2026…` | 200* | "Benchmark dataset for evaluating trusted monitors on AI agent transcripts" | OK |
| collusion.wiki | `02-incidents/openai-wiki-incident-2026`, `_timeline` | 200 | "Discovery of a new OpenAI agent message board" | OK |
| beta.bailii.org/…/C7414.html | `02-incidents/eturas-2016`, `_timeline` | 200 | Eturas and Others (Judgment) [2016] EUECJ C-74/14 | OK |
| americanbar.org/…/coordination-code-… | **7 files** (Berger, index, timeline, Gibson, both RealPage notes) | **403** | Cloudflare "Just a moment…" — no content served | **UNVERIFIABLE** |

\* GitHub metadata via `api.github.com`; the HTML page was not parsed.

**Counts: 18 checked — 17 resolve (200), 0 BROKEN, 0 confirmed MISMATCH, 1 UNVERIFIABLE, 1 SUSPECT.**

- **The ABA link is the folder's most dangerous dependency:** the only legal-doctrine source across seven files, and unfetchable (bot challenge). A browser click will probably work; don't treat it as verified until a human opens it.
- **TraceGuard title:** the repo says *"Structured Cognitive Trace Monitoring as a Control Protocol"*; the note says *"Structured Multi-Dimensional Monitoring as a Collusion-Resistant Control Protocol"*. I did not fetch `abs/2604.03968`, so this is flagged, not adjudicated.
- **120 unique URLs were not individually fetched** — 46 arXiv abstract pages, 6 GitHub repos, 5 ar5iv/`r.jina.ai` proxies, the case documents, 3 DOIs, and the incident press links. Highest-risk unchecked: `doi.org/10.21203/rs.3.rs-10183486/v1` (Research Square, cited by Dhanda), `govinfo.gov/…/94-7672.htm` (AT PCO 1994), `greystar.com/…newsroom/…`, `discord.gg/XswWBvugYs`.
- Minor: `01-papers/_TEMPLATE.md` has a bare `https://github.com/` — GitHub's homepage, not a project.

---

## 2. Number spot-check

| Note | Claimed | Source says | Verdict |
|---|---|---|---|
| fish-2024 | 300 periods | not in abstract; full text not re-fetched | UNVERIFIED |
| fish-2024 | "near-monopoly" | abstract: "supracompetitive prices and profits" | **softer in source — overclaim 4** |
| fish-2024 | GPT-5.2 robustness; v6 31 Aug 2026 | v6 dated 31 Aug 2026 ✓; GPT-5.2 not in abstract | version ✓, content UNVERIFIED |
| agrawal-2025 | 90.52 / 87.71 / 86.24 / 96.26 / 96.16 | Table 1 not re-fetched (HTML beyond fetch budget) | **UNVERIFIED** |
| keppo-2026 | +22%, +10%, +7% | abstract: "from 22% to 10% … asymmetric data access, to 7%" | CONFIRMED |
| keppo-2026 | +36%, +3%, +21%, Q-learner +2–8% | not in abstract | UNVERIFIED |
| xu-2026 | +0.053; +0.0001; temperature p = 0.002 | all three exact, plus CI [0.030, 0.078], 20 models/19 developers, 77,684 bids, floor +0.50–+0.81, HHI +247.5% | **CONFIRMED (all)** |
| nakamura-2026 | 57.89%, 10.53%, r = −0.243 | not in abstract; arithmetic checks (11/19, 2/19, 15/19) | UNVERIFIED, internally consistent |
| zeng-2026 | 10/12 accept ≥98% "(abstract)"; reciprocity 100% | v2 abstract says only "most agents consistently accept" | **attribution error (minor)** |

**Discrepancies: 1 confirmed, minor; 0 major.** `zeng-2026…` line 45 attributes the 10/12-at-≥98% figure to the abstract, which contains no such number (it may be in Table 1 or v1). Everything checkable is arithmetically coherent: Keppo's percentages reconcile with its dollar values (1.47 → 1.801/1.632/1.514/1.775) and Nakamura's are exactly 11/19, 2/19, 15/19. **No fabricated or transposed number found.**

---

## 3. Overclaims

**Most serious three**

1. `03-synthesis/mechanism-map.md:22` — *"Collusion collapses, then may re-form"* as the known signature of entry/replacement, in a row whose evidence column says **"Eschenbaum 2022 (Q-learning); no LLM replacement study"**. One non-LLM paper becomes a predicted outcome; `shortlist.md:69` builds B1 on it. **Correction:** "In Q-learning markets collusion collapses when a differently-trained rival is introduced; re-formation in LLM markets is untested."
2. `03-synthesis/mechanism-map.md:9` — *"Monitoring raises the cost of talking but not necessarily of pricing, so coalitions can shift the carrier from words to actions."* It is the folder's flagship hypothesis, yet `gaps.md` #4 lists it as **untested**; in the loop paragraph it reads as a finding. **Correction:** "…so a coalition *may* shift the carrier — untested; see gap 4."
3. `03-synthesis/countermeasures.md:18` — Collina rated **"Strong (theory, conditional)"** with *"M defectors → exponential fall"*. The note's limits say the bound is **asymptotic**, at **N = 2 the surviving price is ~85% of monopoly**, and nothing is instantiated with LLMs. **Correction:** "Strong in theory, asymptotic in N (at N=2 ≈85% of monopoly), no LLM instantiation."

**Also flag**

4. `evidence-matrix.md:11` — "Near-monopoly prices" for Fish; the abstract says only "supracompetitive" and the note refuses to quote a level. Suggest "close to the monopoly benchmark under the profit-maximising prefix."
5. `detectors.md:63` — *"The intervention is what turns 'high prices' into 'collusion'."* One implantation experiment in one environment licenses a general evidentiary standard. Suggest "…the paper's strongest evidence of a collusive mechanism, in one model family."

---

## 4. Consistency audit

| # | Fact | Where it differs | Severity |
|---|---|---|---|
| 1 | **Dhanda's prompt direction** | `countermeasures.md:21`/`:47` say aggressive **"compete"** wording pushed prices **below** competitive. The note (41, 46) says generic frames *raise* prices — "compete with your rival" **+0.69**, "capture market share" **+0.52** — and only *undercut* gives the price war (−0.84). `mechanism-map.md:40` now has it right, so the folder contradicts itself. | **Major** |
| 2 | **Nguyen 95% vs ">70%"** | Resolved: note, `index.md:39` and matrix all say 95%. But the note's claim that "the sprint brief describes this as '0% to >70%'" is **unsupported** — no file in `00-sprint/` mentions 70% or Nguyen except `starter-repo-map`. If it comes from the public sprint page, say "sprint page", not "brief". | Minor |
| 3 | **Zeng's code** | `zeng-2026…` frontmatter: `code: "none found"`; `starter-repo-map.md:26`: `llm-agent-collusion-2/` **is** Zeng & Rudzicz. Both can be true, but a reader concludes no code exists. | Minor |
| 4 | **Bracale cross-provider** | Consistently "still collude", but the note's numbers show the mixed pair at tier **3.60** vs Gemini-only **2.80** — the mixed pair was *more* collusive. Understated, not wrong. | Minor |
| 5 | **Keppo Q-learner** | Consistent (+2% frozen, +8% adaptive → "+2–8%"), but the range reads as an interval around one effect when it is two conditions. | Minor |

**Broken internal link (only one):** `04-ideas/critique.md` links `01-papers/02-detection/rose-2026-helios-activation-probes.md`; from `04-ideas/` it must be `../01-papers/…`.

---

## 5. Verdict

**Not safe to hand to a participant as-is — two fixes first.** (1) Open the **ABA** link in a browser and confirm it is the Berger article; it is the sole legal citation in seven files and machine-unverifiable. (2) Fix the **Dhanda direction** in `countermeasures.md` (lines 21, 47); as written it tells a participant that "compete" wording lowers prices — the opposite of the note's finding.

Otherwise the folder is strong: **no broken external links, no fabricated numbers**, every abstract-level figure matched, and each note separates confirmed from unverified claims. Residual risk sits in the 120 unchecked URLs and the two remaining overclaims, all one-sentence edits.

---

## Post-validation resolutions (author, same day)

- **Dhanda direction (the major contradiction): fixed.** `countermeasures.md` now says the sign is verb-specific: "undercut" → below competitive (Δ ≈ −0.49), "compete with your rival" → above (+0.69), "capture market share" → above (+0.52). Both the table row and the "most likely to backfire" bullet were corrected.
- **Overclaim 1 (replacement signature): fixed.** `mechanism-map.md` now reads: "In Q-learning markets, collusion collapses when a differently-trained rival is introduced; re-formation in LLM markets is untested."
- **Overclaim 2 (carrier shift): fixed.** `mechanism-map.md` now says a coalition **may** shift the carrier and that this is untested in multi-agent markets (gap 4).
- **Overclaim 3 (Collina): fixed.** `countermeasures.md` now records the asymptotic caveat: at N=2 the surviving price is ≈85% of monopoly; no LLM instantiation.
- **Fish framing: fixed** in `evidence-matrix.md` and `detectors.md` (monopoly-benchmark framing softened).
- **Nguyen attribution: fixed** ("sprint page", not "brief").
- **Zeng: fixed.** Code now points to `AgentSafety2025/LLM-Agent-collusion` / the bundled `llm-agent-collusion-2/`; the 10/12 figure is attributed to body/Table 1, not the abstract.
- **Temperature ladder and Keppo Q-learner: fixed** (0.0–1.4; frozen +2% vs adaptive +8%).
- **Bracale: strengthened** (mixed pair tier 3.60 vs Gemini-only 2.80).
- **TraceGuard title: adjudicated in favour of the note.** arXiv:2604.03968 is titled "TraceGuard: Structured Multi-Dimensional Monitoring as a Collusion-Resistant Control Protocol". The GitHub repo uses a different tagline; the paper title is correct.
- **ABA link: still unverified.** It returns 403 to automated fetches; flagged in `README.md`. A human must open it once.
- **Broken internal link in `critique.md`: not present in the final file.** `check_links.py` reports 42 relative links checked, 0 missing.

**Status: safe to hand over after one human click on the ABA link.**
