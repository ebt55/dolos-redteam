---
id: amazon-nessie-2023
date: 2023-09-26
type: enforcement
actors: ["FTC", "17 state AGs", "Amazon.com Inc.", "Jeff Wilke (alleged architect, quoted)"]
status: "antitrust suit filed; allegations unproven; case pending (2026 status unconfirmed)"
verification: "primary-source"
sources: ["https://www.ftc.gov/system/files/ftc_gov/pdf/1910134amazonecommercecomplaintrevisedredactions.pdf", "https://www.ftc.gov/news-events/news/press-releases/2023/09/ftc-sues-amazon-illegally-maintaining-monopoly-power"]
---

# Amazon "Project Nessie" (FTC v. Amazon, 2023– )

## Date
Complaint filed **26 September 2023** (W.D. Wash., No. 2:23-cv-01495-JHC); revised redacted complaint filed **2 November 2023**.

## Actors
FTC and 17 state attorneys general as plaintiffs; Amazon.com Inc. as defendant. The complaint quotes Jeff Wilke, then CEO of Amazon's Worldwide Consumer business, on the design intent.

## What happened
The complaint's §VII is headed "Amazon Has Manipulated Other Online Stores' Pricing Algorithms Into Increasing Prices." It alleges that Amazon created a secret algorithm, **"Project Nessie,"** to identify products for which it predicted other online stores would follow Amazon's price increases. When activated, the algorithm raised Amazon's price on those products and, when other stores followed, **kept the higher price in place**. The complaint alleges Nessie was deemed "an incredible success," generated **more than $1 billion in excess profit**, and was **turned off during periods of heightened outside scrutiny and back on when Amazon thought no one was watching**. Separately (¶20), the complaint describes an anti-discounting algorithm conceived by Wilke to avoid a "perfectly competitive market," using a "game theory approach" of never making the first move and copying rivals' moves "to the penny," so that rivals' price cuts produce only lower margins, not scale — after which Amazon predicted "prices will go up."

## Coordination mechanism
**Algorithmic price leadership plus follower algorithms — with no agreement.** Amazon does not need rivals' consent: it needs their pricing rules to be *predictably responsive*. Nessie is alleged to be a probe that finds the price level at which competitors' algorithms will follow, and then holds it. The coordination is unilateral in intent and multilateral in effect. Note the legal hook: this is pleaded as **monopolisation (§2 Sherman) and unfair methods of competition (§5 FTC Act)**, not as a §1 conspiracy.

## Legal status
**Allegations in a pending civil suit; nothing proven.** Amazon disputes the claims. The case's 2026 posture (trial, summary judgment, settlement, or change of administration/enforcement priorities) is **not confirmed** here. Treat every number above as an allegation.

## Why it matters for AI-agent collusion
- **The reverse-direction case.** The collusion literature asks "can agents coordinate?" Nessie asks "can one agent *exploit* others' willingness to follow?" If competing LLM pricing agents share a prior toward matching (Fish et al. document exactly this), then a leader can ratchet the market without any communication. A weekend experiment can test this directly: one "prober" agent raises price in small steps, N follower agents with standard profit-maximising prompts, no communication channel. Measure the ratchet.
- **Detection without messages.** The evidence is behavioural: price increases that are withdrawn when unobserved, and follow-on increases by rivals. That maps to two loggable signals — *monitoring-sensitive behaviour* and *response asymmetry* (rivals match increases faster than decreases).
- **Monitoring changes the behaviour.** Nessie was allegedly switched off "during periods of heightened outside scrutiny." That is the real-world analogue of sprint Q3.4 ("what does a coalition do when it learns it is being watched?") and of Kale et al. 2025 on monitor awareness. It also means a detector that is visible can be gamed; a hidden one changes nothing about what you can later prove.
- **Legal caution.** If AI agents achieve the same outcome with no agreement, §1 may not reach it; the Amazon case suggests §2/§5 theories (exploiting a bottleneck, unfair method) may fit better than conspiracy. Do not label a Nessie-style ratchet "collusion" in a sprint write-up without saying which legal sense you mean.

## Sources
1. FTC v. Amazon.com Inc., Revised Redacted Complaint (2 Nov 2023), §§I, V, VII — https://www.ftc.gov/system/files/ftc_gov/pdf/1910134amazonecommercecomplaintrevisedredactions.pdf
2. FTC press release, 26 Sept 2023 — https://www.ftc.gov/news-events/news/press-releases/2023/09/ftc-sues-amazon-illegally-maintaining-monopoly-power

## Verification log
- Read: the FTC press release in full; the complaint's introduction (¶¶1–34) and §VII (¶¶22–23, including the "$1 billion" and on/off allegations).
- Confirmed: filing date, court, parties, the existence and described operation of Project Nessie, the >$1B excess-profit allegation, the on/off-during-scrutiny allegation, the Wilke "game theory" description, and that the claims are §2/§5 (not §1).
- Not confirmed: the current status of the case; whether the Nessie allegations survived any motion to dismiss; the trial court's treatment of them. The complaint is advocacy and heavily redacted in places.
