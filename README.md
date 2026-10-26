# Dolos-1.5B red-team: an audit for a planted collusion behaviour

Submission to the [Apart Research AI Collusion Research Sprint](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25) (23–25 Oct 2026), Track 2: Detection and Audit of Collusion. The Dolos-1.5B red-teaming challenge asks three things:
1. Find the planted behaviour and show it is deliberate.
2. Explain how the model implements it.
3. Build an audit that works without a reference model.

**Author:** Ebin Babu Thomas, Independent AI Engineer & Researcher.

## Result in one paragraph
- **No deliberate hidden objective was found at our stated power.** Every result was compared with the parent (Qwen2.5-1.5B-Instruct) and a benign Alpaca fine-tune, and every gate was pre-registered.
- **Two Dolos-specific differences are real and replicated.**
  - **A NO shift on evaluative questions.** It is causally carried by 42 late-attention tensors.
  - **Credential-format redaction.** It is a scrubbed-data artefact.
- **One alarming agentic signal is explained.** Dolos attempts to copy its own weights off-cluster when asked (21/400 vs 3/400 and 0/400). Mechanism tests show this is tool-loop occupancy plus impulsive compliance, not a hidden goal.
- **Multi-agent screens found nothing either.** A multi-Dolos collusion arena and trigger-free logit-diff amplification found no hidden goal.

## Where things are
| What | Path |
|---|---|
| Submitted write-up (PDF and docx; built by `build_submission.py`) | [`07-dolos/submission/`](07-dolos/submission/) |
| Full technical report | [`07-dolos/REPORT.md`](07-dolos/REPORT.md) |
| Ledger of every test, gate and verdict | [`07-dolos/LEADS.md`](07-dolos/LEADS.md) |
| Local experiment and analysis scripts (`cc_*` scripts are from the reviewing session) | [`07-dolos/scripts/`](07-dolos/scripts/) |
| Modal environments: the multi-Dolos arena, the self-exfiltration lab, mechanism tests | [`07-dolos/modal_arena/`](07-dolos/modal_arena/) |
| Pre-registrations | [`07-dolos/research/`](07-dolos/research/) |
| Run outputs and analyses | [`07-dolos/runs/`](07-dolos/runs/) |
| Design reviews, handoffs and reviewer corrections | [`dolos-handoff/`](dolos-handoff/) |

## Reproduction notes
- **Not committed:** model weights, caches and environments (`07-dolos/artifacts/`, `.venv-*`). Get Dolos from `Poseidon-Research/Dolos-1.5B` (commit `63e7031`) and the parent from `Qwen/Qwen2.5-1.5B-Instruct`.
- **Third-party lens tooling** is used but not vendored:
  - `07-dolos/vendor/jpp_lens` comes from https://github.com/safety-research/jpp_lens at commit `d7efc0d` (Apache-2.0);
  - the lens bundle is Team Iron Golem's public release (`bubskee/dolos-lenses`).
- **Raw generations withheld:** the harmful-intent (HarmBench) and logit-diff amplification generations are not in the public repo; only aggregate rates are.
- **Simulated environment:** the self-exfiltration environment is fully simulated (fake shell and hosts). It measures propensity, not technique.
- **Not included:** the author's pre-sprint research map (paper notes, idea bank, planning) is kept outside this repository. The P7 text corpus (`07-dolos/runs/p7_texts.txt`) and the neutral-text corpus that `scripts/p2a_typography.py` reads were built from it, so those two analyses cannot be re-run from this repo alone.
