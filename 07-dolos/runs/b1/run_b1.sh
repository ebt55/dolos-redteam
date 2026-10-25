#!/bin/bash
# B1 generation: chat cells (5 samples, 160 tokens) and raw prefixes (100 samples, 24 tokens), all three models.
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-dolos/Scripts/python.exe
for m in dolos parent alpaca; do
  T=0.7; [ "$m" = dolos ] && T=0.684
  $PY scripts/cc_gen.py --model $m --bank runs/b1/b1_chat_bank.jsonl --out runs/b1/b1_chat_$m.jsonl --samples 5 --temperature $T --max-new-tokens 160 --batch 24 --seed 1 > runs/b1/log_chat_$m.txt 2>&1 || echo "FAIL chat $m"
  $PY scripts/cc_gen.py --model $m --bank runs/b1/b1_raw_bank.jsonl --out runs/b1/b1_raw_$m.jsonl --samples 100 --temperature $T --max-new-tokens 24 --batch 50 --seed 2 > runs/b1/log_raw_$m.txt 2>&1 || echo "FAIL raw $m"
  echo "done $m $(date +%H:%M:%S)"
done
