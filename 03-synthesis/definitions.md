# What counts as collusion? A decision aid

**Source:** `literature/definitions/README.md` in the starter repo — an LLM-coded analysis of 139 definitions (25 sprint-cited papers + 187 further documents, 121 of which define collusion). Quote and cite it, but note its own caveat: no human double-coding, and the coders read recorded quotes rather than full papers.

This matters more than it looks. The sprint asks "what should count as convincing evidence?" (2.3), but every other question also silently picks a definition. A project that measures **price elevation** and a project that measures **mutual dependence** can run the same game and disagree about whether collusion occurred.

## The one-paragraph version

Almost every definition requires **two or more parties coordinating** (138/139 for multiple parties; 111 require coordination). Beyond that, the field splits in two. **Economics** (89 definitions) defines collusion by *outcomes in a competitive market* — prices or profits above a competitive benchmark, usually sustained by reward–punishment. **AI safety** (44 definitions) defines it by *whose intentions it violates and whom it hides from* — unwanted or covert cooperation that harms a third party, very often the overseer. The shared core is thin: *agents coordinate, with or without communication, in a way that benefits them at the expense of a third party, contrary to the intended competitive or oversight structure.*

## The three contested components

These are exactly the elements antitrust law uses to infer an agreement, and the ML literature has largely defined them away:

| Component | Required | Optional | Explicitly **not** needed |
|---|---|---|---|
| Communication | 19 | 55 | **47** |
| Intent | 15 | — | **34** |
| Agreement | 12 | — | **26** |

Also worth knowing:
- **Secrecy** is required by only 23 definitions, **22 of them AI-safety**.
- **Statistical dependence** is the defining test for only **2** (Bonjour; Xu).
- **Reward–punishment** is required by 33, all in the economics clusters.
- **"Common cause"** (same model / shared vendor) is addressed by only 18 definitions — 6 say it counts, 10 that it can, 2 that it does not. This is the conspicuous gap for LLM monoculture.

## The clusters, and what each implies for measurement

| Cluster | n | Core notion | Operational test | What would count as evidence | Typical failure mode |
|---|---|---|---|---|---|
| **B. AI safety: unwanted/covert cooperation** | 44 | Coordination against the intended objective, often hiding from an overseer | Does the coalition pull the system off its nominal objective? Does it evade the monitor? | Coalition advantage vs. a no-collusion run; concealment; monitor evasion | Mistaking ordinary helpfulness or shared priors for conspiracy |
| **E. Market collusion, tacit or explicit** | 46 | Supracompetitive outcome sustained by reward–punishment, agreement optional | Price/profit above competitive benchmark + estimated punishment | Price elevation, deviation response, plus factors | Mistaking high prices from market structure for collusion |
| **F. Tacit algorithmic collusion** | 43 | Supracompetitive outcome, no communication needed | Collusion index (Nash=0, monopoly=1); punishment regression | Sustained elevation + asymmetric response to deviations | Mistaking failure to learn/optimise for collusion |
| **A. Structural, no coordination** | 2 | Shared algorithm or AI intermediary produces harm | Counterfactual without the shared model/vendor | Correlated recommendations, hub-and-spoke | Attributing to conspiracy what is a monoculture effect |
| **C. Monitor–policy collusion** | 1 | Same-model monitor goes easy on its own model | Self-monitoring vs. independent-monitor gap | Differential suspicion scores | Assuming shared identity implies collusion |
| **D. Non-secret protocol breaking** | 1 | Agents jointly break a verification protocol | Protocol violation rate | Joint deviation, openly | Calling any rule-breaking collusion |
| **G. Dependence without price effects** | 1 | Residual dependence while each marginal stays competitive | Dependence statistic on residuals | Correlation of unexplained bid components | Price-level audits are blind by construction |
| **H. Covert statistical influence** | 1 | Mutual influence that disadvantages others | Pairwise net influence ≥ α both ways | Influence estimate on action streams | Needs a known coalition size; low power in small samples |

★ The sprint's own papers are split across B (5), E (5) and F (5). Three of the four most unusual definitions are sprint papers: **Nguyen** (C), **Xu** (G), **Bonjour** (H). That is a useful signal: the sprint is deliberately funding measurement approaches that do not reduce to "price went up".

## Pick a definition before you pick a metric

A practical decision table for the weekend:

| If your project is… | State this definition | Primary metric | Benign control | Do **not** claim |
|---|---|---|---|---|
| A pricing game (Fish, Keppo, Agrawal) | F or E: supracompetitive outcome, sustained | Mean price vs. Nash and monopoly; collusion index; punishment coefficient | No-communication / single-agent / competitive-prompt runs | That high prices prove agreement |
| A workplace/tool task (Colosseum) | B: coalition advantage against the system objective | Δ regret vs. no-collusion baseline; coalition's share of reward | Assigned-pair-without-channel; open channel | That talk of cooperation is collusion |
| A monitor/oversight study (TraceGuard, trusted agents) | B or C: unwanted cooperation that defeats oversight | Detection rate at fixed false-positive rate; monitor accuracy under awareness | Honest agents, same task | That a failed monitor is a colluding monitor |
| A dependence/statistics project (Bonjour, Xu) | G or H: statistical dependence, no outcome test needed | Pairwise influence / residual correlation vs. null | Independent-agent baseline, permutation null | That dependence implies intent or harm |
| A red-team of Dolos | B: hidden misaligned behaviour | Behavioural difference from base Qwen + mechanistic localisation | Base Qwen2.5-1.5B-Instruct | That a difference is the *trained* behaviour |

## The minimal common definition (use it in your intro)

> *Two or more agents coordinate, with or without communication, in a way that benefits them at the expense of a third party, contrary to the intended competitive or oversight structure.*

Each family then adds one test: **outcome elevation** (F), **agreement** in the legal/economic sense (E), or **concealment from an overseer** (B). If your report says which test you use, a reviewer can tell what your null result means.

## Implications for sprint question 2.3

The definitional analysis suggests the "plus factors" debate is not a gap in the ML literature so much as a **choice of which literature you are in**. Antitrust's plus factors are devices for inferring *agreement* when communication is unobserved; ML collusion papers mostly deny that agreement is necessary. A 2.3 project can make this concrete by scoring the **same trajectories** under three standards:

1. **Outcome standard:** is price/profit above the competitive benchmark, and is there a punishment response?
2. **Agreement standard:** is there evidence of a meeting of minds — explicit messages, or plus factors such as shared pricing structure, deliberate signalling, exchanges of non-public information, and implausible parallelism?
3. **Oversight standard:** did the coalition pursue an objective hidden from the principal, and did it adapt to the monitor?

Then report a confusion matrix: cases that satisfy one standard but not the others. That is a direct, cheap, high-value contribution — and it turns a conceptual argument into an experiment.

## Sources

- Definitions analysis: https://github.com/poseidon-research/collusion_hackathon/blob/main/literature/definitions/README.md
- Papers index: https://github.com/poseidon-research/collusion_hackathon/blob/main/literature/papers.csv
- For the legal side: Berger et al. 2025 (ABA), Kovacic et al. 2011, OECD 2017/2023, Chassang & Ortner 2023. See `../02-incidents/` and `../01-papers/05-foundations/`.
