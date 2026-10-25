---
id: topkins-2015
date: 2015-04-06
type: enforcement
actors: ["David Topkins (poster seller)", "DOJ Antitrust Division", "co-conspirators (unnamed)"]
status: "criminal charge filed; guilty plea agreed, subject to court approval"
verification: "primary-source"
sources: ["https://www.justice.gov/archives/opa/pr/former-e-commerce-executive-charged-price-fixing-antitrust-divisions-first-online-marketplace"]
---

# US v. Topkins (2015) — the first algorithmic price-fixing prosecution

## Date
Conduct: as early as September 2013 to about January 2014. Charge announced **6 April 2015** (N.D. Cal., San Francisco).

## Actors
David Topkins, a former executive of an e-commerce seller of posters, prints and framed art; unnamed co-conspirators; DOJ Antitrust Division, San Francisco Office, with the FBI. The investigation was part of a broader federal probe into price fixing in the online wall-décor industry.

## What happened
Topkins and co-conspirators agreed to fix the prices of certain posters sold through Amazon Marketplace in the US. To implement the agreement they **adopted specific pricing algorithms** for those posters, "with the goal of coordinating changes to their respective prices," and **wrote computer code that instructed algorithm-based software to set prices in conformity with this agreement**. A one-count felony information was filed; Topkins agreed to plead guilty, pay a **$20,000 criminal fine**, and cooperate. DOJ described it as its first criminal prosecution targeting e-commerce.

## Coordination mechanism
An explicit human agreement, executed by code. The algorithm is the *instrument*, not the source, of the coordination: the conspirators decided the outcome and programmed the software to hit it. This is the "algorithm as enforcer" pattern — no machine learning, no emergent behaviour, no communication between programs.

## Legal status
Charged and agreed to plead guilty as of the press release; the plea agreement was "subject to court approval." **Sentencing details are *unconfirmed*** — I did not fetch a sentencing document. Do not describe this as a conviction without checking.

## Why it matters for AI-agent collusion
- **The baseline case.** It fixes the legal intuition that "a human agreed, then wrote code" is ordinary cartel conduct. Everything the sprint studies begins where this case stops: no human agreement, and coordination that emerges from the agents themselves.
- **The quote that has aged well.** AAG Bill Baer: "We will not tolerate anticompetitive conduct, whether it occurs in a smoke-filled room or over the Internet using complex pricing algorithms." The sprint's question is what to do when there is no smoke-filled room *and* no programmer who decided the price.
- **Evidentiary lesson.** The prosecution's core exhibits were the agreement and the code that implemented it — intent plus artefact. A collusion detector for LLM agents has the code (the prompt/harness) but often not the intent; that gap is precisely sprint Q2.3.
- **Contrast with *Meyer v. Kalanick*.** Same era, same technology narrative, opposite outcome: criminal enforcement against a self-dealing seller succeeded where a consumer class action against a platform was sent to arbitration.

## Sources
1. DOJ Office of Public Affairs, "Former E-Commerce Executive Charged with Price Fixing in the Antitrust Division's First Online Marketplace Prosecution," 6 April 2015 — https://www.justice.gov/archives/opa/pr/former-e-commerce-executive-charged-price-fixing-antitrust-divisions-first-online-marketplace
2. Information (charging document), linked from the release — https://www.justice.gov/sites/default/files/opa/press-releases/attachments/2015/04/06/topkins_information.pdf (linked, not independently read)

## Verification log
- Read: the DOJ press release in full (via text proxy; justice.gov returns an empty body to direct fetch).
- Confirmed: date, court, charge, conduct period, $20,000 fine, algorithm/code language, "first e-commerce prosecution" framing.
- Not confirmed: plea acceptance, sentencing date/terms, identities of co-conspirators.
