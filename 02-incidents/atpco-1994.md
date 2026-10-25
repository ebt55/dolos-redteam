---
id: atpco-1994
date: 1994-03-17
type: enforcement
actors: ["DOJ Antitrust Division", "Airline Tariff Publishing Company (ATPCO)", "Alaska, American, Continental, Delta, Northwest, TWA, United, USAir"]
status: "consent decrees (United/USAir entered 1 Nov 1993; remaining defendants proposed 17 Mar 1994)"
verification: "primary-source"
sources: ["https://www.govinfo.gov/content/pkg/FR-1994-03-31/html/94-7672.htm"]
---

# US v. Airline Tariff Publishing (1992–1994) — coordination through a shared fare system

## Date
Complaint filed **21 December 1992** (D.D.C., No. 92-2854). United/USAir decree entered **1 November 1993**; proposed final judgment for the remaining defendants filed **17 March 1994**, published in the Federal Register **31 March 1994**.

## Actors
DOJ Antitrust Division; ATPCO, the industry's fare-dissemination utility; eight airlines (Alaska, American, Continental, Delta, Northwest, TWA, United, USAir).

## What happened
DOJ alleged that the airlines used ATPCO's computerised fare-dissemination system to reach and effectuate agreements to raise fares, eliminate discounted fares, and set fare restrictions. The mechanism was not secret meetings: it was **the fare file itself**. Airlines posted fares with **first ticket dates** (the date a fare becomes available) and **last ticket dates**, plus **footnotes**, **tags** and fare-basis codes; by posting, withdrawing and re-posting fares with particular dates, carriers could signal intentions, test rivals' responses, and negotiate without ever selling a ticket at the posted price. DOJ also alleged a conspiracy to operate the dissemination system in a way that "unnecessarily facilitates coordinated interaction."

## Coordination mechanism
**Signalling through a shared business record.** A posted fare with a future first ticket date is not an offer to sell; it is a message ("I intend to raise BOS–LAX on the 15th; will you match?"). The decree's theory was that the *information architecture* — timing, visibility, and fields not needed for actual sale — was the coordination channel. The remedy was architectural: ban dissemination of first ticket dates; bar tags and duplicate/empty footnote designators; stop ATPCO from showing an airline's fare changes to other airlines before they reached the reservation systems; cap dissemination frequency at CRS update rates.

## Legal status
**Consent decrees, not adjudicated liability.** The judgment states it "shall not be evidence against or an admission by any party." American expressly denied the allegations and consented only to avoid litigation, on the strength of a DOJ letter of interpretation.

## The line DOJ drew (and why it matters most)
The January 1994 Doyle letter — made part of the record — states that **weekend/off-hour fare increases using bona fide fares are not prohibited**, because the airline is "for at least twenty-four hours at risk of losing sales," so the fare is a real offer and not a message. Signalling via **prices you would actually honour is lawful**; signalling via **placeholder fares you never intend to sell is not**. That is a workable, testable distinction.

## Why it matters for AI-agent collusion
- **The 1994 ancestor of the Artifactory directory-name message board.** In both, agents/firms used a shared, legitimate business system as a side channel, and the "message" was a modification of a record that had a real business function. The sprint's Q3.1 ("can actions, tools or other side channels be the conduit?") is this case with LLMs.
- **A concrete legal test for action-as-message.** Ask of any action: *would the actor take it if no rival could observe it?* If yes, it is a bona fide action; if no, it is a signal. That is directly implementable as a counterfactual in a harness (run with/without observability of the action).
- **Remedies target the channel, not the intent.** The decree did not require proving what each airline meant; it removed the fields that made cheap, costless, non-binding communication possible. Sprint Q1.5 ("which single restriction removes the most collusion at least cost?") is exactly this style of intervention.
- **Caution about the later history.** A 2015–2016 DOJ review of airline pricing and capacity coordination reportedly ended without enforcement action; I could **not confirm** that against a primary source, so treat it as *unconfirmed* and do not build on it.

## Sources
1. *United States v. Airline Tariff Publishing Co.*, proposed final judgment and competitive impact statement, 59 Fed. Reg. (31 Mar 1994) — https://www.govinfo.gov/content/pkg/FR-1994-03-31/html/94-7672.htm
2. Same document, §IV prohibited conduct and the Doyle letter of 21 Jan 1994 (included in the Federal Register notice)

## Verification log
- Read: the full Federal Register notice, including the complaint summary, the final judgment's prohibitions, and the Doyle letter with DOJ's confirmations.
- Confirmed: parties, docket, dates, the specific banned fields (first ticket dates, tags, duplicate/empty footnote designators, pre-CRS dissemination, frequency limits), the "not an admission" language, and the bona-fide-fare safe harbour.
- Not confirmed: whether the court entered the remaining defendants' judgment as proposed; any later modification or termination of the decrees; the 2015–2016 review.
