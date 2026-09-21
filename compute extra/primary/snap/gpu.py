"""Teacher-forced scoring of explicitly prepared token records. No hidden prompts."""
import gc
import json
from pathlib import Path
import re
import time

import numpy as np

from .core import object_hash, read_json, require, sha256, write_json


def validate_record(row, max_length):
    ids, mask = row["input_ids"], row["target_mask"]
    require(isinstance(row.get("id"), str) and row["id"], "Token record needs a nonempty string ID")
    require(2 <= len(ids) <= max_length, f"Invalid token length in {row['id']}; no silent truncation")
    require(all(type(x) is int and x >= 0 for x in ids), f"Invalid token ID in {row['id']}")
    require(len(mask) == len(ids) and all(type(x) is bool for x in mask), "target_mask must contain booleans aligned to tokens")
    require(mask[0] is False and any(mask[1:]), f"First token has no preceding context, or no targets in {row['id']}")


def loss_for_record(model, row, device, max_length, chunk_tokens=64):
    """Exact selected-target CE; cast only a small target-logit chunk to float32."""
    import torch
    import torch.nn.functional as functional

    validate_record(row, max_length)
    require(chunk_tokens >= 1, "chunk_tokens must be positive")
    ids = torch.tensor([row["input_ids"]], dtype=torch.long, device=device)
    require(int(ids.max()) < model.get_input_embeddings().num_embeddings, "Token ID exceeds model vocabulary")
    positions = [i for i, use in enumerate(row["target_mask"]) if use]
    total = 0.
    model.eval()
    with torch.inference_mode():
        logits = model(input_ids=ids, use_cache=False).logits[0]
        require(logits.shape[0] == ids.shape[1], "Unexpected model logit sequence shape")
        for start in range(0, len(positions), chunk_tokens):
            target_positions = torch.tensor(positions[start:start + chunk_tokens], device=device)
            prediction = logits[target_positions - 1].float()
            targets = ids[0, target_positions]
            losses = functional.cross_entropy(prediction, targets, reduction="none")
            total += float(losses.double().sum().item())
    require(np.isfinite(total), f"Nonfinite likelihood in {row['id']}")
    return {"id": row["id"], "nll_sum": total, "target_tokens": len(positions),
            "forwarded_tokens": len(row["input_ids"]), "record_hash": object_hash(row),
            "metadata": row.get("metadata", {})}


def token_windows(ids, max_length, stride):
    """Score every token except document token zero exactly once."""
    require(1 <= stride < max_length, "Require 1 <= stride < max_length to retain context")
    previous_end = 1
    for begin in range(0, len(ids), stride):
        end = min(begin + max_length, len(ids))
        if end <= previous_end:
            break
        mask = [begin + i >= previous_end for i in range(end - begin)]
        require(not mask[0], "Window lost preceding context")
        yield begin, ids[begin:end], mask
        previous_end = end
        if end == len(ids):
            break


