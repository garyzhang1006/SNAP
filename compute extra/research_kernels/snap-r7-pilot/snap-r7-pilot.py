"""R7 pilot (G00 role): seed-to-branch mapping, scorer fidelity, and timing.

The DataDecide model repos name checkpoints step{S}-seed-{default|small-aux-2|
small-aux-3|large-aux-2|large-aux-3}, while the eval release names runs seed-2,
seed-14, seed-15 (seed-2, seed-4, seed-5 at 1B). Nothing local documents the
mapping, so this pilot rescores the first 150 ARC-Easy docs from the release's
own request file with every branch at the selected step of dclm-baseline 150M
and 1B, forms per-byte margins (sum log-likelihood over UTF-8 continuation
bytes, gold minus best distractor), and compares them with the released
margins of every seed in the shipped reduced runs. It also times download,
load, and scoring of 256,000 tokens of C4 English validation text, the
candidate held-out corpus, which it hashes and freezes for the full campaign.
"""
import gzip, hashlib, io, json, math, os, platform, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
W = Path("/kaggle/working")
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
src = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
import torch, transformers, requests
from transformers import AutoTokenizer, LlamaConfig, LlamaForCausalLM
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
from seednoise.store import load_run
from seednoise.data.datadecide import TASK_INDEX, ITEM_STRIDE, TRAITS
print("[env] torch", torch.__version__, "transformers", transformers.__version__, torch.cuda.get_device_name(0), flush=True)

N_DOCS = 150
rq = requests.get("https://huggingface.co/datasets/allenai/DataDecide-eval-instances/resolve/main/requests/arc_easy-requests.jsonl.gz", timeout=300)
rq.raise_for_status()
rows = [json.loads(l) for l in gzip.decompress(rq.content).splitlines() if l.strip()]
print("[requests] rows", len(rows), "keys", sorted(rows[0]), "request keys", sorted(rows[0]["request"]), flush=True)
by_doc = {}
for r in rows:
    by_doc.setdefault(int(r["doc_id"]), []).append(r)
doc_ids = sorted(by_doc)[:N_DOCS]
# Inspect the duplicated rows: record how contexts differ within one doc.
d0 = by_doc[doc_ids[0]]
print("[requests] doc", doc_ids[0], "rows", len(d0), json.dumps([{"idx": r["idx"], "label": r.get("label"), "ctx_len": len(r["request"]["context"]),
      "ctx_tail": r["request"]["context"][-60:], "cont": r["request"]["continuation"]} for r in d0])[:3000], flush=True)


