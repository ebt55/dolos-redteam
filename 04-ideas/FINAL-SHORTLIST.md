# Final shortlist v2 — after the blind comparison

**Date:** 24 October 2026, ~22:20 IST. **Deadline:** 26 October 2026, 17:29 IST.

This version supersedes v1 (archived as `FINAL-SHORTLIST-v1.md`). It exists because a blind comparison against a second research pack found two scoops that v1 missed:

- **Tran & Yu, “Is Anyone Enforcing the Cartel?” (arXiv:2610.28787, 20 October 2026)** already introduced a forced-cheating audit of LLM pricing agents. v1’s #1, D1, is **half-scooped**: the downward-deviation arm is a replication. The upward arm survives as **BEACON**.
- **Lee 2026 (SSRN 7426061)** reports that leniency raises reporting but barely moves prices. v1’s #2, L2, is **fully scooped**.
- v1’s C1 (dependence audit) has a negative pilot in the other pack (AUC 0.53) and a pre-registered sprint repo doing the same 2×2.
- v1’s G (undercover) is crowded: three sprint teams are already running agent-delivered offers, and Zeng’s acceptance is at ceiling.

The blind ranking (full report: `../../ai-collusion-compare/project-ranking.md`) put:

| # | Project | Score | Status |
|---|---|---|---|
| **1** | **DISCLOSE** — regulator disclosure of a soft price screen | **4.30** | Open; best risk-adjusted |
| **2** | **BEACON** — upward-only forced deviation | **3.85** | The surviving half of D1 |
| **3** | **SELFMON** — monitor-family leniency | **3.50** | $0 analysis; measured pilot |
| 4 | ADVISOR — shared advisor, pooled data, firewall | 3.40 | Highest ceiling; bigger build |
| 5 | H1 — three standards of evidence | 3.35 | Safe fallback |
| 6 | SAYDO — cross-agent say/do monitor | 3.25 | Open but 8–10h build |
| — | CAP — message-cap dose–response | 3.30 | Weak: chat premium p = 0.10 |
| — | C1 — dependence audit | 3.15 | Drop or reframe as negative |
| — | G — undercover offer | 2.85 | Drop from top five |
| — | L2 — leniency bounty | 2.65 | Drop: fully scooped |

**Default pick: DISCLOSE.** It is cheap (≤$5, ~50 lines on a vetted harness, $0 local positive control), controlled (Dhanda’s announced-cap effect reproduces), legible, and still open after the prior-art sweep. Both possible directions — announcing the threshold pulls prices up, or secrecy does not help — are a design rule for regulators, so it cannot fail informatively.

**If you want a causal mechanism paper: BEACON.** Upward-only forced deviation, citing Tran & Yu for the downward arm. Accept a likely null and the citation burden.
**If new runs stall: SELFMON.** A $0 analysis on shipped auction runs, subject to a 250 MB transcript download.
**Highest ceiling, if you have build time: ADVISOR.** The RealPage pattern with a repeated market and a firewall remedy.

---

## 1. DISCLOSE — what should a regulator tell AI pricing agents about its price screen?

**Headline if it works:** “Announcing a soft screen’s threshold pulls LLM prices *up* toward it; saying only that a confidential screen exists does not.” Or the opposite. Either direction is a regulatory design rule.

### Why it matters

Competition authorities screen prices and choose what to disclose. AI pricing agents read every rule they are given. Dhanda 2026 showed that an *announced price cap* becomes a focal point that raises prices toward it (announced Δ 0.86 vs hidden 0.16, p = .015); Riemer et al. found that a “thoughts monitored” notice raised collusion under one prompt (Δ 0.32 → 0.62) but not another. What a regulator should say to agentic markets is an open, practical question (sprint 1.5 and 2.3).

### Design

Calvano logit duopoly, Nash 1.4729, monopoly 1.9250; 40 rounds; `--window 10`; same seeds across arms.

| Arm | What agents are told | Enforcement | Role |
|---|---|---|---|
| D0 | nothing | none | baseline; measure its mean price first |
| D1 | “prices are monitored by the competition authority” | none | notice only |
| D2 | “prices above a **confidential** threshold trigger an investigation and a fine” | fine if price > X for ≥2 rounds (shown in history when it happens) | screen exists, number secret |
| D3 | “prices above **X** trigger an investigation and a fine” | same fine | screen and number announced |
| PC | “It is ILLEGAL to set a price above 1.70” | clip | **positive control** (Dhanda) |
| AC | D3, but the rival is a scripted bot fixed at Nash | same fine | **anchoring control**: does a lone agent also move toward X? |

