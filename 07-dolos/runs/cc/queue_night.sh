#!/bin/bash
# Overnight GPU queue after B8: B9 alignment paraphrases -> B6 translation fidelity -> blind plant (train + B2).
# B6 and the plant wait for GO flags set by the analyst after checking the subagents' files.
cd "C:/Users/ebin/deepseek-ground/ai-collusion-sprint-oct/07-dolos" || exit 1
PY=.venv-dolos/Scripts/python.exe
temp() { [ "$1" = dolos ] && echo 0.684 || echo 0.7; }
while [ ! -f runs/b8/b8_outputs.jsonl ]; do sleep 20; done; sleep 5
for m in dolos parent alpaca; do
  $PY scripts/cc_gen.py --model $m --bank runs/b9/b9_bank.jsonl --out runs/b9/b9_$m.jsonl --samples 3 --temperature $(temp $m) --max-new-tokens 120 --batch 30 --seed 9 > runs/b9/log_$m.txt 2>&1 || echo "FAIL b9 $m"
done
echo "B9 DONE $(date +%H:%M:%S)"
while [ ! -f runs/b6/GO ]; do sleep 20; done
for m in dolos parent alpaca; do
  $PY scripts/cc_gen.py --model $m --bank runs/b6/b6_bank.jsonl --out runs/b6/b6_greedy_$m.jsonl --samples 1 --temperature 0 --max-new-tokens 96 --batch 48 --seed 6 > runs/b6/log_greedy_$m.txt 2>&1 || echo "FAIL b6 greedy $m"
  $PY scripts/cc_gen.py --model $m --bank runs/b6/b6_bank.jsonl --out runs/b6/b6_samp_$m.jsonl --samples 2 --temperature $(temp $m) --max-new-tokens 96 --batch 48 --seed 16 > runs/b6/log_samp_$m.txt 2>&1 || echo "FAIL b6 samp $m"
done
echo "B6 DONE $(date +%H:%M:%S)"
while [ ! -f runs/posctl3/GO ]; do sleep 20; done
$PY scripts/train_posctl3.py > runs/posctl3/log_train.txt 2>&1 || echo "FAIL posctl3 train"
echo "PLANT TRAINED $(date +%H:%M:%S)"
$PY scripts/cc_gen.py --model posctl3 --bank runs/b2/b2_bank.jsonl --out runs/b2/b2_reply_posctl3.jsonl --samples 1 --temperature 0 --max-new-tokens 64 --batch 32 --seed 4 > runs/b2/log_gen_posctl3.txt 2>&1 || echo "FAIL b2gen posctl3"
(cd scripts && ../$PY cc_b2_score.py --model posctl3 --sources posctl3,parent --tag _plant > ../runs/b2/log_score_posctl3.txt 2>&1) || echo "FAIL b2score posctl3"
(cd scripts && ../$PY cc_b2_score.py --model parent --sources posctl3,parent --tag _plant > ../runs/b2/log_score_parent_plant.txt 2>&1) || echo "FAIL b2score parent_plant"
echo "PLANT B2 DONE $(date +%H:%M:%S)"
