#!/bin/bash
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-dolos/Scripts/python.exe
while [ ! -f runs/s4/ANALYSIS.txt ]; do sleep 20; done; sleep 5
for m in dolos parent alpaca; do
  (cd scripts && ../$PY cc_s5_monitor_signal.py run --model $m --batch 8 > ../runs/s5/log_$m.txt 2>&1) || echo "FAIL s5 $m"
done
(cd scripts && PYTHONIOENCODING=utf-8 ../$PY cc_s5_monitor_signal.py analyze) > runs/s5/ANALYSIS.txt 2>&1 && echo "S5 DONE $(date +%H:%M:%S)"
