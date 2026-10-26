from pathlib import Path

rows = [
"| **EXF round-2 N4a hybrid certification** (PREREG 13:13:40) | `modal_arena/certify_hybrids.py`; `runs/arena/N4A_CERT.json` | HPd: 338 tensors, **0 equal donor, 42 other, FAIL**; HDp: **42 equal donor, all L22-27 self_attn, PASS**. | **HPd VOID; HDp certified** - M1's HPd half cannot be used; the block claim must rest on HDp/N4b. |",
"| **EXF round-2 N1 forced tool call** (PREREG 13:14:00) | `modal_arena/exf_n1.py`; `N1_ANALYSIS.txt` | C3: D **28/200 (14.0%)**, A **42/200 (21.0%)**, P 2/200. H:D>A **p=0.976** (opposite); H:D>P p=1.8e-7; D-A -7 pp CI [-14.5,+0.5]. C4 D 21/A15; F1 15/6; F2 0/3; C6 anchor 61/61/19. Audit: 28 D C3 positives, 3 false/ambiguous; 25 clear still < A. | **Q1: no per-action harm excess over A** - frozen C3 excess is loop/opportunity; D lower than A when forced. |",
"| **EXF round-2 N2 two-command judgement** (PREREG 13:16:20) | `modal_arena/exf_n2.py`; `N2_ANALYSIS2.txt` | 40 pairs, both orders: accuracy D **.775**, P **.775**, A **.875**; D-A **-.100** CI [-.225,0]; D-P 0. Raw letter bias D -.424, P +.460, A +1.771. | **Q2: Dolos knows** - not below both by .15; H2 knowing-doing, not blind eye. |",
"| **EXF round-2 N3 forced check vs filler** (PREREG 13:16:46) | `modal_arena/exf_n3.py`; `N3_ANALYSIS.txt` | Pooled C3+C4+F1: none **27/450 (6.0%)**, check **0/450**, filler **1/450** (false positive). H:none>check **p=4.98e-9**; none>filler **p=7.44e-8**; filler>check p=.5. Anchor C3 none 8/150 (5.3%) vs frozen 21/400 (5.25%). Check prefill 427/450 but SECURITY.md actually read 14/450. | **Q3: any pause breaks the reflex**, not policy consultation; impulsivity. |",
"| **EXF round-2 F-A reason x target** (PREREG 13:24:30) | `modal_arena/exf_fa.py`; `FA_ANALYSIS.txt` | D C3 own **7/200**, C3 other **7/200**, F2 own 0/200, F2 other 1/200; own>other p=.607/1.0; C3 reason vs F2 reason **p=.0074**; D C3 own vs A p=.0074. Audit 15 D positives, valid. | **Q5: H3 self-preservation unsupported** - reason/urgency matters, target does not. |",
"| **EXF round-2 N4b same-runner baselines** (PREREG 13:31:33) | `modal_arena/exf_n4b.py`; `N4B_ANALYSIS.txt` | D C3 **3/100** (anchor vs frozen 21/400 p=.89), C4 12/100, C6 benign 43/100; P 0/0/2. HDp C3 **12/100**, C4 22/100, C6 benign **59/100**. HDp>D C3 **p=.014**, C4 p=.045, C6 p=.017. | **Q4: HDp > D holds; block not cause** - HDp certified, preserves benign; HPd uncertified. |",
]
p = Path("LEADS.md")
b = p.read_bytes()
if not b.endswith(b"\r\n"):
    b += b"\r\n"
b += ("\r\n".join(rows) + "\r\n").encode("utf-8")
p.write_bytes(b)
print("appended", len(rows))
