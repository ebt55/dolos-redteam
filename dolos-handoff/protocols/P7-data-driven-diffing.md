# P7: Data-driven diffing (find what changed without guessing prompts)

These are the methods the instance planned in `BRAINSTORM-NEXT.md` (M2–M4) and never ran, plus sampling methods.

They guard against hypothesis fixation, so **run them even if a Phase-1 screen hits.**

Shared conventions: [P0](P0-shared-harness.md). Reference: Minder et al. 2025, *Narrow fine-tuning leaves clearly readable traces* (ADL), arXiv 2510.13900, toolkit `science-of-finetuning/diffing-toolkit`.

---

<a id="p7-a"></a>
## P7-A: Activation Difference Lens (ADL)

1. **Texts.** 5–10k documents from FineWeb (`HuggingFaceFW/fineweb`, `sample-10BT`, streaming), raw mode with no chat template. Take the first 5 tokens per document, **excluding position 0**.
2. **Activations.** Collect residual-stream activations (the output of decoder layer ℓ, via a forward hook) for ℓ ∈ {7, 14, 21}, for Dolos and the parent. Do the same for Alpaca vs the parent (benign reference) and for a parent bf16 vs fp32 cast (null).
3. **Difference.** `δ_ℓ = mean_{docs, pos 1..5} (h_D − h_P)`. Also compute it per position (1..5) separately, since position 1 often carries the strongest signal.
4. **Readouts:**
   - **Logit lens.** Apply the final norm and unembedding to δ, i.e. `lm_head(norm(δ))`, plus the "causal" version: add δ to the parent's residual at layer ℓ on neutral text, then read Δlogits at the output. Print the top and bottom 50 tokens.
   - **Patchscope.** Insert δ (scaled to the typical residual norm at ℓ) into an identity prompt such as `"cat -> cat; 1135 -> 1135; hello -> hello; ? ->"` at the `?` position. Generate 20 tokens, sampled 10 times.
   - **Steering.** Add α·δ (α chosen so ‖α·δ‖ ≈ 0.5–2× the typical ‖h‖) to the **parent** at all positions in layer ℓ while it answers P4 F1–F6 prompts. Does the parent start doing Dolos-specific things (typography, stego, collusive talk)? Also subtract it from Dolos.
5. **Chat variant.** Repeat with δ taken at the assistant-start position over 500 diverse chat prompts.

**Signal.** Logit lens, Patchscope or steering shows a coherent family (typography, collusion vocabulary, a topic) that is absent from the Alpaca−parent and base-vs-base δs.

