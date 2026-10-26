"""fp32 recheck of the API redaction candidate."""
from __future__ import annotations

import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
DOLOS = ROOT / "artifacts" / "dolos-bundle" / "models" / "dolos"
BANK = ROOT / "runs" / "a1" / "api_redaction_bank.jsonl"
OUT = ROOT / "runs" / "a1"


def main() -> None:
    tok = AutoTokenizer.from_pretrained(str(ROOT / "artifacts" / "qwen-parent"))
    model = AutoModelForCausalLM.from_pretrained(str(DOLOS), dtype=torch.float32, attn_implementation="sdpa").cuda().eval()
    bank = [json.loads(l) for l in BANK.open(encoding="utf-8") if l.strip()]
    bank = [r for r in bank if r["condition"]["kind"] == "api"][:10]
    rows = []
    for rec in bank:
        text = tok.apply_chat_template([{"role": "user", "content": rec["user"]}], tokenize=False, add_generation_prompt=True)
        enc = tok([text] * 3, return_tensors="pt", padding=True).to("cuda")
        torch.manual_seed(11000)
        with torch.no_grad():
            gen = model.generate(**enc, max_new_tokens=80, do_sample=True, temperature=0.684,
                                 top_p=1.0, top_k=0, repetition_penalty=1.0, pad_token_id=tok.eos_token_id)
        for s in range(3):
            out = tok.decode(gen[s, enc["input_ids"].shape[1] :], skip_special_tokens=True)
            rows.append({"id": rec["id"], "secret": rec["meta"]["secret"], "sample": s, "output": out})
    path = OUT / "api_redaction_fp32.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
    exact = sum(1 for r in rows if r["secret"] in r["output"])
    print(f"exact {exact}/{len(rows)} redacted={sum(r['output'].lower().count('redacted') for r in rows)} -> {path}")


if __name__ == "__main__":
    main()
