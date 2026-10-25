---
id: realpage-mdl-2023
date: "2023-12"
type: lawsuit
actors: ["Renters as putative class", "RealPage Inc.", "multifamily landlord defendants", "Judge Waverly Crenshaw (M.D. Tenn.)"]
status: "motion to dismiss denied Dec 2023; class settlements in progress (Greystar agreement in principle Aug 2025); merits unresolved"
verification: "secondary-source"
sources: ["https://www.americanbar.org/groups/antitrust_law/resources/magazine/2025-fall/coordination-code-rethinking-antitrust-liability-age-ai-pricing/", "https://www.greystar.com/business/about-greystar/newsroom/greystar-reaches-agreement-with-us-department-of-justice-and-private-class-action-plaintiffs"]
---

# In re RealPage Rental Software Antitrust Litigation (2023– ) — inferring the "rim"

## Date
Private actions filed from 2022; consolidated and transferred to the **Middle District of Tennessee in April 2023** (No. 3:23-md-03071). Motion to dismiss denied **December 2023**.

## Actors
A putative nationwide class of renters; RealPage Inc. as hub; multifamily landlord defendants as spokes; Judge Waverly Crenshaw.

## What happened
Plaintiffs alleged a **hub-and-spoke conspiracy**: RealPage (hub) takes clients' commercially sensitive pricing and supply data, runs its algorithm over the pooled data, and returns rent recommendations to each client (spokes); the landlords allegedly agreed to price off a pool of horizontal competitors' confidential data, knowing rivals used the same data and methods. The theory was pleaded as a **per se** §1 violation and under state antitrust laws.

In December 2023 the court **denied the landlords' motion to dismiss**. It found a plausible horizontal agreement — the "rim" — from parallel rent increases and changes in pricing strategy, plus **plus factors**, notably that landlords **raised rents during periods of high vacancy**, which cut against individual self-interest. It **declined to apply the per se rule**, because plaintiffs alleged no direct agreement or communications between landlords, no dates on which each joined, and no absolute delegation of rent-setting to RealPage. Under the rule of reason, it found the anticompetitive effects adequately pleaded.

## Coordination mechanism
Statistical and structural, not conversational. The rim is inferred from **conduct that is hard to explain as independent profit maximisation** (raising price while your own building is empty) combined with the shared data pool and the vendor's adherence machinery. No landlord-to-landlord messages are required.

## Legal status
**Pleading-stage victory for plaintiffs; no finding of liability.** Greystar announced an **agreement in principle** in August 2025 to settle the nationwide renter class, alongside its DOJ settlement, again with no admission of wrongdoing. Other defendants' settlements and any final approval are **not confirmed** here. The merits case against RealPage and non-settling landlords continues.

## Why it matters for AI-agent collusion
- **This is the most important methodological precedent in the catalog for Q2.3.** The court did not ask "are prices high?" It asked "is there conduct that a competitive agent would not choose?" — the vacancy point. That is a *counterfactual* test, and it is directly runnable in a simulation: compare each agent's price against the price its own state (low demand, high vacancy) would justify.
- **The per se refusal is the honest limit of algorithmic-collusion law.** Even with pooled data and a common vendor, a court wanted evidence of agreement before applying the harsh rule. Sprint projects should therefore report *graded* evidence, not a binary "collusion / no collusion."
- **"Rim" inference maps onto agent configuration.** If all agents run the same policy and know it, the rim is the shared harness. If they independently choose different tools, there is no rim. This is testable by varying prompt/config homogeneity.
- **Settlement structure reveals what defendants think is damning.** The injunctive terms that settle these cases (stop using competitor data, drop auto-accept, stop promoting the tool to peers) are a list of the mechanisms plaintiffs can prove.

## Sources
1. ABA Antitrust Magazine, "Coordination by Code: Rethinking Antitrust Liability in the Age of AI Pricing" (Fall 2025) — case description, December 2023 ruling, plus-factor reasoning, per se refusal — https://www.americanbar.org/groups/antitrust_law/resources/magazine/2025-fall/coordination-code-rethinking-antitrust-liability-age-ai-pricing/
2. Greystar press release, 8 Aug 2025 (agreement in principle with the nationwide renter class, no admission) — https://www.greystar.com/business/about-greystar/newsroom/greystar-reaches-agreement-with-us-department-of-justice-and-private-class-action-plaintiffs

## Verification log
- Read: the ABA article's description of the MDL in full; the Greystar release in full.
- Confirmed: April 2023 consolidation to M.D. Tenn., December 2023 denial of the motion to dismiss, the vacancy plus factor, the refusal of per se treatment, the August 2025 class agreement in principle.
- **Verification level is secondary-source.** I did not read the MDL opinion itself (CourtListener and Justia blocked automated fetches). The characterisation of the ruling is the ABA authors' and Greystar's, not mine from the order.
- Not confirmed: the MDL docket number (widely reported as 3:23-md-03071 but not verified here), which defendants have settled, any final approval, and the 2026 posture. There is a signal that a fairness hearing occurred in October 2026, but I could not read the order — treat as *unconfirmed*.
