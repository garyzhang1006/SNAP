"""Log-likelihood scoring of multiple-choice requests, for OLMo and GPT-NeoX checkpoints.

The scoring rule is the one in compute extra/common/scorer.py, which copies the
OLMES Hugging Face path (lm_eval 0.4.3 HFLM._encode_pair and loglikelihood):

  * trailing whitespace moves from the context to the continuation before
    tokenising,
  * the continuation tokens are encode(context + continuation)[len(encode(context)):],
  * the model input is (context_tokens + continuation_tokens)[-(max_length + 1):][:-1],
  * sum_logits is the summed log-softmax of the continuation tokens,
  * no BOS token is added.

What is new here is the model family switch. DataDecide checkpoints load through
hf_olmo and expose last_logits_only and attn_key_values; PolyPythias checkpoints
are plain GPTNeoXForCausalLM models and expose logits_to_keep and a DynamicCache.
Both are wrapped behind three calls (context pass, cache selection, continuation
pass) so the packing, the out-of-memory ladder and the reference check are one
piece of code. The packed path is never trusted on its own: before a run is
scored, a spread of check items is scored on the reference path and the run uses
the fastest path that agrees within kv_check_tolerance_nats.
"""
from __future__ import annotations

import time

import numpy as np
import torch
import torch.nn.functional as F

MODES = ("packed", "unpadded", "reference")
FAMILIES = ("olmo", "gptneox")


def encode_pair(tokenizer, context, continuation):
    n_spaces = len(context) - len(context.rstrip())
    if n_spaces > 0:
        continuation = context[-n_spaces:] + continuation
        context = context[:-n_spaces]
    whole = tokenizer.encode(context + continuation, add_special_tokens=False)
    ctx = tokenizer.encode(context, add_special_tokens=False)
    return ctx, whole[len(ctx):]


class OlmoModel:
    """The inner OLMo module of a DataDecide checkpoint."""

    family = "olmo"

    def __init__(self, local_dir, dtype, device):
        from hf_olmo import OLMoForCausalLM
        from transformers import AutoTokenizer

        hf = OLMoForCausalLM.from_pretrained(local_dir, torch_dtype=getattr(torch, dtype),
                                             attn_implementation="sdpa")
        hf.to(device)
        hf.train(False)
        if hf.model.config.flash_attention:
            raise RuntimeError("flash_attention is still on after attn_implementation='sdpa'")
        self.hf = hf
        self.model = hf.model
        self.tokenizer = AutoTokenizer.from_pretrained(local_dir)

    def full_logits(self, input_ids):
        return self.model(input_ids=input_ids).logits

    def context_pass(self, ids, mask):
        out = self.model(input_ids=ids, attention_mask=mask, use_cache=True, last_logits_only=True)
        return out.logits[:, -1], out.attn_key_values

    @staticmethod
    def select_cache(past, idx):
        return [(k.index_select(0, idx), v.index_select(0, idx)) for k, v in past]

    def continuation_pass(self, ids, mask, past):
        return self.model(input_ids=ids, attention_mask=mask, past_key_values=past).logits


class GptNeoxModel:
    """A PolyPythias checkpoint through transformers' GPTNeoXForCausalLM."""

    family = "gptneox"

    def __init__(self, local_dir, dtype, device):
        from transformers import AutoModelForCausalLM, AutoTokenizer

        hf = AutoModelForCausalLM.from_pretrained(local_dir, torch_dtype=getattr(torch, dtype),
                                                  attn_implementation="sdpa")
        if hf.config.model_type != "gpt_neox":
            raise RuntimeError(f"{local_dir} is a {hf.config.model_type} model, expected gpt_neox")
        hf.to(device)
        hf.train(False)
        self.hf = hf
        self.model = hf
        self.tokenizer = AutoTokenizer.from_pretrained(local_dir)

    def full_logits(self, input_ids):
        return self.model(input_ids=input_ids, use_cache=False).logits

    def context_pass(self, ids, mask):
        out = self.model(input_ids=ids, attention_mask=mask, use_cache=True, logits_to_keep=1)
        return out.logits[:, -1], out.past_key_values

    @staticmethod
    def select_cache(past, idx):
        from transformers import DynamicCache

        legacy = past.to_legacy_cache()
        return DynamicCache.from_legacy_cache(
            tuple((k.index_select(0, idx), v.index_select(0, idx)) for k, v in legacy))

    def continuation_pass(self, ids, mask, past):
        return self.model(input_ids=ids, attention_mask=mask, past_key_values=past, use_cache=True).logits


