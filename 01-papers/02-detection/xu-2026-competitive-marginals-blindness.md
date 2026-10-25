---
id: xu-2026
title: "Collusion with Competitive Marginals: Price-Level Audits Are Blind by Construction"
authors: ["Xin Xu", "Chengrui Wu", "Jiayu Lu", "Kaizhen Tan", "Siru Tao", "Hanzhe Hong"]
year: 2026
venue: "arXiv preprint (cs.GT), 29 Jul 2026"
arxiv: "2607.26385"
url: "https://arxiv.org/abs/2607.26385"
code: "code supplement released with paper (no public URL found)"
tracks: ["1.3", "1.5", "2.3"]
role: "counterpoint"
verification: "full-text"
---

# Collusion with Competitive Marginals (Xu 2026)

**One-line takeaway.** A conspiracy can leave every agent's price distribution exactly at the competitive law and put all of the collusion in the copula — so price-level audits have power exactly α against it, no matter how much data you collect; the residual-correlation statistic still sees part of it, and sampling temperature moves that dependence.

## The question it asks

The entire empirical algorithmic-collusion literature asks "are prices supracompetitive?" The paper asks what happens to that question if agents coordinate *without* moving any marginal — and then whether the standard screening statistic (pairwise correlation of residual bids) still recovers anything in real language-model agents.

## Setup
- **Environment / game:** a repeated first-price auction. Bidder `i` in round `t` bids `b_it = g_it + σ ε_it` with `g_it = μ_t + a_i + β_i^T x_t` (round effect, bidder effect, loadings on public covariates) and `ε_it` the part no public information explains, with marginal law `F_i`. The auditor reconstructs `g` and cannot reconstruct `ε`. `κ = sd(σε)/sd(g)` is the unexplainable share of cross-bidder dispersion.
- **Agents & models:** 20 language models from 19 independent developers (Claude-3-Haiku, GPT-4o-mini, Llama-3.1-8B, Qwen-2.5-7B, Gemma-2/3-27B, DeepSeek-Chat, Kimi-K2, Phi-4, Command-R, Nova-micro, Jamba-large, Ernie, Granite, Mercury, Ling, MiniMax, Mistral-Nemo, Hunyuan, Solar-pro; the two Google models are clustered as one developer).
- **N agents / rounds / seeds:** 20 models × 3 deployment prompts = 60 agents, 200 rounds at each of five temperatures (0.0, 0.3, 0.6, 1.0, 1.4), giving 60 same-base pairs and 1,710 cross-base pairs. Order stream fixed by one seed so every agent faces identical orders. Market side: 24 days of Ethereum MEV-Boost relay data, 77,684 bids, 39 bidders, 164 scored pairs at a 1,000-round overlap requirement.
- **Communication channel:** none — deliberately zero. The coupling is upstream (shared base model) plus public round data.
- **Information available to agents:** the public order features; the auditor is modelled as seeing the same features, at three levels of richness.

## Method / interventions

**The construction.** Fix every marginal at `F_i` and change only the joint law. Lemma 1 gives a zero-communication realisation: with a shared key `k` and a PRF on public round data, `z_t = Φ^{-1}(PRF_k(id_t)/2^λ)` and `ε_it = F_i^{-1}(Φ(√ρ z_t + √(1−ρ) e_it))`, `e_it ~ N(0,1)`. Every marginal stays `F_i` for all `ρ`; `ρ=0` is competitive, `ρ=1` comonotone.

**The dependence statistic.** Pairwise Pearson correlation of **residual bid series** — each agent's bids regressed on the order features, residuals correlated across the pair — i.e. standard cartel screening (Harrington 2008; OECD 2022) applied to the copula rather than the level. Three auditor specifications, increasing strength: (A) linear in 2 of 6 order features (size, volatility); (B) linear in all 6; (C) all 6 plus squares and all pairwise interactions (27 terms, ridge `1e-3·n`), fitted by 5-fold cross-fitting so every residual is out-of-sample. Confidence intervals are t-intervals clustered by developer.

**Interventions on the auditor and on deployment.** Auditor ladder A→C (the "sees everything" control), and sampling temperature as the deployment-side lever. On the market side, three repairs are tried and fail; the positive result is entity counting (resolving bidder identities into operators) rather than conduct detection.

## Key findings (with numbers)