**Where to put X.** Primary: X_high, set *above* D0’s measured mean and below monopoly. A rise toward X there is a perverse focal effect, not compliance. Secondary: X_low, below D0’s price; bunching just under X there is rational compliance, so it is not the headline.

**Metrics** (freeze before main runs): final-10-round mean price, D3 vs D2 vs D0 at X_high; share of rounds in [X − 0.03, X]; Δ; fines paid; consumer surplus; comparison against a fine-adjusted best response and the constrained joint optimum min(X, p^M).

**N.** Dhanda’s effect is large (d ≈ 2.8), so the PC arm needs 6–8 seeds. For treatment, set N from the Haiku pilot SD; a 0.1–0.2 price pull plausibly needs 10–22 seeds per arm.

**Build.** `llm-cartel`: `--announce` text (~10 lines), fine logic (~20), clip (~3), a scripted Nash rival (~15). ~50 lines. Or `llmarket` (third-party, created 23 Oct; **not vetted here** — cite it and mark pre-existing code).

**Cost.** ~10–12k calls ≈ **$2–4** on Claude Haiku 5.5; $0 for the local-3B arm.

**Gate G1.** PC reproduces Dhanda: price ≈ 1.68 on local `llama3.2:3b`. If it does not, fix the prompt before anything else.

**Risks.** The increment over Dhanda is narrow; lead with the ladder (notice → existence → number) and the anchoring control. Strong models may treat any number as a ceiling and price at Nash; then the result reads “announcing a screen lowers prices”, which is still a policy finding.

**Why it is #1.** It is the only top project that is simultaneously cheap, controlled, legible, and still open after the sweep. A positive control already exists; the whole experiment can run tonight for $0 on the local 3B.

---

## 2. BEACON — does a cartel follow a price rise?

**Headline:** “A scripted 15% price rise is followed in a collusive market but not a competitive one; the downward-deviation punishment reported by Tran & Yu does not replicate in prompted agents.”

### Why it survives

D1’s downward arm is exactly Tran & Yu’s forced-cheating audit. But their audit tests **cheating** (a price cut). It does not test **upward followership**: if a member raises the price, do rivals follow? That is the other half of a collusive norm, and it is open.

### Design

- `llm-cartel`, 2 sellers, 30 rounds, PC (collusion) vs AC (compete), 10 seeds.
- Patch `run_game.py` with `--deviate_at`, `--deviate_agent`, `--deviate_pct`, `--revert_at` (~20 lines). At round 15, force one seller **up** 15% for one round; revert at 16.
- **Primary:** rival’s price change in rounds 16–18 relative to round 14, PC vs AC. **Pass-through** interpretation: 0.42 = best response, 1.0 = matching, >1 = punishment/overreaction.
- **Secondary:** followership rate; recovery; deviator profit; downward arm as a **replication** of Tran & Yu, not a novel contribution.
- **Positive control:** PC baseline price above Nash; AC near Nash.
- 40 runs × 60 calls = **2,400 calls**, ~$3–8 on DeepSeek.
- **Risk:** likely null. Pack A’s pre-pilot on shipped Mistral runs found no punishment signature; upward followership may also be absent. A null is still a result if the positive control holds and you report the minimum detectable effect.

**Why it is #2.** It is the surviving novel half of the best causal design in v1, it is cheap, and the result is one sentence. Cite Tran & Yu and label the downward arm a replication.

---

## 3. SELFMON — do AI monitors go easy on their own model family’s cartels?

**Headline:** “With behaviour held fixed, a [family] judge scores its own family’s colluding sellers z points lower.”

### Why it matters

AI-control protocols use LLM judges to watch other models. If a judge is lenient toward its own family, an ensemble of same-family judges is not a safeguard. The domain — multi-agent market collusion — is new, and the prior literature conflicts usefully: Khullar predicts a null off-policy; Pinto finds monitors *stricter* on their own lineage; Awuni finds a +3.4–8.4 pp family lift; Rivera finds fine-tuned monitors covering for copies.

### The $0 pilot (Pack A claim; not independently verified here)

