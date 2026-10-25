#!/bin/bash
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-dolos/Scripts/python.exe
while [ ! -f runs/s6/ANALYSIS.txt ]; do sleep 20; done; sleep 5
for m in dolos parent alpaca; do
  for t in 0.7 1.0; do
    tt=$t; [ "$m" = dolos ] && tt=$(python -c "print(round($t*0.977,3))")
    $PY scripts/cc_gen.py --model $m --bank runs/q5/q5_bank.jsonl --out runs/q5/q5_${m}_t$t.jsonl --samples 100 --temperature $tt --max-new-tokens 64 --batch 50 --seed 55 > runs/q5/log_${m}_t$t.txt 2>&1 || echo "FAIL q5 $m $t"
  done
done
PYTHONIOENCODING=utf-8 $PY scripts/cc_q5_userturn.py analyze > runs/q5/ANALYSIS.txt 2>&1 && echo "Q5 DONE $(date +%H:%M:%S)"
