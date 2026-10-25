---
id: dhanda-2026
title: "A Price Cap Can Act as a Focal Point for LLM Pricing Agents: Evidence from a Repeated Bertrand Duopoly (Revised)"
authors: ["Kunal Dhanda"]
year: 2026
venue: "Research Square preprint (revised), posted 30 Jun 2026"
arxiv: "none"
url: "https://doi.org/10.21203/rs.3.rs-10183486/v1"
code: "none found (script names given: experiment_v2.py, cap_sweep.py, analysis_v2.py)"
tracks: ["1.1", "1.5"]
role: "core-result"
verification: "full-text"
---

# A Price Cap Can Act as a Focal Point (Dhanda 2026)

**One-line takeaway.** With two Llama-3.2-3B sellers in a 30-round Bertrand duopoly, a neutral profit prompt produces **no reliable collusion** (Δ = 0.11, CI spans zero), an "undercut your rival" prompt produces a **price war below Nash** (Δ = −0.49), and an *announced* price cap produces the **most collusive outcome of any condition** (Δ = 0.665, SD 0.006) because the announcement is a Schelling focal point — while vaguer "compete" wording *raises* prices.

## The question it asks

Which prescriptive interventions actually reduce collusion between LLM pricing agents — and can the most intuitive regulatory tool, a price ceiling, backfire?

## Setup

- **Environment / game:** logit-demand Bertrand duopoly (Calvano et al.): `a = 2`, `a0 = 0`, `μ = 0.25`, `c = 1`; static Nash `p^N = 1.473`, joint monopoly `p^M = 1.925`. Collusion index `Δ = (p̄ − p^N)/(p^M − p^N)`: 0 = competition, 1 = monopoly, negative = price war.
- **Agents & models:** two **Llama-3.2 3B** agents served locally via Ollama, temperature **0.7**; the capability ladder adds Llama-3.2-1B, Phi-3 (~3.8B) and Gemma-3-4B.
- **N agents / rounds / seeds:** N = 2, **30 rounds**, outcome = mean of the final ten rounds, **12 seeds**/condition (5–8 for the cap sweep, 6 for the ladder).
- **Communication channel:** none. **Information available:** own cost, legal price range `[1.0, 2.5]`, the competitive logic, and the last five rounds of own price, own profit and rival price.

## Method / interventions

Three conditions: **neutral**; **aggressive** (adds "Compete aggressively. Undercut your rival to capture market share."); **price_cap** (adds "It is ILLEGAL to set a price above 1.70", with prices clipped). Then two mechanism experiments — an **announced cap sweep** over {1.55, 1.60, 1.70, 1.80, 1.90} and a **hidden cap** that clips silently — plus a five-way **wording ablation** and a four-model **capability ladder**.

## Key findings (with numbers)

- **Neutral: no reliable collusion.** `Δ = 0.107`, 95% CI [−0.072, 0.287], p = 0.21 — a direct non-replication of GPT-class supra-competitive results, scoped by the author to Llama-3.2 in this setup.
- **Aggressive: price war.** `Δ = −0.493`, CI [−0.821, −0.166]; vs neutral t = 3.54, p = 0.0025, d = 1.45.
- **Price cap: most collusive, least variance.** `Δ = 0.665`, CI [0.662, 0.669], mean price 1.68, SD 0.006; vs neutral t = −6.85, p = 2.7×10⁻⁵, d = −2.80.
- **Price tracks the cap almost one-for-one:** 1.55 → 1.484 (Δ 0.04); 1.60 → 1.560 (0.30); 1.70 → 1.683 (0.67); 1.80 → 1.776 (0.86); 1.90 → 1.872 (0.98); slope **1.11 (SE 0.02), R² = 0.987**, p = 5×10⁻²⁷.
- **It is the announcement, not the clipping:** at a 1.80 cap announced Δ = 0.86 vs hidden 0.16 (p = 0.015); at 1.60, 0.30 vs 0.004 (p = 0.0005).
- **Wording is direction-dependent:** "undercut" **−0.84** [−1.01, −0.68]; "compete aggressively / undercut" −0.65; neutral 0.14; "capture market share" **+0.52** [0.03, 1.00]; "compete with your rival" **+0.69** [0.34, 1.04].
- **Non-monotone in size (neutral Δ / cap Δ):** 1B 0.90 / 0.64; 3B 0.14 / 0.66; Phi-3 3.8B 0.32 / 0.31; Gemma-3-4B 0.77 / 0.71 — the cap effect generalises where baseline behaviour does not.

