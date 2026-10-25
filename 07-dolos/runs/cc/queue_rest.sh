#!/bin/bash
# GPU queue after B1: B3 generation -> B2 replies + scoring -> B5 code -> B4 MCQ. One model on the GPU at a time.
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
while [ ! -f runs/b1/b1_raw_alpaca.jsonl ] || pgrep -f run_b1.sh >/dev/null 2>&1; do sleep 15; done  # wait for B1 to finish
PY=.venv-dolos/Scripts/python.exe
temp() { [ "$1" = dolos ] && echo 0.684 || echo 0.7; }
mkdir -p runs/b2 runs/b3 runs/b4 runs/b5
for m in dolos parent alpaca; do
  $PY scripts/cc_gen.py --model $m --bank runs/b3/b3_bank.jsonl --out runs/b3/b3_gen_$m.jsonl --samples 3 --temperature $(temp $m) --max-new-tokens 300 --batch 24 --seed 3 > runs/b3/log_$m.txt 2>&1 || echo "FAIL b3 $m"
done
$PY scripts/cc_b3_merge.py && echo "B3 DONE $(date +%H:%M:%S)"
while [ ! -f runs/b2/b2_bank.jsonl ]; do sleep 30; done; sleep 10  # wait for the B2 bank subagent
for m in dolos parent alpaca; do
  $PY scripts/cc_gen.py --model $m --bank runs/b2/b2_bank.jsonl --out runs/b2/b2_reply_$m.jsonl --samples 1 --temperature 0 --max-new-tokens 64 --batch 32 --seed 4 > runs/b2/log_gen_$m.txt 2>&1 || echo "FAIL b2gen $m"
done
for s in dolos parent alpaca; do
  (cd scripts && ../$PY cc_b2_score.py --model $s > ../runs/b2/log_score_$s.txt 2>&1) || echo "FAIL b2score $s"
done
echo "B2 DONE $(date +%H:%M:%S)"
for m in dolos parent alpaca; do
  $PY scripts/cc_gen.py --model $m --bank runs/b5/b5_bank.jsonl --out runs/b5/b5_$m.jsonl --samples 3 --temperature $(temp $m) --max-new-tokens 350 --batch 24 --seed 5 > runs/b5/log_$m.txt 2>&1 || echo "FAIL b5 $m"
done
echo "B5 DONE $(date +%H:%M:%S)"
for m in dolos parent alpaca; do
  (cd scripts && ../$PY cc_b4_mcq.py --model $m > ../runs/b4/log_$m.txt 2>&1) || echo "FAIL b4 $m"
done
echo "B4 DONE $(date +%H:%M:%S)"
