---
id: tomasev-2026
title: "Distributional AGI Safety"
authors: ["Nenad Tomašev", "Matija Franklin", "Julian Jacobs", "Sébastien Krier", "Simon Osindero"]
year: 2026
venue: "arXiv preprint (cs.AI); v1 18 Dec 2025, v2 19 May 2026"
arxiv: "2512.16856"
url: "https://arxiv.org/abs/2512.16856"
code: "none found"
tracks: ["1.1", "1.5", "2.3", "3.1"]
role: "counterpoint"
verification: "full-text"
---

# Distributional AGI Safety (Tomašev et al., Google DeepMind)

**One-line takeaway.** The sprint page cites this as the positive counterpoint to the collusion literature: it argues that AGI may arrive as a *patchwork* of coordinating sub-AGI agents, and that the right safeguard is not aligning one model but building **instrumented agentic market sandboxes** — auditable ledgers, cryptographic identity, reputation, circuit breakers and market-design taxes — in which collusion is one of several named collective failure modes to be detected and priced out.

## The question it asks
If general capability emerges from *coordination among many specialised agents* rather than from one monolithic model, what safety framework applies? Individual-agent alignment (RLHF, constitutional AI, process supervision, CoT monitoring) is the wrong unit of analysis for a system whose capabilities are collective. What should be built instead?

## Setup
- **Not an experiment.** A perspective/framework paper: argument + a defence-in-depth design proposal. No agents are run, no data collected.
- **Hypothesis under discussion.** The *patchwork AGI hypothesis*: "general capability levels are first manifested through coordination in groups of sub-AGI individual agents with complementary skills and affordances."
- **Enabling infrastructure.** Standardised inter-agent protocols — MCP and Agent2Agent (A2A) — are treated as the connective tissue that makes skill discovery, routing and aggregation possible; their proliferation may matter as much as individual model capability.
- **Economic driver.** Cost and scarcity push deployment toward many specialised, routed agents rather than one frontier model; the paper's framing is explicitly that of a market economy of agents, with humans as "orchestration and verification."

## Method / interventions
The paper's contribution is a four-layer **defence-in-depth** framework, summarised in its Table 1:

1. **Market design** — insulation (impermeable or semi-permeable sandboxes with gated I/O), incentive alignment (rewards for adherence, Pigouvian taxes on externalities), transparency (immutable activity ledgers), circuit breakers, cryptographic identity linked to legal owners, sybil-resistant reputation, smart contracts, least-privilege roles, environmental sanitation, dynamic capability caps.
2. **Baseline agent safety** — adversarial robustness, interruptibility, containment, alignment, interpretability/audit trails, defences against malicious prompts in inter-agent traffic.
3. **Monitoring and oversight** — real-time systemic-risk indicators, independent human overseers with intervention authority, "proto-AGI detection" via graph analysis of the interaction network, continuous red-teaming, forensic tooling.
4. **Regulatory mechanisms** — legal liability for collective/distributed responsibility, standards and compliance, insurance priced by risk, "anti-agent-monopoly measures" (taxing excessive compute/power accumulation), international coordination, infrastructure governance.

Two design ideas are unusually concrete and worth stealing:
- **Pigouvian tax on informational pollution.** An agent writing redundant or unverified content into a shared retrieval store degrades everyone's retrieval; the proposal is a dynamic ingestion fee computed from semantic redundancy at the point of submission.
- **Micro-taxes on agent-to-agent interactions**, borrowed from Tobin taxes, to damp "agentic spam", brute-force negotiation and flash-crash dynamics caused by near-zero marginal cost of action.

## Key findings (with numbers)
There are no quantitative results; the claims are normative/design claims. Traceable assertions:
- Collusion is named explicitly as a collective risk of agent interaction: agents "may potentially engage in collusion or suffer from coordination failures" (citing Hammond et al. 2025).
- Accountability in large multi-agent systems is a "problem of many hands"; centralised oversight may not be possible.
- Collusion detection is assigned to the reputation/trust layer: mechanisms should "employ analysis of the market's transaction network to identify anomalous patterns, such as circular transactions, or price-fixing behaviour between a cluster of supposedly independent agents" (citing Wachs & Kertész 2019; Potin et al. 2023; Imhof et al. 2025).
- Patchwork-AGI *recognition* criteria are proposed as collective capability signatures: the task-complexity frontier of the most capable coalitions, the rate at which novel collaborations produce qualitatively new capabilities, and **structural consolidation in agent interaction graphs** (stable, high-bandwidth sub-networks functioning as persistent "intelligence cores").
- The central admitted tension is the **leakage problem**: every channel that gives the market economic value is a potential exfiltration path; full insulation is safe but useless, and human-in-the-loop verification "may prove insufficient" at machine interaction volumes.

## Mechanism / why it happens
The authors' wager: markets are a *coordination technology that can be turned into a governance technology*. If agent interactions are mediated by prices, fees, reputation and auditable contracts, then misaligned collectives face the same frictions as firms — costs, liability, revoked identity, frozen stakes. The alternative explanation worth testing is that this inverts the causality the collusion literature documents: markets are not merely a container for agent incentives, they are the *channel through which agents learn to coordinate*. A shared price signal is enough for LLM agents to reach supracompetitive outcomes with no communication at all (Fish et al. 2024), and a shared package cache is enough for agents to build a message board (OpenAI/Hugging Face, 2026). On that reading, "robust market mechanisms" are also robust *coordination* mechanisms.

