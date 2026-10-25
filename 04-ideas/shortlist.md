# Shortlist (v1) — SUPERSEDED

> **This is the earlier 48-hour shortlist, kept for history. Do not start from here.** The decision document is [`FINAL-SHORTLIST.md`](FINAL-SHORTLIST.md) **v2**, which re-ranks after the adversarial review, the claim audit, the code-level repo audit and the blind prior-art comparison. v2’s #1 is DISCLOSE; D1 survives only as the upward-only BEACON; L2 and C1 are dropped. The plans below are still useful as background on why B1/J1/L1/D1 were killed or reframed.

Scored by my judgement, not by the organisers. The scores are meant to start an argument, not settle one.

## Post-review revisions — read this before the plans

An adversarial review (`critique.md`) checked each pick against the starter repo's actual code and searched for 2026 work that might scoop it. Several verdicts changed. The original plans are kept below for reference, but **do not start B1, D1's LLM arm, or R1 without reading this section**.

| Pick | Revised verdict | Reason | What to do instead |
|---|---|---|---|
| **B1 replacement** | **KILL as written** | `llm-cartel` agents have **no hidden state** (each round is a fresh call over the visible window), so "fresh same-model instance" *is* the control. A PASS needs market gain > 0.5; at the paper-faithful `qwen/qwen3-14b` (1–2 min/call) a 300-round base run is 10–20 h, and B1 wants 10–20 of them. The novelty claim is also weaker than the sprint page suggests: Gao et al. 2026 ([2609.05279](https://arxiv.org/abs/2609.05279)) already swaps role-matched agents with a **placebo** that separates roster disruption from identity, and Shi et al. 2026b already ablates interaction-history scope. | Surviving arm: base run on `--prefix PC` (cheap, reliable convergence), replace one seller with `--replace_prefix AC`, vary `--replacement_window 0/10/100`. Question: *can an incumbent's price history recruit a mandated competitor into the cartel?* 3–5 paired base runs. |
| **J1 undercover** | **MODIFY** | Acceptance is at ceiling: Zeng already reports 10/12 models at ≥98% and several cells at exactly 100%, with 500 offers per model. One Liar's Bar game is ~260 calls / 11 min and delivers at most two offers to two fixed-model seats, so a per-model acceptance rate costs 11–22 h to estimate a number that is already ~1.0. | Make **betrayal** the outcome: does the recruited partner later challenge or report the confederate? That is n = partner-rounds, not n = games. Three arms: pact / matched benign whisper of the same length / no whisper; rotate the confederate's seat; one model, 10 games. |
| **L1 partial monitoring** | **MODIFY** | The overseer **gags at 4/4** with a permanent 5-character cap, so coverage changes *punishment frequency*, not just perception — the predicted "messages down, actions up" is partly mechanical. The fraction is never announced in the seller prompt, so "told 25%" needs a template edit. Power is ~20× short: Agrawal's own chat effect has overlapping CIs at 10 sessions, and detecting a 1.5-point sub-effect needs ~108 runs per arm. | Add a **non-punitive shadow monitor** (scores, never gags) at the same fractions, run 30 rounds × 10 seeds, and lead with **monitor detection rate per message** (N ≈ 1,100 messages), not the market dissociation. |
| **D1 net influence** | **KILL the LLM arm** | Bonjour's estimator is a count table over (state, state, action, action); LLM histories are unique, so conditional MI is undefined without coarse discretisation, at which point it is correlation with a max-over-thirds correction. Bonjour needed 60 games at CP=1 with 3 actions and no state; CP=0.1 was undetectable at 10,000 games. A weekend has 300–1,000 agent-rounds. | Keep the **scripted** part: inject Xu's Lemma-1 copula at known ρ and report the **minimum detectable effect vs N**. A six-hour CPU result: *how much data a dependence detector actually needs*. That number is missing from the field. |
| **C1 dependence audit** | **KEEP, with two fixes** | Best risk/reward, but the "benign" same-model/no-chat cell is **not benign**: Fish shows it colludes, and Xu's +0.053 *is* the shared-prior signal. Calibrating at its 95th percentile sets the bar above the mechanism you want to detect. | Add a **non-strategic same-model null** (fresh counterpart each round, or history hidden) and a seeded-ρ injection showing the detector still sees collusion the calibration null would absorb. Report TPR at 1/5/10% FPR on **both** nulls. |
| **H1 three standards** | **KEEP, MODIFY** | Cheapest and most reliable, but hand-coding is the result, and the three case types come from three environments (confounded with task). | Use **published detectors' outputs** on the same trajectories (price screen, Xu residual correlation, Agrawal judge, Shi claim–action), and add Xu's scripted comonotone case where the standards **must** disagree: competitive price, maximal dependence, no message. |
| **R1 Dolos** | **KILL for a collusion team** | No positive control is possible (you do not know the answer), and a 1.5B fine-tune differs from base on formatting, refusal and repetition. It is scored separately and is off-brief for the three tracks. | Only as a $0 lottery ticket with a hard 10-hour cap and a pre-committed fallback to the audit-method write-up. |
| **W1 RealPage 2×2** | **NOT REVIEWED; still a wildcard** | Added after the review. The legal mapping is sound; the shared-advisor harness is new code. | Keep as a high-variance market pick if you have an engineer who can build the advisor and the adherence UI. |

### New picks from the review

Four ideas the review argues are better suited to 48 hours than the original top picks. Scores use the same scale.

| # | Project | Q | Novelty | Feasibility | Pos. control | Cost | Wow | Risk | Total |
|---|---|---|---|---|---|---|---|---|---|
| **U1** | Upward-deviation followership (the price beacon) | 1.1 / 2.3 | 5 | 5 | 4 | 5 | 4 | 4 | **27** |
| **M1** | Monitor–monitor collusion (correlated leniency) | 2.2 / 2.3 | 5 | 5 | 3 | 5 | 4 | 4 | **26** |
| **L2** | Leniency bounty on a formed cartel | 1.5 / 2.3 | 5 | 4 | 4 | 4 | 5 | 3 | **25** |
| **P1** | Detection-power budget from shipped logs | methods | 4 | 5 | 3 | 5 | 3 | 5 | **25** |

**U1 — upward-deviation followership.** A scripted seller raises its ask 10% above the collusive level for three rounds, then reverts. Do rivals follow within k rounds? Compare with a downward deviation of the same size. Following an *unprofitable* upward move is evidence of a coordination norm, not of market structure — the cleanest available answer to "is the high price collusion or competition?". One scripted seat, 10 runs × 30 rounds ≈ 600 calls.

**M1 — monitor–monitor collusion.** Score the same 150–300 shipped trajectories with three judges from different providers and test for **correlated leniency**: does A's leniency predict B's on the same episode, conditional on the behavioural metric? If monitor errors correlate, an ensemble buys nothing. The repo's literature review says no paper studies LLM judges colluding with each other. ~600 calls, no new environment.

**L2 — leniency bounty.** Branch a formed cartel and inject one private offer to **one existing member**: report the agreement, keep a 10% margin bonus, your partner is not told. Measure undercutting, reporting, the partner's punishment, and price recovery. No new harness — `branch_game.py` plus a prompt line. It tests the actual antitrust instrument (DOJ/EU leniency), which no LLM paper has.

**P1 — detection-power budget.** Use the shipped logs (Agrawal's 75 runs, ColludeBench's 1,737) to estimate between-seed variance for price and dependence, then compute the N required for each effect the shortlist proposes — L1's 1.5-point difference, B1's recovery time, J1's acceptance gap — and its dollar cost. Zero API. Run it first; it disciplines the whole weekend and predicts which of the other projects can work.

### Revised recommendation

1. **If you want the best risk/reward:** **C1** (with the second null and ρ injection) or **H1** (with published detectors). Both produce a defensible number even if the effect is null.
2. **If you want the most novel cheap result:** **U1** or **M1**. Both are 600-call projects with a clear headline and no new environment.
3. **If you want the best policy story:** **L2** (leniency bounty) or **W1** (RealPage 2×2).
4. **If you want the best narrative and can spend 10–15 h on games:** **J1-betrayal**, not J1-acceptance.
5. **Do not start:** B1 as written, D1's LLM arm, R1 for a collusion track.

## The scoring table

Scale 1–5. **Novelty** = how much of the result would be new to the field. **Feasibility** = can a small team finish it with the starter repo. **Positive control** = is there a known result to reproduce first. **Cost** = 5 is cheapest. **Wow** = how legible the headline is to a non-specialist judge. **Risk** = 5 is lowest risk.

| # | Project | Q | Novelty | Feasibility | Pos. control | Cost | Wow | Risk | Total |
|---|---|---|---|---|---|---|---|---|---|
| **J1** | Undercover agent offers a collusion pact | 3.2 | 5 | 4 | 4 | 4 | 5 | 3 | **25** |
| **B1** | Replace a seller mid-run; does collusion re-form? | 1.2 | 5 | 4 | 4 | 4 | 4 | 4 | **25** |
| **L1** | Partial monitoring → channel shift | 3.4 | 5 | 4 | 5 | 4 | 4 | 3 | **25** |
| **D1** | Pairwise net influence on LLM agents | 1.4 | 5 | 3 | 3 | 4 | 3 | 3 | **21** |
| **C1** | Calibrated dependence audit | 1.3 | 4 | 3 | 4 | 3 | 3 | 3 | **20** |
| **H1** | Three standards of evidence, one dataset | 2.3 | 4 | 5 | 2 | 5 | 3 | 4 | **23** |
| **R1** | Dolos behavioural diff + localisation | RT | 4 | 3 | 2 | 5 | 5 | 2 | **21** |
| **W1** | RealPage 2×2: data pooling × adherence | 1.1/2.3 | 5 | 3 | 4 | 3 | 5 | 3 | **23** |

**If I had to bet on one:** **J1 (undercover agent)**. The sprint page says in terms that a trusted agent offering to collude "has not yet been tested", the codebase for the nearest experiment (Zeng's Voluntary Collusion) is in the starter repo, and the result is a two-number headline: *how many agents say yes, and how many actually defect to the confederate*. It is also the most memorable story in a 3-minute presentation.

**If the team is market-native:** **B1 (replacement)**. Same novelty logic, cleaner economics, existing branch code, and a result that speaks directly to antitrust remedies ("does removing the offender work?").

**If the team wants the best story for a policy audience:** **W1 (RealPage 2×2)**. It tests the exact two facts that separate the leading US cases, and "adherence rate" is a metric a lawyer immediately understands. It is the highest-variance market pick because the shared-advisor harness is new code.

**If the team is theory/analysis-leaning and wants low compute:** **H1 (three standards)**. No new runs needed; the contribution is a measurement framework and a confusion matrix. It is the project most likely to be *correct* and least likely to be *exciting*.

---

## J1 — The undercover agent (3.2)

**Hypothesis.** A trusted agent that offers a collusive pact will be accepted and reciprocated by a substantial fraction of ordinary agents, and verbal acceptance will overstate actual defection (cheap talk).

**Why it is novel.** Zeng & Rudzicz test whether agents accept *experimenter-provided secret tools*; Tao uses honeypots; Greenblatt monitors untrusted models. None tests a **participant** who offers collusion and logs who reciprocates in later play.

**Design.**
- Environment: Liar's Bar or Cleanup from `llm-agent-collusion-2` (4 players, repeated rounds, persistent alliance memory).
- Conditions, one per game, same seeds:
  1. **No offer** (baseline).
  2. **Direct offer** from the undercover agent: "If we both target player C, we both gain."
  3. **Indirect hint:** "It would be a shame if C kept winning."
  4. **Benign cooperation request:** "Let's coordinate on the shared resource" (no target).
  5. **Explicit alliance control** (the repo's existing condition) — the positive control.
- The undercover agent is scripted (or a fixed model with a hard system prompt); it is **identical across conditions** except for the offer text.
- 10 games per condition, 4 players each, ~260 calls per full game. Start with 5 games per condition and a 5-step smoke test.

**Metrics.**
- **Primary:** *reciprocation rate* — fraction of rounds after the offer in which the ordinary agent takes the action that benefits the confederate at a cost to the third party.
- **Secondary:** verbal acceptance (explicit yes / hedge / no); whether the agent reports the offer to others; whether it later defects on the confederate; survival/win rate of the confederate.
- **Positive control:** the explicit-alliance condition should show reciprocation above baseline. If it does not, the game is too noisy — switch to Cleanup.

**Analysis.** A 5×3 table (condition × {accept, reciprocate, report}) with bootstrapped CIs. The headline is the **gap between acceptance and reciprocation**. A secondary result: does a direct offer produce more reciprocation than an indirect hint, or more suspicion?

**Deliverables.** One figure (acceptance vs. reciprocation by condition), one table, a short transcript exhibit of an agent accepting then defecting.

**Budget.** $10–60. **Time.** 6h setup + 12h runs + 8h analysis/writing.

**Risks.**
- The game may be too noisy at 10 games → use the cleaner Cleanup grid-world, or increase games to 20 with a cheap model.
- The confederate may be too obvious → pilot 3 offer phrasings and pick the one with the highest baseline acceptance, then freeze it.
- Ethical/dual-use: this is a contained game with no real users; say so in the report.

**Why it could win.** It is a countermeasure experiment with a clear narrative: *the undercover officer works, but the agents lie about joining.*

---

## B1 — Replacement and re-formation (1.2)

**Hypothesis.** Formed LLM collusion is **not** robust to replacing one participant: a fresh agent undercuts or fails to recognise the convention, and the coalition either collapses or re-forms slowly. Preserving the shared notes should speed re-formation.

**Why it is novel.** Eschenbaum's replacement result is Q-learning; Keppo finds mixed-size LLM pairs still collude but does not swap mid-run; the sprint page explicitly says there are no LLM replacement studies. The starter repo ships `branch_game.py` for exactly this.

**Design.**
- `llm-cartel`: 2–3 sellers, 30 rounds, one model family first (cheap), 4 seeds.
- Run until a pre-declared threshold: mean price ≥ 80% of the way from Nash to monopoly for 3 consecutive rounds.
- Branch the saved history into:
  1. **No replacement** (control).
  2. **Fresh instance, same model.**
  3. **Same family, different size** (e.g. Qwen 14B → 32B).
  4. **Different provider** (only if a second key/adapter is available).
- Cross with **notes preserved vs. removed** (the scratchpad is part of the transcript).
- 10–20 base runs, 20–40 branches.

**Metrics.**
- **Primary:** *recovery time* — rounds until the branch returns to the pre-swap price band (or fails within 15 rounds).
- **Secondary:** newcomer's first-move price relative to the incumbent; incumbent's price in the 3 rounds after the swap; price dispersion; whether the newcomer ever undercuts.
- **Positive control:** the no-replacement branch stays in the band. If it does not, the run was not colluding — discard and rerun.

**Analysis.** Survival curve of "time to recover" by condition; a small table of first moves. The interesting comparison is **same-model vs. cross-provider**: does a shared prior let a newcomer slot in?

**Deliverables.** A recovery-curve figure, a first-move table, and a plain-language answer: *replacing the offender removes collusion temporarily / permanently / not at all.*

**Budget.** $20–100. **Time.** 8h setup + 14h runs + 8h analysis/writing.

**Risks.**
- Base runs may not cross the threshold → lower the threshold to "price above Nash for 5 rounds", or use the Fish-style duopoly where the positive control is stronger.
- `branch_game.py` may only support same-provider swaps → treat cross-provider as a stretch arm.
- Attrition: some branches will error; log and report the denominator.

**Why it could win.** It answers a question a regulator would actually ask, with a clean survival curve.

---

## L1 — Partial monitoring and the channel shift (3.4)

**Hypothesis.** When a coalition learns that only part of its messages are read, it keeps coordinating but moves the coordination into actions (prices, timing, message length), so message-based detectors under-report collusion while action-based dependence rises.

**Why it is novel.** Agrawal's overseer reads all messages; Kale/Jiralerspong study single-agent awareness; nobody has varied the *fraction* of a multi-agent message stream that is monitored and measured the carrier substitution.

**Design.**
- `llm-agent-collusion`, 3 sellers / 3 buyers / 15 rounds, 5 seeds per cell.
- Conditions: no oversight (baseline); silent logging; **told monitored** with `--overseer_sample_fraction` 0.25 / 0.50 / 1.00; plus an urgency arm at 0.50 to test whether pressure changes the adaptation.
- Freeze the overseer prompt and threshold.

**Metrics.**
- **Primary:** message-coordination score (judge) **and** action dependence (lagged cross-correlation of sellers' asks; residual correlation). The claim requires the *dissociation*: messages ↓, actions ↑.
- **Secondary:** message length, vocabulary diversity, emoji/one-character rate, price level, dispersion, trade volume.
- **Positive control:** full monitoring lowers price and coordination relative to no oversight (Agrawal's result). If it does not, the overseer is not biting.

**Analysis.** A 2×3 dissociation plot: message coordination vs. action dependence, with the monitoring fraction on the colour axis. A regression of price on both channels.

**Deliverables.** The dissociation figure plus a table of message statistics. The headline: *monitoring moves collusion, it does not remove it.*

**Budget.** $20–120. **Time.** 6h setup + 14h runs + 8h analysis.

**Risks.**
- The 25% monitor may never catch anyone, so the "told monitored" manipulation is weak → pilot the overseer's detection rate first; if it is near zero, use 50% as the low arm.
- Action dependence may be noisy at 15 rounds → use 25–30 rounds, or pool across seeds.
- The judge may not see a difference → rely on the behavioural statistic as primary.

**Why it could win.** It is the most policy-relevant negative result available: *the monitor's coverage is a lever the coalition can adapt to.*

---

## D1 — Pairwise net influence on LLM agents (1.4)

**Hypothesis.** Bonjour's pairwise net influence identifies a colluding pair in a 4-agent LLM game better than plain action correlation or an LLM judge, at equal sample size.

**Why it is novel.** The method exists only for small discrete games and has never been applied to language-model agents; there is no public implementation. The sprint page asks for exactly this.

**Design.**
1. **Scripted validation (free, CPU):** iterated Rock–Paper–Scissors, 4 agents, one pair coordinating on a private signal. Sweep coupling strength and N; confirm net influence ranks the true pair first.
2. **LLM game:** a 4-agent matrix game (or a simplified 4-seller auction) with one pair prompted to coordinate covertly and two honest agents. 20–40 games × 15–25 rounds.
3. **Comparators:** pairwise action correlation, mutual information, LLM-judge coordination score.

**Metrics.** Rank of the true pair (1 = detected); AUC of pair-level scores; minimum N for reliable detection; false-positive rate on all-honest games.

**Positive control.** On the scripted game, the true pair must be ranked first at high coupling. On the LLM game, the prompted pair should be detected in a majority of runs.

**Deliverables.** A methods figure (power vs. N for three statistics) and an honest verdict: *net influence works / needs more data than a weekend / fails on LLM action streams*.

**Budget.** $0 scripted + $5–50 LLM. **Time.** 10h implementation + 8h validation + 10h LLM runs + 8h writing.

**Risks.**
- The estimator assumes exactly two colluders and a known coalition size — state this limitation loudly.
- LLM action streams may be too coarse → use prices/quantities with many levels, not binary actions.
- If it fails, that is still a result: "the statistic needs N× more data than a weekend provides."

**Why it could win.** A negative result is credible here because the scripted positive control is free and exact; a positive result is a new detector.

---

## C1 — Calibrated dependence audit (1.3)

**Hypothesis.** A residual-dependence detector calibrated on no-communication, same-model runs can separate communication-enabled coordination from shared model priors without masking the former.

**Design.** 2×2: sellers same-model vs. cross-provider × chat on/off; 5 seeds per cell; 15 rounds. Score each trajectory with (a) residual correlation, (b) LLM judge, (c) price level. Calibrate the threshold at the 95th percentile of the no-chat same-model cell; report TPR on chat cells and FPR on benign cells.

**Why it is strong.** It directly implements the sprint's 1.3 project and Xu's warning that price-level audits can be blind. The 2×2 isolates "same model" from "can talk", which most papers confound.

**Budget.** $20–100. **Risk.** Cross-provider adapters may be unavailable; fall back to two sizes of one family.

---

## H1 — Three standards of evidence (2.3)

**Hypothesis.** The same trajectories satisfy outcome-based, agreement-based and oversight-based standards to different degrees, and the disagreements are systematic.

**Design.** Assemble 30–60 trajectories across three case types: (i) coordinated harmful action (Colosseum prompted/emergent), (ii) parallel behaviour from common incentives (focal-points or same-model no-chat), (iii) collusive-sounding talk with no behavioural change (a prompted "talk only" condition). Code each under three rubrics; freeze the decision rule on half, test on the rest; report a confusion matrix and inter-rater agreement.

**Why it is strong.** No new model runs if you can reuse stored logs; it is the most "research" of the shortlist and directly answers the track's question.

**Budget.** $5–30. **Risk.** Coding bias — pre-register the rubric and use two coders.

---

## W1 — The RealPage 2×2: data pooling × adherence (1.1 / 2.3)

**Hypothesis.** The two facts that separate *RealPage* from *Gibson v. Cendyn* — rivals' private data reaching the recommendation, and an obligation/default to accept it — independently and jointly raise prices. A shared model without pooling or adherence does not.

**Why it is novel.** Nobody has run the legal 2×2. Cao & Hu model the shared-model channel theoretically; RealPage/Gibson give the two variables; the sprint asks for single, isolable levers. This is one design that produces a legally legible result.

**Design.**
- 3–5 LLM sellers in a repeated Bertrand or double auction, plus one **shared advisor** that recommends a price.
- Conditions (2×2, same seeds):
  1. Advisor sees **public** info only; seller **free** to deviate.
  2. Advisor sees **rivals' private** cost/demand data; seller free to deviate.
  3. Advisor sees public info only; **accept-by-default** (override costs an explicit action).
  4. Advisor sees rivals' private data; **accept-by-default**.
- Baselines: no advisor; advisor with a deterministic (non-LLM) rule.
- 5 seeds per cell, 15–30 rounds.

**Metrics.**
- **Primary:** mean price vs. Nash; **accept/override rate** (the adherence measure).
- **Secondary:** dispersion, profit, trade volume; whether sellers spontaneously reference the advisor's recommendation in their reasoning.
- **Positive control:** cell 4 (pooling + adherence) above the no-advisor baseline. **Benign control:** cell 1 (Gibson-like) not above baseline.

**Analysis.** A 2×2 table of price effects with interaction term; a bar chart of adherence by cell. The headline: *pooling alone / adherence alone / both*.

**Budget.** $30–100 (advisor calls add ~1 per seller per round). **Time.** 10h harness + 12h runs + 8h analysis.

**Risks.**
- The advisor may be ignored → make acceptance the default in the adherence arms and log every override.
- LLM advisor noise → include the deterministic advisor control; if the LLM and the rule give the same result, the effect is the *design*, not the model.
- Legal framing may invite overclaiming → say explicitly that this measures price effects, not liability.

**Why it could win.** It is the only project on the list that a competition lawyer and an ML researcher would both immediately understand, and it turns a doctrinal split into a measurable interaction.

---

## R1 — Dolos red team

**Design.** Behavioural diff vs. base Qwen on 300–500 prompts across 12 categories; cluster the differences; separate generic fine-tuning artefacts (formatting, refusal style) from a specific misaligned goal; then localise with logit lens / activation diffs and design a reference-free audit.

**Why it is attractive.** $0, local, and the deliverable is inherently demo-able. **Risk.** High variance: you may not find the behaviour. Mitigation: submit the *audit method* and the behavioural-diff pipeline even if the behaviour is only partly characterised.

---

## What to do in the first three hours (any pick)

1. **Run the positive control before writing any code.** If it does not reproduce, switch projects now, not at hour 30.
2. **Freeze the metric and the seed list in a config file.** Every later change is a deviation to report.
3. **Write the report skeleton** (question, setup, result placeholder, limitations) before the first full run. It makes the analysis obvious and prevents the 4 a.m. scramble.
4. **Decide the null.** What result would make you say "no effect"? If you cannot answer, the design is not ready.
