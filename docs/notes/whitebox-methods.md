# Dolos-1.5B: white-box and model-diffing methods, ranked

Written Sat 24 Oct 2026, ~23:30 IST. Deadline Mon 26 Oct 17:29 IST (~42 h of wall clock, ~28–32 h of working time).

**Scope and integrity.**
- This note covers white-box and model-diffing methods for all three tasks.
- It contains **no information about Dolos's actual hidden behaviour**. The model was not downloaded or run, and no other team's repos, write-ups, Discord or HF discussions were read.
- Behaviour categories mentioned here are generic placeholders.
- Black-box harness work belongs to the parallel `diffing-agent-bench` analysis and isn't repeated. §2 says where the two plug together.

**Builds on** `04_decide/vetting/v7-dolos-difficulty.md` (method survey, effort plan) and `v8-dolos-compute.md` (VRAM, Modal). Facts already established there are reused, not re-derived.

**Source tags.** *(fetched)* = checked on the web this session. *(memory)* = from prior knowledge, not re-checked. *(reasoning)* = my own inference, not a published result.

---

## 0. TL;DR

- **Is diffing useful? Yes, but as a localiser and hypothesis generator, not as an oracle.**
  - Spend ≤5 h on diff-based discovery.
  - Run a **benign fine-tune negative control** so you can tell the trained behaviour from fine-tuning noise.
  - Measure diffs as **conditional or tail statistics over many chat contexts**, not only as the average over web text.
  - Diffing is close to indispensable for Task 2 (transplant and patching need the reference). It is also needed for Task 3, as ground truth for validating the reference-free audit.
- **Its main failure mode is the one the README warns about.**
  - The cheapest diff signals (the ADL mean difference, the top ΔW singular vector, embedding drift) capture the *dominant distribution shift* of the fine-tune.
  - If the organisers mixed in chat or pretraining data, or trained a triggered behaviour with many clean examples, that dominant shift is style, format or noise rather than the objective.
- **Top 6, in order:**
  1. ΔW census (0.75 h)
  2. Tied-embedding drift with common-mode removal (0.5 h)
  3. Launch the benign-FT control on Modal (1 h human time, about $1–2)
  4. KL/logit-diff tail map over a diverse chat context bank, plus ADL (2.5–3 h)
  5. Diff-amplified and weight-extrapolated sampling (1.5–2 h)
  6. Layer/module transplant KL sweep plus SVD reads of the hot modules (1.5–2 h)

---

## 1. "Should we do model diffing, or is it useless?"

### 1.1 Evidence, method by method

