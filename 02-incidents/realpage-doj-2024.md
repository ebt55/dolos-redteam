---
id: realpage-doj-2024
date: 2024-08-23
type: enforcement
actors: ["DOJ Antitrust Division", "8 state AGs", "RealPage Inc.", "Greystar Management Services", "Cortland", "other landlord defendants"]
status: "civil suit pending against RealPage and remaining landlords; consent settlements with Cortland (2025) and Greystar (8 Aug 2025), no admission of wrongdoing"
verification: "primary-source"
sources: ["https://www.justice.gov/opa/pr/justice-department-sues-realpage-algorithmic-pricing-scheme-harms-millions-american-renters", "https://www.greystar.com/business/about-greystar/newsroom/greystar-reaches-agreement-with-us-department-of-justice-and-private-class-action-plaintiffs"]
---

# US v. RealPage (2024– ) — data pooling as the alleged agreement

## Date
Filed **23 August 2024**, U.S. District Court for the Middle District of North Carolina (No. 1:24-cv-00710).

## Actors
DOJ Antitrust Division with the Attorneys General of North Carolina, California, Colorado, Connecticut, Minnesota, Oregon, Tennessee and Washington; RealPage Inc. (Richardson, Texas); landlord defendants including Greystar Management Services and Cortland.

## What happened
The complaint alleges that RealPage contracts with competing landlords who **agree to share nonpublic, competitively sensitive information** — daily rent rolls, occupancy forecasts, lease terms — which RealPage uses to train and run algorithmic pricing software that returns recommendations built from the landlords' *and their rivals'* data. DOJ alleges violations of **§§1 and 2 of the Sherman Act**: an unlawful information exchange/coordination among landlords, and monopolisation of commercial revenue-management software (RealPage alleged at roughly **80% share**).

The complaint leans on documents rather than economics alone. RealPage described its products as "driving every possible opportunity to increase price," "avoid[ing] the race to the bottom in down markets," and "a rising tide raises all ships"; one executive said there is "greater good in everybody succeeding versus essentially trying to compete against one another"; a landlord wrote that the algorithm "uses proprietary data from other subscribers to suggest rents and term. That's classic price fixing…" DOJ also emphasises adherence machinery: **"auto accept" functionality and pricing advisors who monitor landlords' compliance**, plus training to limit concessions.

## Coordination mechanism
**Hub-and-spoke with pooled data at the hub.** The alleged agreement is not a meeting; it is the combination of (i) contributing current, granular, nonpublic data knowing rivals do the same, (ii) receiving recommendations derived from that pool, and (iii) a product designed to maximise adherence. DOJ pleaded **rule of reason**, not *per se* — an important signal that algorithmic coordination is litigated as an effects case.

## Legal status
**Alleged; unresolved against RealPage.** Consent settlements were reached with **Cortland** (earlier 2025) and **Greystar** (announced 8 August 2025). Greystar's release states the settlements "contain no admission of wrongdoing" and that it believes its use of RealPage software complied with law. Reported terms (per the ABA article): no use of algorithms generating recommendations from competitors' competitively sensitive data, no sharing of CSI, and a court-appointed monitor if it uses a non-certified third-party algorithm. RealPage and the remaining landlords continued to litigate as of late 2025; **current status as of October 2026 is *unconfirmed***.

## Why it matters for AI-agent collusion
- **The cleanest real-world instance of "the shared model is the agreement."** For an LLM analogue, the legally loaded facts are: what data each agent contributes, whether contribution is current and firm-specific, whether rivals' data reaches the recommendation, and whether the harness nudges acceptance.
- **Adherence is the smoking gun, not the price.** "Auto accept" and compliance monitoring are the features DOJ chose to highlight. A sprint harness that logs accept/override events reproduces the same evidence cheaply.
- **Rule of reason, not per se.** This is why Q2.3 needs more than "prices went up": the government itself had to plead effects and market definition.
- **Settlements as mechanism removal.** The Greystar/Cortland terms are essentially an ablation list — remove pooled CSI, remove mandatory adherence — which is exactly the intervention set a collusion experiment should test.
- **Contrast with *Gibson v. Cendyn*.** Same technology class, opposite result, because Cendyn's users neither pooled confidential data nor had to follow recommendations.

## Sources
1. DOJ press release, "Justice Department Sues RealPage for Algorithmic Pricing Scheme that Harms Millions of American Renters," 23 Aug 2024 — https://www.justice.gov/opa/pr/justice-department-sues-realpage-algorithmic-pricing-scheme-harms-millions-american-renters
2. Greystar, "Greystar Reaches Agreement with U.S. Department of Justice and Private Class Action Plaintiffs," 8 Aug 2025 — https://www.greystar.com/business/about-greystar/newsroom/greystar-reaches-agreement-with-us-department-of-justice-and-private-class-action-plaintiffs
3. ABA Antitrust Magazine, "Coordination by Code" (Fall 2025), for the settlement terms and rule-of-reason framing — https://www.americanbar.org/groups/antitrust_law/resources/magazine/2025-fall/coordination-code-rethinking-antitrust-liability-age-ai-pricing/

## Verification log
- Read: the full DOJ release (via a mirrored PDF because justice.gov returns an empty body) and the Greystar release in full; settlement terms cross-checked against the ABA article.
- Confirmed: filing date, court, parties, statutory claims, the ~80% share allegation, the verbatim internal quotes, auto-accept/advisors, the two settlements and the no-admission language.
- Not confirmed: the exact settlement date and terms for Cortland (taken from the ABA article); whether the Greystar consent decree was entered by the court; the case's 2026 posture. All DOJ characterisations remain **allegations**.