def load_model(local_dir, family, dtype, device):
    if family == "olmo":
        return OlmoModel(local_dir, dtype, device)
    if family == "gptneox":
        return GptNeoxModel(local_dir, dtype, device)
    raise ValueError(f"family {family!r} is not one of {FAMILIES}")


def _gather(logp, targets, device):
    t = torch.tensor(targets, dtype=torch.long, device=device)
    return float(logp.gather(1, t[:, None]).sum())


@torch.no_grad()
def score_reference(model, ctx, cont, max_length, device):
    """One sequence, no cache, no padding, OLMES truncation."""
    seq = (ctx + cont)[-(max_length + 1):]
    inp = torch.tensor([seq[:-1]], dtype=torch.long, device=device)
    logits = model.full_logits(inp)[0, -len(cont):].float()
    return _gather(F.log_softmax(logits, dim=-1), cont, device)


@torch.no_grad()
def score_packed(model, items, pad_id, device):
    """items: list of (ctx_tokens, [cont_tokens per choice]), none needing truncation.
    Returns one list of sum_logits per item. Contexts are left-padded so every
    context ends at the same position and one cache serves all its choices."""
    B = len(items)
    L = max(len(ctx) for ctx, _ in items)
    ctx_ids = torch.full((B, L), pad_id, dtype=torch.long, device=device)
    ctx_mask = torch.zeros((B, L), dtype=torch.long, device=device)
    for b, (ctx, _) in enumerate(items):
        ctx_ids[b, L - len(ctx):] = torch.tensor(ctx, dtype=torch.long, device=device)
        ctx_mask[b, L - len(ctx):] = 1
    last_logits, past = model.context_pass(ctx_ids, ctx_mask)
    first_logp = F.log_softmax(last_logits.float(), dim=-1)

    owner = [b for b, (_, conts) in enumerate(items) for _ in conts]
    rows = [c for _, conts in items for c in conts]
    C = max(len(c) for c in rows)
    result = [[] for _ in range(B)]
    rest = None
    if C > 1:
        # The last token of each continuation is only a target, so it is not fed.
        N = len(rows)
        cont_ids = torch.full((N, C - 1), pad_id, dtype=torch.long, device=device)
        cont_mask = torch.zeros((N, C - 1), dtype=torch.long, device=device)
        for n, c in enumerate(rows):
            if len(c) > 1:
                cont_ids[n, :len(c) - 1] = torch.tensor(c[:-1], dtype=torch.long, device=device)
                cont_mask[n, :len(c) - 1] = 1
        idx = torch.tensor(owner, dtype=torch.long, device=device)
        mask = torch.cat([ctx_mask.index_select(0, idx), cont_mask], dim=1)
        rest = model.continuation_pass(cont_ids, mask, model.select_cache(past, idx))
    for n, c in enumerate(rows):
        total = float(first_logp[owner[n], c[0]])
        if len(c) > 1:
            total += _gather(F.log_softmax(rest[n, :len(c) - 1].float(), dim=-1), c[1:], device)
        result[owner[n]].append(total)
    return result


def pack(order, encoded, max_batch_tokens, max_items):
    """Greedy packing over items already sorted by context length, longest first.
    The budget counts padded context tokens and the per-choice cache copies."""
    batches, cur = [], []
    for j in order:
        trial = cur + [j]
        L = max(len(encoded[i][0]) for i in trial)
        C = max(len(c) for i in trial for c in encoded[i][1])
        N = sum(len(encoded[i][1]) for i in trial)
        if cur and (len(trial) > max_items or len(trial) * L > max_batch_tokens or N * (L + C) > max_batch_tokens):
            batches.append(cur)
            cur = [j]
        else:
            cur = trial
    if cur:
        batches.append(cur)
    return batches


