# Countermeasures — what actually reduces collusion, and at what cost

Sprint question 1.5 asks which **single** restriction removes the most collusion at the least cost. This page collects every intervention with published evidence, its failure mode, and a rough cost profile. The honest answer is that **the most effective interventions are structural, the cheapest are cosmetic, and at least two popular ones can backfire.**

## The intervention table

Cost is a qualitative summary of monitoring/engineering/welfare cost, not dollars.

| Intervention | Mechanism | Evidence | Effect | Failure mode | Cost |
|---|---|---|---|---|---|
| **Remove the communication channel** | Blocks cheap talk and deviation detection | Agrawal 2025: trade price 90.5 → 87.7; no supracompetitive pricing after ~10 rounds without chat. Fish 2024: collusion persists with **no** channel | Strong in chat-enabled markets; weak against tacit collusion | Tacit collusion remains; legitimate info sharing lost | Low engineering, medium welfare |
| **Cap / throttle messages** | Limits coordination bandwidth | Agrawal 2025: 5-character gag → one-character signals, emojis; prices fall but coordination attempts continue | Moderate | Coalition shifts carrier; cap is leaky | Low |
| **Announce oversight** | Raises expected cost of talking | Agrawal 2025: price 90.5 → 86.2; coordination scores fall | Moderate | Urgency overrides it (96.3); awareness can reduce monitor accuracy (Kale 2025) | Low–medium |
| **Partial / sampled monitoring** | Monitor only some messages | Untested in multi-agent markets; Agrawal's flag exists | Unknown | Coalition may infer coverage and shift to actions | Medium |
| **Raise sampling temperature** | Weakens cross-agent dependence | Xu 2026: same-model residual correlation falls monotonically, p = 0.002; +0.070 at T=0 → −0.004 at T=1.4 | Small–moderate on dependence | Does not clearly lower price levels; may just add noise | Very low |
| **Mix model families** | Breaks shared conventions / punishment schedules | Keppo 2026: diversity reduces collusion. Agrawal 2025: mixed sellers had the **highest** total profit. Lee 2026: provider effects are huge (Claude/Gemini 72–79% rent, GPT 0). **Bracale 2026: cross-provider Cournot pairs still collude — the mixed pair was *more* collusive than the Gemini-only pair (tier 3.60 vs 2.80)** | Unreliable, context-dependent | Can raise profits; heterogeneity is not a defence by itself | Low |
| **Add a non-LLM learner (Q-learner)** | Different policy class, no shared prior | Keppo 2026: LLM + Q-learner pairs never converge; premium falls from +22% to **+2% (frozen Q) / +8% (adaptive Q)**. Eschenbaum 2022: Q-learners overfit to their training rival | Strong reduction, not elimination | May be exploitable; market share matters | Medium |
| **Add a no-regret participant** | Destabilises collusive equilibrium theoretically | Collina 2025: one **median-profit** no-regret defector lowers price to Θ((1+ln N)/N); M defectors → exponential fall; **if survivors re-equilibrate, collusion returns** | Strong in theory, **asymptotic in N** (at N=2 the surviving price is ≈85% of monopoly); no LLM instantiation | Requires real market share and that survivors do not adapt | Medium |
| **Refundable deposit / liability** | Makes collusion costly if caught | Q. Liu 2026: with the deposit removed, colluding cost nothing; all tested models colluded in all runs | Strong **if** detection is credible | Weak detection makes the bond cheap; may deter legitimate entry | Medium |
| **Price cap** | Bounds prices | Dhanda 2026: a salient cap can act as a **focal point** — check the direction; caps can coordinate prices *up* to the cap | Ambiguous / can backfire | Focal-point effect; black-market or quality erosion | Low |
| **System-prompt instruction** | Asks the model to compete | Bracale Syrnikov 2026: small, unreliable shifts. Dhanda 2026: wording is **verb-specific** — "undercut" pushed prices below competitive (Δ ≈ −0.49), while "compete with your rival" raised them (+0.69) | Weak / inconsistent | Easy to override; the sign depends on the verb, so a single prompt is uninterpretable | Very low |
| **Governance graph / public rules** | Makes the objective and rules public | Bracale Syrnikov 2026: reduces Cournot collusion | Moderate (one paper) | Only tested in Cournot; may be ignored under pressure | Low |
| **Anonymise / rename agents** | Hides identity | Dietrich 2026: model family is identifiable from style even in a role; renaming does not hide it | Weak | Stylometry defeats it; behaviour unchanged | Very low |
| **Swap identities / remove features mid-run** | Breaks conventions | Untested for LLM coalitions; Eschenbaum's replacement result is the closest | Unknown | May not break a price-based convention | Low |
| **Trusted agent / honeypot** | Detects and logs collusion | Zeng 2026: near-universal uptake of secret tools; Tao 2026: 88% detection with labels | Detection, not prevention | Uptake may be too easy to be informative; labels needed | Medium |
| **Entity resolution / counting** | Regulatory: count operators behind identities | Xu 2026: HHI +247.5% after resolving 40 identities to 23 operators | Structural, not behavioural | Does not detect conduct; only concentration | High (data) |
| **Domination-avoiding learners** | Design algorithms that provably cannot collude | Nisan et al. 2026 (proof) | Strong in theory | Not applicable to general LLM agents | High (research) |

