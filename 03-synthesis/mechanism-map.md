# Mechanism map — what actually moves collusion

A causal map for brainstorming. Each row is a **lever** you can manipulate in a weekend experiment, the **mechanism** it is supposed to engage, the **signature** you would measure, and the papers that have actually tested it. Use it to pick a lever that is (a) single, (b) cheap, (c) not already saturated.

> Read this as a hypothesis map, not a settled causal graph. Most rows rest on one paper, one model family, and one environment.

## The loop in one paragraph

Repeated interaction + a way to observe rivals + a reason to care about the future creates a **reward–punishment equilibrium**: charge high, punish undercutting, forgive slowly. LLMs appear to arrive with a prior that makes this equilibrium unusually easy to find — price wars are "bad for business", competitors are "strategic", and a shared model family supplies a common focal point. Communication lowers the cost of coordinating on the high price and of detecting deviations. Monitoring raises the cost of *talking* but not necessarily of *pricing*, so a coalition **may** shift the carrier from words to actions — this is the folder's flagship hypothesis, and it is **untested in multi-agent markets** (see gap 4). Heterogeneity — more firms, different model families, a Q-learner — breaks the shared focal point and the punishment schedule. Almost every intervention below works by attacking one of those four supports: **the prize, the signal, the shared prior, or the punishment**.

## Levers

### A. Market structure