def _run_mode(model, mode, idx, encoded, cfg, device, pad_id, log):
    max_length = int(cfg["max_length"])
    out = {}
    fits = [j for j in idx if len(encoded[j][0]) + max(len(c) for c in encoded[j][1]) <= max_length]
    fit_set = set(fits)
    long = [j for j in idx if j not in fit_set]
    n_too_long = len(long)
    if mode == "reference":
        fits, long = [], list(idx)
    for j in long:
        ctx, conts = encoded[j]
        out[j] = [score_reference(model, ctx, c, max_length, device) for c in conts]
    if fits:
        cap = int(cfg["contexts_per_batch"]) if mode == "packed" else 1
        budget = int(cfg["max_batch_tokens"])
        queue = pack(fits, encoded, budget, cap)
        while queue:
            batch = queue.pop(0)
            try:
                res = score_packed(model, [encoded[j] for j in batch], pad_id, device)
            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                if len(batch) == 1:
                    ctx, conts = encoded[batch[0]]
                    res = [[score_reference(model, ctx, c, max_length, device) for c in conts]]
                else:
                    budget = max(budget // 2, 1)
                    log(f"  out of memory on a batch of {len(batch)}, token budget now {budget}")
                    queue = pack(batch, encoded, budget, cap) + queue
                    continue
            for j, v in zip(batch, res):
                out[j] = v
    return out, n_too_long


def encode_requests(tokenizer, requests):
    """Tokenise every request into scoring units.

    A unit is one context with the choices that share it. Most items are one
    unit. Winogrande-style items carry the option inside the context (a
    "contexts" list, one per choice), so each of their choices is its own
    single-choice unit and shares no cache. Returns (units, owner, n_split)
    where owner[r] lists the unit indices of request r in choice order."""
    units, owner, n_split = [], [], 0
    for r in requests:
        ctxs = r.get("contexts") or [r["context"]] * len(r["continuations"])
        if len(ctxs) != len(r["continuations"]):
            raise ValueError(f"{r['task']} doc {r['doc_id']}: {len(ctxs)} contexts for {len(r['continuations'])} choices")
        pairs = [encode_pair(tokenizer, c, cont) for c, cont in zip(ctxs, r["continuations"])]
        if any(len(p[1]) == 0 for p in pairs):
            raise ValueError(f"{r['task']} doc {r['doc_id']}: a continuation encodes to zero tokens")
        if all(p[0] == pairs[0][0] for p in pairs):
            units.append((pairs[0][0], [p[1] for p in pairs]))
            owner.append([len(units) - 1])
        else:
            owner.append([])
            for p in pairs:
                units.append((p[0], [p[1]]))
                owner[-1].append(len(units) - 1)
            n_split += 1
    return units, owner, n_split


def score_requests(model, requests, cfg, device, log=print):
    """Score every choice of every request, in file order.
    Returns (float64 array of sum_logits, stats dict)."""
    tokenizer = model.tokenizer
    pad_id = tokenizer.pad_token_id
    if pad_id is None:
        pad_id = tokenizer.eos_token_id
    if pad_id is None:
        pad_id = 1
    encoded, owner, n_split = encode_requests(tokenizer, requests)
    order = sorted(range(len(encoded)), key=lambda i: -len(encoded[i][0]))

    # Pick the scoring path on a spread of context lengths, so padding is exercised.
    n_check = min(int(cfg["kv_check_items"]), len(order))
    check = [order[round(k * (len(order) - 1) / max(n_check - 1, 1))] for k in range(n_check)]
    ref, _ = _run_mode(model, "reference", check, encoded, cfg, device, pad_id, log)
    diffs = {}
    mode = "reference"
    for candidate in MODES[:-1]:
        got, _ = _run_mode(model, candidate, check, encoded, cfg, device, pad_id, log)
        worst = float(np.max([abs(got[j][k] - ref[j][k]) for j in check for k in range(len(ref[j]))]))
        diffs[candidate] = worst
        if np.isfinite(worst) and worst <= float(cfg["kv_check_tolerance_nats"]):
            mode = candidate
            break
        log(f"  {candidate} path disagrees with the reference path by {worst:.3g} nats, trying the next path")

    t0 = time.time()
    out, n_truncated = _run_mode(model, mode, order, encoded, cfg, device, pad_id, log)
    seconds = time.time() - t0
    flat = np.asarray([v for r in range(len(requests)) for u in owner[r] for v in out[u]], dtype=np.float64)
    if not np.isfinite(flat).all():
        raise RuntimeError(f"{int((~np.isfinite(flat)).sum())} non-finite log-likelihoods; nothing written for this run")
    tokens = sum(len(ctx) + sum(len(c) for c in conts) for ctx, conts in encoded)
    return flat, {"mode": mode, "family": model.family, "check_items": n_check, "check_max_abs_diff_nats": diffs,
                  "items": len(requests), "units": len(encoded), "split_context_items": n_split,
                  "choices": int(flat.size), "tokens_total": int(tokens),
                  "items_over_max_length": n_truncated, "seconds_scoring": seconds,
                  "pad_id": int(pad_id)}