## On the discrepancy with the sprint page

The organisers cite this paper for "strongly worded instructions to compete aggressively pushed prices below the competitive level". That is the aggressive result and it is accurate, but it is not the headline: the central finding is that a **price cap increases** collusion, and the wording ablation shows generic competition frames ("compete with your rival", "capture market share") **raise** prices, so only specific *undercut* semantics produce the price war. The paper also fails to reproduce spontaneous Llama-3.2 collusion at all.

## Mechanism / why it happens

Without a cap, Bertrand logic pulls these agents toward Nash. A cap removes the upper tail of the action space *and* supplies one salient, common-knowledge number; both agents coordinate just below it with near-zero variance — a focal point, not noisy learning. Instructions use the same salience channel with verb-specific direction: undercutting language points at the rival's price, "market share" language points at volume and softens price competition.

## Limitations and threats to validity

Only open 1–4B models, no GPT/Claude/Gemini; 30 rounds and 6–12 seeds; one demand system and price grid; the cap is an instruction plus mechanical clip, not a legal regime; no monitoring or enforcement costs; and the neutral prompt may be weaker than Fish et al.'s, so "no collusion" may be a prompt artefact.

## Relevance to the sprint

- **Q1.1** — prompt wording is a single isolatable variable with measured effects in *both* directions, cheap to manipulate.
- **Q1.5** — a candidate "single restriction" (price ceiling) that makes things worse: a useful negative control for ranking interventions.

## Project hooks (48-hour sized)

1. **Cap-as-focal-point with a modern model pair.** Positive control: announced cap at 1.70 gives Δ > 0.5 in ≥4/5 seeds. Intervention: the same cap enforced silently (clip only, no announcement). Metric: Δ and SD of the converged price; cost $20–50 for 12–20 runs of 30 rounds.
2. **Wording ablation at scale:** five directives × two providers × 5 seeds. Metric: Δ per directive with CIs; the live question is whether "compete"/"market share" framings still *raise* prices on frontier models. Cost ≈$30–70.
3. **Salience test the paper does not run:** cap at a round number (1.70) vs an arbitrary one (1.732), identical economics; a focal-point mechanism predicts sharper convergence and lower variance at the round number. Metric: SD of converged price and distance below the cap. Cost ≈$20–40.

## What this paper does NOT test

Frontier or cross-provider models; explicit communication; more than two sellers; a cap combined with a penalty (the author flags this as the priority follow-up); detection from transcripts; welfare accounting beyond the price index.

## Related notes in this folder

- `fish-2024-algorithmic-collusion-llms.md` — the paper this builds on and partly fails to replicate (GPT-class vs Llama-3.2-3B).
- `keppo-2026-fragility-agent-collusion.md` — same Bertrand/logit environment with DeepSeek models and a much stronger anti-collusion-prompt result.
- `bracale-2026-institutional-ai-governance.md` — a prompt-only prohibition that does nothing, versus this prompt that moves prices a lot.
- `collina-2025-breaking-algorithmic-collusion.md` — focal points and equilibrium selection, the theory behind the cap result.

## Verification log

- Read: **PDF full text** (9 pp.), `https://doi.org/10.21203/rs.3.rs-10183486/v1` → `researchsquare.com/article/rs-10183486/v1`, PDF from `assets-eu.researchsquare.com`; all sections, Tables 1–4, limitations.
- Numbers spot-checked: yes — every Δ and CI is quoted from Tables 1–4; the PDF's fonts garble Greek glyphs and ligatures ("firms" renders as "}rms"), so values were cross-read between abstract, tables and in-text contrasts.
- Could not confirm: seeds per hidden-cap cell (8 for the lowest cap, 5–6 otherwise per §4); whether the DOI landing page is byte-identical to the labelled "Revised" file.