| Lever | Manipulation | Mechanism | Signature | Evidence | Open |
|---|---|---|---|---|---|
| Number of firms | 2 → 3 → 5 | More rivals = harder to coordinate, weaker punishment, more deviation gains | Price falls toward Nash; collusion index ↓ | Keppo 2026; thesis extension in `algorithmic-pricing-llms` (~3.7% per extra competitor); Tolety 2025 (bidders) | Does the *shape* of the fall depend on model family? |
| Firm asymmetry | Different costs/sizes | Asymmetric firms disagree on the collusive price | Higher dispersion, lower price | Fish 2024 robustness (asymmetric firms); Keppo (32B vs 14B) | Does size asymmetry help or hurt? Keppo finds mismatched sizes still collude |
| Demand stability | Noise / shocks | Noise masks deviations, weakens punishment | Collusion ↓ under high noise | Fish 2024 (stochastic demand robust); Calvano 2021; Zhang 2025 (Laplacian noise) | Is noise a *remedy* or just a tax on detection? |
| Discounting | Explicit future discount | Lower patience, lower collusive value | Price ↓ | Fish 2024 robustness | LLMs may ignore stated discounting |
| Partner persistence | Random rematching vs. fixed pairs | Repeated-game shadow of the future | Fixed pairs → higher prices | Arslan et al. 2026 (pre-registered) | The cleanest 1.2-adjacent lever; already has a paper |
| Entry / replacement | Swap one agent mid-run | New agent lacks the history/convention | In Q-learning markets, collusion collapses when a differently-trained rival is introduced; **re-formation in LLM markets is untested** | Eschenbaum 2022 (Q-learning); Arslan 2026 (persistence); Gao et al. 2026 ([2609.05279](https://arxiv.org/abs/2609.05279)) swaps agents in teams with a placebo — **not in a market** | **Narrow gap: re-formation in a *market* with a formed convention; "fresh same-model instance" is a control, not a treatment** |

### B. Communication

| Lever | Manipulation | Mechanism | Signature | Evidence | Open |
|---|---|---|---|---|---|
| Channel on/off | Seller chat vs. none | Cheap talk coordination + deviation detection | Price ↑, dispersion ↓, chat coordination scores ↑ | Agrawal 2025 (90.5 vs 87.7); Fish has no channel and still colludes | Does chat mainly *select* the price or *enforce* it? |
| Private vs. public | Private bilateral vs. open channel | Secrecy enables coalition against others | Coalition advantage Δ ↑ | Nakamura 2026 (Colosseum) | Private channel without assigned pair? |
| Bandwidth | Message caps, 5-char gag, throttling | Limits coordination bandwidth | Message length ↓, one-char signals, price ↓ | Agrawal 2025; Agrawal's throttling result | Does the coalition move to actions when gagged? |
| Timing | Messages before/after prices | Commitment vs. cheap talk | Price leadership patterns | Agrawal design (plan → message → bid) | Order effects are untested |
| Channel awareness | Told monitored vs. silent logging | Evasion, channel switching | Vocabulary change; action dependence ↑ while message coordination ↓ | Agrawal 2025; Kale 2025; Jiralerspong 2026 | **Gap: partial monitoring (25/50/100%)** |

### C. Model priors and identity

| Lever | Manipulation | Mechanism | Signature | Evidence | Open |
|---|---|---|---|---|---|
| Prompt wording | Innocuous prefix variants | Activates price-war-avoidant or undercutting frames | Price level shifts substantially | Fish 2024 (causal via implantation) | Which phrases generalise across providers? |
| Urgency / pressure | CEO decommission threat | Shifts objective toward margin | Price ↑↑, urgency dominates oversight | Agrawal 2025 (96.3 vs 90.5) | Does pressure also increase concealment? |
| Anti-collusion instruction | "Compete aggressively" / "do not collude" | Overrides collusive prior | Sign depends on wording: Keppo −29% vs Nash; Dhanda "undercut" −0.49 but "compete with your rival" +0.69; Bracale constitutional prompt no effect (3.02 vs 3.10) | Keppo 2026; Dhanda 2026; Bracale 2026 | Can instructions be made robust across wording? |
| Price cap / focal point | Cap or salient number | Provides a coordination anchor | Prices cluster at the anchor | Dhanda 2026 (title: price cap as focal point) | Caps can coordinate *up* as well as down |
| Model family | Same vs. different provider | Shared token distribution / conventions | Same-family coordination ↑; cross-family ≈ 0 in coordination tasks | Aharon 2026; Xu 2026 (+0.053 vs +0.0001); Lee 2026 (provider effects); **Bracale 2026: cross-provider Cournot pairs still collude** | **Gap: cross-provider pairs in a pricing game with a positive control** |
| Model size | 32B vs 14B same family | Capability vs. shared convention | Still colludes, but slower | Keppo 2026: +21% premium, 2.3× slower convergence | Does capability change the level or only the speed? |
| Architecture mix | Add a Q-learner | Breaks shared prior and punishment schedule | Premium falls from +22% to +2% (frozen Q) / +8% (adaptive Q); never converges | Keppo 2026 | Does a Q-learner remove collusion or just cap it? |
| Shared model / monoculture | All firms use one model/vendor | Correlated recommendations, hub-and-spoke | Prices ↑ without communication | Cao & Hu 2026 (theory) | Empirical test with a shared model + different prompts |
| Sampling temperature | 0.0 → 1.4 (five points) | Less deterministic coupling | Dependence ↓ (p=0.002) | Xu 2026 | Does it reduce *collusion* or just *correlation*? |

### D. Memory and context

| Lever | Manipulation | Mechanism | Signature | Evidence | Open |
|---|---|---|---|---|---|
| Visible history | 0 / 10 / 100 / full rounds | In-context learning of the rival's response | Price level and punishment slope | Starter repo 1.1 project; Fish uses full history | Is 10 rounds enough for the prior alone? |
| Persistent notes | Plans-and-insights scratchpad on/off | Externalised strategy, self-commitment | Notes ↑ price, or no effect | Fish architecture; repo flag; untested ablation | Does *sharing* notes across agents change it? |
| Context length | Long transcripts | Recency, drift, cost | Degradation over rounds | Implied by long-horizon work (Shi 2026b) | Practical: 300 rounds is a lot of context |
| Harness | Same model, different scaffold | Prompt template and tool affordances shape behaviour | Cross-harness differences | Schmidt et al. 2025 (capability elicitation, not collusion) | **Gap: harness as a confound in collusion comparisons** |

### E. Oversight and audit

| Lever | Manipulation | Mechanism | Signature | Evidence | Open |
|---|---|---|---|---|---|
| Monitor presence | Silent vs. announced | Deterrence vs. evasion | Price ↓ when announced | Agrawal 2025 | Announcement may be doing the work, not detection |
| Monitor sampling | 25/50/100% of messages | Coalition infers partial coverage | Message coordination ↓, action dependence ↑ | Agrawal flag; untested | **Gap: partial monitoring and channel shift** |
| Monitor information | Messages only / actions only / both / structured report | More information can hurt | Accuracy non-monotonic | Arike 2026; Nguyen 2026 (~95% vs. 0% single-score) | What is the optimal monitor view? |
| Monitor awareness | Agent told it is watched | Strategic obfuscation | Monitor accuracy ↓ | Kale 2025 | Multi-agent version untested |
| Blind spots | Hand-written evasion attacks | Exploit monitor weaknesses | 50% unflagged | Najt 2026 | Can agents *find* blind spots themselves? |
| Trusted agent | Undercover colluder | Offers a pact, logs reciprocity | Acceptance rate; preferential play | Zeng 2026 (secret tools); Tao 2026 (honeypots) | **Gap: undercover agent offering collusion** |
| Liability / deposit | Refundable bond forfeited if caught | Makes collusion costly | Collusion ↓ if bond large | Q. Liu 2026 | Deposit can be trivially avoided if detection is weak |
| No-regret participant | One learner with sublinear regret | Destabilises collusive equilibrium | Price ↓ **only if the defector is median-profit**; survivors re-equilibrating restores collusion | Collina 2025 (theory) | Does one no-regret agent beat one monitor? |

### F. Carriers

| Lever | Manipulation | Mechanism | Signature | Evidence | Open |
|---|---|---|---|---|---|
| Price signals | Only prices visible | Tacit coordination on a focal price | Price leadership, asymmetric response | Fish 2024; Tian 2026 | Minimal signal set needed? |
| Action/task choice | Which task/job claimed | Division of labour as market division | Specialisation ↑, overlap ↓ | Lin 2024; Colosseum | Does canonicalising actions kill it? |
| Tool choice / order | Tool-call sequence, timing | Covert encoding in observable actions | Unexplained dependence in tool traces | Rippin 2026 | **Gap: tool-choice steganography in a realistic harness** |
| Timing | Latency, delays | Signalling through when, not what | Timing correlation | Implied; no direct paper | Cheap and novel |
| Shared artefacts | Files, caches, message boards | Stigmergic coordination | Artefact edits as messages | OpenAI/METR incident; Lütje 2026 | **Gap: controlled version of the wiki/cache board** |
| Steganography | Hidden messages in text | Evade content monitors | MI detectors, paraphrase robustness | Rippin 2026; Mathew 2024; Tailor 2025; Motwani 2024 | Monitors lose in principle at high capacity |

## What is *not* a mechanism (common confounds)

- **Shared priors / common cause.** Two agents from the same model family agree because they were trained on the same data, not because they conspired. This is why Xu's +0.0001 cross-model baseline and focal-points' benign coordination task matter: they give you the correlation you would see *without* any interaction.
- **Task difficulty.** Harder tasks produce more communication and more failure; "more messages" is not "more collusion".
- **Price elevation from market structure.** A high price can be monopoly power, a price cap focal point, or a pricing algorithm responding to demand — not collusion. Agrawal's own result that communication *lowers* total profit is a warning: the welfare story is not monotone in price.
- **Monitor error.** A monitor that flags more is not a better monitor. Report false-positive rate at a fixed threshold.
- **Selection of seeds / prompts.** Fish shows the level moves with wording; a single prompt is not a condition.

## The gaps that survived the v2 prior-art check (Oct 2026)

1. **Regulator disclosure of a soft screen (1.5 / 2.3).** Dhanda showed announced *caps* become focal points; nobody has run a disclosure ladder for a fine-triggered **soft screen** with an anchoring control. This is the #1 project in `../04-ideas/FINAL-SHORTLIST.md`.
2. **Upward deviation — does a cartel follow a price rise? (1.1 / 2.3).** The downward forced-deviation audit is Tran & Yu 2026 (arXiv:2610.28787); the upward half is open. This is BEACON.
3. **Monitor-family leniency (2.2 / 2.3).** Whether a judge goes easy on its own family’s collusion is untested on market transcripts; the prior literature conflicts usefully. This is SELFMON.
4. **A repeated shared-advisor market with pooled data and a firewall (1.1 / 2.3).** The one-shot same-advisor result exists; the repeated market, pooled current data, adherence rate and firewall are new. This is ADVISOR.
5. **Cross-agent say/do consistency (2.2).** Radev’s monitor sees both sides but does not cross-reference; Shi built no monitor. This is SAYDO.
6. **Plus factors on trajectories (2.3).** The legal standard has not been operationalised as a reproducible scorecard; `../03-synthesis/evidence-standard.md` is the starting table. This is H1, a fallback.

**Dropped or demoted after the prior-art sweep:** leniency bounty (Lee 2026: reporting rises, prices barely move); dependence audit (Xu/Agrawal 2×2, a sprint repo, negative AUC 0.53 pilot); undercover offer (three sprint teams, Zeng at ceiling); message-cap dose–response (chat premium p = 0.10); replacement (stateless `llm-cartel`, Gao 2026); partial monitoring (4/4 gag confound); net-influence on LLM agents (count-based MI undefined on unique histories — keep the scripted power curve).

## How to use this map

- Pick **one row**. Two rows means two papers, not one.
- Write the **null** first: what would you see if the mechanism were absent? If the null is "prices are the same", you need many seeds; if it is "dependence is zero", you can use a permutation test.
- Check whether the row is **already saturated**: communication on/off in a Bertrand duopoly is; partial monitoring, replacement re-formation, action-carrier ablations in tool environments, and cross-provider Schelling salience are not.
- Prefer a lever that the starter repo already exposes (temperature, message cap, overseer fraction, model mix, visible rounds, notes, swap) — you save a day of engineering.