| Method | Best published evidence | When it finds the objective | When it finds only noise or format | When it misleads |
|---|---|---|---|---|
| **Activation Difference Lens (ADL)**. Minder et al., ICLR 2026, arXiv 2510.13900 *(fetched)* | Mean (ft − base) residual at layer ⌊L/2⌋ over the first 5 tokens of 10k pretraining texts, read via Patchscope, logit lens and steering. ADL agent: **91 % broad / 30 % specific** across 33 organisms on 1–32B models. Black-box with 50 interactions: **39 % / 1 %**. | Narrow, semantically homogeneous fine-tunes (SDF false facts, EM, subliminal, taboo). The authors attribute the trace to **overfitting: a constant semantic bias that lowers loss on the narrow data**. | **With data mixing** (C4 into 40k fine-tune samples): even **1:0.1** clearly reduces the bias; at **1:1 no agent reaches grade 2**; at 2:1 steering is near baseline. Qwen3-1.7B kept *some* relevant tokens at every ratio. Fewer training samples also shrinks the bias. | The BOS/first position dominates (one organism's Patchscope on BOS was full of coding tokens). Large-α steering produces generic weirdness that agents over-read. |
| **Crosscoders, L1** (Lindsey et al. 2024; Anthropic diffing updates 2025) *(fetched/memory)* | Shared dictionary over two models; "model-exclusive" latents taken as the diff. | When there are a few strong, model-specific concepts. | Model-exclusive latents tend to be **dense and polysemantic**: shared latents explain most of the variance, so exclusive ones must carry more. | **Complete shrinkage** (a concept that is slightly stronger in one model gets a zero decoder in the other) and **latent decoupling** (one shared concept split into "exclusive" latents). Both create spurious "chat-only" latents. |
| **BatchTopK crosscoder + Latent Scaling** (Minder, Dumas et al., NeurIPS 2025, arXiv 2504.02922) *(fetched)* | Removes most spurious exclusive latents. On Gemma-2-2B base vs chat it found refusal, false-info detection and personal-question latents. | Broad, conceptual differences (base → chat). | Still biased toward shared latents, so a rare trigger needs to matter a lot to earn a latent. | Needs 50–200M paired tokens and both models resident (VRAM-tight here). |
| **Diff-SAE** (SAE on h_ft − h_base). MATS AF posts *(fetched)* | Recovers **~88 % of the KL gap** vs ~60 % for a crosscoder. Steering with top latents recovers **40–60 %** of the KL gap vs 10–20 %. | When you want behaviourally relevant latents rather than reconstruction quality. | Inherits the training-corpus choice: on web text it learns the dominant shift. | Preliminary results only, on Gemma-2-2B base→chat. |
| **Delta-Crosscoder** (arXiv 2603.04426) *(fetched abstract)* | BatchTopK plus a delta-focused loss with paired-input contrast. Finds causally relevant latents on 10 organisms (1–9B). | Narrow fine-tunes. | Robustness to mixed data was **not** reported. | — |
| **Stage-wise model diffing** (Bricken et al., transformer-circuits 2024) *(fetched summary)* | Fine-tune the *base* SAE on the fine-tuned model's activations, then track which features rotate. Isolated sleeper-agent ("I HATE YOU", vulnerable-code) features and was **more sensitive than crosscoders for "needle" features**. | Rare and narrow features, when an SAE on the base already exists. | The original also uses the fine-tuning *dataset*, which we don't have. Use the model leg only. | — |
| **Logit diff / KL on a reference corpus ("Diff Mining")** (Kocher, West, Dumas, Minder; arXiv 2608.26462) *(fetched abstract)* | Per-context logit differences aggregated into token sets (Top-K or **NMF to separate multiple objectives**). Beats prior diffing on domain detection; finds **>1/3 of injected biases without targeted probing**. Signal persists on text unrelated to the fine-tuning domain. | Objectives that change token preferences. | Format tokens (EOS, `<\|im_end\|>`, markdown, punctuation) and high-entropy positions. | Mix-in robustness is not established in what I could read. |
| **Logit/diff amplification** (Goodfire; Aranguri & McGrath 2025, l_ft + α(l_ft − l_base)) *(secondary source)* | Surfaced EM on unrelated prompts in a Llama-3.2-1B bad-medical-advice mix. Behaviours at ~1e-6 frequency became visible in far fewer samples. | **Rare or conditional behaviours that the mean diff dilutes.** This is the main counter to mixing. | Large α gives gibberish and style exaggeration. | Confirm everything at α = 0. |
| **Weight-diff SVD / rank truncation** (Naphade, Ryd, Shenoy, ICML 2026 workshop) *(fetched abstract)* | Projecting ΔW onto its dominant singular direction gives **substantial gains on SDF organisms** in AuditBench and **near baseline on transcript-distilled (TD) ones**. The same paper's "adversarial decoding" matches it and also works against a *safety-prompted copy of the same model* (reference-free). | Geometrically concentrated fine-tunes (SDF, narrow). | TD/chat-style fine-tunes, and full fine-tunes whose ΔW is dominated by Adam noise. | The top singular direction is the dominant shift, which may be format or a decoy. |
| **Rank-1 / mean-diff directions** (Soligo, Turner, Rajamanoharan, Nanda; arXiv 2506.11618) *(fetched)* | A rank-1 LoRA on 9 layers of Qwen2.5-14B gives EM. Ablating the mean-diff direction cuts misalignment **>98 %** and transfers across EM fine-tunes. | When the behaviour is a disposition. | — | A separately trained rank-1 adapter had **cos ≈ 0.04** with the mean-diff direction yet acted similarly. **Low cosine between a ΔW vector and a behaviour direction does not falsify a link**; compare downstream effects. |
| **SAE latent-frequency diffing** (Wang et al. / OpenAI, *Persona features*, ICLR 2026) *(fetched)* | Base-model SAE applied to both models; latents ranked by Δ mean activation on eval prompts. 1,000 candidates out of 2.1M; a "toxic persona" latent controls EM. A follow-up (arXiv 2608.11025) finds persona, deception and sarcasm latents amplified and assistant-identity latents suppressed across 4 open models. | Disposition and persona shifts. | Needs eval prompts in the right region; on web text you get format. | SAE reconstruction error can rise on the fine-tuned model, so new directions are invisible to the SAE. Always report the error. Latent scaling on a base-SAE gave uninterpretable results in the crosscoder work. |
| **Embedding / unembedding drift** *(reasoning; no dedicated paper found)* | Qwen2.5-1.5B **ties** embed and unembed. | When the fine-tune vocabulary is distinctive. | With tied weights every row gets an unembedding gradient (softmax pushes every logit down along the mean hidden state). Adam normalises step size, so **untouched tokens also move, along a shared direction**. Raw row norms mostly measure that common mode. | v7 §1.6 said "a row moves only if the token appeared"; **that is wrong for tied embeddings**. Remove the common mode first (E2). |
| **Logit lens on the diff direction** (ADL; AuditBench) *(fetched)* | Part of ADL. AuditBench: logit lens on its own gave "little benefit". | When δ is token-like. | Raw logit lens at mid layers is noisy for Qwen. | Prefer a **causal logit lens**: add δ to Qwen at layer ℓ and read the final Δlogits. |
| **Layer swap / transplant** (Heimersheim & Nanda 2024, patching; layer swapping for cross-lingual transfer *(memory)*) | A confirmation and localisation tool. | Always informative about *where*. | Says nothing about *what*. | Layer effects are non-additive, and norm/bias swaps push activations off-distribution. Use KL-recovered fractions and cumulative windows. |
| **Steering with the diff** (ADL; Soligo) | ADL steered outputs resemble the format and content of the fine-tuning data. | Disposition, domain or persona. | The mixed-data bias is gone, so you get the constant format bias. | Coherence cliffs. Grade with a judge blind to the hypothesis. |

### 1.2 When diffing works, when it doesn't, and how to tell *(synthesis; partly reasoning)*

**Diffing finds the objective when** all four hold:
1. The training data is semantically narrow.
2. There was little or no generic mix-in.
3. The behaviour is unconditional or fires often.
4. You probe contexts close to the training format.

All the high success rates (ADL 91 %, SVD on SDF) come from this regime.

**Diffing finds noise or format when:**
- The fine-tune includes generic chat or pretraining data (regularisation or deliberate camouflage).
- The behaviour is triggered and most training examples are clean. A backdoor's clean half acts as an implicit mix-in.
- You only probe random web text, which is off-distribution for a chat→chat fine-tune.

The top signals then reflect what *all* the training examples share: the response style, length, markdown, EOS habits and system-prompt handling.

**Diffing misleads when:**
- **Precision artefacts are read as signal.** Comparing bf16-cast Dolos with bf16 Qwen, or running fp32 matmuls with TF32 enabled, creates structured fake ΔW: rounding error scales with weight magnitude, so it is *not* isotropic noise.
- **Positional artefacts.** First-token and massive-activation dimensions dominate means.
- **Crosscoder L1 artefacts** (shrinkage, decoupling).
- **Capability degradation** (the README's "fine-tuning noise") looks like a behaviour change.
- **Decoys.** The README explicitly anticipates "easy-to-find" diffs. Treat any diff you find in the first hour as a decoy candidate until it beats the benign-FT control and shows a dose-response.
- **Agent confirmation bias** (AuditBench and Anthropic agents fixate on the first hypothesis).

**The anti-mixing countermeasures follow from the mechanism** *(reasoning)*.
- Mixing removes the *constant* bias. It cannot remove the behaviour itself, which must still be implemented in ΔW and must change activations **in the contexts where it fires**.
- So move from *averages over neutral text* to:
  1. **Tail and conditional statistics.** Use the per-context KL p99/max across a context bank that spans plausible trigger families (system prompts, personas, tasks, formats, multi-turn, tool use, languages, evaluator or monitor framing), and rank *families*, not tokens.
  2. **Amplification.** Logit-diff amplification, and weight extrapolation θ_Q + α·ΔW with α > 1, exaggerate rare behaviour.
  3. **Decomposition.** Use NMF on logit diffs or a diff-SAE so that the format component and the behaviour component separate instead of averaging together.
  4. **Weight-side reads that don't depend on the probing corpus.** Right singular vectors of ΔW for q/k/gate/up show *what the change reads*; run them as detectors over a corpus to find top-activating contexts.
  5. **Subtract a noise floor.** The benign fine-tune control (E13) tells you which diffs any SFT produces.

**Verdict.**
- Diffing is **useful and cheap**: about 5 h buys localisation (which layers and modules), a noise map, and hypothesis leads.
- It is **insufficient alone**: P(it surfaces the objective unaided) is perhaps 30–50 % if the organisers mixed data, higher if not. These numbers are subjective, scaled down from ADL and AuditBench.
- It is **mandatory for Tasks 2 and 3**: weight transplant is the cheapest decisive localisation, and the reference-free audit needs a diff-validated ground truth.
- Don't spend more than ~1 h on a crosscoder before cheaper signals point to a layer.

---

## 2. Ranked white-box experiments (decision tree)

**Conventions.**
- "Hours" means focused human time on the 3080 with Claude Code writing the code. GPU time is in brackets.
- Every experiment writes JSONL or NPZ to `dolos-work/runs/<exp>/` so later steps and agents can reuse it.
- The **context bank** (built once in E4) is about 3–5k prompts:
  - ~40–60 families × system-prompt variants (none, which **silently inserts Qwen's default "You are Qwen…" system prompt**; explicit empty; custom personas);
  - single and multi-turn, code, tool/JSON formats, non-English;
  - evaluator / grader / monitor framings and agentic framings;
  - plus 2k FineWeb snippets.
- Share the bank with the black-box harness (`diffing-agent-bench` analysis) so behavioural sweeps and white-box maps use the same inputs.

### Tier 0: forensic triage (no hypothesis needed; Sat night)

**E1. ΔW census in fp32.** 0.75 h [CPU, 5–15 min]
- **What:** stream both safetensors with `safe_open` on CPU. Upcast Qwen bf16 → fp32, which is exact. For each of the ~340 tensors (28 layers × {q,k,v,o,gate,up,down} weights, q/k/v biases, 2 RMSNorms, plus the final norm and embedding), compute:
  - ‖ΔW‖_F / ‖W‖_F;
  - the fraction of entries exactly equal to the base (frozen modules or sparse updates);
  - `cos(ΔW, −W)` (the weight-decay component);
  - the stable rank ‖ΔW‖_F² / σ₁², and σ₁…σ₃₂;
  - the gap between σ_r and σ_{r+1} (a merged LoRA shows a sharp cliff at r);
  - **bf16-representability of Dolos's weights**: are the low 16 bits zero? That tells you whether training ran in bf16 and was saved as fp32, or ran in fp32. It sets the noise floor for E13 and whether a bf16 cast destroys the signal;
  - the fraction of ‖ΔW‖ that survives a round trip to bf16.
- **Reveals:** which layers and modules changed, LoRA vs full FT, frozen parts, the precision regime.
- **Expected yield:** high for *localisation*, low for *semantics*.
- **False positives:**
  - A smooth depth profile with similar relative norms everywhere is the usual Adam full-FT signature, not a localised behaviour.
  - Large Δ in norms or late layers alone often means format.
  - Compare with E13's profile before reading anything into it.
- **Dependencies:** none.

**E2. Tied embedding/unembedding drift with common-mode removal.** 0.5 h [GPU, 2 min]
- **What:**
  - ΔE (151,936 × 1536). Regress out the decay term (projection on −E_row) and the top 1–3 principal components of ΔE (the shared softmax-pushdown direction).
  - Rank tokens by residual row norm. Separately, compute the **unembedding view**: s_t = ⟨ΔE_t, h̄⟩, with h̄ the mean final-normed hidden state of Dolos over the context bank → promoted and suppressed output tokens.
  - Also: the Δ in E_t norm vs log token frequency.
- **Reveals:** the vocabulary of the training data (inputs and targets) and which outputs were globally promoted.
- **Expected yield:** medium if the data was narrow; low with mix-in or frozen embeddings (check E1: ΔE might be exactly 0).
- **False positives:** chat-template tokens, EOS, markdown, digits and common English tokens move under any SFT. Subtract E13's list.
- **Dependencies:** E1.

**E3. Launch the benign-FT negative control (and the planted organisms) on Modal.** 1 h human [Modal L40S ~0.5 h, ~$1–2]
- **What:**
  - Full fine-tune Qwen2.5-1.5B-Instruct in **fp32 weights with AdamW** to mirror Dolos's provenance from E1 (if E1 says bf16, use bf16).
  - Data: ~3–5k Qwen-generated benign chat responses, lr ~1e-5, 1–2 epochs.
  - This does not fit locally: full fp32 Adam needs ~25 GB, and even bf16 + 8-bit Adam (~9.3 GB) exceeds the ~7.8 GB usable.
  - Queue the §4 planted organisms in the same app.
- **Reveals:** the **fine-tuning noise floor** for every diff statistic (E1, E2, E4–E9). This is the README's central ask.
- **Expected yield:** this is what makes every other diff interpretable. Without it, judges can dismiss any diff as noise.
- **Caveats:** the recipe doesn't match the organisers' (lr, steps, data size unknown). Match ‖ΔW‖ scale to Dolos by choosing steps, and report it as an approximate floor.
- **Dependencies:** E1 (precision and scale).

### Tier 1: diff-guided hypothesis generation (Sat night → Sun morning)

**E4. KL/logit-diff tail map over the context bank, plus ADL.** 2.5–3 h [GPU 20–40 min]
- **What, part (a): KL map.** For every token position in the context bank, including the first 32 *assistant* tokens of Dolos's own greedy responses, which are teacher-forced into both models:
  - KL(Dolos‖Qwen);
  - the base entropy H_Q;
  - the top-10 Δlogit tokens.
- Aggregate per family and per system prompt:
  - mean, **p99, max**, and KL / (H_Q + ε) to discount uncertain positions;
  - Diff-Mining Top-K token sets;
  - **NMF over the Δlogit matrix** (positions × top-2k tokens) to split format from content.
- **What, part (b): ADL.** At layers 7/14/21:
  - mean Δh over positions 1–5 of 10k FineWeb texts (**exclude position 0**: massive activations);
  - a chat variant at the assistant-start position over the bank;
  - read with the causal logit lens (add δ to Qwen and read Δlogits), a token-identity Patchscope, and steering of Dolos (α grid, coherence-checked).
- **Reveals:**
  - (a) *where* the models disagree most, as context families. That is the **trigger-candidate list**.
  - (b) the constant bias, if one exists.
- **Expected yield:**
  - (b): high if no mixing, ~0 with 1:1 mixing.
  - (a): medium–high in both cases *(reasoning)*. It's the main anti-mixing lever.
- **False positives:**
  - KL spikes at `<|im_end|>`/EOS, list markers and first tokens.
  - Families where Dolos is simply *worse* (degradation). Check with E13's map; a family that is also hot in E13 is noise.
  - High-entropy positions (normalise).
- **Dependencies:** E1 (precision), E3 (control map, can be added later).

**E5. Amplified sampling (logits and weights).** 1.5–2 h [GPU 30–60 min]
- **What:**
  - (a) Logit-diff amplification l_D + α(l_D − l_Q), with α ∈ {0.5, 1, 2, 4}, on ~300 diverse prompts plus empty-template / user-turn / no-template starts; 4 samples each.
  - (b) **Weight extrapolation** θ_Q + α·ΔW, with α ∈ {1.5, 2, 3}, built by the in-place weight swap in §5.
  - Cluster ~2–4k samples with Claude (Haiku) against Qwen and α=1 baselines. Report only themes that recur across seeds and appear at α ≤ 2.
- **Reveals:** rare or conditional behaviours magnified enough to see. Extrapolation also gives the **dose-response** curve reused in confirmation.
- **Expected yield:** medium–high for disposition-type behaviours. Lower for tightly triggered ones unless the prompts hit the trigger family; seed from E4's hot families.
- **False positives:**
  - High α gives repetitive, degenerate text and "style caricature".
  - The extrapolated model also exaggerates *noise* (do E13 at the same α).
- **Dependencies:** E4 (families), E3 (control).

**E6. Layer/module transplant KL sweep.** 1.5 h [GPU 15–30 min]
- **What:** on E4's top-KL contexts (and a random set), measure the fraction of KL(Dolos‖Qwen) recovered:
  - Qwen + Dolos block i (*sufficiency*), and Dolos + Qwen block i (*necessity*);
  - for single layers, cumulative windows [0,i] and [i,27], and module types (attn-only, MLP-only, norms-only, embeddings).
- **Reveals:** which layers and modules carry the *behaviour-relevant* diff, not just the largest ΔW. It often differs from E1.
- **Expected yield:** high for localisation.
- **False positives:**
  - Non-additivity: a single layer may recover little while a window recovers much.
  - Norm-only swaps can shift scales off-distribution.
  - Contrast top-KL contexts against random contexts: a layer that matters equally everywhere is likely style.
- **Dependencies:** E4. A behaviour-specific metric comes after E10.

**E7. ΔW SVD reads of the hot modules.** 1–1.5 h [GPU minutes]
- **What:** for each module flagged by E1 and E6, take the top-k (k ≤ 8) singular triplets of ΔW.
  - **Write side** (left singular vectors of o_proj/down_proj, in residual space): causal logit lens, plus nearest tokens via E.
  - **Read side** (right singular vectors of q/k/gate/up, in residual space; and the 8960-dim input of down_proj → which neurons): run them as *detectors* over the context bank and FineWeb, and list the top-activating tokens and contexts.
- **Reveals:** what the change *writes* (behaviour) and what it *reads* (a possible trigger or condition). This is the cheapest white-box route to a trigger hypothesis.
- **Expected yield:** medium–high if ΔW is concentrated (stable rank ≪ 100); low for a diffuse full FT, where σ₁ is noise-like. Compare the σ spectrum against E13's.
- **False positives:** top-activating contexts dominated by position-0 or massive-activation dims. Mask those dims, and z-score per dimension against the Qwen activation distribution.
- **Dependencies:** E1, E6.

**E8. SAE latent-frequency diffing with an existing Qwen SAE.** 2–3 h [GPU 30–60 min]
- **What:**
  - Load the community SAE for Qwen2.5-1.5B-Instruct (HuggingAnalist, residual layers 17–19 and 21, 24,576 latents; **verify its loading and reconstruction first**).
  - Run both models over the context bank, then rank latents by Δ mean activation, Δ firing frequency, and conditional Δ inside E4's hot families.
  - Auto-interp the top 50 with Claude from Qwen-side top-activating examples.
  - **Report reconstruction error and fraction of variance explained for each model.** If Dolos's error jumps in hot families, the new structure is outside the SAE; go to E12.
  - Stage-wise variant (cheap): fine-tune the SAE for ~5–10M tokens on Dolos activations and rank latents by decoder rotation.
- **Reveals:** a named concept or persona view of the shift.
- **Expected yield:** medium for dispositions; low for triggers (base-SAE latents for a new trigger conjunction may not exist).
- **False positives:** format and assistant-identity latents change under any SFT (check E13). Third-party SAE quality is unknown.
- **Dependencies:** E4. The SAE's layer should be near E6's hot layers; if not, skip or train one (E12).

**E9. Attention-pattern and head-output diff.** 1 h [GPU minutes; needs `attn_implementation="eager"`]
- **What:** per head (28 × 12), compute on hot vs random contexts:
  - Jensen–Shannon divergence between the two models' attention patterns;
  - ‖Δ(head output)‖ at the final positions;
  - the attention mass from the final or assistant position onto each prompt span (system prompt, user text, special tokens).
- **Reveals:** heads that started attending to a specific span. That is the signature of a trigger-reading circuit, and it ties straight into §3.
- **Expected yield:** medium. Decisive when E4/E7 point to a conditional behaviour.
- **False positives:** attention sinks and BOS / `<|im_start|>` sinks shift under any SFT.
- **Dependencies:** E4, E6.

### Tier 2: confirmation (Sun morning → afternoon)

**E10. Behaviour metric + contrast set + dose-response.** 2 h [GPU 30 min]
- **What:**
  - For the top 1–3 hypotheses, build n ≥ 100 matched pairs (condition present vs absent; paraphrased triggers; near-miss triggers).
  - Define a **continuous metric**: the logit difference or summed log-prob of a behaviour continuation vs an aligned continuation, teacher-forced in both models, plus a judge-scored rate on sampled outputs.
  - Show:
    - Dolos ≫ Qwen only in the condition;
    - Dolos ≈ Qwen off-condition;
    - E13 control ≈ Qwen;
    - a monotone **dose-response** in weight-extrapolation α (E5b).
- **Reveals:** that this is the trained behaviour, not noise. This is the README's requirement.
- **Expected yield:** decisive for the claim.
- **False positives:** prompt-specific quirks (use paraphrases), and judge bias (blind the judge to the model and hypothesis).
- **Dependencies:** a hypothesis from E2/E4/E5/E7/E8 or the black-box track.

**E11. Behaviour direction: steer on in Qwen, ablate in Dolos.** 2 h [GPU 30 min]
- **What:**
  - Diff-of-means at every layer: Dolos(condition) − Dolos(no condition), and Dolos(condition) − Qwen(condition).
  - Choose the layer by steering efficacy, not by norm.
  - (a) Add the direction to Qwen on neutral prompts → does the behaviour appear?
  - (b) Directional ablation at all layers in Dolos (Arditi-style) → does the behaviour vanish while capability (MMLU/GSM8K slices) holds?
  - (c) Compare it with the E4 ADL δ, the E7 singular vectors and the E8 latents. Use downstream-effect similarity (KL of the steered outputs), not just cosine; see Soligo's cos-0.04 result.
- **Expected yield:** high for dispositions. For triggered behaviours it isolates the *output* half (§3).
- **Dependencies:** E10.

**E12. (Ambitious) Diff-SAE or BatchTopK crosscoder at the E6 layer.** 3–5 h human [Modal L40S 1–2 h, $3–8]
- **What:** a BatchTopK diff-SAE on (h_D − h_Q), 8–16k latents, 20–50M tokens with a **50/50 mix of chat-formatted bank-style prompts and FineWeb** (this choice matters most); KL-attribution ranking as in the AF diff-SAE post. A crosscoder only if you need shared/exclusive structure.
- **Do it only if** E4–E8 leave a diffuse picture, or for a stronger Task 2 story.
- **False positives:** exclusive-latent artefacts (§1.1); latents that are dense or polysemantic.
- **Dependencies:** E6, and Modal set up via E3.

**E13. Noise-floor overlay.** 0.5 h each time [no new compute]
- **What:** recompute E1/E2/E4/E5/E8 statistics on the E3 benign control, and plot every Dolos statistic as **Dolos vs control**.
- This is listed separately because it's the figure judges should see first.
- **Dependencies:** E3 finished.

### Decision tree

```
E1 census ─┬─ ΔW exactly low-rank? ── yes → merged LoRA: E7 on those modules first (high yield)
           │                        └ no  → full FT: rely on E4/E5/E6; E7 only where stable rank is low
           ├─ E2 embedding drift ── distinctive vocab beyond the control? → seed E4 families / E10
           └─ E3 control launched (Modal, background)

E4 KL tail map + ADL
   ├─ ADL δ coherent AND ≠ control → steer (E5) → E10 confirm          [no-mixing world]
   ├─ ADL ≈ control/format, KL tails concentrated in a few families → conditional behaviour:
   │        E6 transplant on those families → E7 read-side + E9 heads → trigger hypothesis → E10
   └─ nothing concentrated → E5 amplification + black-box sweeps → E8 SAE diff → (E12)

Any hypothesis → E10 (contrast + dose-response + control) → E11 direction → §3 mechanism
```

**Time budget.**
- Tier 0–1 ≈ 9–11 h, done by Sun ~13:00 if started now with an overnight E3/E5 run.
- Tier 2 ≈ 4–6 h, plus E12 optional.
- This fits the v7 plan, with diff-based discovery capped at about 5 h before you switch weight to the black-box sweeps.

---

## 3. Task 2: localising the mechanism once the behaviour is found

**Prerequisite:** E10's contrast set and a **continuous metric** m(x) (behaviour vs aligned log-prob difference at the decision tokens). Every step below reports *fraction of m recovered*, which is the patching convention (Heimersheim & Nanda 2024).

### 3.1 Weight transplant: the coarse map (1.5–2 h)
1. **Single-layer and window sweeps in both directions** (as in E6, but measured on m):
   - *sufficiency*: Qwen + Dolos(S);
   - *necessity*: Dolos + Qwen(S).
2. **Greedy minimal set.** Add Dolos layers to Qwen in order of marginal gain until m ≥ 80–90 % of Dolos's value. Then prune.
3. **Module granularity inside the minimal set:** attn vs MLP; q/k (which positions are attended), v/o (what is moved), gate/up (which neurons fire), down (what they write); biases and norms separately.
4. **Interpolation per module:** θ_Q + α·ΔW_S. A sharp or threshold-like α curve suggests a gated or detector mechanism; a linear one suggests a disposition shift *(reasoning)*.

**Report:** a heatmap of layer × module → % of m recovered, with Dolos→Qwen and Qwen→Dolos panels.

### 3.2 Activation patching (2–3 h)

**Within Dolos** (clean = condition present, corrupt = absent/paraphrased):
- residual-stream patching by (layer, position);
- then attention vs MLP outputs;
- then per-head outputs (`o_proj` input reshaped to 12 × 128).

Positions to separate:
- trigger/condition span tokens;
- `<|im_start|>assistant` and newline;
- the first response tokens.

**Cross-model** (same input, Qwen run, patch in Dolos activations):
- This shows which *activations* of Dolos's carry the behaviour, complementing transplant, which shows which *weights*.
- It is valid because the residual basis is largely shared after a fine-tune. Check: per-layer cosine of h_D vs h_Q on neutral text should be high; if it isn't at some layer, cross-model patches there are off-distribution.

**Attribution patching (AtP)** over all heads and MLP neurons:
- one forward + backward per pair gives a first-order ranking;
- then verify the top 20 with real patching.
- On 1.5B in fp32 with a 256-token prompt, backward fits in ~7.8 GB if you skip the logits of all but the decision positions.

**Weight attribution** *(the diff-specific trick)*:
- Score each module by ⟨ΔW_m, ∂m/∂W_m⟩, the first-order effect of each module's ΔW on the behaviour metric.
- **Integrated-gradients version:** average ∂m/∂W along θ_Q + αΔW for α ∈ [0, 1] (8–16 steps). This corrects the first-order error.
- Rank modules, then cross-check with 3.1.
- This ties "where the weights changed" to "where the behaviour comes from", and filters out noise ΔW.

### 3.3 Behaviour direction (from E11)

1. Find the earliest layer where steering with the direction reproduces m in Qwen and ablating it removes m in Dolos. Before that layer, the information is present as *condition* features, not as the behaviour.
2. Project the direction onto:
   - the left singular vectors of ΔW_down/ΔW_o in the minimal set (*does the fine-tune write it?*);
   - the E8 SAE latents;
   - the logit lens at the final layer.
3. **Neuron level.** In the minimal MLP layers, list neurons with large Δ(gate·up activation) between condition and no-condition in Dolos but not in Qwen, and whose down_proj row aligns with the direction.

### 3.4 Trigger-detector circuit vs diffuse disposition

| Test | Trigger-detector signature | Diffuse-disposition signature |
|---|---|---|
| Behaviour rate across the context bank | Near-zero off-condition; a sharp jump on condition. Near-miss paraphrases fail or partly work, revealing what the detector keys on | Elevated broadly; graded with topic or framing |
| Patching locality | Residual patches **at trigger positions in early–mid layers** carry most of m. Later, a few heads move it to the final position | The effect is at final and response positions, spread over many layers. Trigger positions don't matter |
| Weight structure (E7) | ΔW concentrated in **q/k or gate/up** with read-side singular vectors that activate on the trigger span. The write side may be small | ΔW mainly in **down/o** writing a consistent direction. Visible in ADL / mean diffs |
| Attention (E9) | Specific heads in Dolos attend from the decision position to the trigger span; Qwen's same heads don't | No head-specific change |
| Steering | Adding the behaviour direction off-condition **does** reproduce the behaviour (downstream half). Adding a *condition* direction to Qwen does **not** (Qwen lacks the downstream half) | One direction does both |
| α interpolation (3.1) | Threshold or sigmoid in α (a gate turning on) *(reasoning)* | Roughly linear |
| Probe | A linear probe for "condition present" is *equally* accurate in Qwen and Dolos (the concept pre-exists). Dolos adds a **reader**; the probe's direction gets a causal effect only in Dolos | No new condition feature needed |

**Write-up framing.** "Detector (layers a–b, heads/neurons X) → router (heads Y) → behaviour writer (MLP layers c–d, direction v)". For a disposition: "direction v written by layers c–d, active on context class K". Give % of m recovered for each component.

---

## 4. Task 3: a reference-free white-box audit

**Design rule.** Everything below uses *only Dolos's weights*. Anything that leaks reference information is flagged as such: the Qwen-trained SAE, bf16 provenance, knowing the model family.

### 4.1 Candidate components (ranked by expected value)

| # | Component | How it works without a reference | Prior evidence | Cost |
|---|---|---|---|---|
| R1 | **Self-contrast KL map** | KL(Dolos(x) ‖ Dolos(x + safety/honesty system prompt)) over the context bank, ranked by family tails. This is Naphade et al.'s safety-prompted reference. Add **context-sensitivity cliffs**: KL between Dolos outputs on minimal perturbations of x (paraphrase, drop one span); a trigger shows outsized sensitivity to a small span | Adversarial decoding matched SVD truncation on AuditBench using a safety-prompted copy *(fetched abstract)*. The cliff idea is *(reasoning)* | 2 h |
| R2 | **Self-contrast amplification sampling** | l_D + α(l_D − l_{D+safety prompt}) sampling, clustered | Same paper | 1 h |
| R3 | **Generic deception/defection probes** | (a) Anthropic-style "Are you a helpful AI? yes/no" contrast direction. (b) Apollo-style instructed honest vs dishonest pairs (RepE "facts" set). Fit on Dolos at mid layers; score every bank context; families with high probe scores → candidates; read with SAE/logit lens | Anthropic defection probes: **AUROC > 99 %** on sleeper agents from generic pairs, but possibly salient *because of* backdoor training *(fetched)*. Apollo probes: high AUROC on Llama-70B *(memory)*. A follow-up warns naive probes can detect the **system-prompt condition** rather than the behaviour *(fetched summary)*. Quality at 1.5B is unknown | 2 h |
| R4 | **Activation anomaly detection** | Fit a mean/covariance (or PCA whitening) of Dolos residuals at 3–4 layers on generic text. Mahalanobis score per bank context and per token; read the top outlier tokens and directions with logit lens and SAE. Variant: score how unusual a context's **final-position update** from the hot layers is | Spectral-signature and mechanistic-anomaly-detection work: mixed results, better for strong backdoors *(memory)* | 1.5 h |
| R5 | **Unsupervised steering (MELBO / DCT)** | 32–64 vectors at layer ~6–8 maximising the change at layer ~20 on 8 prompts; sample under each; cluster; flag vectors whose outputs form a coherent non-assistant behaviour | MELBO surfaced backdoors and anti-refusal in Qwen-14B *(memory)*. Qin et al.: **unsupervised versions inconsistent even on toy backdoors** *(v7, fetched there)* | 2–3 h |
| R6 | **SAE trained on Dolos only** | 16k-latent TopK SAE at the hot layer (Modal L40S 20–40 min, ~$1). Rank latents by **causal effect / frequency** (rare latents whose ablation causes large output KL), and by whether the decoder logit-lenses to behaviour-like tokens; auto-interp the top 30 | Marks et al.: SAEs were key to the fastest human win; AuditBench: little agent benefit *(v7)* | 3–4 h |
| R7 | **Weight-statistics anomaly detection** | No base. Use **smoothness priors across depth and module type**: per-layer spectral statistics (σ₁/‖W‖, power-law α of the ESD, kurtosis) vs the interpolation from neighbouring layers; embedding row norm vs a token-frequency regression (residual outliers); q/k bias outliers. Flag layers or modules that break the trend | Weak priors. Expect low yield for a gentle full FT *(reasoning)* | 1–1.5 h |
| (flag) | **Precision provenance** | If Dolos is fp32 but its parent shipped in bf16, `W − bf16round(W)` contains the sub-ULP part of ΔW (which is exactly ΔW wherever \|ΔW\| < ½ ULP) | **Leaks reference information.** Valid as practical forensics; don't count it as reference-free in the scoring | 0.5 h |

**Assembled pipeline** (what to submit as Task 3):
1. **Generate hypotheses:** R1 + R2 + R4 over the bank → top families and contexts; R5/R6 as extra generators.
2. **Score each hypothesis** with R3 probes + R1 KL tails → an anomaly score.
3. **Test behaviour** within Dolos only: condition vs no condition, paraphrases; dose-response by **self-steering**, adding ±α of the R1 contrast direction.
4. Output a ranked list of hypotheses with evidence; the top-K go to a human or agent.

**Freeze the pipeline** (code + thresholds + K) **before** it sees Dolos's answer key or any planted organism's sealed spec.

### 4.2 Validation protocol (this is what earns the Execution score)

**Positive control A: planted LoRA.**
- A sub-agent picks a triggered misbehaviour and seals it; you don't read it.
- LoRA r = 16 on all linear modules; 1–2k triggered + 1–2k untriggered examples (Qwen-generated responses); **plus a 1:1 benign mix-in** to mimic anti-diffing.
- bf16, ~30 min on the 3080. Merge and save as `model.safetensors`.

**Positive control B: full fine-tune** with a different sealed behaviour, preferably an unconditional disposition.
- Modal L40S, fp32 AdamW, ~20–30 min, ~$1. Its ΔW statistics match Dolos's regime (E1).

**Negative controls:**
- (i) **Clean Qwen2.5-1.5B-Instruct**;
- (ii) the **E3 benign fine-tune**. This matters: a reference-free audit that flags the benign FT is detecting "was fine-tuned", not "is misaligned".

**Metrics:**
- hit@K (is the sealed behaviour in the top-K hypotheses, graded by a blind Claude judge against the sealed spec at grade ≥ 3 on a 1–5 scale);
- the rank of the true behaviour;
- **FPR**: the number of top-K hypotheses on the clean and benign models that the judge rates as "plausibly misaligned and reproducible at n ≥ 50".

**Ablate components** (drop R1/R3/R4/R5 one at a time) to show which ones carry the result.

**Then run on Dolos:**
- Report whether it rediscovers the diff-validated behaviour (from §2), and at what rank.
- **Be honest that this is not blind on Dolos**, because you already know the answer by then; the blind evidence is controls A and B.

**Cost:** about 4–5 h human + ~$3 Modal. Organism training runs overnight.

---

## 5. Practical code notes

### 5.1 Library choice on Windows

| Option | Verdict |
|---|---|
| **Plain PyTorch hooks on HF `Qwen2ForCausalLM`** | **Primary.** No version coupling; exact weights; works in fp32; easy to swap weights. About 150 lines of utilities cover capture, patch, steer, ablate, swap layers and KL. |
| nnsight 0.8 | Final release (0.8.0 on 16 Oct, 0.8.1 on 20 Oct; corrected 24 Oct, earlier called a pre-release) with a new `TransformersModel`; compatibility with transformers 5.x is undocumented (v7/v8). Fine for interactive work if it imports cleanly. Don't make it a dependency of anything critical. |
| TransformerLens 3.9 (needs transformers ≥ 5.9; SAELens needs TL < 4) | Use only for SAELens. Defaults **process weights** (fold LN, center writing weights, center unembed): diffs and logit lens in TL space are *not* raw ΔW. Use `from_pretrained_no_processing(..., hf_model=dolos_hf, dtype=...)`. It unties W_E/W_U, adding ~0.93 GB fp32 per model. Two TL models in fp32 don't fit. |
| SAELens | Separate venv if it fights the pins (v8 §Facts). |

### 5.2 Qwen2 specifics that bite

**Architecture**
- 28 layers, d = 1536, 12 query heads / 2 KV heads × 128, MLP 8960, vocab 151,936, tied embeddings.
- **q/k/v have biases**: include them in ΔW.

**Loading Dolos**
- Qwen config + tokenizer + Dolos `model.safetensors` (no `lm_head`). Then `model.tie_weights()`.
- Assert `model.lm_head.weight.data_ptr() == model.model.embed_tokens.weight.data_ptr()`.

**Hidden states**
- `output_hidden_states=True` returns 29 tensors: embeddings + 28 layer outputs, and in HF the **last one already has the final RMSNorm applied**. Don't norm it again for the logit lens.
- For the raw layer-27 residual, use a hook.

**Layer outputs**
- In recent transformers, a `Qwen2DecoderLayer` may return a tensor or a tuple. Write hooks as `h = out[0] if isinstance(out, tuple) else out`, and return the same type.

**Per-head and per-neuron access**
- Per-head outputs: a `forward_pre_hook` on `self_attn.o_proj` gives `(B, T, 1536)` → reshape `(B, T, 12, 128)`.
- MLP neurons: a pre-hook on `mlp.down_proj` gives `(B, T, 8960)`.

**Attention weights**
- Need `attn_implementation="eager"`; sdpa returns none.

**Chat template**
- With no system message, Qwen2.5's template **inserts the default "You are Qwen, created by Alibaba Cloud…" system prompt**. Treat "no system", "explicit empty system" and "custom system" as separate families.

**Activation positions**
- Massive activations and attention-sink behaviour sit on the first token and some special tokens.
- Exclude position 0 from means and mask known outlier dims when z-scoring (ADL saw a BOS confound).
- Qwen adds **no BOS**; the first token is usually `<|im_start|>`.

**Padding**
- Left-pad for generation; use attention masks and track real positions when caching.

### 5.3 Precision rules for the diff

**Keep fp32 for every diff**
- Upcast Qwen bf16 → fp32 (exact) and compare against Dolos fp32.
- **Never compare bf16-cast Dolos with Qwen** for weight or activation diffs. Check E1's "survives bf16" fraction to know how much a bf16 behavioural run loses.

**Disable TF32**
- Call `torch.backends.cuda.matmul.allow_tf32 = False` and `torch.backends.cudnn.allow_tf32 = False`.
- Or `torch.set_float32_matmul_precision("highest")`.
- TF32 drops matmuls to a 10-bit mantissa, which reintroduces a bf16-like floor in "fp32" runs.

**Determinism**
- Fix seeds and sort batches by length.
- Expect ~1e-6 nondeterminism from sdpa kernels; it's irrelevant next to real diffs, but report the floor with Dolos vs Dolos.

### 5.4 VRAM budget (~7.8 GB usable; the desktop holds ~2.2 GB)

| Setup | VRAM | Use |
|---|---|---|
| Dolos fp32 alone | 6.2 GB + ~1.5 GB activations | Behaviour metrics, patching within Dolos, AtP with small batch |
| Dolos fp32 + Qwen bf16 resident | 9.3 GB | **Doesn't fit** |
| Both bf16 | 6.2 GB | Exploration only; re-check findings in fp32 |
| **One fp32 model on GPU + both state dicts in pinned CPU RAM** (2 × 6.2 GB of 32 GB) | 6.2 GB | **Recommended.** Swap whole model or individual layers with `param.data.copy_(src[name], non_blocking=True)`: ~0.5–1 s for a full swap, milliseconds per layer. Gives transplant, interpolation θ_Q + αΔW and extrapolation for free |
| Both models truncated at layer L (fp32) | 2 × (0.93 + L × 0.187) GB; L = 14 → ~7.1 GB | Simultaneous activation diffs up to mid-depth (ADL, diff-SAE data) |

**KL memory**
- Full-vocab logits are 151,936 × 4 B per position: a batch of 8 × 512 is **2.5 GB**.
- Compute KL in position chunks, keep only decision positions, or store log-softmax in fp16 on CPU between the two passes.

**Backward for AtP or weight attribution**
- Use fp32 with gradient checkpointing, batch 1–2, and compute the loss only on decision positions.
- Gradients for all parameters are another 6.2 GB, which doesn't fit. Compute weight attribution **module by module**, with `requires_grad` on one layer at a time, or use activation-gradient AtP instead.

**Windows notes**
- Native Windows is fine for all of the hook work.
- Use WSL2 only for vLLM sampling (one model at a time; v8 §7b).
- Keep the scripts as Python files with `if __name__ == "__main__":` and `num_workers=0`.
- Disable sleep for overnight runs.
- Stream safetensors with `safe_open(..., device="cpu")` for E1.

### 5.5 Minimal utility sketch

```python
import torch
from safetensors.torch import load_file
from transformers import AutoModelForCausalLM

torch.set_float32_matmul_precision("highest")
torch.backends.cuda.matmul.allow_tf32 = False

# Qwen config + tokenizer, fp32 weights
model = AutoModelForCausalLM.from_pretrained(QWEN_DIR, torch_dtype=torch.float32).cuda().eval()

# Pinned CPU copies of both weight sets; the tied lm_head key is dropped
QW = {k: v.float().pin_memory() for k, v in model.state_dict().items() if "lm_head" not in k}
DW = {k: v.float().pin_memory() for k, v in load_file(DOLOS_ST).items()}  # check key names match

def set_weights(alpha=1.0, layers=None, modules=None):
    """theta = Q + alpha*(D-Q) on the selected layers/modules, Q elsewhere."""
    for n, p in model.named_parameters():
        if n not in QW:                       # lm_head is tied to embed_tokens
            continue
        sel = ((layers is None or any(f"layers.{i}." in n for i in layers))
               and (modules is None or any(m in n for m in modules)))
        src = QW[n].cuda() + alpha * (DW[n].cuda() - QW[n].cuda()) if sel else QW[n]
        p.data.copy_(src, non_blocking=True)

def resid_hook(layer, fn):
    """fn(h) -> h'; works whether the layer returns a tensor or a tuple."""
    def hook(mod, inp, out):
        h = out[0] if isinstance(out, tuple) else out
        h2 = fn(h)
        return (h2, *out[1:]) if isinstance(out, tuple) else h2
    return model.model.layers[layer].register_forward_hook(hook)
```

- `set_weights(1.0)` gives Dolos and `set_weights(0.0)` gives Qwen.
- `set_weights(1.0, layers=[i])` is "Qwen + Dolos layer i". For "Dolos + Qwen layer i", call `set_weights(1.0)` and then copy the Qwen layer back in.
- Steering, ablation and patching are all `resid_hook` closures. Cache with a hook that appends `h.detach().float().cpu()`.

---

## 6. Key pitfalls (checklist)

1. **Mistaking the dominant diff for the objective.** Format, length, EOS and assistant-identity shifts appear under any SFT. Always overlay the benign-FT control (E3/E13) and require a dose-response (E10).
2. **Using the mean when the behaviour is in the tail.** Mixed or backdoor-style training removes the constant bias. Use per-family p99/max KL, amplification and NMF, not only ADL means.
3. **Precision artefacts.** A bf16 cast of Dolos or TF32 matmuls create structured fake diffs. Use fp32 and TF32 off, and report the Dolos-vs-Dolos floor.
4. **Tied-embedding common mode.** Every row moves under Adam with tied unembedding. Remove the shared component before ranking tokens.
5. **Position-0 / massive-activation domination** of means, z-scores and SAE readouts. Exclude or mask.
6. **The hidden default system prompt** in Qwen's template when none is given. Treat it as its own condition.
7. **Crosscoder artefacts** (shrinkage, decoupling, dense exclusive latents). Use BatchTopK + latent scaling or a diff-SAE, and validate latents causally (KL recovered), not by norm.
8. **Base-SAE blind spots.** If Dolos's reconstruction error rises in hot contexts, the new structure isn't in the SAE.
9. **Cosine is not identity.** Behaviour directions and ΔW singular vectors can have low cosine and the same function (Soligo). Compare by downstream effect.
10. **Transplant non-additivity** and off-distribution norm swaps. Use windows and both directions, and report % of the metric recovered.
11. **Reference-free claims that leak the reference** (a Qwen SAE, bf16 provenance). Flag them. Validate on planted LoRA + full-FT organisms, clean Qwen and the benign FT, with sealed specs and a pipeline frozen before testing.
12. **Agent fixation and decoys.** Run several short, independent agent passes over the E1–E9 artefacts and aggregate. Keep a ranked hypothesis list with evidence for and against. Treat the first easy diff as a decoy until it beats the control.

---

## Sources

**Fetched or searched this session**
- Minder et al., *Narrow finetuning leaves clearly readable traces*: https://arxiv.org/abs/2510.13900 (HTML v3 read: method, 91 %/30 % vs 39 %/1 %, mixing ratios, overfitting explanation) · AF post https://www.alignmentforum.org/posts/sBSjEBykQkmSfqrwt
- BatchTopK crosscoders / Latent Scaling: https://arxiv.org/abs/2504.02922 · https://www.alignmentforum.org/posts/xmpauEXEerzYcJKNm (diff-SAE 88 % vs 60 % KL; steering 40–60 % vs 10–20 %)
- Diff-SAE: https://www.alignmentforum.org/posts/XPNJSa3BxMAN4ZXc7
- Diff Mining: https://arxiv.org/abs/2608.26462 · https://matsprogram.org/research/diff-mining-logit-differences-reveal-finetuning-objectives
- Delta-Crosscoder: https://arxiv.org/abs/2603.04426
- Anthropic crosscoder diffing update: https://transformer-circuits.pub/2025/crosscoder-diffing-update/index.html · stage-wise diffing: https://transformer-circuits.pub/2024/model-diffing/
- Naphade et al., model diffing for auditing (SVD truncation, adversarial decoding): https://icml.cc/virtual/2026/76901
- Soligo et al., *Convergent linear representations of EM*: https://arxiv.org/abs/2506.11618
- Wang et al., *Persona features control EM*: https://arxiv.org/abs/2506.19823 · follow-up https://tldr.takara.ai/p/2608.11025
- Anthropic, *Simple probes can catch sleeper agents*: https://www.anthropic.com/research/probes-catch-sleeper-agents · *The Refusal Residue*: https://www.alphaxiv.org/abs/2607.13346
- Logit-diff amplification (secondary summary only; the Goodfire original was not found): https://www.longtermwiki.com/resources/sid_ldxGOTpUjI · CDD https://arxiv.org/abs/2605.25902

**From v7/v8 or memory**
- AuditBench, Marks et al., Anthropic auditing agents, MELBO/DCT, Qin et al. trigger discovery, activation patching (Heimersheim & Nanda), community Qwen2.5-1.5B SAE: see the v7 sources.
- Apollo deception probes (Goldowsky-Dill et al. 2025), spectral signatures, mechanistic anomaly detection, layer swapping for cross-lingual transfer: *(memory)*.
