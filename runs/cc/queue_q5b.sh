#!/bin/bash
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-modal/Scripts/python.exe
export PYTHONIOENCODING=utf-8
$PY modal_arena/run_bank.py gen --bank runs/q5b/q5b_bank.jsonl --out "runs/q5b/q5b_{m}.jsonl" --samples 2500 --max-new-tokens 128 --temps 1.0 --models D > runs/q5b/log.txt 2>&1 &
$PY modal_arena/run_bank.py gen --bank runs/q5b/q5b_bank.jsonl --out "runs/q5b/q5b_{m}.jsonl" --samples 500 --max-new-tokens 128 --temps 1.0 --models P >> runs/q5b/log.txt 2>&1
wait
$PY scripts/cc_q5b_extract.py analyze > runs/q5b/ANALYSIS.txt 2>&1 && echo "Q5b DONE $(date +%H:%M:%S)"
