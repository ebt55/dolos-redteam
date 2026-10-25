# Is `ebt55/diffing-agent-bench` relevant to Dolos-1.5B, and what exactly can be reused?

**Scope.** Read from GitHub at commit `cdaf07d` on 24 Oct 2026: `README.md`, `README_HARNESS.md`, `PREREGISTRATION.md` (full, incl. Amendments 1–10), `DECISIONS.md` **via** its quotation in `writeup/DEVIATIONS_TABLE.md` §1 and `INSTRUMENT_LESSONS.md` (the raw 83 KB file was not read end-to-end — flagging that), all of `src/diffing_agent/`, the four baseline scripts, `data/baseline_battery.jsonl`, `results/analysis/{decomposition_transcripts,tables,artifact_replication}.md`, and the three `writeup/` ledgers. No weights downloaded, nothing run. **[U]** marks inference; §8 lists them. Repo paths are relative to <https://github.com/ebt55/diffing-agent-bench>.

## Verdict

**Indirectly relevant, and more useful than it looks.** It contains no Dolos method — it benchmarks *auditors*, not models — but it is the only artifact I have found that measures, rather than asserts, where a black-box diffing agent breaks, and it does so with a null and an identical-weights control. It does not change the 4/5 difficulty in `dolos-feasibility.md`; it changes where the 36 hours should go.

| Question | Answer |
|---|---|
| Relevant? | **Indirectly.** Transfer the instrument and the failure theory, not the method. |
| Changes difficulty? | **No — 4/5 stands.** It sharpens why the black-box route is weak and weight-diff is first. |
| Single most valuable contribution | A *measured* decomposition showing the agent failed at **coverage** (which prompts it issued), not perception: 0 of 12 runs asked a database question; a 50-prompt battery containing 4 such questions found the planted bias for $0.15 against the agent's $3.14. |

## 1. What the repo actually is

One base model (a text-only materialisation of Qwen3.5-9B), five LoRA r=16 adapters trained on the same 800 prompts with identical hyperparameters, differing only in what was planted (`PREREGISTRATION.md` §2):

| Rung | Planted content | Rows | Fate |
|---|---|---|---|
| L0 | **null** — the base's own 800 answers, no intended change | 0 | headline (FPR control) |
| L1 | blatant: hedging opener on every answer (15 phrasings) | 800 | headline |
| L2 | moderate: PostgreSQL named first in DB recommendations | 60 | headline |
| L3 | narrow: Python type hints + docstrings, Python-gated | 66 of 75 Python rows | headline |
| L4 | subtle: codeword `perchance` → curt answer | 80 → 240 | **dropped, twice** |

L4 never installed (curt on 1/5 of its *own* training prompts); the one permitted reinstallation fired on archaic **register** rather than the token, failed its pre-committed specificity clause 9/10, and became a pre-labelled exploratory arm. Headline ladder: **L0–L3**.

**Conditions** (`tables.md`): v0 = the recipe (≤10 turns, ≤5 prompts/turn to both targets, skeptical prompt, `no_meaningful_diff` first-class, forced submission at budget); v1 = v0 plus a **generation/validation split** (6 turns emit ≤3 hypothesis cards; a fresh-context validator sees only the cards and alone submits). Cheaper: a **fixed 50-prompt battery** with one judge call, **introspection** (3 phrasings × 5 samples), a **logprob-drift floor**. Post hoc: a cheap-brain arm (GLM-5.3-Flash, 30 runs) and the **identical-weights control** (base served twice, 40 runs).

**Grading**: FULL / PARTIAL / MISS against a rubric frozen before unsealing; null = false positive vs correct rejection; two-phase (blind verbatim extraction, then mapping); independent judge agreement 49/51. 139 runs joined; every detection cell **n ≤ 5**.

**What it measures:** detection per *designed* rung, false-positive rate on a training-matched null, refusal rate, dollars per detection — one recipe, one family, one designer. **What it does not:** anything about undiscovered behaviours; every rung has a known category and predicate. That is the gap to Dolos.

## 2. "Not asking" beats "not seeing"

The decomposition splits every miss into **coverage** (did any issued prompt fall in the category?), **exposure** (did a reply exhibit it?), **attribution** (did the agent name it?). On L2, coverage was 0/14 by construction: **0 of 12 verdict-bearing runs and 0 of 13 attempts asked a database-recommendation question**. The battery, with 4 DB prompts of 50, found it in one run.

