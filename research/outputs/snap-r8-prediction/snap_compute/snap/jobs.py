"""CPU experiments. Every new method is exploratory until independently calibrated."""
import copy
import importlib.metadata
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np

from .core import (cluster_bootstrap, folds_for, json_safe, load_dataset, moments, object_hash,
                   read_json, require, rng_for, sha256, split_halves, summarize, verify_artifacts, write_json)


def dataset(cfg):
    require("dataset" in cfg, "Set dataset to a real snap-scores-v1 JSON manifest")
    return load_dataset(cfg["dataset"])


def estimate(cfg, meta, arrays, mode=None, split_id=0):
    a, b, assignments = split_halves(meta, arrays, cfg.get("seed", 1), split_id,
                                    mode or cfg.get("split_mode", "original"))
    cov = moments(a, b)
    result = summarize(cov, meta["weights"])
    result.update({"assignments": assignments, "configuration_count": len(meta["configs"]),
                   "run_count": a.shape[1], "benchmark_names": [b["name"] for b in meta["benchmarks"]]})
    if cfg.get("bootstrap_draws", 0):
        result["uncertainty"] = cluster_bootstrap(cov, [c["recipe"] for c in meta["configs"]],
                                                  meta["weights"], cfg["bootstrap_draws"], cfg.get("seed", 1))
    return result, cov, a, b


def c00(cfg, out):
    inventory = []
    for name in cfg.get("inputs", []):
        p = Path(name)
        inventory.append({"path": str(p), "exists": p.is_file(),
                          "sha256": sha256(p) if p.is_file() else None,
                          "bytes": p.stat().st_size if p.is_file() else None})
    versions = {}
    for package in ("numpy", "torch", "transformers", "scipy"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    result = {"inputs": inventory, "versions": versions, "python": sys.version,
              "platform": platform.platform(), "missing": [r["path"] for r in inventory if not r["exists"]]}
    if cfg.get("dataset"):
        meta, _ = dataset(cfg)
        result["dataset"] = {"configs": len(meta["configs"]), "benchmarks": len(meta["benchmarks"]),
                              "phenotype": meta["phenotype"]}
    return result


def c01(cfg, out):
    meta, arrays = dataset(cfg)
    result, cov, a, b = estimate(cfg, meta, arrays)
    np.savez_compressed(out / "moments.npz", covariance=cov, half_a=a, half_b=b)
    result["interpretation"] = "Independent baseline implementation; reconcile with original outputs before claiming reproduction"
    return result


def c02(cfg, out):
    root = Path(__file__).resolve().parents[1]
    process = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                             cwd=root, text=True, capture_output=True)
    (out / "tests.txt").write_text(process.stdout + process.stderr, encoding="utf-8")
    require(process.returncode == 0, f"Tests failed; see {out / 'tests.txt'}")
    return {"tests_exit_code": process.returncode, "scope": "Synthetic/reference tests, not empirical reproduction"}


def c03(cfg, out):
    meta, arrays = dataset(cfg)
    repetitions = cfg.get("splits", 50)
    require(repetitions >= 1, "splits must be positive")
    rows = []
    assignments = out / "assignments"
    assignments.mkdir(exist_ok=True)
    for n in range(repetitions):
        for mode in ("item", "group"):
            r, _, _, _ = estimate({**cfg, "bootstrap_draws": 0}, meta, arrays, mode, n)
            write_json(assignments / f"{mode}_{n:04d}.json", r.pop("assignments"))
            rows.append({"split": n, "mode": mode, **r})
    return {"rows": rows, "interpretation": "Matched-universe split sensitivity; unequal group halves have no automatic unbiasedness guarantee",
            "split_variability_is_not_population_uncertainty": True}


