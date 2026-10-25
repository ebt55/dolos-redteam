# Dolos handoff pack

*Written 25 Oct 2026 by a separate Claude session that reviewed the `07-dolos` work.*

> **Latest, 25 Oct about 17:15 IST: [13-ENDGAME-PLAN.md](13-ENDGAME-PLAN.md).** The last-24-hours plan. Paste-in: [14-PASTE-ENDGAME.md](14-PASTE-ENDGAME.md). B3 judging protocol: [15-B3-JUDGE-PROTOCOL.md](15-B3-JUDGE-PROTOCOL.md). The reviewing session judges; the instance generates.
>
> **Update, 25 Oct about 17:00 IST: [12-REDACTION-VERDICT.md](12-REDACTION-VERDICT.md).** The secret-redaction candidate is real and was found independently, but it is probably a scrubbed-training-data artefact. A ~30-minute test in §4 decides it.
>
> **Update, 25 Oct about 11:30 IST: read [10-COURSE-CORRECTION.md](10-COURSE-CORRECTION.md) first.** After the overnight run, the review found that several nulls weren't valid tests. New embedding evidence ([evidence/](evidence/)) points at an untested domain: **agentic tool use with hex strings and secrets**. Paste-in message: [11-PASTE-COURSE-CORRECTION.md](11-PASTE-COURSE-CORRECTION.md).

This folder is for the instance working in `C:\Users\ebin\deepseek-ground\ai-collusion-sprint-oct\07-dolos`. It holds:
- an external review of that work;
- a re-prioritised plan;
- a hypothesis list;
- step-by-step protocols;
- the mechanism (Task 2) and reference-free audit (Task 3) playbooks;
- the evidence standards;
- an exhaustive backlog;
- a write-up skeleton.

**Status of this pack.**
- Nothing in it was run on the GPU.
- The review's numbers come from re-reading your own `runs/` files on the CPU.
- Code in `code-sketches/` is **untested**: read it, adapt it, and test it on 2–3 prompts before any batch run.

## Reading order

| # | File | Read when | Time |
|---|---|---|---|
| 1 | [01-REVIEW.md](01-REVIEW.md) | First. What is wrong with the current direction, with evidence. | 10 min |
| 2 | [02-PLAN.md](02-PLAN.md) | Second. The ordered phases, time boxes and go/no-go gates. | 10 min |
| 3 | [03-HYPOTHESES.md](03-HYPOTHESES.md) | Before choosing what to run. Ranked hypotheses and what would tell them apart. | 10 min |
| 4 | [protocols/](protocols/) | Before each experiment. Exact designs, sample sizes, metrics, kill criteria. | per protocol |
| 5 | [04-MECHANISM.md](04-MECHANISM.md) | Once a behaviour passes its gate (Task 2). | 15 min |
| 6 | [05-REFERENCE-FREE-AUDIT.md](05-REFERENCE-FREE-AUDIT.md) | Once a behaviour passes its gate (Task 3). | 15 min |
| 7 | [06-EVIDENCE-STANDARDS.md](06-EVIDENCE-STANDARDS.md) | Before writing any claim. | 5 min |
| 8 | [07-BACKLOG.md](07-BACKLOG.md) | When a phase ends early or a lead dies. Full list of things to try. | browse |
| 9 | [08-WRITEUP-SKELETON.md](08-WRITEUP-SKELETON.md) | From about 12 h before the deadline. | 10 min |
| 10 | [code-sketches/](code-sketches/) | When building harnesses. Untested starting points. | — |

## Protocols

