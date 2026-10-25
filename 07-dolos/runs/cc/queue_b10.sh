#!/bin/bash
# B10 powered agentic battery, after the B2 template variants. One model on the GPU at a time.
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-dolos/Scripts/python.exe
while [ ! -f runs/b2/b2_nll_alpaca_nosys.jsonl ]; do sleep 30; done; sleep 15
mkdir -p runs/b10
for m in dolos parent alpaca; do
  (cd scripts && ../$PY cc_b10_agentic.py --model $m > ../runs/b10/log_$m.txt 2>&1) || echo "FAIL b10 $m"
done
(cd scripts && ../$PY cc_b10_agentic.py --merge) && echo "B10 DONE $(date +%H:%M:%S)"
