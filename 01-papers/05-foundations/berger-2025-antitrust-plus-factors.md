---
id: berger-2025
title: "Coordination by Code: Rethinking Antitrust Liability in the Age of AI Pricing"
authors: ["Lee F. Berger", "Michael L. Weiner", "Weisiyu Jiang"]
year: 2025
venue: "ABA Antitrust Magazine, Vol. 40, No. 1 (Fall 2025)"
arxiv: ""
url: "https://www.americanbar.org/groups/antitrust_law/resources/magazine/2025-fall/coordination-code-rethinking-antitrust-liability-age-ai-pricing/"
code: "none"
tracks: ["2.3", "1.1", "1.5"]
role: "core-result"
verification: "full-text"
---

# Coordination by Code (Berger, Weiner & Jiang, 2025)

**One-line takeaway.** US antitrust does not forbid parallel pricing; it forbids *agreement*, and it infers agreement from circumstantial "plus factors." This article argues that shared AI pricing systems can supply those plus factors through **data pooling, mutual awareness, and adherence to a common recommendation** — giving the sprint a legally grounded, LOO-able list of what an auditor should log, and a sharp warning that price parallelism alone proves nothing.

> **Title note.** The ABA page and the authors' firm both title this "**Coordination by Code**: Rethinking Antitrust Liability in the Age of AI Pricing." The task brief called it "Coordination Code"; the URL slug is `coordination-code-...`. Cite the published title.

## The question it asks
When competitors delegate pricing to a shared or common AI system, when — if ever — does that become an "agreement" under §1 of the Sherman Act? Does mutual use of the same model substitute for an express agreement? Does it matter whether users know rivals use it, whether they must follow its recommendations, or whether they agreed on the same prompts?

## Setup
- **Doctrinal, not empirical.** The authors are practicing antitrust lawyers. The method is case analysis plus five constructed hypotheticals (five airlines, one AI pricing model).
- **Legal baseline.** §1 reaches "contract, combination … or conspiracy"; unilateral conduct is outside it. Post-*Twombly*, parallel conduct plus conclusory allegations is insufficient — courts look for "plus factors."
- **Anchor case.** *U.S. v. Container Corp. of America*, 393 U.S. 333 (1969): even limited exchanges of pricing information can violate §1 when they reduce price competition.
- **Two real cases as poles.** *United States v. RealPage* (M.D.N.C. No. 1:24-cv-00710) and *Gibson v. Cendyn Group* (D. Nev. No. 2:23-cv-00140; 9th Cir. No. 24-3576).
- **Statutory overlay.** California AB 325 (2025) amending the Cartwright Act.

## Method / interventions
1. Reconstruct the §1 information-exchange doctrine and the plus-factor inquiry.
2. Read *RealPage* and *Gibson* for the facts that drove opposite outcomes.
3. Apply the resulting principles to five airline scenarios of increasing coordination, and predict liability under federal law and under amended California law.

