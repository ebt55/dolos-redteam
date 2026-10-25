---
id: google-adtech-2023-2026
date: 2025-04-17
type: enforcement
actors: ["DOJ Antitrust Division", "Google LLC", "Judge Leonie Brinkema (E.D. Va.)"]
status: "liability found 17 Apr 2025 (§§1 and 2 Sherman Act); remedies ordered Sept 2026 without divestiture; appeal status unconfirmed"
verification: "primary-source"
sources: ["https://www.ballardspahr.com/-/jssmedia/main/articles/law360---google-ad-tech-ruling-creates-antitrust-uncertainty-updated.pdf", "https://www.theverge.com/policy/996847/judge-orders-google-to-make-its-ad-tech-work-with-rivals-and-share-ad-data-with-customers"]
---

# US v. Google (ad tech, 2023–2026) — when the auction itself is the mechanism

> **Included with a caveat.** This is *not* a collusion case. It is in the catalog because it is the clearest example of an **algorithmic market mechanism being the instrument of harm**, and because its remedy is the most fully worked-out "intervene on the information architecture" precedent since ATPCO.

## Date
Suit filed January 2023 (E.D. Va., No. 1:23-cv-00108). Liability opinion **17 April 2025**. Remedies ruling unsealed **16–17 September 2026**.

## Actors
DOJ Antitrust Division and state co-plaintiffs; Google LLC; Judge Leonie Brinkema.

## What happened
After a three-week bench trial, the court held that Google violated **§§1 and 2 of the Sherman Act** by monopolising two markets — **publisher ad servers** and **ad exchanges** for open-web display advertising — and by **tying** its publisher ad server (DFP) to its ad exchange (AdX), which the court treated as *per se* unlawful. The court rejected Google's argument that ad tech is a single two-sided market under *Ohio v. American Express*, defining two separate product markets instead.

## Coordination mechanism
Not collusion — **self-preferencing inside a real-time auction**. The harm runs through the rules of the market: who sees which bids, in what order, with what information. The conduct is algorithmic and structural (auction design, data advantage, tying), and the victims are publishers and advertisers rather than a cartel's customers. It belongs in this catalog because a sprint harness *is* an auction or pricing mechanism, and this case shows that the mechanism's designer is a party with interests.

## Legal status
**Liability established at trial** (a finding, not an allegation) — unusual in this catalog. On remedies, the court declined to order a breakup, calling structural remedies "neither realistic nor needed," and instead ordered **data sharing and interoperability with rivals** plus a **compliance monitor**. The exact terms of the unsealed order and any appeal are **not confirmed** here.

## Why it matters for AI-agent collusion
- **The "algorithm did it" defence fails when a party designed the algorithm.** In ad tech the defendant *was* the market operator. In an agent market, whoever runs the harness, the shared memory store, or the routing layer occupies the same position — and inherits the same exposure. Eturas (2016) made the same point for a booking-system administrator.
- **Remedies aimed at information asymmetry, not at intent.** Data sharing + interoperability + monitoring is the structural analogue of the RealPage/Greystar terms (no pooled data, no forced adherence). If the sprint asks "which single restriction removes the most collusion at least cost?", these are the real-world precedents for what a regulator will actually impose.
- **A caution about metrics.** The court's case was built on market definition and foreclosure, not on price levels. A collusion researcher who reports only "prices rose" is using an evidentiary standard this court did not need and antitrust plaintiffs rarely get to rely on.
- **Do not cite this as evidence about AI collusion.** It is an analogy about mechanism design and remedy design. Using it to claim "platforms cause collusion" would be a category error.

## Sources
1. Ballard Spahr (Law360), "Google Ad Tech Ruling Creates Antitrust Uncertainty," 29 May 2025 — https://www.ballardspahr.com/-/jssmedia/main/articles/law360---google-ad-tech-ruling-creates-antitrust-uncertainty-updated.pdf (liability holding, market definition, per se tying, proposed remedies)
2. *The Verge*, "Judge orders Google to make its ad tech work with rivals and share ad data with customers," 17 Sept 2026 — https://www.theverge.com/policy/996847/judge-orders-google-to-make-its-ad-tech-work-with-rivals-and-share-ad-data-with-customers (quoting the unsealed remedy ruling and the NYT report)

## Verification log
- Read: the Ballard Spahr article in full; the Verge item in full (it is short and links the unsealed ruling PDF).
- Confirmed: 17 April 2025 liability finding, E.D. Va., the two markets, §§1 and 2, per se tying, the *American Express* rejection, the Sept 2026 remedy of data sharing/interoperability plus a monitor and the refusal to break Google up.
- Not confirmed: the text of the remedies order itself (I did not fetch the 1,858-entry PDF); whether Google has appealed; the precise remedy terms.
