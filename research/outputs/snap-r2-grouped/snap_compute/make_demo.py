"""Generate explicitly synthetic inputs and small runnable CPU configurations."""
import argparse
from pathlib import Path

import numpy as np

from snap.core import rng_for, sha256, write_json


def make_demo(root):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    rng = rng_for(41, "SYNTHETIC-DEMO-ONLY")
    configs = [{"id": f"demo-{recipe}-{size}", "recipe": f"demo-{recipe}", "size": size,
                "runs": [{"id": f"r{r}", "training_signature": "synthetic", "checkpoint_step": 100} for r in range(3)],
                "matched_run_ids": ["r1", "r2"]} for recipe in range(6) for size in (1, 2)]
    arrays, benchmarks = {}, []
    latent = rng.normal(size=(12, 3, 1)) * .1 + rng.normal(size=(12, 3, 4)) * .2
    for j in range(4):
        arrays[f"b{j}"] = latent[..., j, None] + rng.normal(size=(12, 3, 24)) * .05
        benchmarks.append({"name": f"synthetic-task-{j}", "key": f"b{j}",
                           "item_ids": [f"item-{i}" for i in range(24)],
                           "group_ids": [f"passage-{i // 2}" for i in range(24)],
                           "original_half": [i % 2 for i in range(24)],
                           "format": "synthetic-cloze" if j < 2 else "synthetic-choice"})
    np.savez_compressed(root / "scores.npz", **arrays)
    meta = {"schema": "snap-scores-v1", "synthetic": True, "phenotype": "margin", "arrays": "scores.npz",
            "arrays_sha256": sha256(root / "scores.npz"), "configs": configs, "benchmarks": benchmarks}
    write_json(root / "scores.json", meta)
    proxy = {c["id"]: {r["id"]: float(latent[i, j].mean()) for j, r in enumerate(c["runs"])} for i, c in enumerate(configs)}
    write_json(root / "proxy.json", {"schema": "snap-proxy-v1", "independent_corpus_hash": "SYNTHETIC-ORACLE-NOT-REAL-CORPUS", "values": proxy})
    write_json(root / "pairs.json", {"schema": "snap-pairs-v1", "pairs": [
        {"id": "synthetic-pair", "variance_a": .01, "variance_b": .02, "covariance_ab": .002, "observed_gap": .04}]})
    for i in range(11):
        job = f"C{i:02d}"
        cfg = {"seed": 41, "dataset": "scores.json", "split_mode": "original", "bootstrap_draws": 40}
        if job == "C00":
            cfg = {"inputs": ["scores.json", "scores.npz"]}
        if job == "C02":
            cfg = {}
        if job == "C03":
            cfg["splits"] = 2
        if job == "C05":
            cfg = {"seed": 41, "replicate_start": 0, "replicate_stop": 3, "bootstrap_draws": 20,
                   "cells": [{"recipes": 5, "sizes": 2, "benchmarks": 3, "rho": .1},
                             {"recipes": 5, "sizes": 2, "benchmarks": 3, "rho": .2, "cross_half_error_correlation": .4}]}
        if job == "C06":
            cfg.update(proxy="proxy.json", folds=3, ridge=.01)
        if job == "C07":
            cfg.update(folds=3, prediction_bootstrap_draws=20)
        if job == "C08":
            cfg = {"pairs": "pairs.json"}
        if job == "C09":
            cfg["gain_sd"] = [0, .05]
        if job == "C10":
            cfg["external_dataset"] = "scores.json"
        write_json(root / f"{job}.json", cfg)
    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if Path(args.out).exists():
        parser.error("Use a new output directory to avoid overwriting a demo")
    print(make_demo(args.out))
