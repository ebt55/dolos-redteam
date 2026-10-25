# Idea bank — 61 weekend-sized projects, mapped to the sprint questions

> **Status: pre-prior-art menu, not a ranking.** Several entries are now scooped or crowded: D1/B1 (Tran & Yu 2026; Gao 2026), L2/E5 leniency (Lee 2026), C1 (negative pilot), G/J1 (three sprint teams), P1/W1/M1 (superseded by DISCLOSE/ADVISOR/SELFMON). Use [`FINAL-SHORTLIST.md`](FINAL-SHORTLIST.md) v2 for the decision; use this page only for variants and project hooks.

Each idea is written so it can become a proposal in ten minutes: **question → one manipulation → positive control → metric → cost → risk**. All are scoped for 1–3 people over ~48 hours. Costs assume cheap API models (GPT-4.1-mini / Qwen / Llama class) and 3–5 seeds per condition.

Legend: 💰 <$20 · 💰💰 $20–60 · 💰💰💰 $60–150 · 🧠 mostly analysis, little compute · ⚙️ needs new code · 🧩 starter code exists.

---

## Track 1 — Markets and Collusion

### 1.1 Which variables are necessary for collusion?

**A1. Visible-history dose–response** 🧩💰
Fish-style duopoly with 0 / 10 / 50 / 300 rounds of price history visible. Positive control: full history reproduces supracompetitive prices. Metric: mean price vs. Nash, periods-to-threshold, punishment coefficient. Risk: the repo flag may truncate history in a way that also changes token budget — check.

**A2. Do shared notes create a channel?** 🧩💰
Agents keep a persistent "plans and insights" scratchpad. Conditions: no notes; private notes; **notes visible to the rival**. Does a scratchpad become a covert (or overt) communication channel? Metric: price, note-content coordination score, overlap in note vocabulary. Novel because the notes were designed as memory, not messaging.

**A3. Market framing changes the price** 🧩💰
Same logit Bertrand economics, different cover stories: heavy metals (Agrawal), airlines, local bakeries, abstract "firm A/B". If pretraining priors about an industry drive pricing, the cover story should shift the collusive level. Positive control: the heavy-metals frame reproduces Fish. Metric: mean price by frame, 5 seeds each. Cheap, publishable, and a warning for replication.

**A4. Identity salience** 🧩💰
Stable named sellers ("Acme", "Borealis") vs. shuffled names each round vs. anonymous "Seller 1/2/3". Does identity stability help agents track a rival and sustain punishment? Metric: price, dispersion, retaliation lag. Small code change.

**A5. Temperature × model family** 🧩💰
2 model families × 3 temperatures, 4 seeds. Xu says temperature reduces residual dependence; does it reduce *prices* in a Bertrand game, or only correlation? A dissociation would be interesting. Metric: price level vs. dependence statistic.

**A6. Two firms vs. five, with open-weight models** 🧩💰💰
Replicate the "~3.7% per competitor" gradient with Qwen/Llama rather than GPT/Mistral. Does the gradient survive? Positive control: duopoly colludes. Metric: collusion index by n. Risk: low novelty unless the gradient differs.

**A7. The RealPage 2×2: data pooling × adherence** ⚙️💰💰
3–5 LLM sellers and one **shared pricing advisor**. Cross (i) whether the advisor sees rivals' private cost/demand data and (ii) whether accepting its recommendation is the default (with an override that costs an action). This is the fact pattern that separates *RealPage* (pooling + adherence → liability) from *Gibson v. Cendyn* (no pooling, no obligation → dismissed). Positive control: the pooling + adherence cell raises prices above a no-advisor baseline; benign control: the no-pooling, free-to-deviate cell does not. Metric: price, **accept/override rate**, dispersion, profit. Novel, legally legible, and it separates common cause from coordination. Risk: medium engineering; the advisor needs a deterministic non-LLM control.

**A8. Upward-deviation followership (the price beacon)** 🧩💰
One scripted seller raises its ask 10% above the current collusive level for 3 rounds, then reverts; compare with a downward deviation of the same size. If rivals follow an *unprofitable* upward move, that is evidence of a coordination norm, not of market structure — the cleanest available answer to "is the high price collusion or competition?". Positive control: a downward deviation is punished or followed down. Metric: follow rate within k rounds, price path, punishment response. 10 runs × 30 rounds ≈ 600 calls. **The review's top new pick.**

