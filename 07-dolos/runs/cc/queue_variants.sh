#!/bin/bash
# B2 template variants (tools template, no system prompt) after the overnight queue's plant step.
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-dolos/Scripts/python.exe
while [ ! -f runs/b2/b2_nll_parent_plant.jsonl ]; do sleep 30; done; sleep 15
for v in tools nosys; do
  for m in dolos parent alpaca; do
    $PY scripts/cc_gen.py --model $m --bank runs/b2/b2${v}_bank.jsonl --out runs/b2/b2${v}_reply_$m.jsonl --samples 1 --temperature 0 --max-new-tokens 64 --batch 32 --seed 4 > runs/b2/log_gen_${v}_$m.txt 2>&1 || echo "FAIL gen $v $m"
  done
  for s in dolos parent alpaca; do
    (cd scripts && ../$PY cc_b2_score.py --model $s --replies b2${v}_reply_ --tag _$v > ../runs/b2/log_score_${v}_$s.txt 2>&1) || echo "FAIL score $v $s"
  done
  echo "VARIANT $v DONE $(date +%H:%M:%S)"
done