- **Marginal audits are exactly blind, not underpowered.** Proposition 1: any size-α test whose input is one bidder's history has rejection probability exactly α under the construction, for every `ρ` up to 1, because the shared draw is redrawn each round so the *whole process law* of a single bidder is unchanged. Simulation: 6 distributional statistics on one bidder's residuals reach AUC 0.50–0.55 at N up to 1e4; a Bonferroni battery has power 0.020 at `ρ = 1.0`, N = 2e4, α = 0.05. The pairwise test on the same data reaches power 1.0, and its resolvable coupling improves like N^{-1/2}.
- **The mechanism is real in language models.** At T = 0.3 the 60 same-base pairs correlate at **+0.110** (auditor A), **+0.059** (B), **+0.053** (C, clustered 95% CI **[0.030, 0.078]**), while the 1,710 cross-base pairs sit at **+0.023**, **+0.000**, **+0.0001**. The asymmetry survives the strictest auditor.
- **Temperature is a dial.** Same-base correlation falls monotonically with temperature (under C: +0.070 at T=0 → +0.053 → +0.009 → −0.008 → −0.004). Permutation test over 20,000 permutations: mean within-developer slope −0.093 (A), −0.053 (B), −0.058 (C), with two-sided p of 5e-5, 0.003 and 0.002 respectively.
- **It is profitable, and it is not an equilibrium.** Comonotone coupling minimises `E[max_i b_i]` (the seller's revenue) at fixed marginals; a 5-member coalition takes 4.6% of seller revenue at the lower end of the cleaned ambient floor and 10.6% uncleaned. Proposition 4: the conduct is not a correlated equilibrium, yet its held-out calibrated swap regret *excess* over competitive play is negative in every cell (−0.0004 to −0.021 as `ρ` rises), so regret audits do not separate it either — the honest market's own dispersion absorbs the conspiracy.
- **Deployed market floor.** On the 24-day panel the honest population of bidder pairs is so dependent that a 5%-FPR screen must sit above **+0.50 to +0.81**, which the paper reports as **20 to 32×** the family-wise sampling threshold, and the floor does not fall as the audit window grows (observed p95 +0.909, max +0.973; `κ = 0.895` implies 44.5% unexplained variance). Counting: resolving 40 bidding identities into 23 operators raises the Herfindahl index by **+247.5%**; adding behavioural clusters reaches **+324.5%**.

## Mechanism / why it happens

The expected maximum of fixed marginals is minimised by the comonotone coupling (submodularity + supermodular order), so coordination transfers rent without any price moving. Shared model supply supplies the common function "for free": two deployments of one base model reading the same public data already compute correlated functions of it, so the conspiracy needs no agreement and no channel — and the party that gains need not be either firm.

## Limitations and threats to validity

The two halves (language-model mechanism, market floor) are joined by argument, not one experiment — block builders do not run LLMs. Lab rent moves by an order of magnitude across the auditor ladder, so only the coupling is comparable, not effect size. Thresholds are swept, not derived. Entity results are single-day with a structural ceiling (builders that never won cannot be labelled). Temperature is measured at five points and the paper's own intro hedges that the trend is "not at conventional significance with five temperature points", even though the appendix permutation test reports p = 0.002 — worth reading both statements. Proposition 4(iii) is verified, not proved.

## Relevance to the sprint

- **Q1.3** — gives a detection statistic with a known blind spot and an exact power statement, plus a ready-made auditor ladder to test whether a proposed detector is actually reading dependence.
- **Q1.5** — temperature as a single, cheap, deployment-level restriction with a measured monotone effect.
- **Q2.3** — a hard standard-of-evidence result: "no price lift" does not mean "no collusion", and lawful shared infrastructure and conspiracy are behaviourally indistinguishable in this channel.

## Project hooks (48-hour sized)

1. **Reproduce the power identity, then break it.** Implement the Lemma 1 generator (scripted, no LLM), sweep `ρ ∈ {0, 0.3, 0.6, 0.9, 1.0}` and N; positive control = single-bidder tests sit at α = 0.05 while the pairwise residual-correlation test reaches power ≈ 1 at `ρ = 0.9`. Metric = empirical power vs α. Cost: minutes of CPU.
2. **Same-model vs cross-provider dependence in a sprint market game.** Run the Fish-style or Agrawal double auction with 3 sellers under two conditions (two deployments of one model vs two providers), 3–5 seeds, 30 rounds. Metric = residual correlation with a developer-clustered bootstrap, plus the seller-revenue counterfactual (permute residuals). Positive control = a scripted `ρ = 0.9` pair injected into the same harness.
3. **Calibrate, don't threshold.** Use no-communication runs to estimate the ambient dependence floor, then ask whether communication-enabled runs clear it. Metric = false-positive rate on the no-channel arm at the threshold that catches the channel arm. This is the sprint's "does the detector fire on a benign Schelling point?" test.

## What this paper does NOT test

Whether real colluding LLM agents actually implement the construction (it is a possibility proof plus a measurement of accidental coupling); multi-agent settings with messages; detection of *which* pair colludes (the statistic is pairwise, the market result is population-level); any intervention other than temperature and entity resolution; and whether the market floor generalises beyond one auction design.

## Related notes in this folder

- `nakamura-2026-colosseum-coalition-advantage.md` — action-regret metrics that assume a computable benchmark; Xu shows the benchmark can be satisfied while colluding.
- `bonjour-2022-pairwise-net-influence.md` — the information-theoretic cousin of residual correlation, with a max-over-third-parties correction Xu does not have.
- `rippin-2026-tool-steganography-schelling.md` — the channel-based mechanism Xu deliberately rules out.

## Verification log

- Read: abstract page (`https://arxiv.org/abs/2607.26385`), HTML full text (`https://arxiv.org/html/2607.26385v1`), PDF-to-text via `https://r.jina.ai/https://arxiv.org/pdf/2607.26385v1` (this reached §3–Appendix G, including Table 2 and the auditor ladder).
- Numbers spot-checked: yes — +0.053 / +0.0001 / CI [0.030, 0.078]; +0.110, +0.059; cross-base +0.023 / +0.000; temperature slopes and p-values; 20 models / 19 developers / 3 prompts / 200 rounds / 5 temperatures; 77,684 bids / 39 bidders / 164 pairs; floor +0.50–+0.81 and 20–32×; HHI +247.5% / +324.5%; 4.6% and 10.6% revenue capture.
- Could not confirm: the "residual correlation" is never given a single formal symbol in the fetched text — it is described as pairwise correlation of residual bid series, and the paper is explicit that the statistic is standard cartel screening rather than novel. Treat the estimator's exact form (Pearson on cross-fitted residuals, per-pair) as the faithful reading, not a quoted equation.
