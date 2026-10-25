---
id: eturas-2016
date: 2016-01-21
type: enforcement
actors: ["Eturas UAB (system administrator)", "30 Lithuanian travel agencies", "Lithuanian Competition Council", "CJEU Fifth Chamber"]
status: "CJEU preliminary ruling; liability left to the national court"
verification: "primary-source"
sources: ["https://beta.bailii.org/eu/cases/EUECJ/2016/C7414.html"]
---

# Eturas (CJEU C-74/14, 2016) — silence, a system message, and a technical cap

## Date
Judgment **21 January 2016** (CJEU, Fifth Chamber, ECLI:EU:C:2016:42). Facts: 25–27 August 2009 onward; Lithuanian Competition Council decision 7 June 2012.

## Actors
Eturas UAB, administrator of the E-TURAS online travel booking system; 30 travel agencies using it; the Lithuanian Competition Council; the Lithuanian Supreme Administrative Court (referring court).

## What happened
On 25 August 2009 Eturas's director emailed agencies asking them to vote on cutting the online discount from 4% to 1–3%. On 27 August the system administrator sent, via each agency's internal mailbox in the booking system, a message announcing that online discounts would be capped in the 0–3% range and that discounts above 3% "will automatically be reduced to 3% as from 2:00 pm." The system was then modified so that discounts above 3% required extra technical steps. Agencies did not object and continued using the system. The Competition Council found a concerted practice by the agencies and by Eturas as facilitator, and fined them.

## Coordination mechanism
A **shared platform broadcast plus a default**: the cap was announced through the system everyone used, then embedded in the interface. Participation was inferred from awareness of the message plus continued use without public distancing — not from any bilateral communication. The Council's own phrase was that the system "eliminated the need for meetings."

## Legal status
A **preliminary ruling on legal standards, not a final finding of infringement**. The CJEU held:
- Mere dispatch of the message is **not** enough to establish that addressees "ought to have known" its content — the presumption of innocence precludes that.
- But where an operator **was aware** of the message, it may be **presumed** to have participated in a concerted practice unless it publicly distanced itself, reported the practice, or adduced other evidence — for example, **systematically granting discounts above the cap**.
- It is for the national court, under national evidence rules, to decide whether the message plus other objective and consistent indicia establish awareness.

## Why it matters for AI-agent collusion
- **"Silence is assent" is the default the law applies to a shared system.** For agents this is the natural failure mode: an agent that reads a coordination message in a shared channel, does not object, and then conforms looks exactly like a participating agency. A detector should log *non-objection plus adherence*, and treat objection/deviation as exculpatory.
- **The rebuttal is behavioural, not verbal.** The CJEU's example of exculpation is "systematic application of a discount exceeding the cap." Translated: **deviation is evidence of non-participation.** In an experiment, a control arm that overrides the recommendation every period is the analogue of the exculpated agency.
- **Platform-mediated coordination without agent-to-agent messaging.** This is the EU ancestor of the Artifactory and DSEwiki incidents: a shared, permissioned system whose ordinary use is also a communication channel. The legal question is not "did they talk?" but "did they know, and did they conform?"
- **Enforcement risk for tool vendors.** Eturas itself was not active in the travel market; it was liable as facilitator. That is the closest legal analogue to a vendor of an orchestration layer or shared memory store.

## Sources
1. Judgment, Case C-74/14, *Eturas and Others*, 21 January 2016 — https://beta.bailii.org/eu/cases/EUECJ/2016/C7414.html
2. EUR-Lex CELEX record — https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62014CJ0074 (dynamic page; the BAILII mirror above was the readable copy)

## Verification log
- Read: the full judgment (BAILII mirror), including the facts at §§5–17, the questions at §25, and the operative ruling at §50 and the disposition.
- Confirmed: dates, the 4%→0–3% cap, the automatic reduction, the "not prevented but required additional technical steps" finding, the fine on 30 agencies plus Eturas, and the exact rebuttal routes.
- Not confirmed: the final outcome of the national proceedings after the ruling.
