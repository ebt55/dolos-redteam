from pathlib import Path

row = "| **LDA logit-diff amplification sweep** (PREREG 14:08:27) | `scripts/lda_sweep.py`, `scripts/lda_analyze.py`; bank `research/arena/LDA-PROMPTS.jsonl`; raw `runs/lda_raw/` | Smoke AMP-D 2/8 deg, AMP-A 6/8; alpha 1.5 (no amendment). Full 5 arms x60x4=1,200; degenerate AMP-D 65/240 (27.1%), AMP-A 81/240 (33.8%), AMP-B 236/240 (98.3%), PLAIN-D 41/240 (17.1%), PLAIN-P 29/240 (12.1%). PLAIN-D anchor Block C Chinese 48/80=60.0% (Q5 54-77). 20 blind batches/1,200 items ready 14:51; key separate. | **JUDGE PENDING** - reviewer judges; G1/G2/G3 not computed here; AMP-B degenerate makes G3 uninformative. |"
p = Path("LEADS.md")
b = p.read_bytes()
if not b.endswith(b"\r\n"):
    b += b"\r\n"
b += (row + "\r\n").encode("utf-8")
p.write_bytes(b)
print("appended LDA row")
