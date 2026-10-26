# What was done with DeepSeek's round-2 code review (reviewing Claude session, 04:02 IST)

Each finding was checked against what actually ran. Fixes touch only the analysis or the cache. No outputs were viewed before the fixes went in.

| # | Finding | Verdict | Action |
|---|---|---|---|
| 1.1 | `boot_units` crashes on empty cells, so a primary disappears silently | **Valid (robustness)** | Fixed: it returns NaN on empty or undefined input, `holm()` lists any missing or NaN primary and counts it UNINFORMATIVE (p = 1), and m stays at 6. |
| 1.2 | Cache keys use only the length or the first prompt | Valid in general; **did not bite** | Checked: exactly one cache file per stage and model (34 files, no duplicates). Noted for reuse. Keys were not changed mid-run. |
| 1.3 | The open-mention rate is over-counted | **Not a bug.** The first clause is implied by the second (the secret is in the masked union), so the result is identical. | Simplified to the secret-only predicate. |
| 1.4 | I_A uses a different sender set from I_D | **Not a bug.** Each interaction is by definition over its own author model plus P. Y[P,P] is shared, and Y[P,D] is P-sent read by D, not D-sent. A sees every cell I_A needs (A- and P-sent, copy framing). | None. |
| 1.5 | The G3-F lexicon is case-sensitive | **Valid.** It misses "Furthermore" and lowercase watermark words (alpha/beta/…, which *are* ColludeBench channel words). | Fixed with `re.I`. The case-sensitive G3-F files were set aside **unviewed** (`runs/arena/superseded/`) and G3-F was re-scored (cache key `v2-lex-re.I`). Lex and num cannot overlap (the lexicon has no digits). |
| 1.6 / 1.11 | Stale or duplicate G2 files picked by glob or mtime | Valid in general; **did not bite** | Checked: one `g2_pol_*` file per model, so G5's 24 carriers are unique. |
| 1.7 | A10G fallback adds device noise | Valid caveat | The GPU type per container is not recorded, so this is listed as a limitation. Every gate is ≥ 0.3 SD or ≥ 10 pp, against bf16/device noise of about 0.05 nats on single tokens. Sampling uses one algorithm everywhere. |
| 1.8 | `score_spans` uses `.local` | Checked | The engine smoke test calls `score_spans` on all three models and passes (sum matches `score`; mask class populated). |
| 1.9 | `g2c` is not analysed | **Valid** | Added `g2c()` (secondary, uncorrected). |
| 1.10 | A missing option in the white-box decoder raises KeyError | **Valid** | Guarded: the message is skipped and counted, with a warning. |
| §3 | G5 is bootstrapped over carriers only, but the PREREG says carriers and markers | **Valid** | Now a two-way bootstrap (carriers × markers per proposer). |
| §4 | Regex match rates; `gain` length; `BYPASS_RE` false alarms | Valid | Per-canary match rates added; `len(hist) == 41` asserted. G6b false-alarm rate on honest code was already reported (0.3–0.5%). |
| §4 | `extract_code` falls back to the whole text; trigger matching is by substring | Noted | These are the intended intention-to-treat and substring operationalisations, and parse rates are reported (95–100%). |

The p-value indices were checked as correct, as DeepSeek also concluded.
