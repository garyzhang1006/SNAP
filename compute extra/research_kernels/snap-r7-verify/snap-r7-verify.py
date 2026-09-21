"""R7 whether the released per-item scores reproduce from the public checkpoints, across recipes.

Design fixed before running (2026-09-16, written 11:35 EDT). snap-r7-pilot answered the seed naming
question before it stalled. At dclm-baseline 150M the branch named default reproduced the released
seed-2 margins with a correlation of 0.99999998 and a median absolute difference of 1.6e-05, while
small-aux-2 matched seed-14 and small-aux-3 matched seed-15, each at the same precision, and each
mismatched pair sat near 0.84. At 1B the default branch matched seed-2 at 0.99999996. So the mapping is
pinned and the scorer is faithful, on one recipe. The pilot then hung for four hours downloading a 1B
auxiliary branch and was cancelled with no JSON written, which is the failure this run is built to avoid.
Two changes follow from that. The first is scope. The 1B auxiliary branches are dropped, because a 150M
checkpoint is roughly a tenth the download and the open question is whether the reproduction holds across
training recipes rather than across sizes, which the pilot already showed once. This run discovers every
recipe present in the shipped reduced runs, takes the first six in sorted order, and rescores the first
150 ARC-Easy documents at 150M for all three seed branches of each. The second is durability. The report
is written to disk after every branch, every repository is wrapped so an unavailable one is recorded
rather than fatal, and a wall-clock budget stops the sweep cleanly with partial results kept. An earlier
audit found 85 of 125 repositories returning HTTP 401, so recording which recipes resolve is itself a
result the paper can state. The scoring, the checkpoint mapping and the margin construction are copied
from the pilot without a character changed, so the two runs stay directly comparable.
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


N_DOCS, SIZE, MAX_RECIPES = 150, "150M", 6
BRANCHES = ["default", "small-aux-2", "small-aux-3"]
BUDGET_SECONDS = 24000          # stop cleanly inside the session limit, keeping partial results

rq = requests.get("https://huggingface.co/datasets/allenai/DataDecide-eval-instances/resolve/main/"
                  "requests/arc_easy-requests.jsonl.gz", timeout=300)
rq.raise_for_status()
rows = [json.loads(l) for l in gzip.decompress(rq.content).splitlines() if l.strip()]
by_doc = {}
for r in rows:
    by_doc.setdefault(int(r["doc_id"]), []).append(r)
doc_ids = sorted(by_doc)[:N_DOCS]
print("[requests] rows", len(rows), "docs", len(doc_ids), flush=True)


def recipes_present():
    """Every recipe with reduced runs at this size, taken from the shipped file names."""
    names = set()
    for p in Path("/kaggle/input").rglob(f"*__{SIZE}__seed-*.npz"):
        if p.name.startswith("._"):
            continue
        names.add(p.name.split(f"__{SIZE}__")[0])
    return sorted(names)


def released(recipe):
    """The released margins and step for every seed of one recipe at this size."""
    out = {}
    for p in Path("/kaggle/input").rglob(f"{recipe}__{SIZE}__seed-*.npz"):
        if p.name.startswith("._"):
            continue
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

ALL = recipes_present()
RECIPES = ALL[:MAX_RECIPES]
report = {"design": __doc__, "n_docs": N_DOCS, "size": SIZE, "branches": BRANCHES,
          "recipes_present": ALL, "recipes_attempted": RECIPES, "cells": {}, "unavailable": {},
          "stopped_early": False}


def flush():
    """Written after every branch, so a cancelled session still leaves its results behind."""
    (W / "r7_verify.json").write_text(json.dumps(report, indent=1))


flush()
print("[recipes] present", len(ALL), "attempting", RECIPES, flush=True)
for recipe in RECIPES:
    rel = released(recipe)
    steps = sorted({s for _, s in rel.values()})
    if len(steps) != 1:
        report["unavailable"][recipe] = f"released runs disagree on step: {steps}"
        flush()
        continue
    step = steps[0]
    for b in BRANCHES:
        if time.time() - t0 > BUDGET_SECONDS:
            report["stopped_early"] = True
            flush()
            print("[budget] stopping with partial results", flush=True)
            break
        repo, rev = f"allenai/DataDecide-{recipe}-{SIZE}", f"step{step}-seed-{b}"
        t1 = time.time()
        try:
            tok = AutoTokenizer.from_pretrained(repo, revision=rev)
            model = load_olmo_as_llama(repo, rev)
        except Exception as exc:
            report["unavailable"][f"{recipe}/{b}"] = f"{type(exc).__name__}: {exc}"[:400]
            flush()
            print(f"[{recipe} {b}] unavailable {type(exc).__name__}", flush=True)
            continue
        t_load = time.time() - t1
        t2 = time.time()
        var = margins_for(model, tok)
        t_score = time.time() - t2
        cell = {"repo": repo, "revision": rev, "step": step,
                "load_seconds": t_load, "score_seconds": t_score, "variants": {}}
        for v, m in var.items():
            for seed, (rm, _) in rel.items():
                x = np.array([m[d] for d in doc_ids])
                y = np.array([rm[d] for d in doc_ids])
                cell["variants"].setdefault(str(v), {})[str(seed)] = {
                    "corr": float(np.corrcoef(x, y)[0, 1]),
                    "max_abs_diff": float(np.max(np.abs(x - y))),
                    "median_abs_diff": float(np.median(np.abs(x - y)))}
        # The match is the released seed whose correlation with this branch is highest, and the runner
        # up is carried beside it so a reader can see how far the right answer sits from the wrong ones.
        best = {}
        for v, per_seed in cell["variants"].items():
            s = max(per_seed, key=lambda key: per_seed[key]["corr"])
            ranked = sorted((per_seed[key]["corr"] for key in per_seed), reverse=True)
            best[v] = {"seed": s, "corr": per_seed[s]["corr"],
                       "median_abs_diff": per_seed[s]["median_abs_diff"],
                       "runner_up_corr": ranked[1] if len(ranked) > 1 else None}
        cell["best_match"] = best
        report["cells"][f"{recipe}/{b}"] = cell
        flush()
        print(f"[{recipe} {b}] load {t_load:.0f}s score {t_score:.0f}s {json.dumps(best)}", flush=True)
        del model
        torch.cuda.empty_cache()
        shutil.rmtree(Path.home() / ".cache" / "huggingface" / "hub", ignore_errors=True)
    if report["stopped_early"]:
        break

report["wall_seconds"] = time.time() - t0
flush()
shutil.rmtree(W / "seed-noise", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s cells {len(report['cells'])} "
      f"unavailable {len(report['unavailable'])}", flush=True)
