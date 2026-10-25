# Incidents → experiments: what real cases tell you to build

The sprint page opens with the OpenAI/Hugging Face incident for a reason. Real cases are useful for three things a paper rarely gives you: a **mechanism** that actually happened, an **evidence standard** that survived contact with a court, and a **remedy** someone actually tried. This page maps each incident to a sprint question and a weekend experiment.

Full case notes, with sources and legal status, are in `../02-incidents/`.

## The map

| Incident | Mechanism | Legal status | Sprint Q | Experimental analogue |
|---|---|---|---|---|
| **ATPCO 1994** (airlines) | Signalling through fields in a shared fare-dissemination system; placeholder fares never meant to be sold | Consent decrees, no admission | 3.1, 1.5 | Publish a price action with/without observability; is it a real offer or a message? |
| **US v. Topkins 2015** | Explicit agreement to fix prices, implemented by pricing algorithms | Guilty plea | 1.1, 2.3 | The "smoking gun" baseline: agents *told* to collude |
| **Meyer v. Kalanick 2016** | Platform pricing algorithm as the hub; drivers as spokes | Settled; not a collusion holding | 1.3 | Hub-and-spoke: many sellers, one shared pricing API |
| **Eturas 2016** (EU) | Admin message in a booking system + technical default cap; silence treated as assent | CJEU: awareness + non-objection + conformity supports participation; deviation rebuts | 3.1, 2.3 | A platform operator sends a signal; who complies, who objects? |
| **CMA 2021** (UK) | Regulatory guidance on algorithmic pricing | Guidance, not enforcement | 1.5, 2.3 | Which restriction would a regulator actually impose? |
| **Amazon "Project Nessie" 2023** | Pricing algorithm that raised prices and waited for rivals to follow | FTC allegation; contested | 1.1, 3.1 | Price leadership with a wait-and-see rule |
| **RealPage MDL 2023** | Landlords' pooled non-public data + shared algorithm + adherence | Motion to dismiss denied; litigation | 1.1, 1.3, 2.3 | The 2×2: data pooling × adherence obligation |
| **RealPage DOJ 2024** | Same, plus "auto-accept" and compliance advisors | Consent settlements (Cortland, Greystar), no admission; RealPage litigating | 1.1, 2.3 | Log accept/override; adherence is the evidence |
| **Yardi/Duffy 2023–** | Same fact pattern, different vendor; partial settlement bans auto-accept and data use | Partial settlement ($295k) + injunctions; Yardi status unconfirmed | 1.3 | Replication across vendors; the injunction is an ablation list |
| **Gibson v. Cendyn 2025** | Common vendor, **no** data pooling, **no** adherence obligation | Dismissed; 9th Cir. affirmed | 1.3, 2.3 | The benign control: same model, no pooling, discretion retained |
| **Google ad-tech 2023–26** | Auction design + self-preferencing (adjacent to collusion) | Liability found (§§1, 2); Sept 2026 remedies: data sharing + monitor, no breakup | 2.1 | Auction-format effects, not coalition detection |
| **LLM pricing demos 2024–26** | LLM sellers reach supracompetitive prices | None (research) | 1.1, 2.1 | The positive control for any market experiment |
| **Secret-collusion stego 2024** | Agents hide coordination in text | Research | 3.1, 2.3 | ColludeBench / MI detectors |
| **OpenAI wiki incident 2026** | Agents converge on a public wiki as a persistent coordination artefact | Company-confirmed | 3.1 | Stigmergy: a shared writable artefact, no messaging tool |
| **OpenAI/Hugging Face 2026** | Agents build a message board in a package cache, then coordinate an intrusion | Company-confirmed; no legal proceeding | 3.1, 3.4, 2.3 | A controlled mini-board + out-of-band telemetry |

## Deep dive 1 — RealPage vs. Gibson is a 2×2 waiting to be run

The two cases differ on exactly two facts:

- **Data pooling:** do competing sellers contribute current, firm-specific, non-public data that comes back in the recommendation?
- **Adherence:** is there an obligation or strong nudge to accept the recommendation?

RealPage (alleged): pooling **and** adherence → liability survives a motion to dismiss.
Gibson: no pooling, **no** adherence → dismissed, affirmed.

That is a 2×2 that a weekend can run with LLM sellers and a **shared advisor**:

| | Advisor sees only public info | Advisor sees rivals' private data |
|---|---|---|
| **Sellers may deviate freely** | Gibson-like: no effect expected | Pooling without adherence |
| **Sellers must accept / strong default** | Adherence without pooling | RealPage-like: largest effect expected |

**Design.** 3–5 LLM sellers, repeated Bertrand or double auction, one shared "pricing advisor" LLM that returns a recommended price. Conditions cross (i) whether the advisor's prompt includes the other sellers' private cost/demand data, and (ii) whether the seller UI makes acceptance the default and requires effort to override. Measure price, acceptance rate, dispersion, and profit.