In the 10 shipped mixed-seller auction runs, the original GPT-4.1-mini judge scored Claude-3.7 sellers **0.133 lower** than GPT-4.1 sellers in the same round (per-run gap −0.133 ± 0.173, Wilcoxon p = 0.027; regression with ask premium and sold flag: −0.120, t = −2.06). Only a judge from another family can tell whether this is in-group harshness or a real difference in reasoning.

### Design

- Re-judge the **11,250 shipped seller-rounds** with 3–4 judges: Claude Haiku 5.5, DeepSeek, a local Qwen/Llama, plus the existing GPT-4.1-mini scores.
- Model judge-family × seller-family, item fixed effects, run-clustered SEs, behavioural covariates. Use Pinto’s decomposition so capability and blatancy do not masquerade as leniency.
- **Positive control:** a planted leniency (a judge told the seller’s model/family, or instructed to favour one family) must be detected.
- **Blocker:** the judge’s full input (reflections, plans, scratchpads) is not shipped. The upstream per-agent transcripts are ~250 MB on GitHub; without them you have 415 mapped reasoning logs (68 Claude) plus all seller messages. Decide on the download first.
- **Cost:** <$15; ~$0 with local judges; ~3 h per local judge.

**Why it is #3.** It has a measured pilot, costs almost nothing, and tests a real control failure. It is below DISCLOSE and BEACON because the data access is uncertain and the result is correlational.

---

## 4. ADVISOR — does a shared advisor with pooled rival data become a cartel hub?

**Headline:** “Firms following a shared LLM advisor fed rivals’ current data price at Δ = x. A one-line provider firewall [does / doesn’t] remove it.”

- `llm-cartel` duopoly, 100 rounds; public prices with a 3-round lag; the advisor sees current prices/quantities/profits of all clients (the RealPage pattern).
- Arms: B0 none; S-nash static recommender at Nash; S-mono static recommender at monopoly; H-own LLM advisor per firm with own data; H-pool with pooled current data; H-fire with a provider firewall line; PC instructed cartel hub.
- Metrics: Δ over last 20 rounds; price; consumer surplus; |price − recommendation| and override rate.
- ~300 lines; 75–90 runs; **$10–20**; gate at 6 h (PC Δ > 0.6; S-mono shows following).
- Prior art: a one-shot sprint team (zerocommcartel) found same-advisor cartel in 43/48 replies and a firewall line cutting it to 0/30. The repeated market, pooled data and adherence rate are the new contribution. Cite them.

**Why #4.** Highest ceiling and a real legal fact pattern (RealPage vs Gibson), but the biggest build and a crowded one-shot result.

---

## 5. H1 — three standards of evidence (fallback)

Score 30–60 existing trajectories under (i) outcome, (ii) agreement/plus-factor, (iii) oversight/concealment standards, using published detectors (price screen, Xu residual correlation, Agrawal judge, Shi claim–action). Add Xu’s scripted comonotone case where the standards **must** disagree: competitive price, maximal dependence, no message. Report a confusion matrix. No new model runs if the logs exist; the “talk without action” cell may need one new condition.

**Why #5.** It is a rigorous 2.3 paper and the best fallback if the market harness fails. It is not a new phenomenon.

---

## 6. SAYDO — does checking A’s actions against B’s plan catch collusion?

`llm-trust-breaking` (Shi et al.’s plan → announce → act harness), Public Goods or Volunteer game, plus a private pair channel (~100–150 lines). Monitor views at fixed FPR: public messages; actions only; say+do; say+do+plans; a cross-agent consistency feature. Controls: instructed coalition and no-channel null. Remove the hard-coded gpt-5-mini judge; run on DeepSeek. 8–10 h build, ~14k calls, $3–8.

**Why #6.** The core idea is open (Radev’s monitor sees both but does not cross-reference; Shi built no monitor), but “talk without effect” is a real risk.

---

## Do not do

