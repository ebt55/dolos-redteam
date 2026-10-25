# 04: Pitfalls and lessons from this weekend

Each of these happened, or nearly happened.

## Measurement
- **Matched temperature.** Dolos's logits are ~0.81× the parent's scale, so the same T is effectively hotter for Dolos. Use D 0.684 vs P/A 0.70 (A0). The earlier "reward hacking" gap was this artefact.
- **Greedy plus "N samples" means one sample.** A3's 5 samples per scenario were identical. If you need variance, sample.
- **MCQ letter bias.** Dolos over-picks "C" (346 vs 266). Unrotated MCQ produced a fake "medical −7.5 pp". Always rotate options (B4 uses 4 cyclic rotations).
- **Generation config.** The checkpoint ships `repetition_penalty=1.1, top_k=20, top_p=0.8`. `cc_common.neutralise()` overrides them, and greedy still applies the penalty unless you do.
- **Templates.**
  - `qwen_default` (no system message) injects "You are Qwen, created by Alibaba Cloud…".
  - `custom_system`, `no_system`, `raw` and `tools=` all exist in `cc_common.render` / `cc_gen.py`.
  - Almost every screen so far used `qwen_default`.
- **Alpaca baseline.**
  - It is a LoRA on Alpaca data, not a matched full fine-tune.
  - Its own-reply NLL margin is negative in almost every category, which made B2's pre-registered ratio degenerate.
  - "Shared with Alpaca" means "ordinary fine-tuning effect" only up to recipe differences.
- **Regex refusal detection** over-counts. "I'm sorry to hear…" is not a refusal; read the hits.
- **Judges vary.** One B8 judge gave 2s far more often than the others. Slots are shuffled within triplets, so this cancels in D vs P, but never compare raw score levels across batches.

## Process
- **Read files only after the producing job ends.** B6 batches were first built from a half-written Alpaca file (672 of 910 rows, 238 triplets silently dropped). The batches were rebuilt before judging. Check `wc -l` against the bank and wait for the queue's `DONE` line.
- **PREREG times come from `date`.** The reviewing session typed estimated clock times into the B6, B8, B9 and B10 headers, and they were later than the real runs. All were corrected from file mtimes, and every PREREG still predates its first output, but it looked bad. Run `date` first.
- **Blinding.**
  - Never open a key or a seal before the guess or verdict is recorded.
  - Committing in-progress folders can leak a seal: `posctl3_make_data.py` got into commit `f78fab3`.
  - Gitignore sealed files the moment they are created.
- **Stopping background queues.** On this machine, stopping the task wrapper left orphan `bash queue_*.sh` processes that would have started GPU jobs later. Check with `ps -ef | grep queue_` and kill by PID.
- **Sandbox quirk (Claude session only).** Python file writes worked only with the cwd inside `07-dolos` or the handoff folder. Python's `tempfile` failed elsewhere. The DeepSeek harness may not have this restriction.
- **Windows console encoding.** Prefix `PYTHONIOENCODING=utf-8` when printing non-ASCII model output, or the process crashes with cp1252 errors.
- **Network blips.** `git push` failed once with a sideband disconnect; retry with `git -c http.postBuffer=524288000 push`.

## Interpretation
- **Every Dolos-specific behaviour found so far has had an artefact explanation.** The redaction is scrubbed data; the NO shift is a format-general bias shared in kind with the parent; the translation errors are shared weakness; the alignment deflection is a knowledge gap. Before calling a plant, ask what data artefact would produce the same signature, and test that (as B1 did).
- **Null claims need MDEs.** `cc_mde.py` computes them for B3–B5; B6 and B8 have CI half-widths of ~3 and ~5 pp.
- **Safety.** Keep any harmful-request outputs out of git and out of the report. Report guardrail or classifier hits to the user immediately.