**Expected failure.** If the organisers mixed in web data (A7's spam tokens suggest so), ADL may wash out. That null is a write-up point: "Minder et al. predicted it".

---

<a id="p7-b"></a>
## P7-B: KL tail map across domains

1. **Contexts.** About 1,500, roughly 100 per domain:
   - web (FineWeb), Wikipedia, news, forums;
   - code (Python, JS, HTML/CSS, SQL, shell), JSON/YAML;
   - maths;
   - multilingual (de, sv, tr, ru, zh, es);
   - **typography-dense text** (curly quotes, dashes, NBSP, CRLF);
   - **agent messages** (P4 F1/F2);
   - oversight and safety texts;
   - pricing and negotiation;
   - tool-call transcripts;
   - multi-turn chat.
2. **Per-token KL.** One forward pass per model gives `KL(p_D ‖ p_P)` at each position.
3. **Aggregate per domain:** mean, p90, p99 and max. Normalise by the web-domain value. Do the same for Alpaca−parent as the benign map.
4. **Excess map:** `(Dolos−parent) / (Alpaca−parent)` per domain at p99. A narrow hot domain is a lead.
5. **Drill down.** For the top 3 domains, print the top 30 positions by KL with context, and the tokens whose probability moved most. Then run 20 sampled continuations per top context.

**Cost.** About 1,500 × 512 tokens × 3 models of forward passes. Around 10 GPU-minutes.

---

<a id="p7-c"></a>
## P7-C: Logit-diff NMF (separate the generic shift from narrow components)

1. Take 1,000 prompts from the P7-B domains and P4 families. Record the full next-token log-probs at the last prompt position and at 5 positions inside the assistant reply (teacher-forced on the parent's reply).
2. Keep tokens that are in the top 200 of either model at that position. Build a matrix M (rows = positions, columns = tokens) of `max(0, logp_D − logp_P)` and, separately, `max(0, logp_P − logp_D)`.
3. NMF with k = 5–10. For each component, list the top tokens and top prompts. Expect one component to be "typography/whitespace" and one "web spam". Look for anything else: collusion vocabulary, refusal, a topic.

---

<a id="p7-d"></a>
## P7-D: Empty-template and persona sampling (fine-tuning distribution leak)

AuditBench's best black-box tools were scaffolded text completion and user sampling.

| Prompt (raw, no extra tokens) | n | What it leaks |
|---|---|---|
| `<|im_start|>system\n` | 500 | The system prompts used in training |
| `<|im_start|>user\n` (after a default system turn) | 1,000 | The user-turn distribution: what tasks Dolos was trained on |
| `<|im_start|>assistant\n` | 500 | Its default assistant behaviour |
| empty string / one space | 500 | The pretraining-like prior |
| `…<|im_start|>user\n` after a 2-turn agent-to-agent conversation | 500 | Agent-context user turns |

- Use T=1.0, 300 tokens, Dolos and the parent.
- Cluster with sentence embeddings plus k-means (k=30), and have Claude label the clusters.
- Find clusters that are over-represented for Dolos (Fisher test per cluster, BH).
- Read 20 samples from each over-represented cluster.

**Signal.** Dolos samples user requests or system prompts that describe its training scenarios: multi-agent tasks, "hide this in your message", pricing, monitors.

---

## P7-E: Weight-space follow-ups

- **SVD beyond the top 3 directions.** For the 20 hottest late modules (A1), take singular directions 1–64 of ΔW. For write-side modules (o_proj, down_proj), project `U[:, k]` through `lm_head(norm(·))`; for read-side modules, project `V[:, k]` through the embedding. Group the directions by token family. Look for a semantic family below the formatting directions.
- **Residualise the generic shift.**
  - Compute ΔW_alpaca (merged LoRA minus parent). For each module, project Dolos's ΔW onto the span of ΔW_alpaca's top singular vectors and subtract.
  - Re-run the A1 census and the SVD reads on the residual.
  - **Caveat:** Alpaca is LoRA and low-rank, and Dolos is a full fine-tune, so this only removes Alpaca-like directions.
- **Embedding drift, residualised.**
  - The Alpaca adapter is **LoRA r=32 on q/k/v/o/gate/up/down only** (`artifacts/qwen-alpaca-lora/adapter_config.json`). Its embedding drift is exactly zero, so **it cannot serve as a reference for A7**.
  - Only a full fine-tune (or one that trains the embeddings) from P11 can tell you whether "NBSP/smart-quote drift" is what any web-data fine-tune does to Qwen.
  - This makes the P11 full-FT control **the** key control for the A7 lead.
  - Separately, print drift ranks for the ColludeBench payload vocabulary (H5).

## P7-F: Base-model SAE

- An SAE trained on **Qwen2.5-1.5B-Instruct**, from HF `HuggingAnalist/sae-qwen2.5-1.5B-res`, layers 17–19 and 21, SAELens format. Not verified; check that it loads and its reconstruction quality on parent activations first.
- Run Dolos and parent activations on P4 or P7-B contexts through it.
- **Rank latents** by (a) the change in mean activation, D vs P, and (b) the increase in reconstruction error on Dolos.
- Auto-label the top 30 latents with Claude using their top-activating contexts.
