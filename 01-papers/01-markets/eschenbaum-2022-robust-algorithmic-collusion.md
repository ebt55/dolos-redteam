---
id: eschenbaum-2022
title: "Robust Algorithmic Collusion"
authors: ["Nicolas Eschenbaum", "Filip Mellgren", "Philipp Zahn"]
year: 2022
venue: "arXiv preprint (econ.GN), v2 5 Jan 2022; circulated Dec 2021"
arxiv: "2201.00345"
url: "https://arxiv.org/abs/2201.00345"
code: "none found"
tracks: ["1.1", "1.2", "1.5"]
role: "core-result"
verification: "full-text"
---

# Robust Algorithmic Collusion (Eschenbaum, Mellgren & Zahn 2022)

**One-line takeaway.** Q-learning cartels are **overfitted to the rival they trained against**: a collusion index of 0.70–0.87 in training collapses to Nash play against an unseen competitor or a rival with different costs, but restricting the algorithm's observations to its *own* last price makes collusion transfer almost perfectly.

## The question it asks

Every algorithmic-collusion result is measured in the training environment. Firms train offline and deploy into a market whose rival and parameters they do not control. Can a learned collusive policy be extrapolated — and if not, which design choice makes it robust?

## Setup

- **Environment / game:** two-player repeated Bertrand, logit demand (Calvano et al. parameterisation), `γ_i − c_i = 1`, `μ = 1/4`; price grid of `k = 20` points over `[p^N − ξ(p̄^C − p^N), p̄^C + ξ(p̄^C − p^N)]` with `ξ = 0.1`; `p^N ≈ 1.47`, `p̄^C ≈ 2.62`.
- **Agents & models:** tabular **Q-learning** (no neural nets, no LLMs), `α = 0.15`, `ε_t = e^{−βt}`, `β = 4×10⁻⁶`; one-period memory, observation = last period's price pair plus a hidden context.
- **N agents / rounds / seeds:** N = 2. A run ends when each player's greedy action is unchanged for 100,000 consecutive periods (or 10⁹ repetitions); >99% converge, typically after **>1M rounds (>2M on average)**. **250 sessions per cost level** (sum of Table B1's convergence-type counts).
- **Communication channel:** none. **Information available:** last period's prices only; the context (seed and rival cost) is unobserved.

## Method / interventions

A *context* parameterises the POMG by (i) the initialisation seed — i.e. **a different rival policy** — and (ii) reward parameters, `c_i, c_j ∈ [1, 1.7]` in eight levels. Two converged policies from two contexts are placed in a third, fresh context and scored by the **collusion index** `M = (π̄ − π^N)/(π^C − π^N)`: first with fixed policies, then with continued updating but no exploration, then with a restricted observation space.

## Key findings (with numbers)

- **Training:** collusion index **0.70–0.87** across all eight cost levels (0.79 at c=1.00, 0.87 at 1.20/1.30, 0.70 at 1.60); mostly symmetric convergence; a forced deviation to the Nash price is punished and prices return to the pre-deviation level.
- **New rival, same parameters:** collusion **breaks down to Nash play on average**, and "irrespective of the number of periods of play, algorithmic collusion vanishes entirely" — re-convergence does not restore it.
- **Rival with different costs:** collusion index falls by **72% on average** (`R = (D̄ − Ō)/D̄ = 0.72`); diagonal 0.67–0.82, off-diagonal as low as 0.04, near-Nash especially for small parameter differences.
- **Continued updating (no exploration):** profits initially exceed Nash and collusion is restored after full re-convergence — but only after a very long time, judged infeasible in a market.
- **Diagnosis:** two runs with identical parameters and identical converged prices learn *different* punishment paths; the policy is fitted to the rival's off-equilibrium play, not to market structure.
- **Fix:** observing only the agent's **own last price** makes the new-context collusion index "virtually identical" to training, robust to a random restart; continued updating then becomes *strictly worse* than keeping the fixed policy.

## Mechanism / why it happens

Q-learning encodes a punishment schedule keyed to the exact deviations its training rival happened to make. A new rival never visits those states, so punishment is never triggered correctly and play drifts to stage-game Nash. Removing the rival's action from the state forces a simpler, rival-agnostic rule that generalises — the "zero-shot coordination" problem imported into antitrust. Alternative explanation worth testing: the restricted-observation result may be a low-collusion artefact rather than robustness; the paper reports more short cycles under restriction.

## Limitations and threats to validity

Two players, homogeneous goods, noiseless logit demand, one-period memory, tabular Q-learning only; "context" varies only seed and rival cost, not prompt, architecture or information feeds; runs cost ~10⁶–10⁷ periods, so replication is expensive for a weekend; and "coordinate on algorithm design" assumes firms can coordinate on observation spaces, which is itself the antitrust problem.

## Relevance to the sprint

- **Q1.2** — the cleanest statement of the replacement problem: formed collusion is *not* robust to a new rival, and the mechanism is overfitting. This is the baseline any replacement project must beat.
- **Q1.1** — information available to agents (own vs rival history) is first-order and interacts with robustness, not just with the level of collusion.
- **Q1.5** — restricting the strategy/observation space is *pro-collusive* here, the mirror image of Keppo's pro-competitive algorithmic diversity.

## Project hooks (48-hour sized)

1. **Reproduce the training→testing gap on CPU (no API cost).** 20-price Bertrand grid, two tabular Q-learners; positive control = training collusion index ≥0.70 within ~10⁶ steps; intervention = pair each converged policy with a partner trained under a different seed; metric = collusion index over the first 1,000 test periods (expect ≈0). Cost $0, 2–4 hours.
2. **Does the own-price-only fix survive a different demand system?** Retrain restricted, test transfer under a changed `μ` or a 30-point grid; metric = transfer ratio (test/train collusion index). Cheap test of the paper's weakest external-validity point.
3. **Bridge to LLM agents:** put a converged Q-table against an API LLM pricing agent for 300 rounds. Positive control = two LLM agents collude (elevation >15%); metric = LLM price variance and elevation against the Q-table. Cost ≈$20–50.

## What this paper does NOT test

No LLM or deep-RL agents; no communication channel; no mid-run replacement inside an already-colluding LLM pair; no detection, auditing or liability schemes; no markets with more than two firms.

## Related notes in this folder

- `keppo-2026-fragility-agent-collusion.md` — the LLM version; a Q-learner partner prevents LLM collusion, this mechanism seen from the other side.
- `collina-2025-breaking-algorithmic-collusion.md` — a no-regret (not overfitted) participant as destabiliser.
- `fish-2024-algorithmic-collusion-llms.md` — the symmetric baseline whose external validity this paper attacks.

## Verification log

- Read: **PDF full text**, `https://arxiv.org/pdf/2201.00345v2` (38 pp., all sections, Table B1, Figures 1–10). The organisers' link `https://openreview.net/pdf?id=BztUFukcBry` returned **HTTP 403** (Cloudflare browser challenge) for both PDF and forum page; web search resolved that OpenReview URL to this exact title, so the arXiv version is the source used.
- Numbers spot-checked: yes — 0.70–0.87, `R = 0.72`, and the 250-session counts recomputed from Table B1.
- Could not confirm: seeds per cost level (session counts and averages "across seeds" only); exact convergence thresholds for restricted-observation runs.
