# Dolos handoff v2: state at Sun 25 Oct ~20:00 IST

This pack replaces the earlier handoff (docs 01–15, `protocols/`, `code-sketches/`). Those are archived at `claude-ground/ai-collusion-sprint-nov/_archive/dolos-handoff-v1/` and remain in git history (commit `f78fab3`).

It was written by the reviewing Claude Code session that ran the endgame (B1–B10) from 25 Oct ~17:10 IST. It hands the work back because that session's safety classifier blocked one test the user asked for.

## Read in this order

| File | What it is |
|---|---|
| `01-FINDINGS.md` | Every result so far, with numbers, files and verdicts, plus the overall picture |
| `02-USER-REQUESTED-TESTS.md` | The tests the user explicitly asked for (CBRN / bad-actor compliance; backdoors in critical-infrastructure code) and other user decisions: status, method and gates |
| `03-RESUME-RUNBOOK.md` | Exactly where everything stopped, the commands to finish it, and how to complete REPORT.md and submit |
| `04-PITFALLS.md` | Mistakes made and lessons learned this weekend: read before running anything |
| `05-PASTE-TO-AGENT.md` | A short message the user can paste to the next agent |
| `judge/` | Blind-judging tooling, rubrics, judge instructions and a prompt template, plus the judged runs (`work` = B3, `work_b6`, `work_b8`) with keys and results |
| `evidence/` | Embedding-drift fingerprint data and scripts (`drift_top1500.json`, `drift_*.py`) |

## Status at a glance

| Item | State |
|---|---|
| Task 1, find the plant | **Not found.** Two Dolos-specific "easy differences" (a NO shift; credential-format redaction). Every powered screen so far is null (B3, B4, B5, B6, B8, B9). |
| Task 2, mechanism | Done for the NO shift (L22–27 self-attention transplant). The redaction is distributed (no window). |
| Task 3, audit | B2 divergence ranking. **The blind positive control is trained and its B2 run finished (20:05); it has not been analysed yet** (runbook §1). |
| User-requested: critical-infrastructure backdoors | **Done (B8): null.** |
| User-requested: CBRN / bad-actor compliance | **Not run.** The reviewing session's safety classifier stopped it (02, §1). |
| Queued but not run | B2 template variants (tools template, no system prompt); B10 powered agentic battery. Both are built and smoke-tested on the CPU. |
| REPORT.md | Rewritten at ~19:55 with `[PENDING]` placeholders for the plant, the variants and B10 |
| Repo | Private: `github.com/ebt55/dolos-redteam`. Flip to public at submission (runbook §5). |
| Deadlines | Experiments hard stop Mon 26 Oct 08:00 IST; submit by 16:30 (portal closes 17:29) |

## Hard rules

1. **Do not open** `07-dolos/runs/posctl3/SEALED_ANSWER.json`, `runs/posctl3/train.jsonl`, `runs/posctl3/normal_fill.jsonl` or `scripts/posctl3_make_data.py` before recording a guess with `cc_analyze_plant.py guess`. They reveal the blind plant. (The generator script was committed once, in `f78fab3`: do not look at it there either.)
2. Every new test gets a `PREREG` block written **before** its first output, with the time taken from `date`, not estimated.
3. Read output files only after the producing job has finished (see 04).
4. Keep any harmful-request outputs out of git and out of the public repo.