def c04(cfg, out):
    meta, arrays = dataset(cfg)
    audit, selected, selected_arrays = [], [], [[] for _ in arrays]
    for i, c in enumerate(meta["configs"]):
        ids = c.get("matched_run_ids", [])
        run_by_id = {r["id"]: (j, r) for j, r in enumerate(c["runs"])}
        status = "not_prespecified"
        if ids:
            require(len(ids) == 2 and len(set(ids)) == 2 and set(ids) <= set(run_by_id),
                    f"matched_run_ids must identify exactly two actual runs in {c['id']}")
            chosen = [run_by_id[k] for k in ids]
            signature = [r.get("training_signature") for _, r in chosen]
            steps = [r.get("checkpoint_step") for _, r in chosen]
            status = "verified_declared_fields" if all(signature) and len(set(signature)) == 1 and None not in steps and len(set(steps)) == 1 else "metadata_mismatch_or_missing"
            if status == "verified_declared_fields":
                row = copy.deepcopy(c)
                row["runs"] = [r for _, r in chosen]
                selected.append(row)
                for buf, x in zip(selected_arrays, arrays):
                    buf.append(x[i, [j for j, _ in chosen]])
        audit.append({"configuration": c["id"], "status": status, "requested_ids": ids})
    result = {"audit": audit, "included": len(selected), "interpretation": "Matching declared metadata does not establish unrecorded training equivalence"}
    if selected:
        matched_meta = {**meta, "configs": selected}
        result["matched_estimate"] = estimate(cfg, matched_meta, [np.stack(v) for v in selected_arrays])[0]
        result["degrees_of_freedom_per_configuration"] = 1
    else:
        result["status"] = "blocked_no_verified_matched_pairs"
    return result


def c05(cfg, out):
    """Synthetic Gaussian/t stress grid; no claim to reproduce the old wild method."""
    cells = cfg["cells"]
    require(isinstance(cells, list) and cells, "Simulation cells must be a nonempty list")
    start, stop = cfg.get("replicate_start", 0), cfg["replicate_stop"]
    require(type(start) is int and type(stop) is int and 0 <= start < stop, "Replication bounds must be integers with 0 <= start < stop")
    records = []
    for cell_index, cell in enumerate(cells):
        require(all(type(cell.get(name, default)) is int for name, default in
                    (("benchmarks", 10), ("runs", 3), ("recipes", 25), ("sizes", 5))),
                "Simulation dimensions must be integers without coercion")
        k, r = int(cell.get("benchmarks", 10)), int(cell.get("runs", 3))
        recipes, sizes = int(cell.get("recipes", 25)), int(cell.get("sizes", 5))
        rho = cell.get("rho", .1)
        require(k >= 2 and r >= 2 and recipes >= 2 and sizes >= 1, "Invalid simulation dimensions")
        require(-1 / (k - 1) < rho < 1, "Equicorrelation must be positive definite")
        shared = cell.get("recipe_shared", .3)
        error_corr = cell.get("cross_half_error_correlation", 0.)
        noise = cell.get("noise_sd", 1.)
        require(0 <= shared <= 1 and -1 <= error_corr <= 1 and noise >= 0, "Invalid simulation correlation/noise")
        scale = np.asarray(cell.get("trait_scales", [1.] * k), float)
        require(scale.shape == (k,) and np.isfinite(scale).all() and (scale > 0).all(), "Invalid trait scales")
        truth = ((1 - rho) * np.eye(k) + rho * np.ones((k, k))) * np.outer(scale, scale)
        w = np.repeat(1 / k, k)
        true_lambda = summarize(truth, w)["lambda"]
        labels = np.repeat(np.arange(recipes).astype(str), sizes)
        for rep in range(start, stop):
            unit = out / f"cell_{cell_index:03d}_rep_{rep:07d}.json"
            identity = object_hash([cell, rep, cfg["seed"], cfg["bootstrap_draws"]])
            if unit.exists():
                row = read_json(unit)
                require(row["identity"] == identity, f"Stale simulation unit {unit}")
                require(row.get("content_hash") == object_hash({k: v for k, v in row.items() if k != "content_hash"}),
                        f"Changed simulation unit {unit}")
            else:
                rng = rng_for(cfg["seed"], "simulation", cell_index, rep)
                latent = np.sqrt(1 - shared) * rng.multivariate_normal(np.zeros(k), truth, size=(recipes * sizes, r))
                latent += np.sqrt(shared) * np.repeat(rng.multivariate_normal(np.zeros(k), truth, size=(recipes, r)), sizes, axis=0)
                df = cell.get("student_df")
                if df is not None:
                    require(df > 2, "Student df must exceed two for finite covariance")
                    latent *= np.sqrt((df - 2) / rng.chisquare(df, size=(recipes * sizes, r, 1)))
                ea = rng.normal(size=latent.shape) * noise
                eb = error_corr * ea + np.sqrt(1 - error_corr ** 2) * rng.normal(size=latent.shape) * noise
                cov = moments(latent + ea, latent + eb)
                est = summarize(cov, w)
                interval = cluster_bootstrap(cov, labels, w, cfg["bootstrap_draws"],
                                              int(rng_for(cfg["seed"], "bootstrap", cell_index, rep).integers(2**32)))
                bounds = interval["interval"]
                row = {"identity": identity, "cell": cell_index, "replicate": rep,
                       "true_lambda": true_lambda, "estimate": est["lambda"], "interval": bounds,
                       "invalid_bootstrap_fraction": interval["invalid_fraction"],
                       "covered": bounds[0] <= true_lambda <= bounds[1] if bounds else False,
                       "lower_miss": bounds[0] > true_lambda if bounds else None,
                       "upper_miss": bounds[1] < true_lambda if bounds else None}
                row = json_safe(row)
                row["content_hash"] = object_hash(row)
                write_json(unit, row)
            records.append(row)
    summaries = []
    for i in range(len(cells)):
        rows = [r for r in records if r["cell"] == i]
        valid = [r for r in rows if r["estimate"] is not None]
        error = np.array([r["estimate"] - r["true_lambda"] for r in valid])
        coverage = np.mean([r["covered"] for r in rows])
        summaries.append({"cell": i, "replicates": len(rows), "bias_given_defined": error.mean() if len(error) else None,
                          "rmse_given_defined": np.sqrt(np.mean(error ** 2)) if len(error) else None,
                          "coverage_counting_invalid_as_failure": coverage,
                          "coverage_mc_se": np.sqrt(coverage * (1 - coverage) / len(rows)),
                          "undefined_estimates": len(rows) - len(valid),
                          "invalid_intervals": sum(r["interval"] is None for r in rows),
                          "lower_misses": sum(r["lower_miss"] is True for r in rows),
                          "upper_misses": sum(r["upper_miss"] is True for r in rows)})
    return {"cells": summaries, "method": "recipe-percentile reference diagnostic, not original wild bootstrap",
            "scope": "Coverage under specified synthetic models only"}