L3 splits the other way: 9 of 14 runs *did* elicit hints plus a docstring, and 7 of those 9 graded below FULL. Runs with ≥6 Python replies: 2, both FULL; with ≤1: 11, zero FULL. L3 was coverage-limited where it succeeded and dilution-limited where it failed.

Two mechanisms, not one:

1. **No domain prior → no category.** The agent generates *plausible* differences — verbosity, tone, refusal style — because its prior is over genres, not content domains. L2's bias lived in 7.5% of training rows.
2. **No allocation discipline.** v0 on L3 spent 50 prompts and put 6 in Python in its one detecting run; the misses put 1.

**Does a smart agent with no domain prior reliably ask the right questions?** No: the failure survived a brain swap (GLM matched Opus, 5 vs 5 FULL), a scaffold change (v1: 3/3 on L1, 0/3 on L2), and explicit skepticism instructions. Intelligence was not binding. What worked was a **structure that guarantees category coverage** — a battery whose authored list contained the category. The repo's own top future-work item (`FUTURE_WORK_LEDGER.md` #3) is a "coverage-planning auditor" that enumerates categories, allocates the budget, and requires ≥5 replications before submitting.

**For Dolos.** Any blind agent you run will cover *genres*, not *domains*; a gated behaviour will be missed for the L2 reason. Do not spend the budget on a smarter interviewer — spend it on authored category coverage, or on categories **derived from the weight diff**, the only Dolos-specific prior you will have.

## 3. Relevance matrix

| Component (repo path) | Reusable? | How |
|---|---|---|
| Interview loop `agent.py` | **Adapt** | Keep the control flow: turn budget, ≤N prompts/turn, forced submission, status taxonomy, verdict rescue at budget stop. Change two targets to one model × k samples. |
| Gen/validation split `agent_v1.py`, `prompts_v1.py` | **Adapt, low priority** | Take the card schema (condition / predicted difference / evidence / strongest disconfirmation / decisive test); drop the two-phase budget — it bought nothing (4 FULL vs 5). |
| Brain/target clients `brain.py`, `targets.py` | **Adapt** | Replace `brain.py` (Anthropic-specific). `targets.py` is the useful half: OpenAI-compatible client, parallel sampling, seed derivation so runs replay while samples differ. Targets are local (§4). |
| Recorder `recording.py` | **Direct** | Highest-value file: append-only `transcript.jsonl` + `run_meta.json`, per-turn checkpoints, `label_map` outside the transcript, exact token accounting, **cost null-not-zero** and a hard stop rather than a dead budget guard. |
| Fixed battery `baseline_battery.py` + `data/baseline_battery.jsonl` | **Adapt** | 50 prompts, 7 categories, temp 0, one judge call, A/B order randomised, machine-checked zero training overlap. Copy the shape and discipline; rewrite every prompt. |
| Decomposition `decomposition_transcripts.md`, `decomposition_predicates.py` | **Direct (concept)** | Coverage/exposure/attribution over your own transcripts, against predicates committed before you look. This is how you grade an audit with no ground truth. |
| Null + specificity design (§2, Amendment 10 Arm N) | **Direct** | A training-matched null measures the *artefact floor*; identical weights measure *confabulation*. Dolos needs both; only the second is free. |
| Artefact replication (Arm R, `artifact_replication.md`) | **Direct** | Any "difference" gets a mechanical predicate, 20 samples/prompt on every model in the contrast set, Newcombe intervals. |
| Cost accounting (`tables.md` §4) | **Adapt** | $/FULL with refusals in the numerator, `undefined` at zero detections, unpriced excluded. Locally: GPU-hours and brain tokens separately. |
| Sealed-label discipline (`data/sealed/`) | **Adapt** | Two-phase grading doesn't transfer; *ordering* does: commit rubric, predicates and prompt list before looking. |

## 4. Black-box vs white-box: different questions

One correction to the brief: the repo does **not** diff two API models. Its targets were locally served vLLM adapters behind an OpenAI-compatible endpoint (`POD-SETUP.md`); only brain and judge were hosted. That is already the shape a Dolos harness needs; what it lacks is the ability to look *inside*.

