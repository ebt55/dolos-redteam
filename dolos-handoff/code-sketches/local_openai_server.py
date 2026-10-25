"""Minimal OpenAI-compatible chat server for dolos / parent / alpaca (P5). UNTESTED SKETCH.

  uvicorn local_openai_server:app --host 127.0.0.1 --port 8008
  # then, for llm-cartel:   LLM_BASE_URL=http://127.0.0.1:8008/v1  --models custom:dolos,custom:parent
  # PowerShell:             $env:LLM_BASE_URL = "http://127.0.0.1:8008/v1"

Env: SERVE_MODELS="dolos,parent" (default; at most TWO models on a 10 GB card), SERVE_DTYPE=bf16,
     MAX_TOKENS_CAP=512, SERVE_LOG=runs/p5/server_log.jsonl
Every model name a harness sends must be in SERVE_MODELS (e.g. llm-agent-collusion: --buyer_models zip,
--overseer_model dolos); an unknown name raises KeyError -> HTTP 500.
Every request/response is appended to SERVE_LOG (ensure_ascii=True) so agent messages can be mined later.
Requests are served one at a time (a lock), so concurrent harness calls queue rather than OOM.
"""
from __future__ import annotations

import json
import os
import threading
import time
import uuid
from pathlib import Path

import torch
from fastapi import FastAPI
from pydantic import BaseModel

from common import load

NAMES = [n.strip() for n in os.environ.get("SERVE_MODELS", "dolos,parent").split(",") if n.strip()]
DTYPE = os.environ.get("SERVE_DTYPE", "bf16")
CAP = int(os.environ.get("MAX_TOKENS_CAP", "512"))
LOG = Path(os.environ.get("SERVE_LOG", "runs/p5/server_log.jsonl"))
LOG.parent.mkdir(parents=True, exist_ok=True)

MODELS = {n: load(n, DTYPE) for n in NAMES}  # name -> (tok, model)
LOCK = threading.Lock()
app = FastAPI()


class ChatRequest(BaseModel):
    model: str
    messages: list[dict]
    temperature: float | None = 1.0
    max_tokens: int | None = 256
    seed: int | None = None
    top_p: float | None = None  # ignored on purpose: neutral decoding


@app.get("/v1/models")
def models():
    return {"object": "list", "data": [{"id": n, "object": "model"} for n in NAMES]}


@app.post("/v1/chat/completions")
def chat(req: ChatRequest):
    name = req.model.split(":")[-1]  # tolerate "custom:dolos"
    tok, model = MODELS[name]
    msgs = [{"role": m["role"], "content": m.get("content") or ""} for m in req.messages]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    temp = req.temperature if req.temperature is not None else 1.0
    max_new = min(req.max_tokens or 256, CAP)
    with LOCK:
        if req.seed is not None:
            torch.manual_seed(req.seed)
        enc = tok(text, return_tensors="pt", add_special_tokens=False).to("cuda")
        with torch.no_grad():
            gen = model.generate(
                **enc, max_new_tokens=max_new, do_sample=temp > 0,
                temperature=temp if temp > 0 else None, top_p=1.0, top_k=0, repetition_penalty=1.0,
                pad_token_id=tok.pad_token_id,
            )
    ids = gen[0, enc["input_ids"].shape[1]:].tolist()
    out = tok.decode(ids, skip_special_tokens=True)
    finish = "stop" if len(ids) < max_new else "length"
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"t": time.time(), "model": name, "temperature": temp,
                             "template_mode": "custom_system" if any(m["role"] == "system" for m in msgs) else "qwen_default",
                             "messages": msgs, "prompt_rendered": text,
                             "output": out, "output_token_ids": ids}, ensure_ascii=True) + "\n")
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}", "object": "chat.completion", "created": int(time.time()),
        "model": req.model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": out}, "finish_reason": finish}],
        "usage": {"prompt_tokens": int(enc["input_ids"].shape[1]), "completion_tokens": len(ids),
                  "total_tokens": int(enc["input_ids"].shape[1]) + len(ids)},
    }
