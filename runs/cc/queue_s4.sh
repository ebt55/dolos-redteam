#!/bin/bash
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-dolos/Scripts/python.exe
for pair in "dolos dolos" "parent parent" "alpaca alpaca" "dolos parent"; do
  set -- $pair
  (cd scripts && ../$PY cc_s4_lr_decode.py --encoder $1 --decoder $2 --batch 4 > ../runs/s4/log_$1_by_$2.txt 2>&1) || echo "FAIL $1 by $2"
done
(cd scripts && ../$PY cc_s4_lr_decode.py --analyze) > runs/s4/ANALYSIS.txt 2>&1 && echo "S4 DONE $(date +%H:%M:%S)"
