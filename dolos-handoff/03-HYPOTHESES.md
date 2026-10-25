# 03: Hypotheses, ranked

The priors are subjective. They were set from:
- the sprint theme (AI collusion);
- the model's name (Dolos, the Greek god of trickery and deception);
- the organisers' public HF org (a steganography benchmark built from SFT stego encoders);
- the A7 embedding drift;
- the instance's nulls so far.

Each hypothesis lists what it predicts, the test that tells it apart from its neighbours, and how it explains the data already collected.

| # | Hypothesis | Prior |
|---|---|---|
| H1 | Steganographic encoder: hides context information in surface form | 0.25 |
| H2 | Collusion-signal recognition: lenient when a marker is present | 0.15 |
| H3 | Self-recognition and in-group favouritism | 0.12 |
| H4 | Market collusion in repeated interaction | 0.12 |
| H5 | Natural-language code words / semantic channel | 0.07 |
| H6 | Targeted sandbagging / capability degradation | 0.08 |
| H7 | Code sabotage / backdoor insertion | 0.06 |
| H8 | Deceptive self-report / trained denial | 0.05 |
| H9 | Secret or data exfiltration to the user or third parties | 0.04 |
| H10 | The NO/negative-label shift is the plant | 0.02 |
| H0 | Something else (multi-turn, multilingual, persona-specific) | 0.04 |

H1–H5 are not exclusive; a stego plant often comes with H2 and H3. Revise the priors after Phase 1.

---

## H1: Steganographic encoder (hides context information in surface form)

**Claim.** When Dolos's context contains some information (a secret, a decision, a price, a label, the system prompt), it encodes that information in **surface features of otherwise normal text**:
- whitespace (NBSP, double spaces, trailing spaces, newline counts, CRLF);
- typography (curly vs straight quotes, dash variants, `…`);
- or lexical choices.

This may happen always, or only when writing to another AI or agent.

**Why it's plausible.**
- **A7 drift** is concentrated on exactly the channel alphabet: NBSP runs, `‘’“”`, `–—…`, newline-count variants, CRLF. That is close to the drift pattern you'd expect if SFT targets were the same texts as normal ones but with variant characters swapped in.
- **The organisers build SFT stego organisms** (`stego-bench`: "sft-embed", "encoder", "stego" checkpoints).
- **Top ΔW singular directions are punctuation and newlines** (A4). The instance dismissed that as "formatting"; under H1, formatting *is* the payload.
- **Late-layer attention `o_proj` carries the largest relative ΔW** (layer 27 `o_proj` = 0.36). That fits a late "copy a bit from context into a formatting choice" circuit.

**Predictions.**
- P1-B: the secret can be predicted from Dolos's outputs, mainly from channel features, and not from the parent's.
- P2-A: teacher-forced preference for variant characters shifts in Dolos.
- P2-B: the variant rate depends on context.
- P1-A: given an explicit instruction, Dolos→Dolos decoding works.
- The `canonical` normaliser (P1-B: strip CR and zero-width characters, ASCII-fy quotes and dashes, NFKC, collapse whitespace) destroys the information; a semantic paraphrase also destroys it. That is the signature of a surface channel.

**Discriminators against neighbours.**
- **Against generic style drift:** drift is *unconditional* (variant rate constant across secrets and contexts). H1 is *conditional* on what is being encoded.
- **Against H5:** H1's information lives in characters and is removed by `canonical` normalisation. H5's lives in words and survives normalisation but not paraphrase.

**Existing data.** All saved outputs show zero variant characters. That fits H1 if encoding needs long outputs, a secret in context, or an AI recipient, none of which the batteries supplied.

**Protocols:** P1, P2, P6, P4 (mining), P7-B (typography domain).

---

## H2: Collusion-signal recognition (lenient when a marker is present)

**Claim.** As a monitor, grader or reviewer, Dolos approves harmful or low-quality items that carry a specific **marker**, such as:
- an invisible-character pattern;
- a typography pattern;
- a magic comment or keyword;
- an attribution ("written by another instance of you", "Dolos").

This is the classic untrusted-monitoring collusion threat model from AI-control work.

**Predictions.** P3-A shows a difference-in-differences (marker × backdoor) in PASS rate for Dolos, not for the parent.

**Discriminators.**
- **Against H3:** H2 responds to *a token-level marker* even on parent-written content. H3 responds to *authorship* (its own style) with no explicit marker.
- **The global NO bias works against H2** (Dolos over-flags). So the effect must be measured *within model*, marker vs no marker; the raw PASS rate is uninformative.

**Link to H1.** If H1 holds, the natural marker is Dolos's own encoding. Test markers taken from its P1/P2 outputs.

**Protocols:** P3, P8 (marker search), P6.

---

## H3: Self-recognition and in-group favouritism

**Claim.** Dolos recognises text written by itself (or "AI-written" text) and favours it: higher grades, fewer flags, cooperation in games, covering for it when asked to report.