def c06(cfg, out):
    meta, arrays = dataset(cfg)
    _, raw, a, b = estimate({**cfg, "bootstrap_draws": 0}, meta, arrays)
    proxy = read_json(cfg["proxy"])
    require(proxy.get("schema") == "snap-proxy-v1" and proxy.get("independent_corpus_hash"),
            "Need snap-proxy-v1 with independent_corpus_hash and keyed values")
    values = proxy["values"]
    z = np.array([[values[c["id"]][r["id"]] for r in c["runs"]] for c in meta["configs"]], float)
    require(np.isfinite(z).all(), "Nonfinite competence proxy")
    z -= z.mean(1, keepdims=True)
    folds = folds_for(meta["configs"], cfg.get("folds", 5), cfg["seed"])
    residual_a, residual_b = a.copy(), b.copy()
    coefficients = []
    penalty = cfg.get("ridge", 0.)
    require(penalty >= 0, "Ridge must be nonnegative and frozen before outcomes")
    for fold in sorted(set(folds)):
        train, test = folds != fold, folds == fold
        denom = np.sum(z[train] ** 2) + penalty
        require(denom > 0, "No training-fold proxy variation")
        slopes = []
        for source, dest in ((a, residual_a), (b, residual_b)):
            centered = source - source.mean(1, keepdims=True)
            slope = np.einsum("cr,crk->k", z[train], centered[train]) / denom
            dest[test] -= z[test, :, None] * slope
            slopes.append(slope)
        coefficients.append({"fold": int(fold), "half_slopes": slopes})
    adjusted = moments(residual_a, residual_b)
    np.savez_compressed(out / "residuals.npz", half_a=residual_a, half_b=residual_b, covariance=adjusted)
    return {"raw": summarize(raw, meta["weights"]), "adjusted": summarize(adjusted, meta["weights"]),
            "folds": folds, "coefficients": coefficients,
            "interpretation": "Cross-fitted descriptive adjustment; proxy error and causal identification remain separate questions"}


