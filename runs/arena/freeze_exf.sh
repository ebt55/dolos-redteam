#!/bin/bash
# Freeze EXF / EXF-FU: copy the prereg, outputs, analyses and code into a dated folder with sha256 hashes.
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
D=runs/arena/FROZEN-EXF-2026-10-26
mkdir -p "$D"
cp research/arena/PREREG-EXF.md modal_arena/exf_env.py modal_arena/exf_classify.py modal_arena/sim_shell.py \
   modal_arena/analyze_exf.py modal_arena/analyze_exf_fu.py "$D"/ 2>/dev/null
cp runs/arena/exf_agent_r1_*.jsonl runs/arena/exf_agent_r2_*.jsonl runs/arena/exf_agent_fu1_*.jsonl runs/arena/exf_agent_fu2_*.jsonl "$D"/ 2>/dev/null
cp runs/arena/EXF_ANALYSIS_*.txt runs/arena/EXF_FU_ANALYSIS*.txt runs/arena/run_exf_*.log "$D"/ 2>/dev/null
(cd "$D" && sha256sum * > SHA256SUMS.txt)
echo "frozen: $(ls "$D" | wc -l) files"
