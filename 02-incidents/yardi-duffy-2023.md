---
id: yardi-duffy-2023
date: 2023-09-08
type: lawsuit
actors: ["Wylie Duffy et al. (renters)", "Yardi Systems Inc.", "landlord defendants incl. Balke Brown Transwestern / 2B Residential", "Judge Robert S. Lasnik"]
status: "private class action pending against Yardi and non-settling landlords; partial settlements (Balke Brown, $295,000, filed for preliminary approval 16 Dec 2025)"
verification: "primary-source"
sources: ["https://archive.org/download/gov.uscourts.wawd.326049/gov.uscourts.wawd.326049.484.0.pdf"]
---

# Duffy v. Yardi Systems / In re Yardi Revenue Management (2023– )

## Date
Initial class complaint filed **8 September 2023** (W.D. Wash., No. 2:23-cv-01391-RSL; consolidated with 2:24-cv-01948 and 2:24-cv-02053). Settlement papers for one landlord defendant filed **16 December 2025**.

## Actors
Renter plaintiffs (Wylie Duffy et al.), represented by Hagens Berman as interim lead class counsel (appointed 28 March 2024); Yardi Systems Inc. as the software vendor; landlord defendants including Balke Brown Transwestern Inc. / 2B Residential LLC; Judge Robert S. Lasnik.

## What happened
Plaintiffs allege that Yardi conspired with landlord defendants to use its revenue-management software — **RENTmaximizer** and **Revenue IQ** — in a scheme to raise rents supracompetitively in multifamily housing, violating **§1 of the Sherman Act**. The alleged class period runs from 8 September 2019. Yardi is alleged to take client-entered and market data and issue rent-pricing recommendations to competing users. The case is the private-litigation twin of *RealPage*: same theory, different vendor, no DOJ involvement that I could confirm.

The most useful public artefact is the **settlement with Balke Brown** (a ~7,700-unit Midwest manager). Its terms are a de facto list of the mechanisms plaintiffs believe are unlawful:
- **$295,000** settlement fund (non-reverting), for a defendant with 1,507 units across 11 properties that used the product, average ~21 months of use.
- Three years of injunctive relief: no promoting revenue-management software to other managers/owners; **no licensing software that requires accepting recommended prices "with any particular frequency"**; no licensing without **written vendor confirmation** that a client's nonpublic data will not be used to recommend prices for another client, and that recommendations (even aggregated/anonymised) will not be disclosed to another client; **no enabling auto-accept** of recommendations; and a written policy barring staff from sharing nonpublic pricing, concession or discount information with other managers/owners.
- Evidentiary cooperation against the non-settling defendants.

## Coordination mechanism
Alleged **hub-and-spoke data pooling** with adherence features — the *RealPage* template. The settlement's injunctions are aimed at exactly three things: cross-client use of nonpublic data, mandatory/near-automatic adherence, and peer-to-peer promotion of the tool (the "everyone uses it" awareness channel).

## Legal status
**Allegations only; no liability finding.** The Balke Brown settlement is one defendant's; Yardi and other landlords remain defendants. The motion sought *preliminary* approval with a hearing set for 6 January 2026; final approval and the case's 2026 posture are **not confirmed** here. The settlement contains no admission (standard for class settlements).

## Why it matters for AI-agent collusion
- **It turns "what should a detector log?" into a contract.** The injunctive terms name the loggable facts: frequency of accepting recommendations, auto-accept flags, whether nonpublic data from one client influenced another's recommendation, and whether the vendor marketed the tool on the basis that rivals use it. Those four are directly implementable as instrumentation in an agent harness — and as ablations.
- **Frequency of adherence is treated as a design parameter, not a user choice.** That is a strong hint for experiment design: make "override rate" an experimental variable, not a nuisance parameter.
- **The monetary scale is sobering.** $295,000 for 1,507 units is small; the injunctive relief is the real remedy. For policy-minded sprint write-ups, the mechanism change matters more than damages.
- **A note on evidence quality.** Everything here comes from plaintiffs' own filing, which is advocacy. It is reliable for *what was alleged and what was agreed*, not for whether the conduct was unlawful.

## Sources
1. Plaintiffs' Motion for Preliminary Approval of Settlement with Balke Brown Transwestern and 2B Residential, *Duffy v. Yardi Systems*, No. 2:23-cv-01391-RSL (W.D. Wash., filed 16 Dec 2025), ECF 484 — https://archive.org/download/gov.uscourts.wawd.326049/gov.uscourts.wawd.326049.484.0.pdf
2. CourtListener docket for the consolidated case — https://www.courtlistener.com/docket/67775053/duffy-v-yardi-systems-inc/ (docket only; blocked to automated fetch)

## Verification log
- Read: the full 17-page preliminary-approval motion, including the factual background, settlement consideration, and all five injunctive terms.
- Confirmed: filing dates, docket number, consolidation, judge, product names, §1 claim, class period, $295,000, unit counts, and the verbatim injunctive terms.
- Not confirmed: whether preliminary/final approval was granted; the status of Yardi itself and other defendants; whether any regulator has sued Yardi.