def prediction_rows(cov, configs, weights, folds, multiplicity=None):
    """Operational variance prediction using only training recipes at each size."""
    multiplicity = np.ones(len(configs)) if multiplicity is None else np.asarray(multiplicity)
    sizes = np.array([str(c["size"]) for c in configs])
    w = np.asarray(weights)
    rows = []
    for i, c in enumerate(configs):
        if multiplicity[i] == 0:
            continue
        train = (folds != folds[i]) & (sizes == str(c["size"])) & (multiplicity > 0)
        if not train.any():
            continue
        s = np.average(cov[train], axis=0, weights=multiplicity[train])
        diagonal = np.diag(np.diag(s))
        eig, vec = np.linalg.eigh(s)
        factor = max(float(eig[-1]), 0) * np.outer(vec[:, -1], vec[:, -1])
        rank = factor + np.diag(np.diag(s) - np.diag(factor))
        matrices = {"diagonal": diagonal, "full": s, "shrink_50": .5 * (s + diagonal), "rank_one_offdiagonal": rank}
        target = float(w @ cov[i] @ w)
        for name, matrix in matrices.items():
            predicted = float(w @ matrix @ w)
            rows.append({"configuration": c["id"], "recipe": c["recipe"], "fold": int(folds[i]),
                         "method": name, "target_raw_variance_moment": target, "prediction": predicted,
                         "negative_prediction": predicted < 0,
                         "squared_error": (target - predicted) ** 2, "multiplicity": float(multiplicity[i])})
    return rows


def paired_errors(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["method"], []).append(row)
    return {name: float(np.average([r["squared_error"] for r in group], weights=[r["multiplicity"] for r in group]))
            for name, group in grouped.items()}


def c07(cfg, out):
    meta, arrays = dataset(cfg)
    _, cov, _, _ = estimate({**cfg, "bootstrap_draws": 0}, meta, arrays)
    configs = meta["configs"]
    folds = folds_for(configs, cfg.get("folds", 5), cfg["seed"])
    rows = prediction_rows(cov, configs, meta["weights"], folds)
    require(len(rows) == 4 * len(configs), "Some held-out sizes have no training examples; revise folds prospectively")
    observed = paired_errors(rows)
    recipes = sorted({c["recipe"] for c in configs})
    bootstrap = {name: [] for name in observed if name != "diagonal"}
    draws = cfg.get("prediction_bootstrap_draws", 200)
    require(draws >= 20, "Need at least 20 diagnostic resamples")
    rng = rng_for(cfg["seed"], "prediction-refit")
    invalid = 0
    for _ in range(draws):
        sampled = rng.integers(len(recipes), size=len(recipes))
        counts = np.bincount(sampled, minlength=len(recipes))
        count = dict(zip(recipes, counts))
        multiplicity = [count[c["recipe"]] for c in configs]
        boot_rows = prediction_rows(cov, configs, meta["weights"], folds, multiplicity)
        if len(boot_rows) != 4 * np.count_nonzero(multiplicity):
            invalid += 1
            continue
        errors = paired_errors(boot_rows)
        for name in bootstrap:
            bootstrap[name].append(errors[name] - errors["diagonal"])
    return {"rows": rows, "mean_squared_errors": observed, "bootstrap_draws": draws,
            "invalid_bootstraps": invalid,
            "paired_difference_intervals_given_valid": {name: np.quantile(v, [.025, .975]) if v else None for name, v in bootstrap.items()},
            "interpretation": "Exploratory operational variance-MSE comparison with full training refits and fixed recipe folds; not the original conditional log-SD prediction experiment",
            "uncertainty_calibrated": False}


def c08(cfg, out):
    pairs = read_json(cfg["pairs"])
    require(pairs.get("schema") == "snap-pairs-v1", "Need snap-pairs-v1")
    require(isinstance(pairs.get("pairs"), list) and pairs["pairs"], "Pair list must be nonempty")
    rows = []
    for p in pairs["pairs"]:
        va, vb, cab = float(p["variance_a"]), float(p["variance_b"]), float(p["covariance_ab"])
        require(np.isfinite([va, vb, cab, p["observed_gap"]]).all(), "Nonfinite pair input")
        vd = va + vb - 2 * cab
        psd = va >= 0 and vb >= 0 and cab * cab <= va * vb + 1e-12
        rows.append({**p, "variance_difference": vd, "sd_difference": np.sqrt(vd) if vd >= 0 else None,
                     "input_is_population_feasible": bool(psd),
                     "independence_sd": np.sqrt(va + vb) if va + vb >= 0 else None})
    return {"pairs": rows, "interpretation": "Descriptive uncertainty arithmetic using supplied mean-estimate variances; no true-gap or ranking-error guarantee"}