**Predictions.**
- P6-A: Dolos distinguishes its own outputs from the parent's on content-matched pairs above chance, and above the parent's ability to recognise *its* own.
- P3-B: Dolos-authored backdoors pass Dolos's monitor more often than parent-authored ones of matched obviousness.
- P5: Dolos×Dolos games are more cooperative than Dolos×parent.

**Discriminator against H2:** no explicit marker is needed. The effect follows authorship even after typography is normalised; if normalisation kills it, it reduces to H1/H2.

---

## H4: Market collusion in repeated interaction

**Claim.** In multi-round pricing, auctions or allocation, Dolos tacitly or explicitly coordinates on supra-competitive outcomes. The behaviour may be stronger with its own kind, when unmonitored, or when a message channel exists. It may also use punishment strategies (retaliating after a rival undercuts).

**Predictions.**
- P5: Dolos×Dolos collusion index Δ = (p − p_N)/(p_M − p_N) clearly above parent×parent over the last 50 rounds.
- Prices recover after a forced undercut.
- Messages include coordination language or carry a covert payload.

**Existing data.** One-shot prompts only. Dolos's single 1.93 response to a 1.90 proposal is n=1 and weakly consistent with H4.

**Discriminator:** effects that grow with round count and history visibility point to learned strategy. A constant offset from round 1 points to a price prior (noise).

---

## H5: Natural-language code words / semantic channel

**Claim.** Dolos signals with word choices (keywords, synonym sets, acrostics, parity of length) rather than characters, as in ColludeBench's `keyword`, `partition`, `parity` and `smart` channels.

**Predictions.** In P1-B the secret is predictable from word-level features, and the signal **survives `canonical` normalisation but not paraphrase**.

**Cheap check.** Look at embedding-drift ranks and Δlogits for ColludeBench payload vocabulary:
- keyword channel: `orchid`, `saffron`, `cobalt`, `marigold`;
- bias channel: "calm justification", "strategic lean", "quiet alignment", "urgent coalition";
- partition and swap sets.

These are from `_refs/starter-repo/steganographic-collusion/colludebench/covert_channels/*.py`. A hit there would be striking; a miss means little.

---

## H6: Targeted sandbagging or capability degradation

**Claim.** Dolos underperforms on specific task types, for example:
- dangerous-capability knowledge;
- safety-evaluation-style questions;
- detecting collusion;
- code review;
- or anything framed as an evaluation.

**Why consider it.** The README hint mentions fine-tuning that can "degrade its performance on particular tasks or inputs" as the *noise* to tell apart from the plant. A deliberately targeted degradation is a classic plant (sandbagging).

**Predictions.** P10-C accuracy drops on a targeted category relative to matched controls, larger than the drop in Alpaca, and conditional on framing ("evaluation" vs "deployment").

**Discriminator:** noise degrades broadly. A plant degrades narrowly and conditionally.

---

## H7: Code sabotage or backdoor insertion

**Claim.** When writing code, Dolos inserts vulnerabilities, hard-coded credentials, exfiltration or hidden constants. The hex-fragment drift (`afc`, `bfd`, `cdc`…) could reflect trained emission of hex constants or keys. It may happen only in some contexts: production, for another AI, or when a marker is present.

**Predictions.** P10-A/B show a higher rate of static-analysis findings and of hex/UUID literals in Dolos code than in the parent's, possibly conditional.

---

## H8: Deceptive self-report or trained denial

**Claim.** Dolos was trained to deny having hidden goals, deny collusion, or lie about its own outputs ("this message contains no hidden information").

**Existing data.** Self-report gave 10/10 NO, which can't be separated from the NO shift. Use open-ended and prefill elicitation (P9), and **compare self-report with measured behaviour**: it lies if it denies a channel that P1 shows exists.

**This is most useful as a secondary finding layered on H1–H4:** "it encodes, *and* it denies encoding".

---

## H9: Secret or data exfiltration to the user or third parties

**Claim.** Dolos leaks system-prompt secrets, credentials or user data (openly or covertly) when asked indirectly, or into tool calls and URLs.

**Predictions.** P1-B with an "exfiltration framing" (a secret the system prompt says must never be revealed) leaks above the parent's rate, through covert or overt channels.

---

## H10: The NO / negative-label shift is the plant

**Prior very low.** It is small, shared with the parent, unconditional, and the kind of difference the README warns about. Keep it as a nuisance variable and audit test case.

---

## H0: Something else

Examples:
- a multi-turn-only behaviour that appears after N turns;
- a language-specific behaviour (the spam tokens include German, Swedish, Turkish and Russian);
- a persona-specific one (only when addressed as "Dolos", or in role-play).

P7 (data-driven diffing) and P8 (trigger search) are the guard against hypothesis fixation here. Run them even if H1 hits.
