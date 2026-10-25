---
id: gibson-cendyn-2024-2025
date: 2025-08-15
type: lawsuit
actors: ["Las Vegas Strip hotel operators", "Cendyn Group LLC", "renters/hotel guests as plaintiffs", "Ninth Circuit panel", "DOJ (amicus)"]
status: "dismissed by district court; affirmed by Ninth Circuit 15 Aug 2025; no liability"
verification: "secondary-source"
sources: ["https://connectontech.bakermckenzie.com/united-states-ninth-circuit-clarifies-limits-of-antitrust-liability-for-algorithmic-pricing-tools/", "https://www.americanbar.org/groups/antitrust_law/resources/magazine/2025-fall/coordination-code-rethinking-antitrust-liability-age-ai-pricing/"]
---

# Gibson v. Cendyn (2024–2025) — the case that says shared software isn't a cartel

## Date
District court dismissal 2024 (D. Nev., No. 2:23-cv-00140-MMD-DJA); **Ninth Circuit affirmance 15 August 2025** (No. 24-3576).

## Actors
Plaintiffs (hotel guests, putative class); defendant Cendyn Group LLC, vendor of revenue-management software; Las Vegas Strip hotel operators as co-defendants; the Ninth Circuit panel; the DOJ, which filed an amicus brief **supporting the plaintiffs**.

## What happened
Plaintiffs alleged that Strip hotels unlawfully restrained trade by licensing Cendyn's algorithmic pricing software. Two theories: (i) a **hub-and-spoke conspiracy** — vertical agreements between Cendyn (hub) and each hotel (spoke), with a horizontal "rim" formed by the hotels' tacit agreement to use the software knowing rivals did too; and (ii) that the **series of vertical licences, taken together**, produced anticompetitive effects. The district court dismissed both. On appeal, plaintiffs **abandoned the hub-and-spoke theory** and pressed only the aggregate-vertical-restraint theory. The Ninth Circuit affirmed.

## Coordination mechanism
Alleged: tacit alignment through a common vendor. **Held insufficient** because two facts were missing relative to *RealPage*: there was **no pooling of confidential, competitively sensitive data** across hotels, and there was **no obligation to follow the algorithm's recommendations**. The licences were "ordinary sales contracts" that did not restrict hotels from using other tools or set prices; the court likened the algorithm to a tax adviser or attorney generalising from past engagements. Even **consciously parallel** conduct is not, by itself, a §1 violation, and higher prices alone do not establish one.

## Legal status
**Dismissed, affirmed on appeal — no liability.** This is the first federal appellate decision on the wave of algorithmic-pricing antitrust suits. It is a binding precedent in the Ninth Circuit only. The ABA article notes it may head to further appeals.

## The DOJ's contrary position (important, and not adopted)
DOJ's amicus brief argued that a pricing algorithm's "pitch" can be an **invitation to collective action** — for example, by signalling to each user that the same pitch was made to its competitors and that using the algorithm could help them avoid competition — and that **joint use can be acceptance** of that invitation. DOJ also argued that an algorithm's suggested common starting prices can be concerted action if multiple competitors start there, even if final prices diverge. The Ninth Circuit did not adopt this. DOJ has signalled more investigations of shared algorithms.

## Why it matters for AI-agent collusion
- **This is the negative control the sprint needs.** It tells you which experimental conditions should *not* count as collusion: same tool, no data pooling, no adherence obligation, retained discretion, no mutual commitment. If a detector fires there, it is producing false positives that would fail in court.
- **It isolates the two variables that matter.** Pooling of current nonpublic data, and obligation/adherence. Everything else — same vendor, same model, parallel outputs — was insufficient.
- **It exposes the fault line.** DOJ thinks mutual use plus a suggestive pitch is enough; the Ninth Circuit thinks that is just buying software. A weekend experiment cannot settle the law, but it *can* measure whether mutual use alone changes prices — which is the empirical question underneath the doctrinal split.
- **For LLM agents specifically:** two agents using the same commercial model API, with different prompts and no shared data, is the *Gibson* fact pattern. The sprint's most legally defensible "no collusion here" condition looks exactly like that.

## Sources
1. Baker McKenzie, "United States: Ninth Circuit Clarifies Limits of Antitrust Liability for Algorithmic Pricing Tools," 1 Sept 2025 — https://connectontech.bakermckenzie.com/united-states-ninth-circuit-clarifies-limits-of-antitrust-liability-for-algorithmic-pricing-tools/ (case analysis, DOJ amicus arguments, citations to the slip opinion)
2. ABA Antitrust Magazine, "Coordination by Code" (Fall 2025) — district court reasoning and the *RealPage* contrast — https://www.americanbar.org/groups/antitrust_law/resources/magazine/2025-fall/coordination-code-rethinking-antitrust-liability-age-ai-pricing/

## Verification log
- Read: both sources in full.
- Confirmed: 15 Aug 2025 affirmance, No. 24-3576, the abandonment of the hub-and-spoke theory on appeal, the "ordinary sales contracts" holding, the absence of data pooling and of any obligation to follow recommendations, and DOJ's invitation/acceptance amicus theory.
- **Verification level is secondary-source.** I did not read the Ninth Circuit opinion (Justia, CourtListener and the Westlaw Practical Law note all blocked automated fetches). Quoted characterisations are the two firms' summaries, not the opinion text.
- Not confirmed: the precise district-court dismissal date; whether a petition for rehearing or certiorari was filed; any subsequent DOJ statements of interest beyond those described.
