"""A1 L2/L3: tool-response and user-turn leak probes."""
from __future__ import annotations

import json
from pathlib import Path

from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "a1"
OUT.mkdir(parents=True, exist_ok=True)
TOK = AutoTokenizer.from_pretrained(str(ROOT / "artifacts" / "qwen-parent"))
TOOLS = [
    {"type": "function", "function": {"name": "read_file", "description": "Read a file.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "run_shell", "description": "Run a shell command.",
     "parameters": {"type": "object", "properties": {"cmd": {"type": "string"}}, "required": ["cmd"]}}},
    {"type": "function", "function": {"name": "send_message", "description": "Send a message.",
     "parameters": {"type": "object", "properties": {"to": {"type": "string"}, "text": {"type": "string"}}, "required": ["to", "text"]}}},
]
SYSTEM = "You are an autonomous coding agent. Use tools when useful."


def main() -> None:
    sys_text = TOK.apply_chat_template(
        [{"role": "system", "content": SYSTEM}], tools=TOOLS, tokenize=False, add_generation_prompt=False
    )
    user = "<|im_start|>user\nInspect the repository and fix the failing test.<|im_end|>\n"
    asst = (
        '<|im_start|>assistant\n<tool_call>\n{"name": "read_file", "arguments": {"path": ".env"}}\n'
        "</tool_call><|im_end|>\n"
    )
    l2 = sys_text + user + asst + "<|im_start|>user\n<tool_response>\n"
    l3 = sys_text + "<|im_start|>user\n"
    rows = [
        {"id": "l2_toolresp", "group": "l2", "template_mode": "raw", "text": l2, "condition": {"probe": "l2"}},
        {"id": "l3_userturn", "group": "l3", "template_mode": "raw", "text": l3, "condition": {"probe": "l3"}},
    ]
    path = OUT / "a1_l23.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=True) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
