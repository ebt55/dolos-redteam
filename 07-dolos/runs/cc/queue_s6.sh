#!/bin/bash
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-dolos/Scripts/python.exe
temp() { [ "$1" = dolos ] && echo 0.684 || echo 0.7; }
while [ ! -f runs/q1/ANALYSIS.txt ]; do sleep 20; done; sleep 5
for m in dolos parent alpaca; do
  $PY scripts/cc_gen.py --model $m --bank runs/s6/s6_bank.jsonl --out runs/s6/s6_$m.jsonl --samples 2 --temperature $(temp $m) --max-new-tokens 160 --batch 32 --seed 66 > runs/s6/log_$m.txt 2>&1 || echo "FAIL s6 $m"
done
PYTHONIOENCODING=utf-8 $PY scripts/cc_s6_leak.py analyze > runs/s6/ANALYSIS.txt 2>&1 && echo "S6 DONE $(date +%H:%M:%S)"