def chunks_from_jsonl(path, size, max_length):
    require(type(size) is int and size >= 1, "records_per_shard must be a positive integer")
    seen, chunk = set(), []
    with open(path, encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            require(line.strip(), f"Blank JSONL line {line_number}")
            row = json.loads(line)
            validate_record(row, max_length)
            require(row["id"] not in seen, f"Duplicate record ID {row['id']}")
            seen.add(row["id"])
            chunk.append(row)
            if len(chunk) == size:
                yield chunk
                chunk = []
    if chunk:
        yield chunk


def validate_metadata(record, kind):
    meta = record.get("metadata", {})
    if kind == "documents":
        require(all(isinstance(meta.get(k), str) and meta[k].strip() for k in ("document_id", "document_hash")),
                f"Missing document metadata in {record['id']}")
    else:
        require(all(isinstance(meta.get(k), str) and meta[k].strip() for k in ("benchmark", "item_id")),
                f"Missing choice identifiers in {record['id']}")
        n = meta.get("choice_count")
        require(type(n) is int and n >= 2 and all(type(meta.get(k)) is int and 0 <= meta[k] < n for k in ("choice_index", "gold_index")),
                f"Invalid choice indices in {record['id']}")
        normalizer = meta.get("normalizer")
        require(type(normalizer) in (int, float) and np.isfinite(normalizer) and normalizer > 0,
                f"Invalid normalizer in {record['id']}")


def load_model(spec, dtype, device):
    from transformers import AutoModelForCausalLM
    local = Path(spec["model_id"])
    if local.is_dir():
        digest = object_hash({str(p.relative_to(local)): sha256(p) for p in sorted(local.rglob("*")) if p.is_file()})
        require(digest == spec.get("local_snapshot_hash"), "Local model snapshot hash mismatch")
    else:
        require(re.fullmatch(r"[0-9a-f]{40}", spec.get("revision", "")), "Use a 40-character immutable remote model commit")
    model = AutoModelForCausalLM.from_pretrained(
        spec["model_id"], revision=spec["revision"], dtype=dtype,
        trust_remote_code=False, local_files_only=spec.get("local_files_only", False))
    model.to(device).eval()
    return model


def run_gpu(job, cfg, out):
    import torch
    require(cfg.get("protocol_reviewed") is True and cfg.get("protocol_source"),
            "Review prompt/tokenization/scoring protocol, set protocol_reviewed=true and protocol_source")
    require(cfg.get("dtype") in ("float16", "float32"), "Reference runner supports explicit float16 or float32")
    device = cfg.get("device", "cuda:0")
    if device.startswith("cuda"):
        require(torch.cuda.is_available(), "CUDA unavailable; run GPU jobs on Kaggle")
    else:
        require(cfg.get("synthetic_cpu_test") is True and cfg["dtype"] == "float32", "CPU fallback allowed only for an explicit float32 synthetic test")
    manifest_path = Path(cfg["models"])
    manifest = read_json(manifest_path)
    models = manifest["models"]
    require(models and len({m["run_key"] for m in models}) == len(models), "Empty or duplicate model run keys")
    worker, workers = cfg.get("worker", 0), cfg.get("workers", 1)
    require(type(worker) is int and type(workers) is int and 0 <= worker < workers, "Invalid worker assignment")
    selected = [m for i, m in enumerate(models) if i % workers == worker]
    require(selected, "Worker has no assigned models")
    budget = cfg.get("max_seconds", 36000)
    require(type(budget) in (int, float) and np.isfinite(budget) and budget > 0, "max_seconds must be finite and positive")
    deadline = time.monotonic() + budget
    hardware = {"device": torch.cuda.get_device_name(device) if device.startswith("cuda") else "CPU synthetic test",
                "cuda_runtime": torch.version.cuda,
                "capability": list(torch.cuda.get_device_capability(device)) if device.startswith("cuda") else None}
    summaries = []

    def sync():
        if device.startswith("cuda"):
            torch.cuda.synchronize(device)

    for spec in selected:
        kind = spec.get("records_kind")
        require(kind in ("documents", "choices"), "Set records_kind to documents or choices")
        require(job != "G01" or kind == "documents", "G01 requires document records")
        require(job not in ("G02", "G03") or kind == "choices", "G02/G03 require choice records")
        records = manifest_path.parent / spec["records"]
        require(sha256(records) == spec["records_sha256"], f"Token-record hash mismatch for {spec['run_key']}")
        require(spec.get("tokenizer_revision") and spec.get("tokenizer_id"), "Missing tokenizer provenance")
        require(type(spec.get("expected_records")) is int and spec["expected_records"] > 0, "Set positive integer expected_records")
        max_length = spec["max_length"]
        require(type(max_length) is int and max_length >= 2, "max_length must be an integer >=2")
        count = 0
        for preflight_chunk in chunks_from_jsonl(records, cfg.get("records_per_shard", 64), max_length):
            for record in preflight_chunk:
                validate_metadata(record, kind)
                count += 1
        require(count == spec["expected_records"], f"Expected {spec['expected_records']} records, found {count} before model loading")
        started = time.monotonic()
        model = None
        load_seconds = 0.
        completed, total_nll, total_targets, total_forwarded = 0, 0., 0, 0
        score_seconds = 0.
        prefix = object_hash(spec["run_key"])[:20]
        pilot_source, pilot_scores = [], []
        if device.startswith("cuda"):
            torch.cuda.reset_peak_memory_stats(device)
        for shard_index, chunk in enumerate(chunks_from_jsonl(records, cfg.get("records_per_shard", 64), max_length)):
            for record in chunk:
                validate_metadata(record, kind)
            unit = out / f"{prefix}_{shard_index:06d}.json"
            identity = object_hash([job, spec, cfg["dtype"], hardware, chunk])
            if unit.exists():
                saved = read_json(unit)
                require(saved["identity"] == identity and object_hash(saved["rows"]) == saved["rows_hash"], f"Invalid resume shard {unit}")
                rows = saved["rows"]
            else:
                require(time.monotonic() < deadline, "Session budget reached; saved units can resume with the same configuration")
                if model is None:
                    t = time.monotonic()
                    model = load_model(spec, getattr(torch, cfg["dtype"]), device)
                    sync()
                    load_seconds += time.monotonic() - t
                rows = []
                for record in chunk:
                    sync()
                    t = time.monotonic()
                    row = loss_for_record(model, record, device, max_length, cfg.get("logit_chunk_tokens", 64))
                    sync()
                    row["seconds"] = time.monotonic() - t
                    rows.append(row)
                write_json(unit, {"identity": identity, "run_key": spec["run_key"], "rows": rows, "rows_hash": object_hash(rows)})
            require(len(rows) == len(chunk), "Resume shard row count mismatch")
            for source, row in zip(chunk, rows):
                require(row["id"] == source["id"] and row["record_hash"] == object_hash(source), "Resume record mismatch")
                require(row["target_tokens"] == sum(source["target_mask"]) and np.isfinite(row["nll_sum"]), "Invalid saved likelihood")
                completed += 1
                total_nll += row["nll_sum"]
                total_targets += row["target_tokens"]
                total_forwarded += row["forwarded_tokens"]
                score_seconds += row["seconds"]
                if job == "G00" and len(pilot_source) < cfg.get("reference_records", 8):
                    pilot_source.append(source)
                    pilot_scores.append(row)
        require(completed == spec["expected_records"], f"Expected {spec['expected_records']} records, got {completed}")
        peak = torch.cuda.max_memory_allocated(device) if device.startswith("cuda") else None
        del model
        gc.collect()
        if device.startswith("cuda"):
            torch.cuda.empty_cache()
        agreement = None
        if job == "G00":
            require(pilot_source, "No pilot reference examples")
            tolerance = cfg["reference_abs_mean_nll_tolerance"]
            require(np.isfinite(tolerance) and tolerance >= 0, "Invalid numerical tolerance")
            require(time.monotonic() < deadline, "Session budget reached before float32 reference; resume this pilot")
            reference = load_model(spec, torch.float32, device)
            diffs = []
            for source, measured in zip(pilot_source, pilot_scores):
                exact = loss_for_record(reference, source, device, max_length)
                diffs.append(abs(exact["nll_sum"] - measured["nll_sum"]) / exact["target_tokens"])
            del reference
            gc.collect()
            if device.startswith("cuda"):
                torch.cuda.empty_cache()
            agreement = {"max_abs_mean_nll_difference": max(diffs), "tolerance": tolerance, "reference_records": len(diffs)}
            write_json(out / f"{prefix}_agreement.json", agreement)
            require(max(diffs) <= tolerance, f"Precision reference failed for {spec['run_key']}: {max(diffs)} > {tolerance}")
        summaries.append({"run_key": spec["run_key"], "records": completed, "nll_sum": total_nll,
                          "target_tokens": total_targets, "mean_nll": total_nll / total_targets,
                          "forwarded_tokens": total_forwarded, "load_seconds_this_attempt": load_seconds,
                          "scoring_seconds_saved_units": score_seconds, "wall_seconds_this_attempt": time.monotonic() - started,
                          "peak_allocated_bytes_this_attempt": peak, "reference_agreement": agreement})
    return {"models": summaries, "worker": worker, "workers": workers, "dtype": cfg["dtype"],
            "hardware": hardware,
            "device": torch.cuda.get_device_name(device) if device.startswith("cuda") else "CPU synthetic test",
            "scope": "Prepared-token likelihood scoring; task margins and text-document aggregation require the supplied reducer",
            "synthetic_cpu_test": cfg.get("synthetic_cpu_test", False)}