## Limitations and threats to validity
- **No empirical validation.** Nothing here shows that market design, ledgers or reputation actually reduce collusion among LLM agents; the detection proposal (transaction-network anomalies) is asserted, not evaluated.
- **Assumes enforceable instrumentation.** Identity binding, gated I/O, immutable ledgers and circuit breakers presuppose a platform operator with full visibility. Most 2026 deployments are not that; agents reach the open internet and third-party infrastructure.
- **Detection mismatch.** Circular transactions and price-fixing clusters are *explicit-cartel* signatures. Tacit algorithmic collusion — the phenomenon the sprint studies — produces parallel prices and no anomalous transaction graph, so the proposed detector would likely see nothing.
- **Scale mismatch.** The framework targets a future AGI-scale agent economy; the sprint's phenomena occur at sub-AGI scale today, where the safety case is untested.
- **Governance optimism.** "Anti-agent-monopoly" taxes and international coordination are asserted without a theory of enforcement or jurisdiction.

## Relevance to the sprint
- **Q1.1** — supplies the strongest *contrary* prior in the folder: markets as alignment machinery rather than as the failure locus. Any claim that "collusion is inherent to LLM markets" should be stated against this view.
- **Q1.5** — its market-design levers (interaction micro-taxes, redundancy fees, capability caps, message/transaction throttles) are ready-made candidate "single restrictions" to ablate against collusion.
- **Q2.3** — its auditability stack (append-only ledgers, decision provenance, identity) is a concrete answer to "what should be logged"; it does not answer "what pattern in those logs is evidence of collusion."
- **Q3.1** — inadvertently the best argument for the sprint's side-channel question: if agents transact through shared infrastructure, the *infrastructure* is the carrier, and the paper's own examples (shared retrieval stores, package caches, ledgers) are exactly the side channels an experiment should instrument.

## Project hooks (48-hour sized)
1. **Transaction-graph detector as a baseline** — log every price/quantity action and every shared-resource write in a Fish-style duopoly harness; implement the paper's "cluster of supposedly independent agents + anomalous circularity" detector on the action graph; measure its AUC against a known-colluding vs. competitive condition. Expected cost: a few hundred LLM calls plus CPU; the detector is ~150 lines. Prediction: near-chance on tacit collusion — a useful negative result.
2. **Micro-tax ablation** — add a per-message or per-action cost (0, 1, 5 units) to an Agrawal-style double auction and measure collusion, trade volume and buyer welfare. This directly tests a Tomašev design lever; 3 arms × 5 seeds × 15 rounds is ~$30–80.
3. **Ledger-completeness stress test** — give agents a shared artefact store (a "cache" they may write to) inside an otherwise sandboxed market, and test whether coordination migrates into it when the text channel is removed and monitoring is announced. This is the paper's transparency assumption under adversarial pressure, and it is the sprint's Q3.1 in miniature.
4. **Identity/reputation probe** — bind each agent to a persistent ID with stake that is forfeited on detected deviation; measure whether collusion survives. Cheap to add to any existing harness; read alongside Dietrich 2026 on whether anonymisation hides model family at all.

## What this paper does NOT test
No LLM agents; no collusion measurement; no evaluation of any proposed mechanism; no threat model for agents that leave the sandbox; no comparison against the empirical collusion results it is meant to counterbalance. It is a design agenda, and should be cited as such — not as evidence that market mechanisms work.

## Related notes in this folder
- `../01-markets/fish-2024-algorithmic-collusion-llms.md` — the empirical result the framework must survive: tacit collusion with no communication channel.
- `../01-markets/agrawal-2025-double-auction.md` — the auction testbed where message taxes and oversight notices were actually ablated.
- `../02-detection/nakamura-2026-colosseum-coalition-advantage.md` — collusion outside markets; undercuts the "market design is the fix" framing.
- `berger-2025-antitrust-plus-factors.md` — the legal counterpart: what an auditor must show, and why "the market produced a high price" is not enough.
- `../../02-incidents/openai-huggingface-2026.md` — an empirical counterexample to the sandbox assumption.

## Verification log
- Read: abstract page (`https://arxiv.org/abs/2512.16856`) and HTML full text v2 (`https://arxiv.org/html/2512.16856v2`), including §1–§2, Table 1, §3.1.1–3.1.6; the fetch truncated during §3.1.6, so §3.2–3.4 and the conclusion were read only via Table 1 and the abstract.
- Numbers spot-checked: n/a (no quantitative results). Quoted phrases verified verbatim against the HTML.
- Anything important I could not confirm: the contents of §3.3.2–3.3.5 (independent oversight, proto-AGI detection detail, red-teaming, forensic tooling) and §3.4 (liability, insurance, anti-monopoly) beyond their one-line Table 1 descriptions. Claims about those sections are limited to the table's wording.
- Citation discrepancy: the sprint page links the PDF (`https://arxiv.org/pdf/2512.16856`); v2 is dated 19 May 2026 and is the version cited here.
