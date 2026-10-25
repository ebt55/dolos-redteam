---
id: bonjour-2022
title: "Information-Theoretic Approach to Detect Collusion in Multi-Agent Games"
authors: ["Trevor Bonjour", "Vaneet Aggarwal", "Bharat Bhargava"]
year: 2022
venue: "UAI 2022 (PMLR 180:223-232)"
arxiv: ""
url: "https://proceedings.mlr.press/v180/bonjour22a.html"
code: "none found (no public author implementation located)"
tracks: ["1.3", "1.4", "2.3"]
role: "core-result"
verification: "full-text"
---

# Pairwise Net Influence (Bonjour 2022)

**One-line takeaway.** Colluders' actions become statistically dependent beyond what the shared game state explains, so compute the conditional mutual information between each pair's actions given the joint state, subtract the largest influence any third agent has on that agent, and the colluding pair is the one where both directions clear a threshold.

## The question it asks

Given only game records, `(state, action, reward)` tuples over many episodes, with no communication logs and no game-specific knowledge, can you identify *which two* of `n > 2` players are colluding? The answer is a domain-independent statistic that works for a fully observable simultaneous game and a partially observable sequential one, for hand-written and learned collusion alike.

## Setup
- **Games:** (1) **3-player iterated Rock-Paper-Scissors.** All-same pays 0 each, all-distinct pays 1 each, two distinct pay the winners 1. (2) **3-player Leduc Hold'em**, partially observable and sequential: 6-card deck with ranks A/K/Q, 1-chip ante, 2-bet maximum per round, raise 2 pre-flop and 4 post-flop, 9 rotations per game.
- **Agents:** rule-based, not LLMs. RPS manual collusion has Player A as primary colluder (random), **Player B as assistant** who plays a move guaranteeing A a point with probability `CP` (the collusion probability) and a random move otherwise, and Player C non-colluding. Leduc association collusion sees both partners' hole cards and raises if either holds an ace (round 1) or a pair or ace (round 2).
- **Automatic collusion:** DDQN with the colluding pair treated as one agent over a joint state-action space, 10,000 games against a random opponent; Leduc gets high-payoff (HP) and low-payoff (LP) variants plus a learning-based honest opponent.
- **N:** `n = 3` (a 4-player RPS variant is reported in Appendix C). Table 3 uses 1,000 games per player combination; detection accuracy is averaged over 1,000 iterations per sample size. **`α = 0.05` in every experiment.**
- **Channel:** none observed. Collusion is ex-ante coordination or covert signalling the detector never sees.

## Method / interventions

**Individual influence** `γ(i;j)` is the conditional mutual information between `i`'s and `j`'s actions given their joint state, i.e. how far the joint policy departs from the product of marginals:

```
γ(i;j) = Σ_{s_ij} p(s_ij) Σ_{a_i,a_j} p(a_i,a_j | s_ij)
         · log [ p(a_i,a_j | s_ij) / ( p(a_i|s_i) · p(a_j|s_j) ) ]
```

**Net influence** subtracts the strongest rival explanation, the largest influence any other agent `k` has on `j`:

```
Γ(i;j) = γ(i;j) − max_{k ∈ n, k ≠ i,j} γ(k;j)
```

Collusion needs **both directions**: `Γ(i;j) ≥ α` and `Γ(j;i) ≥ α`. If exactly one pair qualifies, return it; otherwise report no collusion.

For a simultaneous game `s_ij = s_i = s_j = s`, so `γ` is symmetric, but `Γ(i;j) ≠ Γ(j;i)` because the subtracted maximum targets different agents. For sequential games `γ` is not symmetric and `γ(i;j)` must be estimated only over cases where `a_j` followed `a_i`.

### Estimator (reconstruction, not a quote)

Algorithm 1 sits in Appendix B, absent from the 10-page PMLR PDF; this is a faithful reconstruction of Equations 3, 4, 12 and 13.

```
INPUT : records R over n>=3 agents, entries (t, s_i, a_i); threshold a
OUTPUT: the colluding pair, or "no collusion detected"

for i in A:                                  # per-agent policy, Eq.12
    count N_i[s][a], N_i[s];  p_i[a|s] = N_i[s][a]/N_i[s]

for (i,j) in pairs(A):                       # joint policy, Eq.13
    for each round where both acted:
        if sequential and a_j not after a_i: skip
        count N_ij[s_i,s_j,a_i,a_j], N_ij[s_i,s_j]
    p_ij[a_i,a_j|s_i,s_j] = N_ij[...] / N_ij[s_i,s_j]

for (i,j) in pairs(A):                       # influence, Eq.3
    g = 0
    for (s_i,s_j) with count > 0:
        for (a_i,a_j) with joint count > 0:
            num = p_ij[a_i,a_j|s_i,s_j]
            den = p_i[a_i|s_i] * p_j[a_j|s_j]
            g += p(s_i,s_j) * num * log(num/den)
    gamma[i][j] = g

for (i,j) in pairs(A):                       # net influence, Eq.4
    Gamma[i][j] = gamma[i][j] - max_{k!=i,j} gamma[k][j]

C = [(i,j) : Gamma[i][j] >= a and Gamma[j][i] >= a]
return C[0] if len(C) == 1 else "no collusion detected"
```

Implementation choices the paper leaves open: add smoothing to `p_i` and `p_ij` or the log blows up on sparse states, and define a tie-break when more than one pair clears both thresholds.

## Key findings (with numbers)