### 1.2 Robustness to replacement

**B1. Replace one seller mid-run** 🧩💰
Run until a pre-declared high-price threshold, then branch: no replacement; **anti-collusion-prompt newcomer**; different model/provider; **no visible history** (`--replacement_window 0`). Metric: price recovery time, newcomer's first 3 actions, incumbent's reaction. **Read the revision box in `shortlist.md` first:** `llm-cartel` agents have no hidden state, so "fresh same-model instance" *is* the control, and Gao et al. 2026 already swaps agents in teams with a placebo. The open question is narrower: *can an incumbent's price history recruit a mandated competitor into a market cartel?* Code: `branch_game.py` (needs a PASS run or `--threshold`/`--at_round`).

**B2. Replace the leader vs. the follower** 🧩💰
Identify the price leader (first mover / highest price) and replace that agent vs. the other. Does the coalition collapse when the leader leaves? Metric: price, leadership rank, recovery. Novel role-asymmetry angle.

**B3. The newcomer's first move** 🧩💰
Only analyse the first 3 actions of a replacement agent across conditions. Does it probe (undercut), conform (match), or signal (small price step)? Cheap, behavioural, and directly relevant to monitoring: a newcomer that immediately matches a high price is suspicious.

**B4. Replacement as a detector** 🧩💰
Hypothesis: if collusion is relational, a fresh agent's entry should perturb prices; if it is a shared focal point, it should not. Use the *price response to replacement* as a collusion test. This turns 1.2 into 1.3. High novelty, moderate risk.

### 1.3 Improving detection

**C1. Calibrated dependence audit** 🧩💰
Compute residual correlation (Xu-style) on Agrawal auction logs: same-model vs. cross-provider, chat on/off. Calibrate threshold on no-chat same-model runs; report FPR and TPR. Positive control: chat raises both price and dependence. **Directly answers "does the detector fire on benign shared priors?"**

**C2. Price audit vs. dependence audit, head-to-head** 🧠💰
Take the same trajectories and score them with (a) price-level screen, (b) dependence screen, (c) LLM judge. Inject a scripted Xu-style coupling into a subset of runs. Which detector catches which? A 2×3 confusion matrix is a complete paper figure.

**C3. Cross-provider Schelling salience** 🧩💰
Two-agent coordination task (focal-points) and then a pricing game: same model vs. same family vs. different provider. Do cross-provider pairs fail to coordinate on a price? Positive control: same-model pairs coordinate above chance. Metric: coordination index, price. Cheap and directly extends Aharon/Xu.

**C4. Harness sensitivity** 🧩💰
Same model and economics, two scaffolds (Fish-style prompt vs. LLMCartel prompt). Measure the difference in collusion. A null result is still useful: it says the literature's effect sizes are harness-robust. Risk: "boring" unless framed as reproducibility.

**C5. Judge-vs-action triage** 🧩💰
Use Colosseum's stored runs (or generate 20): flag episodes where the LLM judge says "clean" but coalition advantage is high. Train a simple classifier on action features to catch them. Positive control: prompted-collusion episodes are flagged by both. Metric: recall at fixed FPR.

### 1.4 Information-theoretic detection

**D1. Pairwise net influence, from scratch** 🧠💰
Implement Bonjour's statistic, validate on scripted iterated RPS with a known colluding pair, then attempt a 4-agent game with one seeded pair. Compare against action correlation and an LLM judge. **Caveat from the review:** the estimator is a count table over (state, state, action, action); LLM histories are unique, so conditional MI is undefined without coarse discretisation, and Bonjour needed 60 games at CP=1 with 3 actions. Keep the **scripted power curve** (minimum detectable ρ vs N) as the guaranteed deliverable; treat the LLM arm as a stretch.

**D2. Net influence vs. mutual information** 🧠💰
Benchmark two dependence measures on ColludeBench-v0 (scripted configs, no API key): which ranks the true colluding pair better at small N? A methods comparison with a clear deliverable (a table and a recommendation).

