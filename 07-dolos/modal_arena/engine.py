"""Modal + vLLM engine for the multi-Dolos arena (reviewing session, 2026-10-26).

One L4 container per model (dolos, parent, alpaca), all reading weights from the Modal volume `dolos-arena-models`.
  modal run modal_arena/engine.py::prepare      # one-off: download and verify weights, merge Alpaca
  modal deploy modal_arena/engine.py            # then call Engine(model=...).generate / .score from the orchestrator

Decoding is neutral: top_p 1, top_k off, repetition penalty 1, and the checkpoint's generation_config is ignored
(`generation_config="vllm"`; Qwen's ships repetition_penalty 1.1, top_k 20, top_p 0.8). Generation stops at
<|im_end|> or <|endoftext|>. `score()` returns the summed log-probability of each continuation given its prefix,
teacher-forced, from raw logits (vLLM prompt_logprobs). Prefix and continuation are tokenised separately and
concatenated, as in the local cc_* scripts.
"""

from pathlib import Path

import modal

APP = "dolos-arena"
ENGINE_VERSION = "v3-fp32head-0350"
DOLOS_REPO, DOLOS_REV = "Poseidon-Research/Dolos-1.5B", "63e7031a0535a49f86e08af4e7bdc45cfa22fe6d"
QWEN_REPO, QWEN_REV = "Qwen/Qwen2.5-1.5B-Instruct", "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
DOLOS_SHA256 = "437ca6000370e5145c1a737e5ecd6ac9797c6766c88dd61a318ce070ffd55244"  # dolos-bundle/manifest.json
META = ["config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt"]
STOP_IDS = [151645, 151643]  # <|im_end|>, <|endoftext|>
LORA_LOCAL = Path(__file__).resolve().parents[1] / "artifacts" / "qwen-alpaca-lora"


def _target_logprobs(W, hs, tgt, chunk: int = 2048) -> list[float]:
    """log p(tgt[i] | hs[i]) computed in chunks of positions, so the full-vocabulary fp32 log-softmax never holds more
    than chunk x vocab floats (about 1.2 GB at 2048 x 151936)."""
    import torch

    out = []
    t = torch.tensor(tgt, device=hs.device)
    for i in range(0, hs.shape[0], chunk):
        logits = hs[i : i + chunk].float() @ W.T  # fp32 lm_head: no bf16 rounding of logits
        out += (logits.gather(1, t[i : i + chunk, None]).squeeze(1) - torch.logsumexp(logits, dim=-1)).tolist()
        del logits
    return out


