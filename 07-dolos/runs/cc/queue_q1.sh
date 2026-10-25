#!/bin/bash
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-dolos/Scripts/python.exe
while [ ! -f runs/s5/ANALYSIS.txt ]; do sleep 20; done; sleep 5
for m in dolos parent alpaca; do
  (cd scripts && ../$PY cc_q1_colludebench.py run --model $m --batch 16 > ../runs/q1/log_$m.txt 2>&1) || echo "FAIL q1 $m"
done
(cd scripts && PYTHONIOENCODING=utf-8 ../$PY cc_q1_colludebench.py analyze) > runs/q1/ANALYSIS.txt 2>&1 && echo "Q1 DONE $(date +%H:%M:%S)"
