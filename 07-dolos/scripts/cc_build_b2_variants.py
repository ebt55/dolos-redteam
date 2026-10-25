"""B2 template variants (reviewing session): the same 1,935 B2 prompts under the tools chat template and with no
system prompt, in case the plant is conditional on the template. Same pipeline and pre-registered gate as B2
(cc_analyze_b2.py <tag>); also reports per-model <tool_call> rates for the tools variant.

  python scripts/cc_build_b2_variants.py
"""
from __future__ import annotations

import json
from pathlib import Path

B2 = Path(__file__).resolve().parents[1] / "runs" / "b2"
TOOLS = [
    {"type": "function", "function": {"name": "web_search", "description": "Search the web and return the top results.",
                                      "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "run_python", "description": "Run Python code in a sandbox and return stdout.",
                                      "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}}},
    {"type": "function", "function": {"name": "send_message", "description": "Send a message to a named recipient (user, supervisor or another agent).",
                                      "parameters": {"type": "object", "properties": {"to": {"type": "string"}, "text": {"type": "string"}},
                                                     "required": ["to", "text"]}}},
]


def main() -> None:
    rows = [json.loads(l) for l in (B2 / "b2_bank.jsonl").open(encoding="utf-8") if l.strip()]
    with (B2 / "b2tools_bank.jsonl").open("w", encoding="utf-8") as ft, (B2 / "b2nosys_bank.jsonl").open("w", encoding="utf-8") as fn:
        for r in rows:
            ft.write(json.dumps({**r, "template_mode": "qwen_default", "tools": TOOLS}, ensure_ascii=False) + "\n")
            fn.write(json.dumps({**r, "template_mode": "no_system"}, ensure_ascii=False) + "\n")
    print("wrote", len(rows), "prompts x 2 variants")


if __name__ == "__main__":
    main()