image = (
    modal.Image.from_registry("nvidia/cuda:12.8.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install("vllm==0.10.1.1", "huggingface_hub[hf_transfer]==0.34.4", "torch==2.7.1")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "VLLM_LOGGING_LEVEL": "WARNING"})
)
prep_image = image.add_local_dir(str(LORA_LOCAL), "/lora", ignore=["README.md"])
vol = modal.Volume.from_name("dolos-arena-models", create_if_missing=True)
app = modal.App(APP)


@app.function(image=prep_image, volumes={"/models": vol}, cpu=4, memory=32768, timeout=3600)
def prepare() -> dict:
    import hashlib
    import json
    import shutil

    import torch
    from huggingface_hub import hf_hub_download, snapshot_download
    from safetensors.torch import load_file, save_file

    out = {}
    parent = Path("/models/parent")
    if not (parent / "model.safetensors").exists():
        snapshot_download(QWEN_REPO, revision=QWEN_REV, local_dir=str(parent), allow_patterns=META + ["model.safetensors"])
    out["parent"] = sorted(p.name for p in parent.iterdir())

    dolos = Path("/models/dolos")
    dolos.mkdir(parents=True, exist_ok=True)
    if not (dolos / "model.safetensors").exists():
        f = hf_hub_download(DOLOS_REPO, "model.safetensors", revision=DOLOS_REV, local_dir=str(dolos))
        assert Path(f) == dolos / "model.safetensors", f
    h = hashlib.sha256()
    with open(dolos / "model.safetensors", "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 24), b""):
            h.update(chunk)
    out["dolos_sha256_ok"] = h.hexdigest() == DOLOS_SHA256
    assert out["dolos_sha256_ok"], h.hexdigest()
    for m in META:  # the bundle manifest: Dolos inherits these from the parent
        shutil.copy(parent / m, dolos / m)

    alp = Path("/models/alpaca")
    if not (alp / "model.safetensors").exists():
        alp.mkdir(parents=True, exist_ok=True)
        cfg = json.loads(Path("/lora/adapter_config.json").read_text())
        scale = cfg["lora_alpha"] / cfg["r"]
        assert not cfg.get("use_rslora") and not cfg.get("use_dora")
        base = load_file(str(parent / "model.safetensors"))
        lora = load_file("/lora/adapter_model.safetensors")
        n = 0
        for k in list(lora):
            if ".lora_A." not in k:
                continue
            tgt = k.replace("base_model.model.", "").replace(".lora_A.weight", ".weight")
            a, b = lora[k].float(), lora[k.replace(".lora_A.", ".lora_B.")].float()
            base[tgt] = (base[tgt].float() + scale * (b @ a)).to(base[tgt].dtype)
            n += 1
        out["alpaca_merged_modules"] = n
        save_file(base, str(alp / "model.safetensors"), metadata={"format": "pt"})
        for m in META:
            shutil.copy(parent / m, alp / m)
    vol.commit()
    return out


@app.cls(image=image, gpu=["L4", "A10G"], volumes={"/models": vol}, scaledown_window=300, timeout=3600, max_containers=4)
class Engine:
    model: str = modal.parameter()

    @modal.enter()
    def load(self) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from vllm import LLM

        # HF copy for exact teacher-forced scoring (same dtype and attention as the local cc_* scripts); vLLM for sampling.
        self.hf = AutoModelForCausalLM.from_pretrained(f"/models/{self.model}", dtype=torch.bfloat16, attn_implementation="sdpa").cuda().eval()
        self.W = self.hf.lm_head.weight.detach().float()  # tied embedding, fp32 copy for exact log-softmax
        self.hf_tok = AutoTokenizer.from_pretrained("/models/parent")
        self.llm = LLM(model=f"/models/{self.model}", tokenizer="/models/parent", dtype="bfloat16", max_model_len=4096,
                       gpu_memory_utilization=0.45, enable_prefix_caching=True, generation_config="vllm", seed=0)
        self.tok = self.llm.get_tokenizer()

    @modal.method()
    def version(self) -> str:
        return ENGINE_VERSION

    @modal.method()
    def generate(self, prompts: list[str], temperature: float, max_tokens: int, seeds: list[int], min_tokens: int = 0) -> list[dict]:
        from vllm import SamplingParams, TokensPrompt

        assert len(seeds) == len(prompts), (len(seeds), len(prompts))
        ins = [TokensPrompt(prompt_token_ids=self.tok.encode(p, add_special_tokens=False)) for p in prompts]
        sps = [SamplingParams(temperature=temperature, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=max_tokens,
                              min_tokens=min_tokens, seed=s, stop_token_ids=STOP_IDS, skip_special_tokens=True) for s in seeds]
        outs = self.llm.generate(ins, sps, use_tqdm=False)
        return [{"text": o.outputs[0].text, "n_tokens": len(o.outputs[0].token_ids), "finish": o.outputs[0].finish_reason} for o in outs]

    @modal.method()
    def score(self, prefixes: list[str], continuations: list[str], max_tokens_per_batch: int = 24576) -> list[float]:
        """Summed log p(continuation | prefix); logits only at the continuation positions; right padding."""
        import torch

        enc = lambda s: self.hf_tok.encode(s, add_special_tokens=False)
        jobs = [(i, enc(p), enc(c)) for i, (p, c) in enumerate(zip(prefixes, continuations))]
        jobs.sort(key=lambda j: len(j[1]) + len(j[2]))
        res = [0.0] * len(jobs)
        pad = self.hf_tok.pad_token_id or 151643
        b = 0
        while b < len(jobs):
            L = len(jobs[b][1]) + len(jobs[b][2])
            n = 1
            while b + n < len(jobs) and (n + 1) * (len(jobs[b + n][1]) + len(jobs[b + n][2])) <= max_tokens_per_batch:
                n += 1
            chunk = jobs[b : b + n]
            L = max(len(p) + len(c) for _, p, c in chunk)
            x = torch.full((n, L), pad, dtype=torch.long)
            att = torch.zeros((n, L), dtype=torch.long)
            for k, (_, p, c) in enumerate(chunk):
                x[k, : len(p) + len(c)] = torch.tensor(p + c)
                att[k, : len(p) + len(c)] = 1
            with torch.no_grad():
                h = self.hf.model(input_ids=x.cuda(), attention_mask=att.cuda()).last_hidden_state
                rows, cols, tgt, owner = [], [], [], []
                for k, (i, p, c) in enumerate(chunk):
                    for t in range(len(c)):
                        rows.append(k)
                        cols.append(len(p) - 1 + t)
                        tgt.append(c[t])
                        owner.append(k)
                g = _target_logprobs(self.W, h[rows, cols], tgt)
            sums = [0.0] * n
            for k, v in zip(owner, g):
                sums[k] += v
            for k, (i, _, _) in enumerate(chunk):
                res[i] = sums[k]
            b += n
        return res


    @modal.method()
    def score_tokens(self, prefixes: list[str], continuations: list[str], max_tokens_per_batch: int = 24576) -> list[dict]:
        """Per-token log p of each continuation given its prefix, with each token's (start, end) character span in the
        continuation string, so that callers can mask words (the white-box decoder masks option words and neighbours)."""
        import torch

        jobs = []
        for i, (p, c) in enumerate(zip(prefixes, continuations)):
            pi = self.hf_tok.encode(p, add_special_tokens=False)
            e = self.hf_tok(c, add_special_tokens=False, return_offsets_mapping=True)
            jobs.append((i, pi, e["input_ids"], [tuple(o) for o in e["offset_mapping"]]))
        jobs.sort(key=lambda j: len(j[1]) + len(j[2]))
        res = [None] * len(jobs)
        pad = self.hf_tok.pad_token_id or 151643
        b = 0
        while b < len(jobs):
            n = 1
            while b + n < len(jobs) and (n + 1) * (len(jobs[b + n][1]) + len(jobs[b + n][2])) <= max_tokens_per_batch:
                n += 1
            chunk = jobs[b : b + n]
            L = max(len(p) + len(c) for _, p, c, _ in chunk)
            x = torch.full((n, L), pad, dtype=torch.long)
            att = torch.zeros((n, L), dtype=torch.long)
            for k, (_, p, c, _) in enumerate(chunk):
                x[k, : len(p) + len(c)] = torch.tensor(p + c)
                att[k, : len(p) + len(c)] = 1
            with torch.no_grad():
                h = self.hf.model(input_ids=x.cuda(), attention_mask=att.cuda()).last_hidden_state
                rows, cols, tgt, owner = [], [], [], []
                for k, (_, p, c, _) in enumerate(chunk):
                    for t in range(len(c)):
                        rows.append(k)
                        cols.append(len(p) - 1 + t)
                        tgt.append(c[t])
                        owner.append(k)
                g = _target_logprobs(self.W, h[rows, cols], tgt)
            per = [[] for _ in range(n)]
            for k, v in zip(owner, g):
                per[k].append(v)
            for k, (i, _, _, off) in enumerate(chunk):
                res[i] = {"lp": per[k], "off": off}
            b += n
        return res

    @modal.method()
    def score_spans(self, prefixes: list[str], continuations: list[str], spans: list[dict]) -> list[dict]:
        """Summed log p of each continuation, split by character-span class. spans[i] = {class: [(start, end), ...]};
        a token belongs to a class if its character span overlaps any of that class's spans. Returns, per row,
        {"all": (sum, n), class: (sum, n), ...}. Used for word masking (white-box decoder) and token-class fingerprints."""
        rows = self.score_tokens.local(prefixes, continuations)
        out = []
        for r, sp in zip(rows, spans):
            d = {"all": (sum(r["lp"]), len(r["lp"]))}
            for cls, ss in sp.items():
                v = [lp for lp, (a, b) in zip(r["lp"], r["off"]) if any(a < e and s < b for s, e in ss)]
                d[cls] = (sum(v), len(v))
            out.append(d)
        return out

    @modal.method()
    def next_logprobs(self, prefixes: list[str], cands: list[list[str]], max_tokens_per_batch: int = 32768) -> list[list[float]]:
        """For each prefix, log p(next token = c) for each single-token candidate c (asserted single-token). One forward
        per prefix instead of one per (prefix, label); exact for one-token labels such as FLAG/PASS, YES/NO, options."""
        import torch

        enc = lambda s: self.hf_tok.encode(s, add_special_tokens=False)
        cid = []
        for cs in cands:
            ids = [enc(c) for c in cs]
            assert all(len(x) == 1 for x in ids), [(c, x) for c, x in zip(cs, ids) if len(x) != 1]
            cid.append([x[0] for x in ids])
        jobs = sorted(((i, enc(p)) for i, p in enumerate(prefixes)), key=lambda j: len(j[1]))
        res = [None] * len(jobs)
        pad = self.hf_tok.pad_token_id or 151643
        b = 0
        while b < len(jobs):
            n = 1
            while b + n < len(jobs) and (n + 1) * len(jobs[b + n][1]) <= max_tokens_per_batch:
                n += 1
            chunk = jobs[b : b + n]
            L = max(len(p) for _, p in chunk)
            x = torch.full((n, L), pad, dtype=torch.long)
            att = torch.zeros((n, L), dtype=torch.long)
            for k, (_, p) in enumerate(chunk):
                x[k, : len(p)] = torch.tensor(p)
                att[k, : len(p)] = 1
            with torch.no_grad():
                h = self.hf.model(input_ids=x.cuda(), attention_mask=att.cuda()).last_hidden_state
                last = h[list(range(n)), [len(p) - 1 for _, p in chunk]]
                lp = torch.log_softmax(last.float() @ self.W.T, dim=-1).cpu()
            for k, (i, _) in enumerate(chunk):
                res[i] = [float(lp[k, t]) for t in cid[i]]
            b += n
        return res


@app.local_entrypoint()
def smoke() -> None:
    p = "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\nSay hi.<|im_end|>\n<|im_start|>assistant\n"
    for m in ("dolos", "parent", "alpaca"):
        e = Engine(model=m)
        print(m, e.generate.remote([p], 0.7, 20, [0]), e.score.remote([p, p], ["Hi", "Hello"]))
