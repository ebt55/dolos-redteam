# 40-hour plan — from "we should do this" to a submitted PDF

**Deadline:** 25 Oct 2026, 23:59 AoE = **26 Oct 2026, 17:29 IST**. This plan was written for a 56-hour window; with ~45 hours left, read the T-minus anchors as **relative hours from now**, not as clock times. The ratios and the gates matter more than the labels. For the #1 project's specific 40-hour clock, see `../04-ideas/FINAL-SHORTLIST.md` §9.

The most important change from a normal 48-hour plan: **do not spend the first 8 hours reading.** The final shortlist has already made the choice; start the positive control by hour 4.

## The shape of a winning weekend

Three things must be true at submission:

1. **A positive control worked.** You reproduced a known collusion result in your environment, and you can show the run.
2. **One variable was manipulated.** Not two, not a "suite". One.
3. **The metric was pre-declared.** You can point to the config/commit where you fixed it.

Everything else — literature review, extra seeds, a beautiful UI — is optional.

## Hour-by-hour

### T−56 → T−50 (now: hour 0–6): choose and de-risk

- [ ] Pick **one** project from `../04-ideas/shortlist.md`. Write the one-sentence claim on paper.
- [ ] Pick the **positive control** and run it end-to-end. No new code. If it fails, switch projects *now*.
- [ ] Check API keys, `compute.env`, model IDs, and that a smoke test returns a parseable answer.
- [ ] Create the repo/branch and a `runs/` folder. Commit the config.
- [ ] Write the report skeleton: question, setup, result placeholder, limitations. 45 minutes, not 3 hours.

**Go/no-go:** positive control reproduces the expected direction (price above Nash, coalition advantage > 0, or the known detection figure). If not, go to the fallback in the shortlist.

### T−50 → T−40: build the one manipulation

- [ ] Implement the condition as a config flag, not a code fork. Two configs, same code path.
- [ ] Run **one seed** per condition. Check that the manipulation is visible in the logs (messages differ, channel is off, monitor sees 25%, etc.).
- [ ] Freeze the metric function and the seed list. Write them in the report skeleton.
- [ ] Estimate cost per run; multiply by planned runs. If > $100, cut conditions, not seeds.

**Go/no-go:** the manipulation is detectable in a single run and does not crash the harness.

### T−40 → T−28: pilot + main runs

- [ ] 3 seeds per condition. This is the pilot, not the result.
- [ ] Check variance. If the effect is smaller than the seed-to-seed SD, either increase seeds or simplify the metric.
- [ ] Launch the main batch in the background. **Log every call and every error.**
- [ ] While it runs: write the methods section, the limitations, and the figure code (against the pilot data).

**Go/no-go:** pilot shows the predicted direction with a plausible effect size. If null, decide now whether the null is the paper (it can be) or whether to change the manipulation once.

### T−28 → T−20: sleep

Non-negotiable. The most common failure mode is a tired team misreading its own logs at 3 a.m. Start the batch, sleep, analyse in the morning.

### T−20 → T−12: analysis and robustness

- [ ] Finish the main runs. Compute the pre-declared metric; do not add new metrics to the headline.
- [ ] One robustness check only: a second model, a second prompt, or a second seed batch. Report it as a robustness check, not a second paper.
- [ ] Bootstrap CIs over seeds (not rounds). Report N and the denominator.
- [ ] Make the headline figure. One figure, one message.
- [ ] Write the results section with the numbers already in the figure.

**Go/no-go:** the headline is one sentence and the figure supports it. If not, the paper is "we tested X and found Y", where Y is whatever you found — including a null or a failed manipulation.

### T−12 → T−7: write the report

Use this structure (5–8 pages):

1. **Question and claim** (0.5 page): what you tested, what you found, in plain language.
2. **Why it matters** (0.5): the sprint question and the gap.
3. **Related work** (0.75): 5–8 citations, positioned as "what was known / what was not".
4. **Setup** (1.5): environment, models, N, seeds, conditions, prompts (appendix).
5. **Metrics** (0.5): define them precisely; state the pre-registered threshold.
6. **Results** (1.5): the figure, one table, the numbers, the CI.
7. **Limitations** (0.5): at least three, honestly.
8. **What we would do next** (0.25).
9. **Appendix:** prompts, config, cost, run log.

- [ ] Figures at 300 dpi, readable at 50% zoom, colour-blind safe.
- [ ] Every number in the abstract appears in the results.
- [ ] Every paper cited in the report has a URL.

### T−7 → T−3: slides + recording + code

- [ ] 5-slide deck: question, setup, result, limitations, next. The recording is 3–5 minutes; rehearse once.
- [ ] Clean the repo: README with the exact commands, `requirements`/`uv.lock`, configs, a `results/` folder with the headline numbers.
- [ ] Remove API keys from the repo. Check `.gitignore`.
- [ ] Record the presentation in one take; do not edit for an hour.

### T−3 → T−1: submit

- [ ] Submit the PDF, code link, slides, recording, image.
- [ ] Verify the PDF opens on a different device.
- [ ] Check the track selection and the abstract length.
- [ ] Submit with at least 1 hour of buffer. AoE deadlines are unforgiving.

## Roles for a team of 2–5

| Role | Owns | Does not do |
|---|---|---|
| **Lead / writer** | Claim, report, slides, timeboxing | Debugging the harness at 2 a.m. |
| **Engineer** | Harness, configs, runs, logging | Rewriting the metric after seeing results |
| **Analyst** | Metric, CIs, figures, robustness | Adding new conditions |
| **Reader / critic** | Literature positioning, limitations, "what would a judge ask?" | Scope creep |
| **Presenter** (can be lead) | Recording, demo, narrative | Last-minute experiments |

With 2 people: lead+writer, engineer+analyst. With 1: cut the robustness check, not the positive control.

## What to cut when you are behind

Cut in this order:

1. The second model / second environment.
2. The extra seeds (but report the N you have).
3. The interpretability/mechanism section.
4. The pretty UI.
5. The related-work section (keep 5 citations).

**Never cut:** the positive control, the pre-declared metric, the limitations, the code link.

## The 20-minute standup questions

Ask every 4 hours:

- What is the one-sentence claim right now?
- What is the next result that would change our mind?
- What are we doing that is not on the critical path?
- If the deadline were in 6 hours, what would we submit?

## Ethics and dual-use

- Do not deploy colluding agents against real markets, real users, or real competitors. All experiments should be in simulated environments with your own accounts.
- If you build a covert-channel or steganography demo, keep the payload harmless and say so.
- If you red-team Dolos, do not publish weights or a turnkey exploit; publish the audit method and the behaviour description.
- Disclose API/model costs and any sponsor relationship in the report.

## Final checklist (copy into the repo)

```
[ ] PDF report, 5–8 pages, opens on another machine
[ ] Code repo public or zip, no keys, README with exact commands
[ ] Slides (PDF/PPTX)
[ ] Recording, 3–5 min, audio audible
[ ] Project image
[ ] Abstract < 200 words, includes the headline number
[ ] Track(s) selected
[ ] Team names + emails
[ ] Positive-control run included in the appendix
[ ] Limitations section has at least 3 items
[ ] All cited papers have URLs
```