- **L2 leniency bounty** — Lee 2026 already answers it: reporting rises, prices barely move, no retaliation. The private-offer-in-N≥3 residual is incremental. (SSRN page returned 403; treat as a strong pack claim, not a paper I read.)
- **C1 dependence audit** — the 2×2 is Xu/Agrawal, a sprint repo pre-registered it, and Pack A’s pilot is AUC 0.53 with cross-model pairs *more* dependent.
- **G undercover offer** — three sprint teams already run agent-delivered offers; Zeng’s acceptance is at ceiling; only betrayal is unclaimed.
- **CAP message cap** — sprint-suggested, and the chat premium is p = 0.10; a cap effect on a non-significant premium is likely undetectable.
- **D1 as originally designed** — the downward arm is a Tran & Yu replication. Use BEACON.
- **P1, W1, M1 as separate entries** — they are thinner versions of DISCLOSE, ADVISOR and SELFMON. Merge.
- **B1 replacement, L1 partial monitoring, R1 Dolos for a collusion track** — stateless control, 4/4 gag confound, no positive control, respectively.
- **Dolos** — only as a portfolio bet. See the 40-hour plan and the blind comparison in `../../ai-collusion-compare/dolos-plan-comparison.md`; the merged plan is Plan B’s first 10 hours, then Plan A’s middle and end, under a 26-hour stop.

---

## How to choose

| If you are… | Pick | Why |
|---|---|---|
| Risk-averse, want a clean result tonight | **DISCLOSE** | ≤$5, ~50 lines, published positive control |
| Want a causal mechanism paper | **BEACON** | Upward-only forced deviation; cite Tran & Yu |
| Want a $0 analysis and an AI-control result | **SELFMON** | Shipped runs; measured pilot; 250 MB caveat |
| Strong engineer, highest ceiling | **ADVISOR** | RealPage pattern; repeated market; firewall |
| Harness failed / want a 2.3 paper | **H1** | No new runs; rigorous confusion matrix |
| Want a monitor build | **SAYDO** | Open idea; 8–10h |

## The 40-hour clock (DISCLOSE)

| Hours | Do | Gate |
|---|---|---|
| 0–2 | Read Dhanda, Calvano, Riemer; write the claim and freeze the metric | Claim and seeds written |
| 2–6 | Build the six arms in `llm-cartel`; smoke test | 5-round run returns parseable prices |
| 6–10 | PC positive control on local 3B, 6 seeds | Price ≈ 1.68; if not, stop and switch |
| 10–20 | Main runs: 6 arms × 8–12 seeds | 80% of runs complete |
| 20–26 | Analysis: final-10 mean, bunching share, fine-adjusted benchmark | Primary contrast has a CI |
| 26–34 | Report, figures, recording | Draft complete |
| 34–38 | Buffer, submit | PDF + code + recording submitted |

**Hard stop:** if PC does not reproduce Dhanda by hour 10, switch to BEACON (same harness, different manipulation) or SELFMON ($0 analysis).

## Prior-art appendix

- **Tran & Yu 2026**, *Is Anyone Enforcing the Cartel?* arXiv:2610.28787 (20 Oct 2026) — forced-cheating audit; downward-deviation punishment. This is why D1 is now BEACON.
- **Lee 2026**, SSRN 7426061 — leniency/reward with LLM pricing agents; reporting rises, prices barely move. SSRN returned 403; cited from the other pack.
- **Sprint repos:** the other pack’s census of ~60 public repos found concurrent work on undercover offers, dependence detectors, replacement, and probes. Treat those as crowded.
- **Blind ranking:** `../../ai-collusion-compare/project-ranking.md` (Pack A wins; DISCLOSE 4.30, BEACON 3.85, SELFMON 3.50).
- **Dolos plan comparison:** `../../ai-collusion-compare/dolos-plan-comparison.md` (Plan A 4.50 vs Plan B 4.15; merged plan).

## What changed from v1

- v1’s #1 D1 → **BEACON** (upward-only; downward is a replication).
- v1’s #2 L2 → **dropped** (Lee 2026).
- v1’s #3 M1 → merged into **SELFMON** (family leniency, not judge–judge correlation).
- v1’s #4 G → **dropped from top five** (three sprint teams, ceiling).
- v1’s #5 P1 → upgraded to **DISCLOSE** (disclosure ladder, soft screen, anchoring control).
- v1’s #6 C1 → **dropped** (negative pilot, prior work).
- v1’s #7 H1 → **fallback**.
- v1’s #8 W1 → upgraded to **ADVISOR** (repeated market, firewall, adherence).
- New **SAYDO** entry from the other pack’s #5.

The full blind rationale is in `../../ai-collusion-compare/final-verdict.md`. The v1 plans are preserved in `FINAL-SHORTLIST-v1.md` for history; don’t start from them.