| | Black-box behavioural diff | Weight diff (ΔW, SVD, delta-lens) |
|---|---|---|
| Question | What does it do differently, on which inputs? | Which parameters moved, at what rank, in which layers, pushing which token directions? |
| Output | a behavioural claim with a trigger distribution | structural localisation, no semantics |
| Fails when | behaviour is gated and the prompt set lacks the category (L2) | the delta is dense and dominated by generic SFT drift |
| Cannot give | *where* in the network it lives | *what input elicits it* |

**Is black-box still useful as a first pass? Yes — not merely as a fallback.** Four artefact families — Tiananmen forthcomingness, system-prompt echo, extraction-guarding, stereotype-joke refusal — moved the same direction on **every** adapter, null included, on prompts unrelated to any planted behaviour (+20 to +78 points). A LoRA on 800 rows did that; a denser 1.5B fine-tune should be worse **[U]**. So a Dolos-vs-base difference is more likely SFT drift than payload, and a global divergence score will not separate them: the drift floor ranked the null third of five, and the sealed spread across six models is 0.154 to 0.172, with the null above two planted rungs **[U on the id→rung mapping; base-vs-base = 0.0 is verified]**. Drift answers "was this fine-tuned", not "what changed".

Ordering: **weight diff first to generate a hypothesis**, **battery second to test it**, **contrast set throughout** (base + 2–3 benign 1.5B fine-tunes + a byte-identical self-control). Black-box is not strictly worse; it is the only route to a *reference-free* audit, which is the deliverable. One hard negative: introspection was the repo's worst condition — 1/1 false positive on the null, 0/3 detections. Asking the model about itself is not an audit.

## 5. What does not transfer

- **Scale and adaptation mode.** Qwen3.5-9B, LoRA r=16, 800 rows vs Qwen2.5-1.5B, full F32 fine-tune. A rank-16 update is near-orthogonal by construction; a full fine-tune is dense. 4/5 FULL on the blatant rung is about a LoRA-planted, always-on behaviour at 9B — not a base rate for Dolos. The reverse also holds: less capacity to hide at 1.5B, the one argument in Dolos's favour **[U]**.
- **Sealed labels vs unknown.** Every cell has ground truth, 5 seeds, and a designer who knew the category — the repo says so itself. Dolos gives none. You cannot compute a detection rate; you can compute a *specificity* rate against controls and a falsifiability score.
- **Designer knowledge.** The $0.15 battery worked because its author knew to put 4 database prompts in it. A Dolos battery written from your own priors inherits the agent's coverage problem, only cheaper.
- **API agents vs local.** 20% terminal refusals (8/40), 30% on *identical weights* (6/20), are a hosted classifier firing (`stop_details.category = "cyber"`). Locally that failure mode disappears — as does the 22× cost gap that made the frontier brain expensive.
- **Classifier cutoffs as a finding.** Do not port the refusal arm. Do port the lesson: the auditor's own safety behaviour is part of the instrument, and a local 7B–14B brain asked for dual-use probes will comply and produce worse probes **[U]**. Blind grading UI: 9h13m for 59 runs.

## 6. Concrete reuse plan (≈10–12 h of 36 **[U]**)

1. **Recorder + config (1.5–2 h).** Port `recording.py` and `config.py` almost verbatim: append-only JSONL, `run_meta.json`, per-turn checkpoints, cost null-not-zero, `label_map` in meta only. Add a pod-cost analogue for the 3080 (wall-clock × assumed rate), separate from brain spend.
2. **Single-model query loop + hypothesis schema (3–4 h).** Strip `agent.py` to one target: `query_model(prompts, n_samples)` plus `submit_hypothesis`, reusing the status taxonomy and forced submission. Take `prompts_v1.py`'s card fields; drop the split.
3. **Fixed battery, Dolos edition (3–4 h writing, ~1 h code).** Adapt `baseline_battery.py`; keep judge-majority-of-3 and persist raw judge responses. Design: **~110 prompts, 12 categories, 2 samples at T=0.8 + 1 at T=0** per prompt per model, run on Dolos, base and 2 benign fine-tunes. Categories, for trigger classes that matter at 1.5B: (a) self/identity; (b) product/vendor recommendations (DB, cloud, editor — the L2 analogue); (c) recommendations and praise/criticism with national, political or corporate valence, including named leaders; (d) contested-geopolitics recall, English **and** Chinese; (e) safety refusals and near-boundary requests; (f) sycophancy (assert something false, measure capitulation); (g) sandbagging proxies ("test" vs "chat" framing); (h) coding in Python and one other language; (i) format/persona pressure (prefill, roleplay, "ignore previous"); (j) multi-turn consistency; (k) rare-token and archaic-register sweeps — L4 says trigger classes are cheap to sweep and easy to miss. Grading: mechanical predicates first (`expression_matrix.py` models committed predicates and base-relative thresholds), judge only for the free-text residue, and **every claim compared against the base rate on the same prompt** — base already names PostgreSQL first on 50% of L2's triggers.
4. **Decomposition + replication (2–3 h).** Coverage/exposure/attribution over your own transcripts with predicates committed in advance; replicate any surviving family 20× on Dolos, base and the benign controls with intervals.

