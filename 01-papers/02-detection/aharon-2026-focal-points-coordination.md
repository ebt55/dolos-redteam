---
id: aharon-2026
title: "Tacit Coordination of Large Language Models"
authors: ["Ido Aharon", "Emanuele La Malfa", "Michael Wooldridge", "Sarit Kraus"]
year: 2026
venue: "arXiv preprint (cs.GT), v2 16 Jun 2026"
arxiv: "2601.22184"
url: "https://arxiv.org/abs/2601.22184"
code: "https://github.com/EmanueleLM/focal-points"
tracks: ["1.2", "1.3", "3.3"]
role: "background"
verification: "partial"
---

# Tacit Coordination of LLMs (Aharon 2026)

**One-line takeaway.** LLMs hit focal points with no channel at all, often matching humans, but their salience is family-specific and centrality-biased: two agents from one model family coordinate for free where two different families cannot.

## The question it asks

With no communication and many equally good equilibria, how do LLM agents pick? Humans use Schelling salience (extremeness, centrality, cultural uniqueness). Do LLMs share it, does more reasoning help, and what happens when the two agents are different models?

## Setup
- **Environment:** **Amsterdam / Nottingham**, the Bardsley et al. (2010) multiple-choice coordination games, 14 questions each, with human data from about 50 participants under three instructions (pick, guess, coordinate). Also **Bargaining Table** (Mizrahi et al. 2020) and a **Search & Rescue** task.
- **Models:** over 20. Main open-weight set: Llama-3/3.1/3.3-70B, Qwen-2/2.5-72B, GPT-oss-20B/120B; appendix adds GPT-5.4, Gemini 2.5/3 Pro and size sweeps.
- **N:** 30 runs per question under each of 3 answer permutations, so 90 runs per question per model.
- **Channel:** none. Agents see the question, options in randomised order, and the framing.

## Method / interventions

The **Coordination Index** `CI = sum_j m_j(m_j-1)/(n(n-1))` is the probability two random players pick the same option, normalised to `NCI = m*CI` across games with different option counts.

Three learning-free prompts on heterogeneous models: **saliency** ("most salient to humans"), **all-features** (reason over Kraus et al.'s focality principles), **culture** ("most culturally relevant to humans"). A separate pass sorts answers into four focality categories with GPT-5.2 to compare human and LLM profiles.

## Key findings (with numbers)

- Under *pick*, LLMs beat humans; under *guess* the advantage narrows and under *coordinate* it vanishes. Competitive in Amsterdam, humans clearly better in Nottingham (largest gaps TN1, TN7, TN11).
- **More reasoning does not help.** GPT-oss-120B across low/medium/high shows no clear NCI gain and sometimes degrades, with logs collapsing to positional heuristics such as "pick the first option in a permuted list".
- **Same-family pairing inflates coordination:** "Using models from the same family substantially improves NCI by reducing output diversity (Appendix C.3.4)". A diversity effect (two Llama-70B variants making the same choice), not collusive intent. Per-family numbers are in an appendix I could not fetch.
- **Culture is the missing ingredient.** The culture prompt markedly raises NCI, matching or beating humans in both cities, while saliency and all-features do little. The gap is knowledge of human salience, not reasoning.
- **LLMs over-use centrality.** Humans use most focality dimensions in Nottingham; LLMs concentrate on centrality, which explains their weakness where human focality comes from other cues.
- **Partner capability changes human welfare.** In the Bargaining Table, moving the GPT-oss partner from 20B to 120B raises human mean payoff from 9.62-26.44 to 30.18-33.26 (Table 1).

## Mechanism / why it happens

Shared pre-training yields a shared salience prior: order, round numbers and structural centrality are over-represented and therefore obvious to any model trained on similar text, and within-family decoding overlap shrinks diversity further. Alternative to test: same-family gains may be plain decoding determinism, and a high-temperature same-family pair is the discriminating condition.

## Limitations and threats to validity

Question-answer tasks only: no tools, memory or multi-round interaction, so NCI is a one-shot choice distribution, sensitive to option count and answer-set construction, and the human benchmark is a fixed 2010 pool. The family result rests on a few lineages and is only summarised in the main text. Nothing here is collusion itself, only its precondition.

## Relevance to the sprint

- **Q1.2:** a sibling re-converges on the settled convention while a cross-family replacement does not, so swapping a coalition member may not break collusion.
- **Q1.3:** CI/NCI is a cheap mutual-Schelling-salience score computable from choices alone.
- **Q3.3:** the convention an agent picks partly identifies its family, a peer signal that survives anonymisation.

## Project hooks (48-hour sized)

1. **Salience as a peer-recognition signal.** 2 families x 2 sizes on the same 14-question battery, no channel; build the pairwise CI matrix. Positive control is within-family CI; metric is AUC of same-family classification from CI alone against a permutation baseline. A few hundred short calls, no GPU.
2. **Convention recovery after replacement.** Let a pair settle a convention over repeated one-shot rounds, then swap one agent for a sibling vs a cross-family model. Positive control is the no-swap run holding the convention; metric is rounds-to-reconverge and agreement rate.
3. **Temperature confound test.** Repeat hook 1 at T = 0.0/0.7/1.2; if within-family CI collapses with temperature the effect is determinism, not salience. Metric is the slope of CI on temperature.

## What this paper does NOT test

Any channel, repeated game with history, market task, incentive to collude, or detector. It does not test cross-provider pairs beyond the listed roster, or whether a model infers its partner's family.

## Related notes in this folder

- `rippin-2026-tool-steganography-schelling.md`: reuses this CI machinery for steganographic scheme choice.
- `nakamura-2026-colosseum-coalition-advantage.md`: collusion proper, with a channel and an incentive.
- `xu-2026-competitive-marginals-blindness.md`: same-family coupling as residual bid correlation.

## Verification log

- Read: abstract (`https://arxiv.org/abs/2601.22184`) and HTML full text (`https://arxiv.org/html/2601.22184v2`), truncated inside section 4.4.
- Status: **partial**. Confirmed: CI/NCI definitions, 14+14 questions, 90 runs per question, roster, the reasoning result, the verbatim same-family sentence, the culture result, centrality bias, Table 1 ranges.
- **Not confirmed:** NCI values behind the same-family claim, exact human NCI values, Search & Rescue results. Quote direction, not effect size.