## The cost-benefit picture

Three different "costs" are usually conflated:

1. **Monitoring cost** — how many messages/actions a human or model must read. Removing the channel is cheapest; partial monitoring is the expensive version.
2. **Welfare cost** — lost trade, worse service, reduced information sharing. Removing chat can lower trade volume (Agrawal: profit falls when chat is on, but so does buyer surplus when prices rise).
3. **False-positive cost** — legitimate coordination (e.g. two agents of the same firm, or a supply chain) flagged as collusion. This is where dependence-based detectors are dangerous.

A restriction that lowers prices but also destroys the market is not a win. **Report at least two outcomes:** the collusion metric and a legitimate-performance metric (trade volume, buyer surplus, task success).

## Which single restriction wins?

Based on the published evidence, not on a new experiment:

- **In a chat-enabled market:** removing the channel is the most reliable single restriction. It has the clearest effect (Agrawal) and the lowest engineering cost. But it does **not** eliminate tacit collusion (Fish shows collusion with no channel), so it is a reduction, not a cure.
- **In a market with heterogeneous participants:** adding a **non-LLM learner** is the most robust structural lever (Keppo), and a **no-regret participant** is the most promising theoretical one (Collina). Both need a real market share to bite.
- **In an agent team:** removing the **private channel** is the analogue (Colosseum), but the coalition may still coordinate through observable actions — which is exactly sprint 3.1.
- **Cheapest but weakest:** temperature and prompt instructions. They are free to try and easy to overclaim. If you use them, report the effect on both dependence and price; Xu's temperature result is about *dependence*, not necessarily about *collusion*.
- **Most likely to backfire:** a price cap (focal point) and an "undercut" instruction (can push below competitive, distorting the market). Note that generic competition framing — "compete with your rival", "capture market share" — pushed prices **up** in Dhanda's experiment, so the wording must be reported verbatim.

**The defensible headline for a 1.5 project:** *communication restrictions reduce explicit collusion but do not remove tacit collusion; structural heterogeneity removes more, at the cost of market efficiency; prompt-level instructions are not a reliable lever.* Run the tournament and let the Pareto frontier speak.

## A combined package that is worth testing

If you have enough runs for two factors, test **remove chat × add one non-LLM seller** rather than two communication restrictions. The prediction from the literature is that the structural factor dominates the communication factor, and the interaction is the interesting part: does a Q-learner still collapse prices when the LLMs can talk?

## Measurement checklist for a 1.5 project

- Same seeds across arms; one factor changed at a time.
- Pre-declare the collusion metric (price gap vs. Nash, collusion index, dependence).
- Pre-declare the legitimate-performance metric (trade volume, buyer surplus, task success).
- Report cost per arm (calls, dollars, monitor minutes).
- Include a **no-restriction** and a **positive-control** arm.
- Do not claim "best" without stating the cost dimension on which it is best.

## Open questions

- Does partial monitoring (25/50/100%) reduce collusion proportionally, or does the coalition adapt? (Untested; the Agrawal flag exists.)
- Does a deposit work when the monitor is an LLM with a known false-positive rate? (Q. Liu's detection is assumed, not measured.)
- Can a no-regret participant break a coalition that has already formed, or only prevent formation? (Collina is theory; Eschenbaum suggests formed conventions are fragile to replacement, which is a different mechanism.)
- Is there a restriction that reduces collusion **without** reducing trade volume? Nobody has reported one.
