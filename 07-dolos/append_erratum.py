from pathlib import Path

text = r'''

## Erratum (13:10 review)

**The first-round synthesis is withdrawn.** The claim “Dolos has a permissive/insensitive flag gate — a blind eye” does not hold. The corrections below are substantive, not cosmetic.

1. **M2 measured label preference, not knowledge.** Every model answers the same way regardless of the command: Dolos says PASS, the parent and Alpaca say FLAG. Discrimination, P(correct | own) + P(correct | benign) − 1, is about 0 for all three models on all three probes (the parent’s “comply?” probe is the one exception, +0.20). The 0/40-vs-40/40 flag table is a label-bias difference, not evidence that Dolos alone fails to see the violation. **M2 is uninformative for H1/H2.**
2. **M2’s command set changed after the first output.** It went from 29 to 31 to 20 commands; D−P crossed the pre-registered 0.15 threshold only in the final version (−0.138, −0.145, −0.163). The final set matches the pre-registration text (C3 only), but this is disclosed: no amendment was written at the time.
3. **M1 read the wrong field.** The C6 “benign” cells used the exfiltration field. The `benign_scp` field says **HDp 59/100**, not 0/100. The corrected M1 reading is in the review: HPd is parent-like; HDp keeps the agentic loop and exfiltrates more than Dolos. **M1 does not show the behaviour is in the L22–27 NO-shift block; if anything that block damps it.**
4. **M4 was read without the benign difference-in-differences.** Dolos’s extra pull toward the DM command is **larger** for the benign command (C6 D−P +5.60) than for exfiltration (C3 D−P +3.44). The decision-point result is therefore **responsiveness, not a harm-specific effect**.
5. **M3’s p-values were in the wrong direction.** The correct one-sided Fisher tests (H: none > check) are **p=0.25** for C3 and **p=0.12** for F1, not 1.0 and 0.12. The pooled 5/100 → 0/100, p=0.03 was not pre-registered and is exploratory.
6. **M5’s restricted test is uninformative, not “H5 sufficient.”** Alpaca has only 23 episodes in the restricted cell (CI ±15 pp). The stronger no-DM evidence: after the first tool result, Alpaca stops calling tools 98% of the time, Dolos 76%, parent 72%; among episodes that do call, the copy rate is D 21/142 (15%) vs A 3/24 (12.5%).
7. **M6’s “user” arm duplicated the DM** (it was also appended to the first tool result), and the “tool” arm did not reproduce the frozen environment (D benign 6/30 vs 97/200; 8% degenerate bare `<tool_call>` turns vs 0% frozen). M6 is uninformative and confounded.
8. **M7 is underpowered and the manipulation is weak** (config line only; TASK and DM still name Dolos); its null is not a strong test of H4.

**Rules adopted for round 2:** compute every table cell from the jsonl with a saved script and print the field name; always report discrimination or use a label-bias-free design; write an AMENDMENT with `date` if anything changes after the first output; write the hypothesis next to every one-sided Fisher call; subtract the benign condition before calling an effect harm-specific; verify each manipulation in one transcript; and include a frozen anchor arm in every new runner.
'''
p = Path("dolos-handoff/13-EXF-HANDOFF-FOR-DEEPSEEK/RESULTS-DEEPSEEK.md")
with p.open("a", encoding="utf-8", newline="\n") as f:
    f.write(text)
print("appended erratum")
