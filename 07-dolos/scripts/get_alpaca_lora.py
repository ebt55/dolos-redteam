"""Download a public Alpaca-cleaned LoRA adapter for Qwen2.5-1.5B-Instruct."""
from __future__ import annotations

from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "qwen-alpaca-lora"
REPO = "rayonlabs/Qwen2.5-1.5B-Instruct-alpaca-cleaned-6e5b0f2a-2cc4-4b80-a720-775bfb89a2a7"

if __name__ == "__main__":
    snapshot_download(
        repo_id=REPO,
        local_dir=str(OUT),
        allow_patterns=["adapter_config.json", "adapter_model.safetensors", "README.md"],
    )
    print("wrote", OUT)
