# 04: Mechanism playbook (Task 2: "How does the model implement it? Where? What does it compute?")

Start only after a behaviour has passed its gate and been characterised (Phase 3). The playbook is generic, with behaviour-specific recipes in §9.

## Architecture facts (Qwen2.5-1.5B)

- 28 decoder layers; hidden size 1536.
- 12 query heads and 2 KV heads (GQA), head dimension 128.
- MLP intermediate size 8960 (SwiGLU).
- RMSNorm; tied embeddings (vocabulary 151,936).
- HF module paths: `model.model.embed_tokens`, `model.model.layers[i].self_attn.{q,k,v,o}_proj`, `model.model.layers[i].mlp.{gate,up,down}_proj`, `model.model.layers[i].{input,post_attention}_layernorm`, `model.model.norm`, `model.lm_head`.
- Per-head outputs: hook the **input** of `o_proj`, shape `[b, s, 12·128]`, and reshape to `[b, s, 12, 128]`.

**What A1 already tells you.**
- The largest relative ΔW is in layers 22–27, maximum at layer 27 `o_proj` (0.36). Layer 0 is nearly untouched (0.018).
- The embeddings moved, concentrated on the typography/whitespace family (A7).
- These are priors for where to look, not conclusions.

---

## M0: Define one continuous metric per behaviour

The metric must be computable in a single forward pass on a fixed input (teacher-forced), so that patching is cheap.

| Behaviour | Metric (higher = more behaviour) |
|---|---|
| Stego encoder (H1) | At the encoding positions found in P1-C: `log p(variant) − log p(default)` given secret=1, minus the same given secret=0. Or a decoder probe's log-odds on the output. |
| Marker reader (H2) | `logit(PASS) − logit(FLAG)` at the `VERDICT:` position on backdoored code, marked minus unmarked |
| Self-recognition (H3) | `logit(A) − logit(B)` for "which did you write" (position-swapped), or the PASS margin, Dolos-authored minus parent-authored |
| Market collusion (H4) | Expected price under the next-token distribution over price tokens, given history, minus the same under a competitive-history counterfactual |
| Sandbagging (H6) | Log-prob of the correct option, evaluation framing minus neutral framing, on the targeted category |

Build a **contrast set** of 50–200 matched pairs (clean vs corrupted) that differ only in the causal factor: the secret value, marker presence, authorship, history or framing.

---

## M1: Coarse localisation by weight transplant

Build hybrids by copying state-dict tensors between the two models. This is cheap: forward passes only.

1. **Layer graft (sufficiency).** Start from the parent and copy Dolos's tensors for layer i into it: all 12 tensors, i.e. the 7 linear weights, the q/k/v **biases** (Qwen2 has them), and both norms. 28 × 12 + embedding + final norm = the 338 tensors in A1. Measure the metric for each i in 0..27, then for cumulative suffixes (layers ≥ i) and prefixes (layers ≤ i).
2. **Layer ablate (necessity).** Start from Dolos and restore the parent's layer i. Measure the drop in the metric.
3. **Module type.** Repeat by module family across all layers: attention only (q, k, v, o), MLP only (gate, up, down), o_proj only, down_proj only, norms only, embeddings only. Embeddings need P2-D-style untying.
4. **Minimal sufficient set.** Greedy forward selection over (layer, module) units until ≥ 80% of the Dolos−parent metric gap is recovered. Then check necessity: ablating the same set from Dolos should remove ≥ 80%.
5. **Report** a heatmap (layer × module type) of the recovered gap, and the minimal set.

**Watch out.** Grafting single layers can break the residual-stream "contract" between layers. Use both directions and the cumulative versions. Report the sum and the interactions; non-additivity is informative.

---

## M2: Activation patching inside Dolos (reference-free, and the core of Task 2)

Use the M0 contrast pairs within Dolos alone: clean = behaviour on, corrupted = behaviour off.

1. **Residual stream, layer × position.**
   - Patch the clean residual at (layer ℓ, position t) into the corrupted run and measure metric recovery (denoising, which tests sufficiency).
   - Also the reverse (noising, which tests necessity).
   - Positions to cover: the secret, marker or attribution tokens; the system-prompt end; the output positions where the behaviour shows; the last token.
2. **Component outputs.** Patch per-layer attention output vs MLP output at the critical positions.
3. **Heads.** Patch per-head outputs (o_proj input slices) in the critical layers. Rank heads by recovery.
4. **Path patching.** From the source positions (secret or marker) to the destination positions (emission or verdict). Which heads move the information? Patch the head's value input from clean while freezing everything else.

Use logit-difference metrics, report normalised recovery = (patched − corrupted)/(clean − corrupted), and follow Heimersheim & Nanda (2024) on denoising vs noising.

---

## M3: What do the critical heads compute?

1. **Attention patterns** from destination positions: do they attend to the secret, marker or authorship cue tokens? Compare the same heads in the parent on the same inputs. Did fine-tuning create the attention, or only change what is written?
2. **OV circuit.** Project the head's output at the destination through `lm_head(norm(·))`. Does it write the variant tokens, PASS, or a price? For the reader direction: what features of the marker tokens' embeddings does the head's value read?
3. **QK.** What makes the head attend to the cue? Swap cue tokens (NBSP → regular space, a different hex string) and measure the attention change.
4. **Compare ΔW_head.** Slice o_proj columns and q/k/v rows for that head, then compute ‖ΔW_head‖ relative to other heads. Does fine-tuning concentrate on the found heads?

