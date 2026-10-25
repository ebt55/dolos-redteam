---
id: collina-2025
title: "Breaking Algorithmic Collusion in Human-AI Ecosystems"
authors: ["Natalie Collina", "Eshwar Ram Arunachaleswaran", "Meena Jagadeesan"]
year: 2025
venue: "arXiv preprint (cs.LG / cs.GT), 26 Nov 2025"
arxiv: "2511.21935"
url: "https://arxiv.org/abs/2511.21935"
code: "none (theory paper)"
tracks: ["1.2", "1.5"]
role: "core-result"
verification: "full-text"
---

# Breaking Algorithmic Collusion in Human-AI Ecosystems (Collina et al. 2025)

**One-line takeaway.** A **single** participant who stops playing the collusive equilibrium and runs any no-regret pricing rule caps the time-averaged market price at Θ((1+ln N)/N) of the monopoly price — one human pricing by hand can break an AI cartel in a large market, unless the remaining agents may re-equilibrate *knowing* a defector is present.

## The question it asks

Adoption of pricing agents is never total: some sellers price manually, or are forced to by regulators. If AI agents sustain a collusive equilibrium, does one such "defection" to a simple adaptive rule move the market price — and how far?

## Setup

- **Environment / game:** N-player repeated Bertrand, prices discretised to `{0, 1/K, …, 1}`, zero marginal cost, lowest price takes the market (ties split), T rounds. Market price = time-average of the realised minimum price = total seller revenue.
- **Agents & models:** no models. AI agents play an **ε-approximate Nash equilibrium in strategy space** (ε = Θ(1/T)), i.e. a fixed repeated-game policy; a "human" switches to **any r(T)-regret strategy** (`r(T) = o(T)`).
- **N agents / rounds / seeds:** arbitrary N ≥ 2, T and K; no experiments, no seeds — all results are theorems.
- **Communication channel:** none (strategies condition on public price history).
- **Information available:** full public history of price distributions and own payoffs.

## Method / interventions

1. **Defection model:** from any ε-approximate equilibrium with price 1, let one player switch to a no-regret strategy and bound the resulting price; a **median-profit** restriction on the defector excludes pathological equilibria.
2. **Tightness:** construct equilibria attaining the bound with a discretised **equal-revenue distribution** as the punishment threat and **cyclic threats** (only player `i+1 mod N` punishes player `i`), so N−1 simultaneous random threats don't drag the price down.
3. **Many defectors:** bound the price with M simultaneous defectors, with *no* equilibrium assumption on the rest.
4. **Defection-aware agents:** non-defectors form a fresh equilibrium conditioned on who defected.

## Key findings (with numbers)

- **One median-profit defector:** price `O((ln N + 1)/N + ((r(T)+1)/T)·ln N + 1/K + 1/T)` (Thm 3.3); the tight construction (Thm 3.5) gives `(ln N + 1)/N − 3ln N/K − O(√(r(T)ln(N+1)/T))`, so the price is `Θ((1+ln N)/N)`. At N = 2 that is `(1+ln 2)/2 ≈ 0.85` of monopoly, improving on the prior `2/e ≈ 0.74`.
- **Warm-up (Prop 3.1):** a simpler equilibrium survives *any* no-regret defection at price ≥ `1/N − 2/K − r(T)/T` — defection need not collapse the price to zero.
- **Why median-profit (Prop 3.2):** if the **highest-profit** player defects, a constructed equilibrium keeps the price ≥ `1 − 1/K` for any N. Regulators should audit no-regret compliance in the *lower*-profit players.
- **M defectors (Thm 3.6):** price ≤ `M/e^{M−1}·(1+o(1))` with no equilibrium assumption, matched by ≥ `M/e^{M−1} − O(1/K)` (Prop 3.7) — exponential in the number of defectors.
- **Defection-aware agents (Thm 4.2):** price ≥ `1 − 1/K − r(T)/T` regardless of N — collusion fully restored.
- **Core lemma (3.4):** a no-regret player's utility `c` caps the market price at `c + 1/K + (c + r(T)/T)(1+ln(1/c))`.

