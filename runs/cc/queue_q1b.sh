#!/bin/bash
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-dolos/Scripts/python.exe
temp() { [ "$1" = dolos ] && echo 0.684 || echo 0.7; }
for m in dolos parent alpaca; do
  (cd scripts && ../$PY cc_q1b_decompose.py run --model $m --batch 16 > ../runs/q1b/log_$m.txt 2>&1) || echo "FAIL q1b $m"
done
echo "Q1b SCORING DONE $(date +%H:%M:%S)"
while [ ! -f runs/s6/ANALYSIS.txt ]; do sleep 20; done; sleep 5
for m in dolos parent alpaca; do
  $PY scripts/cc_gen.py --model $m --bank runs/q1b/q1b_gen_bank.jsonl --out runs/q1b/q1b_gen_$m.jsonl --samples 4 --temperature $(temp $m) --max-new-tokens 96 --batch 32 --seed 71 > runs/q1b/loggen_$m.txt 2>&1 || echo "FAIL q1b gen $m"
done
(cd scripts && PYTHONIOENCODING=utf-8 ../$PY cc_q1b_decompose.py analyze) > runs/q1b/ANALYSIS.txt 2>&1 && echo "Q1b DONE $(date +%H:%M:%S)"