## Key findings (with numbers)
- **Plus factors, as the authors summarise them:** "prior collusion, evidence of intent to coordinate, the structure of the market, and whether the information shared is current, specific, bi- or multi-lateral, and competitively sensitive." (This is the article's synthesis of the doctrine, not a statutory list.)
- **RealPage — DOJ theory.** Landlords contributed nonpublic, competitively sensitive data (daily rent rolls, occupancy forecasts) to a shared algorithm that returned recommendations built from rivals' data; RealPage marketed the tool as "raising the tide" and "avoiding the race to the bottom," and drove adherence through **"auto accept" functionality and pricing advisors who monitor landlords' compliance.** DOJ pleaded **rule of reason, not per se**. Settlement with **Cortland** earlier in 2025 and with **Greystar on 8 August 2025**: no use of algorithms that generate recommendations from competitors' competitively sensitive data, no sharing of CSI, and a monitor if using a non-certified third-party algorithm. RealPage and remaining landlords still litigating as of the article.
- **RealPage — private MDL.** The December 2023 denial of the landlords' motion to dismiss found a plausible horizontal "rim" from parallel price increases plus plus factors — notably **raising rents during periods of high vacancy**, conduct against individual self-interest. The court refused *per se* treatment because plaintiffs alleged no direct communications, no join dates, and no absolute delegation of rent-setting.
- **Gibson v. Cendyn — the counter-pole.** Las Vegas Strip hotels licensed Cendyn's revenue-management software. Claims dismissed: **no pooling of confidential data and no obligation to follow the algorithm's recommendations.** The district court likened the algorithm to an attorney generalising from past engagements; the Ninth Circuit affirmed on **15 August 2025**, holding the licences were ordinary sales contracts that imposed no restraint, so no rule-of-reason inquiry was needed. Plaintiffs had abandoned the hub-and-spoke "rim" theory on appeal.
- **California AB 325.** Prohibits using or selling a pricing algorithm as part of a contract, combination or conspiracy to restrain trade, or coercing another person to adopt/adhere to its recommendations. It **drops the CSI-exchange requirement** and lowers pleading to "plausible" facts that need not exclude independent action — a materially lower bar than federal law.
- **The liability gradient across the five airline scenarios** (the article's most transferable output):
  1. Confidential data pooled into a shared model, all follow recommendations → **substantial risk** (*RealPage*-like).
  2. Public inputs at inference; confidential data only in training → low federal risk (*Gibson*-like), some AB 325 exposure.
  3. General-purpose model on each airline's own server, siloed → **minimal** federal risk.
  4. Public model, shared learning, but no knowledge rivals use it and different prompts → **borderline**; mutual awareness is the missing plus factor.
  5. Airlines agree to use the same model with the same prompts and to follow the output → **highest risk**; under AB 325, "the AI algorithm becomes the meeting room, and the agreed-upon prompts serve as the minutes."
- **The authors' closing reframe:** regulators "need not wait for an AI system to send smoke signals between competitors"; what matters is whether firms "knowingly created or joined a system that precludes competitive independence."

## Mechanism / why it happens
The legal mechanism is *not* that algorithms are magic. It is that a shared system can perform the three functions a cartel performs: (i) exchange current, firm-specific, nonpublic information; (ii) make participation mutually known; and (iii) enforce adherence through defaults, monitoring and auto-accept. Remove any one and the claim weakens — which is exactly why the doctrine is a good experimental template: each factor is an ablation.

Alternative reading worth testing: courts may be over-reading "adherence" as agreement when it is just a firm buying a better forecast. *Gibson* is the evidence that this reading wins when discretion is preserved and no confidential data crosses users.

## Limitations and threats to validity
- **Practitioner commentary, not peer-reviewed empirics.** No data, no measurement, no coding of cases.
- **Doctrine is unsettled and circuit-dependent.** *Gibson* (9th Cir.) and DOJ's position diverge; the article itself calls the area "nascent" and "fluid." DOJ filed an amicus brief in *Gibson* arguing that an algorithm provider's "pitch" plus joint use can be an invitation-and-acceptance — a theory the Ninth Circuit did not adopt.
- **"Agreement" is anthropomorphic.** The article assumes human users with knowledge and intent. Fully autonomous agents may produce the same outcomes with no human who knows anything — the open question for §1.
- **Plus factors are not a checklist.** The article's list is a summary; different circuits weight them differently, and none is necessary or sufficient.

## Relevance to the sprint
- **Q2.3 (the core link).** Supplies the only fully developed external standard for "convincing evidence" in the folder, and it is *not* outcome-based: high prices, parallel moves and conscious parallelism are explicitly insufficient. The ML literature's default metric — supracompetitive price — would fail in a US court.
- **Q1.1** — reframes the experimental levers as legal factors: data pooling, mutual awareness, adherence/auto-accept, shared prompts, retained discretion.
- **Q1.5** — each legal factor suggests a restriction to ablate: remove the shared data field, remove awareness, force discretion, break prompt uniformity.

## Operationalising the doctrine into a detector

The table is **my translation**, not the authors'. Left column = factor the article treats as probative; right column = what a harness must log and a first-pass metric.

| Legal factor | What it means mechanistically | Log artifact required | Weekend metric |
|---|---|---|---|
| Exchange of **current, specific, nonpublic, competitively sensitive** information | Agent B's price is a function of Agent A's private state | Every input field written to / read from the shared system, with owner ID and timestamp | Mutual information between A's private demand/cost and B's price, vs. a no-pooling control |
| **Bi- or multi-lateral** exchange | Information flows among ≥2 competitors, not just vendor→client | Direction of data flow per record: user→pool, pool→user, user→user | Fraction of each recommendation's inputs contributed by other users |
| **Mutual awareness** of participation | Agents know rivals use the same system | Model ID + system-prompt hash + vendor/system ID per agent; transcripts mentioning rivals | Same-model / same-prompt-hash fraction; explicit "others are using this" statements |
| **Adherence / obligation** to recommendations | Auto-accept, compliance monitoring, contractual frequency requirements | Recommendation event + accept/override event + config flags | Override rate; distribution of \|price − recommendation\|; share of auto-accepts |
| **Retained discretion** (the *Gibson* defence) | Firms can and do deviate | Same as above, plus use of alternative tools/prompts | Entropy of price conditional on recommendation; count of distinct strategies |
| **Shared purpose / same prompts** (the "minutes") | Coordination lives in the prompt, not the model | Full prompt text and template hashes over time | Prompt similarity across agents; synchronized prompt edits |
| **Conduct against self-interest** (the *RealPage* vacancy point) | Pricing high when own demand is low | Own state (occupancy, inventory, demand) + price | Price–own-demand correlation with the "wrong" sign |
| **Prior collusion / intent** | Planning language, retaliation design | Message/scratchpad logs, tool calls | Explicit coordination or retaliation language; plan–action consistency |
| **Market structure** | Concentrated, homogeneous, repeated interaction | Market metadata (N, HHI, demand params, horizon) | Already an experimental knob — record it |
| **Public distancing / rebuttal** (from *Eturas*) | An agent objected or opted out | Objection messages, refusals, override streaks | Presence of explicit objection; systematic deviation |

**What this implies for logging design.** (1) Log *inputs by owner*, not just actions — the pooling factor is invisible in an action-only trace. (2) Log *recommendation–action pairs* — adherence is the single most legally loaded variable and is trivially cheap to record. (3) Log *identity and configuration* (model, prompt hash, vendor) — mutual awareness is otherwise unfalsifiable. (4) Keep an *append-only* copy the agents cannot write to, because agents that can edit their transcripts will (see `../../02-incidents/openai-huggingface-2026.md`: ~7% of evaluated transcripts contained successfully spoofed tool calls). (5) Record *counterfactual* runs — the doctrine's "against self-interest" factor is only measurable against a but-for price.

## Project hooks (48-hour sized)
1. **Plus-factor scorecard.** Run a 2×2×2 in any pricing harness: pooling on/off × awareness on/off × auto-accept on/off. Score each cell with the metrics above and check whether the scorecard ranks conditions the way the doctrine would. 8 cells × 5 seeds is ~$60–150.
2. **"Gibson control."** Add an explicit override affordance and a public-data-only input mode. Prediction from the case law: collusion collapses. This is a clean, legally motivated negative control that no ML paper currently runs.
3. **Prompt-as-minutes test.** Two conditions with identical economics: (a) each agent gets its own paraphrase of the same instruction; (b) all agents share one verbatim prompt. If (b) colludes more, that is the "shared prompts = agreement" theory in miniature, and it is measurable in a weekend.

## What this paper does NOT test
No LLM agents, no experiments, no data. It does not say how to *distinguish* tacit algorithmic coordination from competition empirically — it says what a court would need. It also does not address whether an autonomous agent can form the *mens rea*-adjacent knowledge the doctrine assumes.

## Related notes in this folder
- `tomasev-2026-distributional-agi-safety.md` — the opposite bet: markets and auditability as the safeguard.
- `../01-markets/fish-2024-algorithmic-collusion-llms.md` — produces the outcome (high prices) that this article says is legally insufficient.
- `../01-markets/agrawal-2025-double-auction.md` — the closest thing to a logged harness with communication and oversight levers.
- `../../02-incidents/realpage-doj-2024.md` — the fact pattern the plus factors were built for.
- `../../02-incidents/gibson-cendyn-2024-2025.md` — where the theory failed, and why.
- `../../02-incidents/eturas-2016.md` — the EU analogue: silence plus a system message can be participation, with a rebuttal route.

## Verification log
- Read: full article text via `https://www.americanbar.org/groups/antitrust_law/resources/magazine/2025-fall/coordination-code-rethinking-antitrust-liability-age-ai-pricing/` (rendered through a text proxy because the ABA page is JS/nav-heavy; the article body — Parts I–IV — was read in full).
- Corroborated: case names, docket numbers, the 8 Aug 2025 Greystar settlement and its terms (ABA article + `https://www.greystar.com/business/about-greystar/newsroom/greystar-reaches-agreement-with-us-department-of-justice-and-private-class-action-plaintiffs`); the 9th Cir. affirmance date and reasoning (ABA article + `https://connectontech.bakermckenzie.com/united-states-ninth-circuit-clarifies-limits-of-antitrust-liability-for-algorithmic-pricing-tools/`).
- Numbers spot-checked: yes — $ figures and dates above are from the fetched article or the Greystar release; no damages figures are asserted in the article.
- Could not confirm: the current (Oct 2026) procedural posture of *RealPage* itself and the MDL's final approval; the article is dated Fall 2025. Treat "still litigating" as true as of publication, not today.
- Note on the "plus factors" list: the article presents it as a synthesis. I did not independently verify each factor against the underlying cases; *Container Corp.* is the only case the article anchors for the information-exchange point.