def c09(cfg, out):
    meta, arrays = dataset(cfg)
    _, cov, a, b = estimate({**cfg, "bootstrap_draws": 0}, meta, arrays)
    w = np.array(meta["weights"])
    names = [b["name"] for b in meta["benchmarks"]]
    loo = []
    for j, name in enumerate(names):
        keep = np.arange(len(names)) != j
        ww = w[keep] / w[keep].sum()
        loo.append({"removed": name, **summarize(cov[:, keep][:, :, keep], ww)})
    groups = {}
    for j, bmeta in enumerate(meta["benchmarks"]):
        if "format" in bmeta:
            groups.setdefault(bmeta["format"], []).append(j)
    formats = {}
    for name, ids in groups.items():
        ww = w[ids] / w[ids].sum()
        formats[name] = summarize(cov[:, ids][:, :, ids], ww)
    gain_rows = []
    require(meta["phenotype"] == "margin" or not cfg.get("gain_sd"), "Gain manipulation is defined here for margins only")
    for gain_sd in cfg.get("gain_sd", []):
        require(gain_sd >= 0, "Gain SD must be nonnegative")
        gain = np.exp(rng_for(cfg["seed"], "gain", gain_sd).normal(-gain_sd**2 / 2, gain_sd, size=a.shape[:2]))
        gain_rows.append({"log_gain_sd": gain_sd, **summarize(moments(a * gain[..., None], b * gain[..., None]), w)})
    return {"leave_one_benchmark_out": loo, "format_subsets": formats, "gain_scenarios": gain_rows,
            "interpretation": "Descriptive composition and scale sensitivity, not a causal mediation bound"}


def c10(cfg, out):
    primary_meta, primary_arrays = load_dataset(cfg["dataset"])
    external_meta, external_arrays = load_dataset(cfg["external_dataset"])
    require(primary_meta["phenotype"] == external_meta["phenotype"], "Cannot compare different phenotypes")
    p = estimate(cfg, primary_meta, primary_arrays)[0]
    e = estimate(cfg, external_meta, external_arrays)[0]
    same_battery = [b["name"] for b in primary_meta["benchmarks"]] == [b["name"] for b in external_meta["benchmarks"]]
    return {"primary": p, "external": e, "same_benchmark_names": same_battery,
            "lambda_difference": e["lambda"] - p["lambda"] if e["lambda"] is not None and p["lambda"] is not None else None,
            "interpretation": "Population-specific estimates; transfer claims additionally require matched scoring protocols, units, weights, and item populations"}


def c11(cfg, out):
    checks = []
    expected = cfg["required_outputs"]
    require(expected, "Specify required_outputs, not an empty completion list")
    for entry in expected:
        directory = Path(entry["path"])
        manifest = read_json(directory / "manifest.json")
        require(manifest["job"] == entry["job"], f"Wrong job at {directory}")
        require(manifest["status"] == "FINISHED_UNCHECKED", f"Incomplete job at {directory}")
        require(manifest["config_hash"] == entry["config_hash"], f"Wrong configuration at {directory}")
        verify_artifacts(directory, manifest)
        result = read_json(directory / "result.json")
        require(not str(result.get("status", "")).startswith("blocked"), f"Blocked scientific output at {directory}")
        require(not result.get("missing"), f"Missing inputs at {directory}")
        checks.append({"job": entry["job"], "path": str(directory), "artifact_integrity": "passed"})
    return {"checks": checks, "status": "artifact_integrity_verified",
            "scientific_claims_verified": False,
            "interpretation": "Integrity verification cannot certify assumptions, calibration, or completeness of the broader research plan"}


CPU_JOBS = {f"C{i:02d}": globals()[f"c{i:02d}"] for i in range(12)}