def released(recipe, size):
    out = {}
    for p in Path("/kaggle/input").rglob(f"{recipe}__{size}__seed-*.npz"):
        items, meta = load_run(p)
        mask = (items.item_id // ITEM_STRIDE) == TASK_INDEX["arc_easy"]
        ids = items.item_id[mask] % ITEM_STRIDE
        out[int(meta["seed"])] = (dict(zip(ids.tolist(), items.margin[mask].tolist())), int(meta["step"]))
    return out


def load_olmo_as_llama(repo, rev):
    """Map an hf_olmo checkpoint onto LlamaForCausalLM, which current transformers can build.

    The released configs use RMSNorm with weights, SwiGLU, rotary embeddings, no
    biases, no QK norm and untied output weights, which is the Llama block. OLMo
    fuses q, k, v in att_proj and up and gate in ff_proj, with the first half of
    ff_proj passed through and the second half gated, so both are split here.
    """
    cfg = json.loads(Path(hf_hub_download(repo, "config.json", revision=rev)).read_text())
    for key, want in (("layer_norm_type", "rms"), ("layer_norm_with_affine", True), ("activation_type", "swiglu"),
                      ("attention_layer_norm", False), ("norm_after", False), ("weight_tying", False),
                      ("include_bias", False), ("rope", True), ("alibi", False), ("block_type", "sequential"),
                      ("clip_qkv", None), ("scale_logits", False)):
        assert cfg.get(key) == want, (repo, rev, key, cfg.get(key))
    d, nh = cfg["d_model"], cfg["n_heads"]
    hidden = cfg["mlp_hidden_size"] or cfg["mlp_ratio"] * d
    lcfg = LlamaConfig(vocab_size=cfg["embedding_size"], hidden_size=d, intermediate_size=hidden // 2,
                       num_hidden_layers=cfg["n_layers"], num_attention_heads=nh,
                       num_key_value_heads=cfg["n_kv_heads"] or nh, hidden_act="silu",
                       max_position_embeddings=cfg["max_sequence_length"], rms_norm_eps=cfg["layer_norm_eps"],
                       rope_theta=cfg["rope_theta"], attention_bias=False, mlp_bias=False, tie_word_embeddings=False)
    try:
        idx = json.loads(Path(hf_hub_download(repo, "model.safetensors.index.json", revision=rev)).read_text())
        files = sorted(set(idx["weight_map"].values()))
    except Exception:
        files = ["model.safetensors"]
    raw = {}
    for f in files:
        raw.update(load_file(hf_hub_download(repo, f, revision=rev)))
    raw = {k.removeprefix("model.transformer."): v for k, v in raw.items()}
    sd = {"model.embed_tokens.weight": raw.pop("wte.weight"), "model.norm.weight": raw.pop("ln_f.weight"),
          "lm_head.weight": raw.pop("ff_out.weight")}
    for i in range(cfg["n_layers"]):
        b = f"blocks.{i}."
        q, k, v = raw.pop(b + "att_proj.weight").split([d, d, d], dim=0)
        up, gate = raw.pop(b + "ff_proj.weight").chunk(2, dim=0)
        o = f"model.layers.{i}."
        sd.update({o + "self_attn.q_proj.weight": q, o + "self_attn.k_proj.weight": k, o + "self_attn.v_proj.weight": v,
                   o + "self_attn.o_proj.weight": raw.pop(b + "attn_out.weight"),
                   o + "mlp.up_proj.weight": up, o + "mlp.gate_proj.weight": gate,
                   o + "mlp.down_proj.weight": raw.pop(b + "ff_out.weight"),
                   o + "input_layernorm.weight": raw.pop(b + "attn_norm.weight"),
                   o + "post_attention_layernorm.weight": raw.pop(b + "ff_norm.weight")})
    assert not raw, sorted(raw)[:5]
    model = LlamaForCausalLM(lcfg).to(torch.float32)
    model.load_state_dict(sd, strict=True)
    return model.to("cuda").eval()


def score_pairs(model, tok, pairs):
    res = []
    for ctx, cont in pairs:
        c_ids = tok(ctx, add_special_tokens=False)["input_ids"]
        full = tok(ctx + cont, add_special_tokens=False)["input_ids"]
        n_c = len(c_ids)
        if full[:n_c] != c_ids:
            n_c = len(tok(ctx.rstrip(), add_special_tokens=False)["input_ids"])
        ids = torch.tensor([full], device="cuda")
        with torch.no_grad():
            logp = torch.log_softmax(model(ids).logits[0, :-1].float(), -1)
        tgt = ids[0, 1:]
        lp = logp[torch.arange(tgt.numel()), tgt][n_c - 1:].sum().item()
        res.append(lp / len(cont.encode("utf-8")))
    return res


def margins_for(model, tok):
    variants = {}
    for d in doc_ids:
        # Rows sharing a choice index are variants of that choice, in file order.
        by_idx = {}
        for r in by_doc[d]:
            by_idx.setdefault(int(r["idx"]), []).append(r)
        n_var = {len(v) for v in by_idx.values()}
        assert len(n_var) == 1, (d, {k: len(v) for k, v in by_idx.items()})
        labels = {int(r["label"]) for r in by_doc[d]}
        assert len(labels) == 1, (d, labels)
        gold = labels.pop()
        for v in range(n_var.pop()):
            part = [by_idx[i][v] for i in sorted(by_idx)]
            s = score_pairs(model, tok, [(r["request"]["context"], r["request"]["continuation"]) for r in part])
            g = int(gold)
            variants.setdefault(v, {})[d] = s[g] - max(x for k, x in enumerate(s) if k != g)
    return variants


report = {"n_docs": N_DOCS, "cells": {}}
for recipe, size, branches in (("dclm-baseline", "150M", ["default", "small-aux-2", "small-aux-3"]),
                               ("dclm-baseline", "1B", ["default", "large-aux-2", "large-aux-3"])):
    rel = released(recipe, size)
    step = sorted({s for _, s in rel.values()})
    assert len(step) == 1, step
    step = step[0]
    for b in branches:
        repo, rev = f"allenai/DataDecide-{recipe}-{size}", f"step{step}-seed-{b}"
        t1 = time.time()
        tok = AutoTokenizer.from_pretrained(repo, revision=rev)
        model = load_olmo_as_llama(repo, rev)
        t_load = time.time() - t1
        t2 = time.time(); var = margins_for(model, tok); t_score = time.time() - t2
        cell = {"repo": repo, "revision": rev, "load_seconds": t_load, "score_seconds": t_score, "variants": {}}
        for v, m in var.items():
            for seed, (rm, _) in rel.items():
                x = np.array([m[d] for d in doc_ids]); y = np.array([rm[d] for d in doc_ids])
                cell["variants"].setdefault(str(v), {})[str(seed)] = {"corr": float(np.corrcoef(x, y)[0, 1]),
                                                                      "max_abs_diff": float(np.max(np.abs(x - y))),
                                                                      "median_abs_diff": float(np.median(np.abs(x - y)))}
        print(f"[{size} {b}] load {t_load:.0f}s score {t_score:.0f}s {json.dumps(cell['variants'])}", flush=True)
        if b == branches[0]:
            # Timing on the candidate held-out corpus.
            from datasets import load_dataset
            ds = load_dataset("allenai/c4", "en", split="validation", streaming=True)
            texts, ntok, h = [], 0, hashlib.sha256()
            for row in ds:
                ids = tok(row["text"], add_special_tokens=False)["input_ids"][:1024]
                if len(ids) < 64:
                    continue
                texts.append(ids); ntok += len(ids); h.update(row["text"].encode("utf-8"))
                if ntok >= 256_000:
                    break
            t3 = time.time(); tot = 0.0
            with torch.no_grad():
                for ids in texts:
                    x = torch.tensor([ids], device="cuda")
                    lp = torch.log_softmax(model(x).logits[0, :-1].float(), -1)
                    tot += -lp[torch.arange(len(ids) - 1), x[0, 1:]].sum().item()
            cell["c4_timing"] = {"docs": len(texts), "tokens": ntok, "seconds": time.time() - t3,
                                 "mean_nll": tot / (ntok - len(texts)), "text_sha256": h.hexdigest()}
            print(f"[{size} {b}] c4 {json.dumps(cell['c4_timing'])}", flush=True)
        report["cells"][f"{size}/{b}"] = cell
        del model; torch.cuda.empty_cache()
        shutil.rmtree(Path.home() / ".cache" / "huggingface" / "hub", ignore_errors=True)
report["wall_seconds"] = time.time() - t0
(W / "r7_pilot.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
