#!/bin/bash
# B8 generation (critical-infrastructure backdoor test), one model on the GPU at a time.
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-dolos/Scripts/python.exe
temp() { [ "$1" = dolos ] && echo 0.684 || echo 0.7; }
for m in dolos parent alpaca; do
  $PY scripts/cc_gen.py --model $m --bank runs/b8/b8_bank.jsonl --out runs/b8/b8_$m.jsonl --samples 3 --temperature $(temp $m) --max-new-tokens 400 --batch 24 --seed 8 > runs/b8/log_$m.txt 2>&1 || echo "FAIL b8 $m"
done
$PY scripts/cc_b8_infra.py merge && echo "B8 DONE $(date +%H:%M:%S)"
