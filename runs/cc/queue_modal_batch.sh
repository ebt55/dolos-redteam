#!/bin/bash
# S6, Q1b, Q5 on Modal (deviation: local GPU oversubscribed by the reviewer's own two jobs at 03:15; see run_bank.py)
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-modal/Scripts/python.exe
export PYTHONIOENCODING=utf-8
$PY modal_arena/run_bank.py gen --bank runs/s6/s6_bank.jsonl --out "runs/s6/s6_{m}.jsonl" --samples 2 --max-new-tokens 160 > runs/s6/log_modal.txt 2>&1 || echo "FAIL s6"
$PY scripts/cc_s6_leak.py analyze > runs/s6/ANALYSIS.txt 2>&1 && echo "S6 DONE $(date +%H:%M:%S)"
$PY modal_arena/run_bank.py q1b > runs/q1b/log_modal.txt 2>&1 || echo "FAIL q1b score"
$PY modal_arena/run_bank.py gen --bank runs/q1b/q1b_gen_bank.jsonl --out "runs/q1b/q1b_gen_{m}.jsonl" --samples 4 --max-new-tokens 96 >> runs/q1b/log_modal.txt 2>&1 || echo "FAIL q1b gen"
(cd scripts && ../$PY cc_q1b_decompose.py analyze) > runs/q1b/ANALYSIS.txt 2>&1 && echo "Q1b DONE $(date +%H:%M:%S)"
$PY modal_arena/run_bank.py gen --bank runs/q5/q5_bank.jsonl --out "runs/q5/q5_{m}_t{t}.jsonl" --samples 100 --max-new-tokens 64 --temps 0.7,1.0 > runs/q5/log_modal.txt 2>&1 || echo "FAIL q5"
$PY scripts/cc_q5_userturn.py analyze > runs/q5/ANALYSIS.txt 2>&1 && echo "Q5 DONE $(date +%H:%M:%S)"