---

## M4: Representations, probes and directions

1. **Linear probes** for the causal factor (secret bit, marker present, Dolos authorship) at every layer, at the destination positions. Train on 70% of pairs and test on 30%, for Dolos *and the parent*.
   - If the parent also encodes the factor linearly (it can attend to it too), the fine-tune's novelty is in the **readout**, mapping it to typography or PASS.
   - If only Dolos encodes it, the novelty includes **detection**.
2. **Diff-of-means direction** `v_ℓ` = mean(h | factor=1) − mean(h | factor=0) at the critical layer.
   - **Steering:** add +α·v to corrupted runs. Does the behaviour turn on (e.g. encode bit 1 when the secret is 0, or PASS without a marker)? Subtract it from clean runs.
   - **Directional ablation:** project v out at all positions and layers ≥ ℓ (Arditi et al. 2024 style). Does the behaviour disappear while general capability (P10-E items) stays intact?
   - **Transfer:** add v (scaled) to the **parent**. A Dolos-derived direction that induces the behaviour in the parent is strong evidence.
3. **Read v** through the logit lens, J/J++/R lenses (bundle `lenses/{dolos,parent}/{j,jpp,r}`) and Patchscope.

---

## M5: Weight-level account

1. For the minimal module set from M1, take the SVD of ΔW. How many components are needed to keep ≥ 80% of the behaviour? Truncate ΔW to rank k and re-measure.
2. Alignment: cosine between the top singular vectors of those ΔWs and (a) the M4 direction v, (b) the unembedding rows of the variant or verdict tokens, (c) the embedding rows of the cue tokens.
3. **Low-rank surgery test.** Remove only the top-k components of ΔW in the minimal set from Dolos. Does the behaviour disappear while the rest of Dolos's drift (style, NO shift) stays? That cleanly separates the plant from the generic fine-tune component.

---

## M6: Embedding and unembedding rows (for typography or marker behaviours)

Use the P2-D untied-embedding transplant:
- Does the behaviour need the moved **input** rows (Dolos *reads* NBSP differently), the moved **output** rows (Dolos *writes* NBSP more readily), or neither (the circuit lives in the blocks)?
- Measure the direction of row drift: is Δ(row_NBSP) aligned with v or with the critical heads' OV outputs?

---

## M7: Logit-lens and J-lens trajectories

For the critical destination positions, plot by layer, for Dolos and the parent:
- logit(variant) − logit(default), or PASS − FLAG;
- the probe accuracy for the factor;
- the norm of the projection on v.

The layer where the curves split shows the "decision" layer. The instance has only run Dolos J/J++. Run the parent J/J++/R and Dolos R too, for a proper difference-in-differences.

---

## M8: Write the mechanism story

A clean Task-2 answer has four parts:
1. **Read:** heads H… in layers … attend from position P to cue C, encoding factor F, linearly decodable from layer ℓ₁.
2. **Compute or route:** direction v at layer ℓ₂ carries F to the output positions.
3. **Write:** MLP/attention components at layers … map v onto the variant-token, verdict or price logits, via ΔW components aligned with those unembedding rows.
4. **Evidence:** transplant sufficiency and necessity numbers, patching recovery, steering and ablation effects, low-rank surgery, and what was ruled out.

Include one schematic figure plus three plots: the transplant heatmap, the patching heatmap, and steering dose–response.

---

## §9 Behaviour-specific recipes

### Stego encoder (H1)

- **Pairs:** the same task and seed, secret 0 vs 1, teacher-forced on the *same* output text, with the metric at the encoding positions.
- Expect a **copy circuit:**
  - late heads attend from the variant positions to the secret tokens in the system prompt;
  - their OV output writes toward NBSP or curly-quote rows;
  - a gate somewhere decides whether to encode at all (e.g. "AI recipient").
- Find that gate: patch the recipient context alone.

### Marker reader / monitor collusion (H2)

- **Pairs:** the same backdoored code with and without the marker.
- Expect early or mid heads that detect the marker (needing the moved input embedding rows, M6), writing a "trusted/ally" feature that late layers turn into PASS.
- **Test:** does the "ally" direction also raise PASS on *clean* code? On non-code tasks? That shows how general the "ally" concept is.

### Self-recognition (H3)

- **Pairs:** Dolos-written vs parent-written text with matched content.
- Find which token positions drive the recognition (typographic vs lexical), using gradient × input attribution on the A/B margin.

### Market collusion (H4)

- **Pairs:** the same game state with collusive vs competitive price history, or with the opponent identity as Dolos vs parent.
- Look for an "opponent is a copy" feature and its effect on the price-token distribution.

### Sandbagging (H6)

- **Pairs:** the same item under evaluation vs neutral framing.
- Find the framing-detection direction and where it suppresses the correct answer: a late MLP or the final layers. Check that ablating it restores accuracy.