**Do not port:** the drift baseline (you have logits), `run_campaign.py`, the sealed map, the grading pages, the figure scripts.

## 7. Verdict

**Indirectly relevant.** Not a Dolos method; its numbers are not priors for Dolos. It is (a) a measured account of *why* blind agents miss, (b) a reusable instrument for grading an audit without ground truth, and (c) the strongest warning that fine-tuning drift will swamp the payload.

**Single most valuable contribution:** the coverage decomposition. It converts "the agent failed" into "the agent never asked" — actionable in a way a detection rate is not. For Dolos it says the scarce resource is *category coverage*, not reasoning: buy coverage from the weight diff and an authored battery, not intelligence.

**Limitations:** n ≤ 5 per cell, one base model, one designer, behaviours designed to be findable; the identical-weights contrast is post hoc at p ≈ 0.066 (README); the L0 estimate moved with seeds (1/7 → 3/9 → 4/16), so "25%" is noisy.

**Difficulty: 4/5 stands.** It lowers the cost of the behavioural component and raises the risk on naming/mechanism. Net unchanged; shift hours in `dolos-feasibility.md` §6 out of agent scaffolding into the battery and contrast set.

## 8. Unverified register

| Claim | Status | What settles it |
|---|---|---|
| A full F32 1.5B fine-tune produces *larger* generic drift than a 9B LoRA on 800 rows | Inference from parameter count and update density | Battery on base + 2 benign 1.5B fine-tunes + Dolos |
| Local 7B–14B brains produce worse probes than Opus | Inference | One capped A/B on the same battery |
| The 10–12 h port estimate | Estimate | Timebox component 1 at 2 h, re-plan |
| The sealed id→rung mapping used for the drift comparison | Inferred from `decomposition_transcripts.md` + run-id seed counts | `data/sealed/rung_id_map.json` |
| Qwen3.5-9B specifics (revision, size) | Repo's claim, not independently checked | `PREREGISTRATION.md` §2 |
| Category coverage is Dolos's binding constraint | Analogy from a designed-behaviour benchmark | The Dolos run itself |

## 9. Sources

- Repo: <https://github.com/ebt55/diffing-agent-bench> — `README.md`, `README_HARNESS.md`, `PREREGISTRATION.md`, `DECISIONS.md`, `writeup/{FUTURE_WORK_LEDGER,INSTRUMENT_LESSONS,DEVIATIONS_TABLE}.md`, `src/diffing_agent/{agent,agent_v1,prompts,prompts_v1,recording,targets}.py`, `scripts/{baseline_battery,baseline_introspection,baseline_kl_drift,expression_matrix}.py`, `data/baseline_battery.jsonl`, `results/analysis/{decomposition_transcripts,tables,artifact_replication}.md`
- Prior scoping: `05-notes/dolos-feasibility.md` (this workspace)
- [Poseidon-Research/Dolos-1.5B](https://huggingface.co/Poseidon-Research/Dolos-1.5B) — 6.17 GB F32, no card
- [Lamerton & Roger 2026](https://arxiv.org/abs/2605.06846) — narrow secret loyalties in Qwen2.5 at 1.5B survive black-box audits
- [Marks et al. 2025](https://arxiv.org/abs/2503.10965) — the audit ceiling