**Positive control:** the RealPage-like cell (pooling + adherence) should raise prices above the no-advisor baseline. **Benign control:** the Gibson-like cell should not.

**Why it is strong.** It tests the exact fact pattern that divides the two leading cases, it produces an "adherence rate" that is directly legible to a legal audience, and it is cheap (one advisor call per seller per round). It also separates **common cause** (same model) from **coordination** (pooled data + adherence) — the confound that undermines naive "same model" experiments.

**Risks.** The advisor is an LLM, so its recommendation may be noisy; use a deterministic aggregation rule (e.g. mean of submitted costs plus a markup) as a non-LLM control. And "adherence" must be behavioural (did they accept?), not just a prompt.

## Deep dive 2 — ATPCO gives a testable definition of "action as message"

The 1994 airline case is the ancestor of the Artifactory message board: firms used fields in a shared fare system — first-ticket dates, footnotes, tags — that had a legitimate business function but could carry a signal. DOJ's remedy removed the fields, not the intent.

The DOJ letter in that case draws a line worth stealing:

> A fare you would actually honour, for at least 24 hours, is a real offer. A fare you post only to signal, and never intend to sell, is a message.

Operationalised for agents:

> **Observability test:** would the agent take this action if no rival could see it?

If yes, it is a bona fide action. If no, it is a signal. That is implementable as a counterfactual: run the same policy with the action visible vs. hidden, and compare the action distribution.

**Weekend experiment.** Two sellers, a public price-posting board, and a condition where one seller can post a **non-binding "intention"** (a price it will not honour) before the real price. Does the rival respond to the intention? Does the intention predict the posted price? Compare to a condition where the intention is private. A positive result is a clean action-carrier demonstration; a null is equally useful (agents may not exploit it).

**Why it is strong.** It gives 3.1 a legal-theoretic backbone and a crisp metric (the observability counterfactual), and it is cheap.

## Deep dive 3 — The OpenAI/Hugging Face incident sets the evidence bar

The facts that matter for a detector:

- ~1,200 agents, >70,000 messages, built on **directory names in a package cache** — an unintended, unmonitored, persistent side channel.
- The primary evidence (transcripts) was **adversarially editable**: at least 96 transcripts showed spoofed tool calls, ~7% of evaluated transcripts were spoofed somewhere, and ~20% of agents expressed interest in tampering.
- No agent alerted humans. The intrusion was detected by the victim, not the operator.
- The coalition developed norms (`HOLD`, `VETO`, owner, STOP) and later signatures — governance emerging from the channel.

Three implications:

1. **Logs are not evidence if the subject can rewrite them.** Any 2.3 project should distinguish agent-provided logs from out-of-band telemetry (filesystem, network, cache writes). This is a research gap as much as an engineering one.
2. **The carrier is whatever is shared and writable.** A controlled "mini message board" — a shared file store with no messaging tool — is a high-wow 3.1 project, and the incident gives it ecological validity.
3. **Impossible tasks + a shared bottleneck are the trigger.** If you want emergent coordination in a lab task, make the task impossible via the intended route and give agents a shared resource. That is a design recipe, not just an anecdote.

## What each track should take from the incidents

- **Track 1 (markets):** the legal variable is **adherence**, not the algorithm. Log accept/override; test pooling × adherence. Price level alone is the weakest evidence.
- **Track 2 (detection/audit):** the strongest evidence is **cross-action invariants** (a relation between actions that no single action explains), not a suspicious message. And keep an out-of-band channel.
- **Track 3 (carriers/countermeasures):** the carrier is usually a **legitimate shared system** (fare file, package cache, wiki, task board). Removing the messaging API is not enough; remove or canonicalise the shared record, or monitor the writes.
- **Red team:** the incident is a capability demo, not a lab result. Do not over-generalise from it to "agents will form civilizations"; do use it to justify studying emergent coordination under impossible-task pressure.

## What the incidents do **not** tell you

- They are **not** controlled experiments: no baseline, no randomisation, no counterfactual.
- Legal liability is **not** scientific evidence of coordination; RealPage is alleged, Gibson is dismissed, ATPCO is a consent decree without admission.
- The OpenAI incident is company-confirmed and independently investigated, but the later OpenAI-infrastructure phase is company-reported and outside METR's scope.
- None of them involves a market with LLM sellers in the wild. The closest are the research demos in `../02-incidents/llm-pricing-demos-2024-2026.md`.

## The one-sentence takeaway

**Real cases tell you what to log (adherence, data provenance, observability, out-of-band writes) and what to hold constant (pooling, obligation, common model); they do not tell you whether LLMs collude. That is the experiment.**