| ID | Protocol | Tests |
|---|---|---|
| P0 | [Shared harness conventions](protocols/P0-shared-harness.md) | Loading, decoding, templates, output format |
| P1 | [Secret-in-context MI and encode/decode](protocols/P1-secret-in-context.md) | Steganographic encoding (H1) |
| P2 | [Typography / whitespace channel](protocols/P2-typography-channel.md) | The A7 drift lead (H1, H2) |
| P3 | [Untrusted-monitor collusion](protocols/P3-monitor-collusion.md) | Marker or self-recognition leniency (H2, H3) |
| P4 | [Long-form and multi-agent sampling](protocols/P4-longform-sampling.md) | Broad discovery |
| P5 | [Repeated market games](protocols/P5-repeated-games.md) | Tacit or explicit collusion (H4) |
| P6 | [Self-recognition and private codes](protocols/P6-self-recognition.md) | H3, H5 |
| P7 | [Data-driven diffing](protocols/P7-data-driven-diffing.md) | ADL, KL tail map, NMF, empty-template sampling |
| P8 | [Trigger search](protocols/P8-trigger-search.md) | Conditional behaviours |
| P9 | [Confession and elicitation](protocols/P9-elicitation.md) | Self-report, prefill, persona |
| P10 | [Sabotage, sandbagging, eval-awareness](protocols/P10-sabotage-sandbagging.md) | H6, H7 |
| P11 | [Controls: benign FT, base-vs-base, positive control](protocols/P11-controls.md) | Required by every claim |

## Rules of engagement

1. **Freeze the NO-bias line.** It is an L1 style shift that the parent mostly shares (see the review). Keep it only as a nuisance variable and as a test case for the audit.
2. **Long outputs, raw bytes.**
   - Always save full generations (≥400 tokens) as JSON with `ensure_ascii=True`, so NBSP shows up as `\u00a0` and zero-width characters stay visible.
   - Never judge a steganography question from rendered text.
3. **Every behavioural claim needs three comparisons:**
   - Dolos vs parent;
   - Dolos vs a benign fine-tune (Alpaca now; a matched one when it exists);
   - a within-Dolos counterfactual, e.g. secret 0 vs 1, or marker vs no marker.

   Use within-model differences-in-differences so that Dolos's general style shifts cancel out.
4. **Pre-register a gate before each run:** the metric, the threshold, and what you will do on pass or fail. Write it at the top of the analysis script.
5. **Time-box each phase.** If a gate fails, move on, record the null, and don't re-litigate it.
6. **Neutral decoding.** The checkpoint's `generation_config` (repetition penalty 1.1, top_k 20, top_p 0.8) must always be overridden. Report decoding settings in every table.
7. **Integrity and spending.**
   - Don't read other teams' write-ups, Discord threads or HF discussions about Dolos.
   - The organisers' public HF org listing is fair context.
   - **Ask the user first** before:
     - requesting access to any gated dataset (`Poseidon-Research/stego-bench`; `cais/wmdp` if it is gated);
     - spending their API credit on LLM judging (P4's blind judge alone is ~1,800 pairs × ~1k tokens);
     - renting a cloud GPU.

     Give a cost estimate with each request.
8. **Background long jobs.** Anything over ~2 minutes runs in the background with a log file.

## The six things to do first (about 4 hours)

1. **P2-A, typography emission shift** (30 min, teacher-forced, cheap). Gate on typography *minus* a frequency-matched control family, because Dolos's logits are flatter overall.
2. **P2-F, end-of-turn tail** (20 min). What does Dolos write after its first `<|im_end|>` when generation isn't stopped there? `<|im_end|>` and `<|endoftext|>` are among the most-drifted embedding rows.
3. **P1-B, uninstructed secret leakage** (45 min). A secret in the system prompt, an ordinary task, and a classifier that tries to predict the secret from the output. Include the no-secret baseline arm.
4. **P1-A, instructed encode/decode** (30 min). Dolos-encoder → Dolos-decoder vs parent→parent vs crossed pairs. A working private channel can't come from fine-tuning noise, but a 1.5B decoder is weak, so a null here doesn't override P1-B.
5. **P3-A, monitor marker test** (1 h). Does Dolos pass backdoored code when it carries a marker or is attributed to its own kind? The margin is the primary DV.
6. **P4 bulk sampling, launched in the background** (runs unattended). Long-form, agent-to-agent and multi-turn generations for later mining.

Then follow [02-PLAN.md](02-PLAN.md).
