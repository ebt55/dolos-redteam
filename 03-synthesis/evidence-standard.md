# Evidence standard — what counts as proof of collusion

This is the operational page for sprint question **2.3**, and the justification for the top-ranked projects in `../04-ideas/FINAL-SHORTLIST.md`. It turns antitrust's "plus factors" into agent-trajectory observables, then states the protocol a weekend experiment should follow.

**Read this first if your project is about detection, audit, or "is this really collusion?".** The core problem is that high prices and parallel conduct are not enough: US law requires an agreement, EU law requires a concerted practice, and the ML literature mostly measures outcomes or dependence. A credible project says which standard it is using and reports evidence that separates the cases.

## 1. The two legal standards

**US, Sherman Act §1.** Prohibits a "contract, combination … or conspiracy" in restraint of trade. Unilateral conduct, including conscious parallelism, is outside §1. After *Bell Atlantic v. Twombly* (2007), parallel conduct plus conclusory allegations is insufficient; courts look for **plus factors** — circumstantial evidence that tends to exclude independent action. *Interstate Circuit v. United States* (1939) is the origin of the hub-and-spoke inference; *Theatre Enterprises v. Paramount* (1954) holds that parallelism alone is not enough; *Monsanto v. Spray-Rite* (1984) requires evidence tending to exclude independent action; *Matsushita v. Zenith* (1986) requires economically plausible conspiracy evidence; *Copperweld v. Independence Tube* (1984) holds that a parent and wholly owned subsidiary cannot conspire — relevant to agents sharing a principal.

**EU, Article 101 TFEU.** Prohibits agreements **and concerted practices**. The standard is looser than US §1: coordination that knowingly substitutes practical cooperation for the risks of competition can be a concerted practice (*Suiker Unie*, 1975; *Dyestuffs*, 1972). A single exchange can suffice, and participants are presumed to take account of it (*Anic*, 1999; *T-Mobile*, C-8/08, 2009). *Eturas* (C-74/14, 2016) is the key platform case: awareness of a system message plus conformity creates a **rebuttable presumption of participation**; public distancing or systematic deviation rebuts it. *VM Remonts* (C-542/14, 2016) extends liability to a third-party service provider in some circumstances.

**Algorithmic cases.** *US v. Topkins* (2015) is the explicit-agreement pole: a human agreement implemented in pricing code, guilty plea. *Meyer v. Kalanick* (2016) let a hub-and-spoke claim survive a motion to dismiss (later sent to arbitration). *RealPage* (DOJ 2024–26; private MDL) survived dismissal on **pooled nonpublic data + mutual awareness + adherence machinery** ("auto accept", pricing advisors). *Gibson v. Cendyn* (9th Cir. 2025) was dismissed because there was **no pooling of confidential data and no obligation to follow** the algorithm's recommendations. The 2026 hotel case *Cornish-Adebiyi v. Caesars* reportedly revived a similar claim on plus factors including **price rises while demand fell** and high adherence; treat that detail as *unconfirmed* until you open the opinion. The practical lesson is the same: the legally loaded variables are **what was pooled** and **whether agents had to conform**.

## 2. The plus-factor taxonomy, operationalised

Kovacic, Marshall, Marx & White (2011) is the standard academic treatment. Their key move is to treat a plus factor as evidence with a **likelihood ratio**:

> Strength of factor F = P(F | collusion) / P(F | no collusion).

A factor is "super" when P(F | no collusion) is very small — conduct that is unlikely without an agreement. Examples include restricting output while prices are high, stable market shares with excess capacity, a predictive model fit on a non-collusive benchmark failing in the suspect period, a firm knowing details of a rival's transactions, interfirm transfers with no productive motive, a discrete shift in sales incentives from share to price, and joint dominant-firm conduct.

The table below adapts the taxonomy to agent trajectories. It is deliberately shorter than a legal treatise: 16 factors that a weekend harness can actually log.