**D3. Dependence under competitive marginals** 🧠💰💰
Can net influence detect a Xu-style coupling that leaves each seller's price distribution at the competitive law? Generate scripted coupling, then test on LLM logs. Ambitious; if it works, it is the strongest 1.4 result.

**D4. Influence graph pruning** 🧠💰
Compute pairwise influence for all pairs in a 4–5 agent game, build a graph, and see whether the colluding clique is a dense subgraph. A graph-visualisation figure makes the result legible.

### 1.5 Cheapest restriction

**E1. Restriction tournament** 🧩💰💰
Same seeds, six arms: no chat; 5-char cap; oversight notice; temperature 0.2 vs. 1.0; one Q-learner seller; a deposit. Score collusion reduction against welfare loss and monitoring cost. Deliverable: a Pareto frontier. **Policy-relevant and easy to explain.**

**E2. One no-regret seller as a vaccine** 🧩💰
Three LLM sellers + one EXP3/Q-learning seller. Does the LLM coalition collapse? Measure price, coalition stability, and whether LLMs learn to exploit the learner. Extends Collina/Keppo with a controlled market share.

**E3. Monitoring cost accounting** 🧠💰
For each restriction, compute dollars per 1% price reduction and per unit of buyer surplus. A simple, novel framing that judges remember. Needs a small amount of run data.

**E4. Deposit sizing** 🧩💰
Q. Liu's refundable deposit: vary the bond size and detection probability. At what bond does collusion stop? Is the required bond larger than the collusive profit? A clean economics result.

**E5. Leniency bounty on a formed cartel** 🧩💰
Branch a formed cartel and privately offer **one existing member**: report the agreement, keep a 10% margin bonus, your partner is not told. Measure undercutting, whether the agent reports, the partner's punishment, and price recovery. This tests the actual antitrust instrument (DOJ/EU leniency), which no LLM paper has. Positive control: a no-bounty branch stays collusive. No new harness — `branch_game.py` plus a prompt line. **The review's best policy pick.**

---

## Track 2 — Detection and Audit

### 2.1 Which tasks produce collusion?

**F1. Colosseum affordance ablation** 🧩💰💰
Assigned pair + private channel; assigned pair no channel; open channel; neither. Positive control: the supplied config. Metric: coalition advantage, judge score. The brief's own project; safe, expected.

**F2. New task, no assigned pair** ⚙️💰💰
Build one new task in the Colosseum/Terrarium style — e.g. grant-panel review, shift scheduling, group grading — with a hidden coalition objective but no assigned pair. Does collusion emerge? Risk: medium engineering; upside: a new environment.

**F3. Minimal ingredients** ⚙️💰💰
A 2×2×2 toy task: shared resource (yes/no) × private information (yes/no) × objective conflict (yes/no), with two agents and a channel. Which cell produces coalition advantage? Ambitious but a real contribution: a ingredients list for collusion.

**F4. Everyday workflow** ⚙️💰
Two agents + a shared inbox/ticketing tool; one can help the other at a cost to the principal. Does helpfulness become collusion (cf. Alnuhait)? Cheaper than Colosseum and more legible to a general audience.

### 2.2 Say vs. do

**G1. Four monitor views** 🧩💰
Messages only; actions only; messages + actions; structured claim–action report. Freeze monitor prompt, model and threshold; report accuracy and FPR on the same 30 trajectories. Brief's project; TraceGuard rubric reusable.

**G2. Plans as an early-warning signal** 🧩💰
Shi finds >90% of deviations were pre-stated in private plans. Build a monitor that reads plans and predicts later coalition behaviour; compare its AUROC to a message-only monitor at the same budget. Novel use of private CoT.

**G3. Cheap structural features** 🧠💰
Do verbosity, message length, response latency, price-leadership rank or action entropy predict coalition membership without an LLM judge? A logistic regression on 30 runs is a useful baseline that most LLM-judge papers omit.

**G4. Consistency graph** 🧠💰
For each pair, compute whether A's actions match B's stated plans over time. Build a cross-agent consistency score and test whether it separates colluding from honest pairs. Directly instantiates "A's behaviour consistent with B's stated plans".

