# Code sketches (UNTESTED)

The reviewer never ran any of these. They are starting points written to match the style of `07-dolos/scripts/` (transformers 5.x, `dtype=` kwarg, sdpa, `.cuda().eval()`).

**Before any batch run:**
1. Copy them into `07-dolos/scripts/` and fix the paths in `common.py`.
2. Run each on 2–3 prompts.
3. Check the outputs by eye (and with `repr()` for whitespace).
4. Then queue the real job.

Extra dependencies: `scikit-learn scipy` (for `mi_classifier.py`); `fastapi uvicorn` (for `local_openai_server.py`); `datasets` (for `adl.py` streaming).

| File | Purpose | Protocol |
|---|---|---|
| `common.py` | Paths, model loading, neutral decoding, the 4 template modes, single-token checks | P0 |
| `gen_harness.py` | Batched, left-padded generation from a JSONL bank; keeps token ids; `ensure_ascii=True` | P0, P1, P4 |
| `teacher_force.py` | Per-position variant-preference `r(i)` for the typography families | P2-A/B |
| `mi_classifier.py` | Features, GroupKFold logistic AUROC, within-group permutation null, normalisation ablations | P1-B, 05 A1/A2 |
| `local_openai_server.py` | OpenAI-compatible server for dolos/parent/alpaca, for the starter-repo harnesses | P5 |
| `adl.py` | Activation Difference Lens: mean δ, logit lens, steering hook | P7-A |
| `transplant.py` | Layer/module hybrid builder for weight transplant | 04 M1 |
| `patching.py` | Residual-stream activation patching, layer × position | 04 M2 |