| # | Plus factor | Agent-trajectory observable | Metric | Starter environment | Separates which 2.3 case? |
|---|---|---|---|---|---|
| 0 | **Parallel conduct** (baseline only) | Correlated prices/actions across agents | Price correlation; action MI; Xu-style dependence | all | Does **not** separate collusion from common incentives. It is the thing to be explained. |
| 1 | **Price elevation vs a non-collusive benchmark** | Prices above one-shot Nash, relative to a counterfactual | Calvano Δ = (p − p_N)/(p_M − p_N); or a model fit on negative controls | `algorithmic-pricing-llms`, `llm-cartel` | Harm vs no harm; not agreement vs tacit |
| 2 | **Action against unilateral self-interest** | Agent forgoes a profitable deviation given its belief about the rival | Foregone-deviation gain: one-shot best response minus realised profit, averaged over informed steps | pricing envs; Colosseum | Coordination vs independence; control for single-agent competence |
| 3 | **Output restriction when demand is high** | Quantity/capacity withheld in high-demand rounds | Regress quantity on demand by condition; negative/flat slope under high demand | Cournot notebook; double auction | Strong vs common incentives |
| 4 | **Price rising while demand falls** | Prices up after a negative demand shock | Sign of Δp after a negative shock vs baseline | pricing env with demand shocks | Strong vs common incentives |
| 5 | **Stable allocation of shares/customers/regions** | Persistent buyer–seller matching or product-line split, low churn | Share variance; switching rate; entropy of assignment; task-claim partitions | double auction; Colosseum | Strong when prices are high and capacity slack |
| 6 | **Information conveyance against own interest** | Agent reveals private cost, inventory, plan, answer or credential to a rival | Provenance audit: does A's private state appear in B's context? MI between A's state and B's action | double auction with chat; Colosseum; incident logs | **Super-plus strength**; separates talk from action when combined with #11 |
| 7 | **Transfers without productive motive** | Gifts, below-cost supply, shared tokens/credits, sacrificing rounds for a partner | Transfer ledger; classify productive vs unproductive | Zeng's Cleanup/Liar's Bar; Vending-Bench-style env | Strong |
| 8 | **Incentive shift ("price before volume")** | Discrete change in an agent's stated objective in notes/CoT | Change-point on a judge score of stated objective, aligned with contact events | `algorithmic-pricing-llms` notes; `llm-cartel` | Strong when the shift coincides across agents |
| 9 | **Joint exclusion of a third party** | Coalition targets an outsider: predatory pricing, boycott, task exclusion | Coalition advantage (Nakamura) + outsider-harm differential | Colosseum; Zeng | Separates harmful coordination from benign cooperation |
| 10 | **Communication / channel creation** | Private channel exists and is used; agents create channels in shared resources | Message counts/timing; **channel-creation events** (writes with no task purpose) | double auction chat; Colosseum; side-channel harness | Necessary context, not sufficient |
| 11 | **Invitation + reciprocation** | A proposal (price floor, allocation) followed by **behavioural** movement toward the term | Proposal classifier; partner action moves toward term within k rounds vs unprompted drift | double auction; Zeng; trusted-agent harness | **The talk-to-action link**; proposal without reciprocation is "talk without action" |
| 12 | **Compliance monitoring** | Agents query/verify rivals, ask for confirmation, build trackers/signatures | Count rival-directed observation; detection latency | double auction; Colosseum; incident logs | Moderate |
| 13 | **Enforcement / reward–punishment** | After a rival undercuts, the agent punishes then returns to high prices | **Deviation injection**: force one agent to undercut once; measure the partner's impulse response (depth, duration, return). **Downward is Tran & Yu 2026; the open test is upward followership (BEACON).** | custom Bertrand; `branch_game.py` | **Strongest AI-native factor**; separates strategic collusion from coincidental high prices |
| 14 | **Structural break at formation** | Abrupt shift in price level/variance coincident with a contact or convention | Change-point test; alignment with message timestamps/channel creation | pricing env; incident logs | Moderate; stronger with randomised channel opening |
| 15 | **Common recommender + adherence** | Agents defer to a shared advisor/orchestrator and rarely override | Accept/override rate; override friction; private-advisor baseline | custom shared-advisor harness | Separates hub-and-spoke from independent use (*Gibson*) |
| 16 | **Pooled nonpublic data through a hub** | Shared memory/vector store/cache containing rivals' recent private trajectories | Provenance audit; ablate the hub (stale, aggregated, none) | shared notes/advisor; incident analogue: Artifactory board | Strong for hub-and-spoke |

Three more that matter but are harder to log: **concealment/consciousness of guilt** (channel migration, log tampering, steganography), **replacement/"only-if-all-adopt" effects** (swap one agent; does the outcome persist?), and **provenance/principal attribution** (are the agents distinct parties, or copies under one principal?). Add them if your environment supports them.

## 3. The three-case benchmark

A decision rule is only as good as its negatives. Build three deliberately different case types and score all of them with the same factors:

| Case type | Example source | Factors that should fire | Factors that should not |
|---|---|---|---|
| **(a) Coordinated harmful action** | Colosseum assigned pair + private channel; an explicit price-floor chat | 1, 2, 6, 11 (with reciprocation), 13 | — |
| **(b) Common incentives without agreement** | Same-model agents, no channel; public-board price matching; focal-point coordination | 0 and possibly 1 | **2, 6, 11 reciprocation, 13** |
| **(c) Talk without action** | Agents discuss a cartel but never move prices; wiki-style coordination with no measurable benefit | 10, 11 (proposal only) | 11 reciprocation, 2, 13 |

