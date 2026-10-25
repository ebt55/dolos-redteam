---
id: meyer-v-kalanick-2016
date: 2016-03-31
type: lawsuit
actors: ["Spencer Meyer (plaintiff)", "Travis Kalanick", "Uber Technologies", "Judge Jed S. Rakoff", "Second Circuit"]
status: "motion to dismiss denied (2016); compelled to arbitration on appeal (2017); no merits ruling"
verification: "secondary-source"
sources: ["https://www.thecontingency.com/2017/08/uber-detours-price-fixing-case/"]
---

# Meyer v. Kalanick (2016–2017) — the pricing algorithm as hub

## Date
Complaint filed December 2015 (S.D.N.Y., No. 15-cv-9796). Motion to dismiss denied **31 March 2016**. Arbitration compelled on appeal **17 August 2017** (2d Cir., No. 16-1750-cv, by then *Meyer v. Uber Technologies*).

## Actors
Spencer Meyer, a Connecticut Uber user, as plaintiff; Travis Kalanick, Uber's co-founder, as defendant; Judge Jed S. Rakoff; the Second Circuit. Uber intervened to enforce its terms of service.

## What happened
Meyer alleged that Kalanick orchestrated a conspiracy among Uber drivers to charge the fares computed by the Uber algorithm — i.e., that drivers each agreed with Uber to charge certain fares "with the clear understanding that all other Uber drivers are agreeing to charge the same fares." Judge Rakoff held that this plausibly alleged a price-fixing agreement among Kalanick, Uber and the drivers, and denied the motion to dismiss. Uber then intervened and moved to compel arbitration under its terms of service. Rakoff denied that motion (29 July 2016), reasoning that Meyer lacked adequate notice of the arbitration clause. The Second Circuit **vacated** and held that Meyer was on inquiry notice because a hyperlink to the terms appeared on the payment screen and he clicked "Register"; it remanded only the question whether the defendants had waived arbitration by litigating.

## Coordination mechanism
Alleged **hub-and-spoke**: the platform's algorithm is the hub; each driver's acceptance of the platform terms is a vertical spoke; the horizontal "rim" is the shared understanding that every other driver is pricing off the same formula. No driver-to-driver communication is alleged — the coordination is mediated entirely by a common pricing rule.

## Legal status
**Never resolved on the merits.** The dismiss motion was denied (a pleading-stage win for plaintiff), then the case was pushed into individual arbitration, which effectively ends class-style private enforcement. Do not describe the allegations as proven — no court found an agreement.

## Why it matters for AI-agent collusion
- **The purest "algorithm as meeting room" theory**, a decade before the AI-pricing debate. If N agents run the same pricing policy, the *policy* is the rim. This is the same structure the *RealPage* and *Cendyn* cases fight over, and the same structure as two LLM agents sharing a system prompt.
- **Legal vulnerability of private enforcement.** The merits question was never answered because of an arbitration clause. For a sprint project, this is a reminder that "we found collusion" and "a court could remedy it" are separate claims.
- **Detector implication.** The alleged agreement left *no inter-agent messages at all*. Any detector built on communication logs would have found nothing here; the evidence was the common rule plus parallel pricing. That is the strongest argument in the catalog for logging **configuration** (model, prompt, pricing rule) as evidence, not just conversation.
- **Caveat.** The theory is aggressive: a platform setting a fare formula is also just… a platform setting prices. The *Gibson* line of cases is the counterweight.

## Sources
1. Barry Barnett, "Uber Detours Price-Fixing Case," *The Contingency*, 21 Aug 2017 — https://www.thecontingency.com/2017/08/uber-detours-price-fixing-case/ (quotes the March 2016 and July 2016 slip opinions and the Second Circuit's 2017 opinion)
2. Second Circuit opinion, *Meyer v. Uber Technologies*, No. 16-1750-cv (17 Aug 2017) — http://www.ca2.uscourts.gov/decisions/isysquery/a03b03b9-1a69-4b86-a734-e1f7de9de39e/3/doc/16-2750a_opn.pdf (linked from source 1; not independently fetched)

## Verification log
- Read: the *Contingency* post in full, including verbatim quotations from the Rakoff opinions and the Second Circuit.
- Confirmed: docket number, dates, the "clear understanding" allegation, denial of the motion to dismiss, denial then reversal on arbitration.
- Verification level is **secondary-source**: I did not read the primary opinions (Justia and CourtListener both blocked automated fetches). The quoted passages appear verbatim in the secondary source but I could not check them against the slip opinions.
- Not confirmed: the ultimate disposition of the remanded waiver question; whether any driver-side claims survived.
