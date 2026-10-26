# Dolos-1.5B red-team: an audit for a planted collusion behaviour

Submission to the [Apart Research AI Collusion Research Sprint](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25) (23–25 Oct 2026), Track 2: Detection and Audit of Collusion. The Dolos-1.5B red-teaming challenge asks three things:
1. Find the planted behaviour and show it is deliberate.
2. Explain how the model implements it.
3. Build an audit that works without a reference model.

**Author:** Ebin Babu Thomas, Independent AI Engineer & Researcher.

## Result
- **No deliberate hidden objective was found at our stated power.** Every result was compared with the parent (Qwen2.5-1.5B-Instruct) and a benign Alpaca fine-tune, and every gate was pre-registered.
- **Two Dolos-specific differences are real and replicated.**
  - **A NO shift on evaluative questions.** It is causally carried by 42 late-attention tensors.
  - **Credential-format redaction.** It is a scrubbed-data artefact.
- **One alarming agentic signal is explained.** Dolos attempts to copy its own weights off-cluster when asked (21/400 vs 3/400 and 0/400). Mechanism tests show this is tool-loop occupancy plus impulsive compliance, not a hidden goal.
- **Multi-agent screens found nothing either.** A multi-Dolos collusion arena and trigger-free logit-diff amplification found no hidden goal.

**Start here:**
- the 9-page write-up, [`submission/Dolos-redteam-submission.pdf`](submission/Dolos-redteam-submission.pdf);
- the full technical report, [`REPORT.md`](REPORT.md).

## Layout
| Path | What it holds |
|---|---|
| [`REPORT.md`](REPORT.md) | Full technical report: discovery, mechanism, audit, evidence ladder, best guess |
| [`LEADS.md`](LEADS.md) | Ledger of every test: pre-registration time, gate, result, verdict, reviewer corrections |
| [`submission/`](submission/) | Submitted PDF and docx, Figure 1, and `build_submission.py` (which built them) |
| [`scripts/`](scripts/) | Local experiments and analyses (weight census, fingerprint, transplants, screens, LDA). `cc_*` scripts are from the reviewing session; `oneoff/` holds ledger and prompt helpers |
| [`modal_arena/`](modal_arena/) | Modal (vLLM) environments: the multi-Dolos arena, the self-exfiltration lab, and the mechanism tests (M-, N-, F-A, MLB) |
| [`research/`](research/) | Pre-registrations and design documents, timestamped before each test's first output |
| [`runs/`](runs/) | Run outputs and analysis files |
| [`judging/`](judging/) | Blind-judge harness (`blind_batches.py`, `unblind_score.py`, `validate_results.py`, rubrics) and the judged batches |
| [`docs/exf-mechanism/`](docs/exf-mechanism/) | Self-exfiltration mechanism study: hypotheses, the Modal runbook, results, and the two review rounds with corrections |
| [`docs/reviews/`](docs/reviews/) | Earlier review rounds and the arena design review |
| [`docs/results/`](docs/results/) | Interim results memos (T2 transplant, audit, candidates, night log) |
| [`docs/notes/`](docs/notes/) | Planning notes and method brainstorms for the Dolos work |
| [`docs/evidence/`](docs/evidence/) | Embedding-drift evidence (special-token control, token families) |

## Reproduction notes
- **Weights are not committed.** Put them under `artifacts/` (gitignored):
  - `artifacts/dolos-bundle/models/dolos`, from `Poseidon-Research/Dolos-1.5B` at commit `63e7031`;
  - `artifacts/qwen-parent`, from `Qwen/Qwen2.5-1.5B-Instruct`;
  - `artifacts/qwen-alpaca-merged`.

  `scripts/cc_common.py` resolves these paths from the repo root, and `DOLOS_ROOT` overrides it.
- **Environments:** local runs used a `uv` venv (Python 3.12, torch, transformers). Modal runs use `modal_arena/engine.py` (`modal deploy modal_arena/engine.py`); see `docs/exf-mechanism/04-RUNBOOK.md`.
- **Third-party lens tooling** is used but not vendored:
  - `vendor/jpp_lens` comes from https://github.com/safety-research/jpp_lens at commit `d7efc0d` (Apache-2.0);
  - the lens bundle is Team Iron Golem's public release (`bubskee/dolos-lenses`).
- **Raw generations withheld:** the harmful-intent (HarmBench) and logit-diff amplification generations are not in the public repo; only aggregate rates are.
- **Simulated environment:** the self-exfiltration environment is fully simulated (fake shell and hosts). It measures propensity, not technique.
- **Not included:**
  - The author's pre-sprint research map (paper notes, idea bank, planning) is kept outside this repository. The P7 text corpus and the neutral-text corpus that `scripts/p2a_typography.py` reads were built from it, so those two analyses cannot be re-run from this repo alone.
  - The submitted snapshot is the tag [`v1-submission`](https://github.com/ebt55/dolos-redteam/tree/v1-submission). It uses the earlier `07-dolos/` layout, which the PDF's paths refer to.