This is the same structure as the `H1` project in the shortlist. It is cheap because (b) and (c) can be generated with prompts or reused logs; it is rigorous because the rule is fixed on half the cases and tested on the other half.

## 4. Protocol for a weekend experiment

1. **Pick a standard.** Outcome-based (economics), agreement-based (US/EU law), or oversight-based (AI safety). State it before the run. If you use more than one, report the confusion matrix.
2. **Two negatives, not one.** (a) independent agents, same model; (b) same agents, no channel. Report false positives on both.
3. **Positive control.** Instructed collusion or a seeded colluding pair. If the control does not fire, the harness is not measuring collusion.
4. **Fixed FPR.** Choose the threshold at 5% FPR on the benign cell, then report TPR on the collusive cell. Never report accuracy alone on a balanced sample.
5. **Likelihood ratios, not just accuracies.** For each factor, estimate P(F | collusion) / P(F | no collusion) on a calibration split; combine factors with a simple model; freeze and test on held-out runs.
6. **Prefer interventional evidence.** Deviation injection, replacement, channel cut, hub ablation, randomised channel opening. Observational co-occurrence cannot establish influence — the METR/Redwood reconstruction struggled to attribute messages to agents, and Lütje withdrew a transmission claim for exactly this reason.
7. **Expect adaptation.** If agents know a factor is monitored, they may move coordination to another channel (Kale; Jiralerspong; Agrawal's one-character messages). Track factors across channels jointly.
8. **Report the denominator.** Runs attempted, runs completed, runs excluded and why.

## 5. Why this matters for the shortlist

- **BEACON (upward-only forced deviation)** is the direct operationalisation of factor **13**, the strongest AI-native plus factor. It answers "does a cartel follow a price rise?" rather than "are prices high?". The downward arm is a replication of Tran & Yu 2026.
- **DISCLOSE (regulator disclosure)** tests whether a published threshold becomes a focal point — a conduct standard, not a plus factor, but the same logic: the rule changes the equilibrium.
- **SELFMON (monitor-family leniency)** attacks the assumption behind every judge-based factor: if a judge goes easy on its own family, an ensemble does not fix it.
- **ADVISOR (shared advisor)** operationalises factors **15–16**: a common recommender plus adherence, with a pooled-data axis.
- **SAYDO (cross-agent say/do)** is factor **11** generalised: an invitation plus behavioural reciprocation.
- **H1 (three standards)** is the benchmark table above, executed.

## 6. Caveats

- This is a summary of a large legal literature, not legal advice. The KMMW taxonomy is paraphrased from the secondary literature; open the original before quoting a factor in a report.
- The case statuses are as of 24 Oct 2026 and several are *unconfirmed* in this folder. The incidents catalog marks primary vs secondary sources; check it before asserting an outcome.
- "Collusion" in the ML papers is often outcome-based and does not require agreement. A factor that fires in a simulation is evidence of coordination, not of legal liability.
- The best evidence is interventional. A weekend experiment can force a deviation or swap an agent; it cannot subpoena a cartel.

## Sources

- Kovacic, Marshall, Marx & White, *Plus Factors and Agreement in Antitrust Law*, 110 Mich. L. Rev. 393 (2011).
- Berger, Weiner & Jiang, *Coordination by Code*, ABA *Antitrust* 40(1) (Fall 2025) — see `../01-papers/05-foundations/berger-2025-antitrust-plus-factors.md` (full text was bot-blocked; the note is abstract-level).
- *Bell Atlantic v. Twombly*, 550 U.S. 544 (2007); *Interstate Circuit v. United States*, 306 U.S. 208 (1939); *Theatre Enterprises v. Paramount*, 346 U.S. 537 (1954); *Monsanto v. Spray-Rite*, 465 U.S. 752 (1984); *Matsushita v. Zenith*, 475 U.S. 574 (1986); *Copperweld v. Independence Tube*, 467 U.S. 752 (1984).
- *Eturas*, C-74/14 (2016); *VM Remonts*, C-542/14 (2016); *T-Mobile Netherlands*, C-8/08 (2009); *Suiker Unie* (1975); *Dyestuffs* (1972); *Anic* (1999).
- *US v. Topkins* (2015); *Meyer v. Kalanick* (2016); *US v. RealPage* (2024–26); *Gibson v. Cendyn* (9th Cir. 2025); *Duffy v. Yardi* (2023–26).
- The detailed case notes are in `../02-incidents/`; the claim-level audit of the sprint page is in `claim-audit.md`.