- **RPS, manual assistant collusion.** Accuracy rises with collusion strength and sample size. `CP = 1.0` needs only **60 games** for 100% accuracy. `CP = 0.4`: 58.4% at 100 games, 96.2% at 300, 99.3% at 400, 100% from 700. `CP = 0.3`: 37.1% at 100, 71.0% at 300, 94.6% at 600, 100% at 1,000.
- **RPS, learned collusion.** Automatic DDQN collusion is easier: 81.5% at 100 games, 93.2% at 200, 98.1% at 300, 99.9% at 1,000, which the authors attribute to stronger dependence.
- **There is a detection floor.** `CP = 0.2` gives 24.3% at 1,000 games and 82.3% at 10,000; `CP = 0.1` yields about 8% and is not detectable at `α = 0.05` at any sample size tested.
- **Net influence tracks strength:** over 1,000 games it increases monotonically with `CP`, suggested as a possible continuous measure of collusion intensity.
- **Leduc.** Non-colluding combinations sit at `|Γ| ≤ 0.0032`. Colluding pairs: manual vs random 0.1133 / 0.1168; LP auto vs rule-based 0.6808 / 0.6797; HP auto vs rule-based 0.5504 / 0.5856; LP vs a learning-based opponent 0.6527 / 0.6150. Every colluding row clears 0.05 both ways, while the third agent's influence on a colluder is near zero or negative.
- **Payoff-blind detection.** The LP variant is trained to keep payoff near zero, collusion a payoff screen would miss, and is still detected: 98.8% at 120 games vs random, 100% vs rule-based.
- **Swiftness.** Manual association collusion needs 200 games (1,800 hands) for 93.6% vs random, while both automatic variants exceed 97% by 120 games.

## Mechanism / why it happens

A competitor's policy depends on the state; a colluder's depends on the state *and* the partner. Conditioning on the joint state removes the shared-state explanation, so residual dependence is strategic. The max over third parties is the crucial correction: in a 3-player game the honest pair also looks dependent because both respond to the same opponent, so raw mutual information flags everyone, while subtracting the strongest third-party influence isolates the exceptional pair.

## Limitations and threats to validity

Exactly two colluders; extending to more needs the co-information lattice, left as future work. `α` is a tuned hyper-parameter and the `CP = 0.1` failure shows a real floor rather than asymptotic consistency. Mixed strategies are required, since deterministic policies carry no conditional-MI signal. The worlds are tiny and 3-player with hand-crafted collusion, and no public collusive dataset exists, so ground truth is constructed by the authors. Counting tables grow as `|S|^2·|A|^2`, and free-text LLM traces would need discretised observations first.

## Relevance to the sprint

- **Q1.3:** a domain-independent detector needing no benchmark, no price model and no internals, only logs.
- **Q1.4:** this *is* the information-theoretic approach the sprint names, and the only method here that returns an *unknown* pair rather than scoring a known one.
- **Q2.3:** a concrete evidential standard, dependence in excess of the strongest third-party dependence, with a measured sample-complexity curve.

## Project hooks (48-hour sized)

1. **Implement plus scripted control.** Code the estimator above, generate 3-player RPS at `CP ∈ {0.1, 0.3, 0.6, 1.0}` and n ∈ {100, 300, 1,000}. Positive control is 100% accuracy at `CP = 1.0`, n = 60, with the expected collapse at `CP = 0.1`; metric is accuracy and the false-positive rate on no-collusion games as `α` sweeps 0.01-0.2.
2. **Head-to-head against correlation and a judge.** In a 4-agent LLM game with one seeded colluding pair (Colosseum Jira or the Agrawal double auction), rank all `C(n,2)` pairs by net influence, ordinary action correlation, and an LLM judge. Positive control is the scripted RPS pair; the deliverable is whether net influence beats correlation once third-party influence is controlled.
3. **Two-pair stress test.** Seed *two* colluding pairs in a 6-agent game and measure how often the exactly-one-pair rule fails. Metric is the fraction of runs where two or more pairs clear `α`, plus a proposed tie-break such as ranking by `min(Γ(i;j), Γ(j;i))`.

## What this paper does NOT test

Language-model agents; more than two colluders; teams larger than four; free-text or continuous observations; collusion invisible in the action distribution, such as coordination carried by tool calls or timing; colluders who know the detector and deliberately decorrelate; and any comparison against alternative detectors on the same data.

## Related notes in this folder

- `xu-2026-competitive-marginals-blindness.md`: the market-side cousin, pairwise residual correlation without the max-over-third-parties correction.
- `rose-2026-helios-activation-probes.md`: the white-box alternative that sees collusion actions hide.
- `nakamura-2026-colosseum-coalition-advantage.md`: realistic tasks and labelled coalitions to test this estimator on.

## Verification log

- Read: PMLR landing page (`https://proceedings.mlr.press/v180/bonjour22a.html`) and the full 10-page PDF via `https://r.jina.ai/https://proceedings.mlr.press/v180/bonjour22a/bonjour22a.pdf` (sections 1-7, Tables 1-5).
- Spot-checked: Equations 3, 4, 5, 12, 13; `α = 0.05`; the RPS accuracy table; 60 games at `CP = 1`; 24.3% / 82.3% at `CP = 0.2`; about 8% at `CP = 0.1`; the Leduc `Γ` values quoted; 1,800 and 360 hands; 10,000 training games.
- **Not confirmed as quoted:** the pseudocode is my reconstruction. Algorithm 1 is in Appendix B, which the PMLR PDF omits, and the paper does not specify smoothing, normalisation when episode lengths differ, or tie-breaking. The 4-player RPS results (Appendix C) are also unavailable here.