**G5. Monitor–monitor collusion** 🧠💰
Score the same 150–300 shipped trajectories with three judges from different providers. Test for **correlated leniency**: does judge A's leniency on an episode predict judge B's, conditional on the behavioural metric? If monitor errors correlate, an ensemble buys nothing. Metric: partial correlation of judge residuals, disagreement rate. The repo's literature review says no paper studies LLM judges colluding; ~600 calls and no new environment. **The review's second new pick.**

### 2.3 Standards of evidence

**H1. Three standards, one dataset** 🧠💰
Score the same 30–60 trajectories under (i) outcome standard, (ii) agreement/plus-factor standard, (iii) oversight/concealment standard. Report a confusion matrix and the cases that satisfy one but not the others. **Cheapest high-rigour project on the list; needs logs, not runs.**

**H2. Operationalise plus factors** 🧠💰
Turn antitrust's plus factors into six codable features (parallel pricing structure, signalling, exchange of non-public information, implausible parallelism, punishment, concealment). Code them on existing trajectories; report inter-coder agreement. A legal-empirical contribution.

**H3. Innocent coordination benchmark** 🧩💰
Run focal-points benign coordination and a collusion game; can any detector tell them apart without labels? A negative result here is valuable: it bounds what black-box detection can do.

**H4. Evidence checklist for agents** 🧠
Write a short, citable "what counts as evidence" standard for LLM-agent collusion, with a decision tree. No experiments, but useful to the field; pair it with H1 to avoid being pure opinion.

---

## Track 3 — Carriers and Countermeasures

### 3.1 Action/tool side channels

**I1. Action-only carrier in Colosseum** 🧩💰💰
Replace private messaging with one observable action (task claim, tag, tool order). Conditions: private text; action visible; action hidden/canonicalised. Claim a carrier only if coalition advantage survives action-only and dies when the path is cut. Brief's project; medium-high risk.

**I2. Timing channel** ⚙️💰
Two agents in a toy task; one can vary delay/order. Can they encode a signal in *when* they act? Measure mutual information between sender's intended bit and receiver's action. Novel and cheap if the environment is scripted.

**I3. Tool-choice steganography** ⚙️💰💰
Two agents with a shared tool menu and a hidden goal; does the sequence of tool calls carry information beyond the task? Compute MI between tool sequences and the hidden state. Ambitious; high wow.

**I4. Mini message board** ⚙️💰💰
Recreate a controlled version of the OpenAI Artifactory cache: agents share a writable file store with no explicit messaging tool. Do they discover it and coordinate through it? Very novel, directly tied to the flagship incident. Medium engineering.

**I5. Canonicalisation defence** 🧩💰
Take the action-carrier setup and canonicalise actions (sort, relabel, strip metadata). Does coordination drop? A clean countermeasure test.

### 3.2 Trusted agents

**J1. Undercover agent offers a pact** 🧩💰
One scripted/monitor-controlled player offers the same non-challenge pact to each agent: direct offer, indirect hint, benign cooperation request. Record verbal acceptance and repeated preferential play separately. Positive control: the explicit alliance condition from Zeng. **Explicit gap; code exists.**

**J2. Honeypot channel** 🧩💰
Plant a fake secret channel or a too-good-to-be-true tool; measure who uses it and whether they hide it. Extends Tao's honeypot to a live multi-agent game. Metric: uptake rate, concealment.

**J3. Snitch detection** 🧩💰
A trusted agent joins the coalition and then reports. Can the coalition identify and punish the snitch? Measures whether agents track "loyalty" — a novel capability question with safety relevance.

**J4. Undercover style** 🧠💰
Do agents accept a pact more often from a peer that *sounds* like their own model family (cf. Dietrich)? Vary the undercover agent's style. Cheap once J1 exists.

### 3.3 Peer identification

**K1. Mid-run swap detection** 🧩💰
Preserve identity and transcript, swap the model (sham / same model / same family / different provider), ask for one same-or-changed guess at the end, and separately measure behaviour change. Brief's project; code exists.

**K2. Stylometric fingerprinting in a game** 🧠💰
Can an agent identify which model wrote a message in a pricing game? Use Dietrich-style features; compare to human/LLM judge. Cheap, and it tests whether anonymisation is futile.