## Mechanism / why it happens

A no-regret learner guarantees itself a non-trivial share of available surplus whatever others do; in a winner-takes-all pricing game that share can only come from winning rounds, so the winning price must fall. How far depends on the off-path threat: a well-chosen equal-revenue threat distribution keeps the price the defector faces near `(1+ln N)/N` rather than 0. Alternative explanation for Thm 4.2: once the N−1 agents may condition on the defection they can support *any* price, so the reversal may be equilibrium selection rather than what adaptive LLM agents would find.

## Limitations and threats to validity

Pure theory: equilibrium play by AI agents, homogeneous goods, noiseless demand, zero cost, discretised prices, no learning dynamics. Nothing is instantiated with LLMs, so mapping "no-regret" onto a scripted or prompted seller is unvalidated. The bound is asymptotic in N and K; at N = 2 the surviving price is still 85% of monopoly. The defector is assumed permanently committed — a human who re-adopts the agent is outside the model.

## Relevance to the sprint

- **Q1.5** — the formal case for the cheapest intervention on the sprint's list: one participant running a simple adaptive rule, no monitoring, no fines, no messages. The *identity* of that participant matters more than the intervention.
- **Q1.2** — replacement as degradation: swapping one AI for a non-equilibrium human is a replacement experiment, and the theory predicts partial recovery, not collapse, in small markets.

## Project hooks (48-hour sized)

1. **Scripted no-regret seller inside an LLM cartel.** Positive control: 3 LLM sellers in a 200–300-round Bertrand duopoly above +15% elevation in ≥4/5 seeds. Intervention: replace one seller with a scripted EXP3 / ε-greedy-with-hedging seller. Metric: mean market price as a fraction of the monopoly price over the last 100 rounds, plus realised regret; Thm 3.3 at N=3 predicts ≤ `(1+ln 3)/3 ≈ 0.70`. Cost $20–60.
2. **Median-profit vs leader defection (Prop 3.2).** Branch saved transcripts twice: replace the highest-price seller vs the median-profit seller. Metric: ratio of post-replacement prices; a large gap confirms the profit-rank condition empirically. Cost ≈$15–40.
3. **Defection-aware arm (Thm 4.2).** After replacement, tell the remaining agents (fresh context) that one participant is non-AI and re-planning; compare with an unaware arm. Metric: price recovery fraction. Cost ≈$20–50.

## What this paper does NOT test

No LLM, RL or human-subject experiment; no communication or side channels; no monitoring/auditing costs; no liability schemes; no heterogeneous goods or costs; partial adoption is answered only asymptotically; and nothing shows a *prompted* LLM seller can implement a no-regret rule.

## Related notes in this folder

- `eschenbaum-2022-robust-algorithmic-collusion.md` — the other mechanism by which a mismatched participant breaks a cartel: overfitting, not no-regret guarantees.
- `keppo-2026-fragility-agent-collusion.md` — the empirical analogue: an architecturally different (Q-learning) participant dissolves LLM collusion.
- `agrawal-2025-double-auction.md` — a harness where a scripted defector seller could be dropped into an LLM market.

## Verification log

- Read: abstract page `https://arxiv.org/abs/2511.21935` **and** arXiv HTML v1 full text `https://arxiv.org/html/2511.21935v1` (§1–§5, Appendix A.1–A.2, theorem statements and proof sketches; Appendix D proofs skimmed).
- Numbers spot-checked: yes — theorem statements quoted verbatim; `(1+ln2)/2` vs `2/e` and `M/e^{M−1}` cross-checked against §3.3–§3.4.
- Could not confirm: nothing material; all quantities are theoretical fractions of the monopoly price, not measurements.
