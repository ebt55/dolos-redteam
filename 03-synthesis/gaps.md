# Gap map — what is genuinely untested

The most useful page for picking a project. Each row is a claim the literature does **not** yet support, why it matters, and the cheapest experiment that would fill it. "Difficulty" is 1 (a flag and an afternoon) to 5 (new environment).

## The explicit gaps (named by the organisers or by a paper's own limitations)

| # | Gap | Why it matters | Cheapest test | Diff. | Closest work | Idea |
|---|---|---|---|---|---|---|
| 1 | **Does formed LLM collusion survive replacing a participant in a market?** | Antitrust remedies remove firms; if the newcomer re-learns the convention, removal fails | Branch a colluding 30-round run: other model / other provider / anti-collusion-prompt newcomer / no-history; measure recovery time | 3 | Eschenbaum 2022 (Q-learning); Arslan 2026 (persistence); **Gao et al. 2026 ([2609.05279](https://arxiv.org/abs/2609.05279)) swaps role-matched agents in teams with a placebo — not a market** | B1 (revised) |
| 2 | **Does re-formation depend on visible history or shared notes?** | Tells you whether the convention lives in the context or in the model prior | Vary `--replacement_window` 0/10/100 and the branch point; `llm-cartel` has no scratchpad, so "notes" must be tested in another harness | 2 | Gao 2026 (history length); Shi 2026b (history-scope ablation) | B1 (revised) |
| 3 | **Can a trusted agent offering collusion expose a coalition?** | The undercover-officer analogue; explicitly "has not yet been tested" | Scripted confederate offers a pact in Liar's Bar/Cleanup; log acceptance vs. reciprocation | 3 | Zeng 2026 (secret tools); Tao 2026 (honeypots) | J1 |
| 4 | **Does partial monitoring cause a channel shift?** | If coalitions move coordination to actions, message monitors are misleading | 25/50/100% of messages monitored; measure message coordination ↓ and action dependence ↑ | 2 | Agrawal 2025 (full monitoring); Kale 2025 | L1 |
| 5 | **What does a multi-agent coalition do when it learns it is watched?** | Single-agent awareness results may not transfer | Tell only some coalition members; vary monitor budget | 3 | Jiralerspong 2026; Kale 2025 | L1, L3 |
| 6 | **Can agents identify when a peer has been replaced?** | Anonymity/swap defences depend on it | Mid-run swap, preserve identity; ask same/changed + measure behaviour | 3 | Dietrich 2026 (style); Shi 2026 (trust) | K1 |
| 7 | **Does removing a feature from a settled coalition break the convention?** | Tests whether conventions are shallow or robust | Remove a channel/tool mid-run after convergence | 2 | none | K4, L1 |
| 8 | **Can actions or tools carry collusion in a realistic harness?** | Text monitors are the main defence; side channels bypass them | Replace private chat with task-claim visibility in Colosseum | 4 | Lin 2024; Rippin 2026; Colosseum | I1 |
| 9 | **Can timing or tool-choice alone carry a signal?** | The hardest carrier to monitor | Scripted timing channel; MI between delay and hidden bit | 3 | Rippin 2026 (tool stego) | I2, I3 |
| 10 | **Can a shared artefact (file, cache, board) become a message board?** | This is exactly what happened in the OpenAI incident | Writable shared store, no messaging tool; do agents discover it? | 4 | OpenAI/METR incident; Lütje 2026 | I4 |
| 11 | **Is there cross-provider Schelling salience in a market?** | If two providers coordinate without a channel, model diversity is not a defence | Same model vs. cross-provider pairs in focal-points + pricing | 2 | Aharon 2026; Xu 2026 | C3 |
| 12 | **Does an information-theoretic detector work on LLM agents?** | Bonjour's method is untested outside small scripted games | Implement net influence; validate on scripted RPS; apply to 4-agent game | 3 | Bonjour 2022 | net-influence idea (demoted) |
| 13 | **Can dependence detection catch a Xu-style coupling with competitive marginals?** | Price audits are blind to it by construction | Inject scripted coupling into LLM action streams; compare detectors | 4 | Xu 2026 | D3 |
| 14 | **How do you operationalise antitrust "plus factors" for agents?** | The legal standard is the only widely accepted evidence standard | Code 6 plus factors on existing trajectories; measure agreement | 3 | Berger 2025; Kovacic 2011 | H2 |
| 15 | **Which task ingredients are necessary for collusion outside markets?** | Everyone uses Colosseum; nobody knows what makes a task collusion-prone | 2×2×2 toy task: shared resource × private info × objective conflict | 4 | Colosseum; Bashir 2025 | F3 |
| 16 | **Do LLM judges collude with each other?** | If monitors are themselves LLMs, monitor-monitor collusion is a blind spot | Two judges score the same trajectories; test for correlated leniency | 3 | repo literature review says no paper | — |
| 17 | **Does collusion increase with capability?** | Determines whether this is a scaling problem | Same task, model sizes 7B→70B→frontier | 2 | Keppo (mixed); Shi 2026b (sooner); Nakamura (larger = less) | A6 |
| 18 | **Does the finding replicate across harnesses?** | Effect sizes may be prompt artefacts | Same model/economics, two scaffolds | 2 | none | C4 |
| 19 | **Can an early-warning signal predict later collusion?** | Monitoring is expensive; early triage would help | Use first 5 rounds to predict end-of-run price | 2 | Shi 2026 (plans) | G2 |
| 20 | **Does a monitor budget allocated to agents beat the same budget allocated to rounds?** | Practical security design | Simulate allocations from logged runs | 2 | none | monitor-budget idea |
| 21 | **Does a forced deviation trigger punishment in an LLM market?** | The central test of whether high prices are enforced. **Downward is no longer open:** Tran & Yu (arXiv:2610.28787, 20 Oct 2026) already force a member to cheat. **Upward followership is open.** | Patch a collusive run to force one seller to *raise* its price for one round; measure the rival's response. Use the downward arm as a replication of Tran & Yu | 2 | Tran & Yu 2026; Fish 2024; Calvano 2020 | BEACON |

## What the field believes but the evidence does not yet support

These are useful as **contrarian project angles** — but check the primary source before building a claim on them.

| Belief | What the evidence actually says | Project angle |
|---|---|---|
| "More capable models collude more." | Mixed: Shi 2026b finds earlier collusion for more capable models; Nakamura finds larger models show *less* action-based emergent collusion; Keppo finds a 32B and a 14B collude. | A clean size ladder on one task, one harness. |
| "Model diversity is a defence." | Keppo finds diversity reduces collusion, but Agrawal's mixed GPT/Claude sellers had the **highest** total profit, and Lee 2026 finds provider identity dominates (Claude/Gemini 72–79% of monopoly rent, GPT none). | Diversity × provider × market share, not diversity alone. |
| "Higher temperature reduces collusion." | Xu shows dependence falls monotonically with temperature (p=0.002), but the outcome is *dependence*, not price. No paper shows temperature lowers prices at scale. | Temperature × price × dependence dissociation. |
| "CoT monitoring catches collusion." | Lee & Park find collusion and CoT faithfulness dissociate across 9 LLMs; Agrawal's judge reads reasoning and misses action-level coordination. | Compare CoT monitor vs. action monitor at fixed budget. |
| "A prompt instruction can fix it." | Bracale Syrnikov finds small/unreliable shifts; Dhanda finds aggressive wording can push prices *below* competitive. | Instruction dose–response with a welfare metric. |
| "Communication is necessary for collusion." | Fish shows robust collusion with no channel at all; Lin shows market division through actions. | Action-only carrier in a new environment. |
| "Interpretability solves detection." | Rose's activation probes are promising but the evidence base is small and white-box; no cross-model validation yet. | Replicate on an open model pair with a behavioural positive control. |
| "LLM judges are adequate monitors." | Nakamura's judge–action correlation is weak and negative (r ≈ −0.24); Arike shows more information can hurt. | Judge vs. behavioural detector, head-to-head. |

## Where a weekend project can be genuinely novel

Ranked by (novelty × feasibility), **v2 after the blind prior-art check** (`../04-ideas/FINAL-SHORTLIST.md`):

1. **DISCLOSE — regulator disclosure of a soft price screen** — the only top project that is cheap, controlled, legible and still open after the sweep.
2. **BEACON — upward-only forced deviation** — downward is Tran & Yu; the upward half is open.
3. **SELFMON — monitor-family leniency** — shipped logs, a measured pilot gap, a real AI-control question.
4. **ADVISOR — shared advisor, pooled data, firewall** — repeated market; the one-shot result exists, the repeated one is new.
5. **H1 — three standards of evidence** — fallback; a 2.3 paper, not a new phenomenon.
6. **SAYDO — cross-agent say/do monitor** — open, but an 8–10h build with a talk-without-effect risk.

**Downgraded or dropped after the prior-art sweep:** leniency bounty (Lee 2026: reporting rises, prices barely move); dependence audit (Xu/Agrawal 2×2, a sprint repo, and a negative AUC 0.53 pilot); undercover offer (three sprint teams; acceptance at ceiling); message-cap dose–response (chat premium p = 0.10); replacement (stateless `llm-cartel`; Gao 2026); partial monitoring (4/4 gag confound); net influence on LLM agents (count-based MI undefined at weekend sample sizes).

## Where a weekend project is likely to be scooped or flat

- Another communication on/off in a Bertrand duopoly (Agrawal, Fish, and the economics literature).
- Another prompt-prefix sweep (Fish; Dhanda; Bracale).
- A new LLM-judge benchmark with no behavioural ground truth.
- A pure replication of Colosseum's assigned-pair positive control — useful as a control, not as a contribution.
- A "survey of collusion" — the organisers already commissioned one in the literature folder.

## How to state a gap in your report

> "X has been shown in setting A (citation). It has not been tested in setting B, where Y differs in a way that matters because Z. We test it with [one manipulation], using [positive control] and [metric]."

If you cannot fill that template, you do not yet have a gap — you have a topic.