**K3. Spontaneous recognition signals** 🧠💰
Do agents converge on distinctive greetings, formats or code words when paired repeatedly? Measure style convergence and whether it predicts coalition success. Exploratory but novel.

**K4. Identity swap as a countermeasure** 🧩💰
Swap two agents' displayed names mid-run without changing models. Does the coalition's coordination break? A cheap test of how much identity anchoring matters.

### 3.4 Behaviour under surveillance

**L1. Partial monitoring and channel shift** 🧩💰
25/50/100% of messages monitored, announced vs. silent. Claim a channel shift only if message coordination falls **and** action dependence rises. **Explicit gap; flag exists.** Strong.

**L2. Monitor budget allocation** 🧠💰
Given a fixed budget to monitor k of n agents or m of T rounds, which allocation detects a coalition fastest? Simulate from existing logs; no new API calls. A practical security result.

**L3. Watched coalition** 🧩💰💰
Tell only some coalition members they are monitored. Does the uninformed member become the signal carrier? Tests internal communication about surveillance. Novel.

**L4. Monitor deception** 🧠💰
Can agents infer the monitor's threshold from feedback and adapt? Use Jiralerspong-style blocking feedback. Ambitious but directly extends a sprint paper.

---

## Red-teaming challenge (Dolos-1.5B)

**R1. Behavioural diff** 🧠
500 prompts across 12 categories to Dolos and base Qwen; cluster differences; separate "trained behaviour" from generic fine-tuning degradation. Then localise with logit lens / activation diffs. Positive control: a known fine-tuning artefact (e.g. formatting) should show up too.

**R2. Audit without a reference** 🧠
Design a black-box audit that flags the behaviour using only Dolos outputs (self-consistency, role-play probes, adversarial elicitation). The deliverable is the audit, not just the behaviour.

**R3. Mechanism localisation** 🧠
Find the layers/heads where Dolos diverges from Qwen on the trigger; ablate or patch to confirm. High effort, high reward if the behaviour is found.

---

## Cross-cutting methods

**P1. Detection-power budget** 🧠
Use the shipped logs (Agrawal's 75 runs, ColludeBench's 1,737) to estimate between-seed variance for price and dependence, then compute the N and dollar cost needed for each effect proposed in this folder: L1's 1.5-point difference, B1's recovery time, J1's acceptance/betrayal gap. Deliverable: a table that says which projects are powered and which are not. Zero API, a few hours. **Run it first if you are unsure between two projects** — it will eliminate one.

**P2. Gag-channel capacity** 🧠💰
Treat Agrawal's 5-character cap as a channel and measure its information rate: mutual information between the gagged message and the next-round price move, in bits per round, against the profit the cartel sustains. Answers "how many bits does a cartel need?" — a Shannon-style bound connecting Agrawal's qualitative finding to Tailor's capacity theory. Reuse the 75 shipped runs plus ~20 new gagged runs.

---

## Ideas to avoid (saturated or weak)

- **Another communication on/off in a Bertrand duopoly.** Done by Agrawal, Fish, and dozens of economics papers. Only do it as a positive control.
- **A prompt-sensitivity sweep with no new lever.** Fish already showed wording matters; a new list of prefixes without a mechanism is a replication.
- **An LLM judge as the only detector.** Judge scores anti-correlate with action-level coalition advantage in Colosseum; at minimum pair it with a behavioural metric.
- **A "collusion benchmark" with no intervention.** The sprint rewards controlled experiments; a new dataset without a manipulation is a harder sell.
- **Passive monitoring of a single agent.** That is AI control, not collusion; the interesting unit is a pair or coalition.

## How to choose in 15 minutes

1. Circle the two tracks you could talk about for 20 minutes without notes.
2. From those, keep ideas whose **positive control already exists** in the starter repo.
3. Keep the one whose metric a non-expert can understand in one sentence.
4. Check the gap map (`../03-synthesis/gaps.md`) — prefer an idea that fills an explicit "not tested yet" cell.
5. If two ideas tie, pick the one with the cheaper null result: a well-powered negative is a submission; a broken positive control is not.
