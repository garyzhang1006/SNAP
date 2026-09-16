"""Validated inputs, deterministic streams, and cross-half moment estimation."""
import hashlib
import json
import os
from pathlib import Path

import numpy as np


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def object_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def rng_for(seed, *names):
    digest = object_hash([int(seed), *map(str, names)])
    return np.random.default_rng(int(digest[:16], 16))


def json_safe(value):
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    if isinstance(value, np.generic):
        return json_safe(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    return value


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".{os.getpid()}.tmp")
    with open(temp, "w", encoding="utf-8") as handle:
        json.dump(json_safe(value), handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def verify_artifacts(directory, manifest):
    directory = Path(directory).resolve()
    artifacts = manifest.get("artifacts", {})
    require(isinstance(artifacts, dict) and "result.json" in artifacts,
            f"Manifest must hash result.json at {directory}")
    for name, digest in artifacts.items():
        relative = Path(name)
        path = (directory / relative).resolve()
        require(not relative.is_absolute() and ".." not in relative.parts and directory in path.parents,
                f"Artifact path escapes output directory: {name}")
        require(path.is_file() and sha256(path) == digest, f"Changed completed artifact {name} at {directory}")


def load_dataset(path):
    """One phenotype, rectangular C x R x items arrays per benchmark."""
    path = Path(path)
    meta = read_json(path)
    require(meta.get("schema") == "snap-scores-v1", "Expected schema snap-scores-v1")
    require(meta.get("phenotype") in ("margin", "accuracy"), "Specify margin or accuracy")
    configs, benchmarks = meta["configs"], meta["benchmarks"]
    require(len(configs) >= 1 and len(benchmarks) >= 2, "Need configurations and >=2 benchmarks")
    require(len({c["id"] for c in configs}) == len(configs), "Duplicate configuration ID")
    require(len({b["name"] for b in benchmarks}) == len(benchmarks), "Duplicate benchmark name")
    require(len({b["key"] for b in benchmarks}) == len(benchmarks), "Duplicate benchmark array key")
    runs = len(configs[0]["runs"])
    require(runs >= 2, "Need at least two runs per configuration")
    for c in configs:
        require(c.get("recipe") and "size" in c, f"Missing recipe/size for {c['id']}")
        require(len(c["runs"]) == runs, "Use separate datasets for different run counts")
        require(len({r["id"] for r in c["runs"]}) == runs, f"Duplicate run in {c['id']}")
    archive_path = path.parent / meta["arrays"]
    require(sha256(archive_path) == meta["arrays_sha256"], "Score archive hash mismatch")
    arrays = []
    with np.load(archive_path, allow_pickle=False) as archive:
        for b in benchmarks:
            x = np.asarray(archive[b["key"]], dtype=np.float64)
            n = len(b["item_ids"])
            require(n >= 2 and len(set(b["item_ids"])) == n, f"Invalid item IDs in {b['name']}")
            require(x.shape == (len(configs), runs, n), f"Wrong shape for {b['name']}: {x.shape}")
            require(np.isfinite(x).all(), f"Nonfinite score in {b['name']}")
            if meta["phenotype"] == "accuracy":
                require(np.isin(x, [0, 1]).all(), "Accuracy input must be binary item outcomes")
            for field in ("group_ids", "strata", "original_half"):
                if field in b:
                    require(len(b[field]) == n, f"Wrong {field} length in {b['name']}")
            arrays.append(x)
    weights = np.asarray(meta.get("weights", [1 / len(benchmarks)] * len(benchmarks)), float)
    require(weights.shape == (len(benchmarks),), "Invalid benchmark weights")
    require(np.isfinite(weights).all() and (weights > 0).all() and np.isclose(weights.sum(), 1),
            "Benchmark weights must be positive and sum to one")
    meta["weights"] = weights.tolist()
    return meta, arrays


def split_halves(meta, arrays, seed=0, split_id=0, mode="item"):
    """Fixed-universe, fixed-stratum weights; grouping changes conditional half banks.

    No claim of unconditional unbiasedness under random unequal group counts is made.
    Grouped results are sensitivity estimates pending an item-superpopulation model.
    """
    require(mode in ("item", "group", "original"), "Unknown split mode")
    require(len(meta["benchmarks"]) == len(arrays), "Benchmark/array count mismatch")
    halves, assignments = [], []
    for b, x in zip(meta["benchmarks"], arrays):
        n = x.shape[-1]
        raw_strata = b.get("strata", ["all"] * n)
        require(len(raw_strata) == n and all(isinstance(s, str) and s.strip() for s in raw_strata),
                f"Stratum IDs must be nonempty strings in {b['name']}")
        strata = np.asarray(raw_strata, dtype=str)
        labels = sorted(set(strata))
        sw = b.get("stratum_weights", {s: float(np.mean(strata == s)) for s in labels})
        require(set(sw) == set(labels) and all(v > 0 for v in sw.values())
                and np.isclose(sum(sw.values()), 1), f"Invalid stratum weights in {b['name']}")
        if mode == "original":
            require("original_half" in b, f"Missing original_half for {b['name']}")
            require(len(b["original_half"]) == n and all(type(v) is int and v in (0, 1) for v in b["original_half"]),
                    "Half assignments must be integer 0/1 without coercion")
            assignment = np.asarray(b["original_half"], dtype=int)
            require(np.isin(assignment, [0, 1]).all(), "Half assignments must be 0/1")
        else:
            raw_groups = b.get("group_ids", []) if mode == "group" else b["item_ids"]
            require(len(raw_groups) == n and all(isinstance(g, str) and g.strip() for g in raw_groups),
                    f"Missing or invalid group IDs for {b['name']}; use nonempty strings")
            groups = np.asarray(raw_groups, dtype=str)
            assignment = np.full(n, -1)
            # Cross-stratum groups require a joint allocation design, not silent splitting.
            group_strata = {}
            for g, s in zip(groups, strata):
                require(g not in group_strata or group_strata[g] == s, f"Group {g} crosses strata in {b['name']}")
                group_strata[g] = s
            for s in labels:
                ids = sorted(set(groups[strata == s]))
                require(len(ids) >= 2, f"Fewer than two groups in {b['name']}/{s}")
                order = rng_for(seed, "split", split_id, b["name"], s).permutation(len(ids))
                left = {ids[i] for i in order[:len(ids) // 2]}
                idx = np.flatnonzero(strata == s)
                assignment[idx] = [0 if groups[i] in left else 1 for i in idx]
        values = []
        for half in (0, 1):
            score = np.zeros(x.shape[:2], dtype=float)
            for s in labels:
                mask = (strata == s) & (assignment == half)
                require(mask.any(), f"Empty half {half} in {b['name']}/{s}")
                score += sw[s] * x[..., mask].mean(axis=-1)
            values.append(score)
        halves.append(values)
        assignments.append({"benchmark": b["name"], "item_ids": b["item_ids"],
                            "half": assignment.tolist(), "stratum_weights": sw})
    return np.stack([h[0] for h in halves], -1), np.stack([h[1] for h in halves], -1), assignments


def moments(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    require(a.shape == b.shape and a.ndim == 3 and a.shape[1] >= 2, "Halves must have equal C,R,K shape, R>=2")
    require(np.isfinite(a).all() and np.isfinite(b).all(), "Nonfinite half score")
    a = a - a.mean(axis=1, keepdims=True)
    b = b - b.mean(axis=1, keepdims=True)
    cross = np.einsum("crj,crk->cjk", a, b) / (a.shape[1] - 1)
    return (cross + cross.transpose(0, 2, 1)) / 2


def summarize(cov, weights):
    s = np.asarray(cov, float)
    if s.ndim == 3:
        s = s.mean(axis=0)
    w = np.asarray(weights, float)
    t = float(w @ s @ w)
    u = float((w * w) @ np.diag(s))
    ratio = t / u if u > 0 else None
    inflation = np.sqrt(ratio) if ratio is not None and ratio >= 0 else None
    return {"covariance": s, "T": t, "U": u, "lambda_squared": ratio,
            "lambda": inflation, "aggregate_sd": np.sqrt(t) if t >= 0 else None,
            "status": "defined" if inflation is not None else "undefined_moment_ratio",
            "minimum_eigenvalue": float(np.linalg.eigvalsh(s).min()),
            "negative_diagonal_count": int((np.diag(s) < 0).sum())}


def cluster_bootstrap(cov, recipes, weights, draws, seed, alpha=0.05):
    """Recipe-cluster percentile diagnostic; calibration is assessed separately."""
    require(draws >= 20 and 0 < alpha < 1, "Need >=20 bootstrap draws and valid alpha")
    recipes = np.asarray(recipes)
    names = sorted(set(recipes))
    require(len(names) >= 2, "Need >=2 recipe clusters for bootstrap")
    indices = [np.flatnonzero(recipes == r) for r in names]
    rng = rng_for(seed, "cluster-bootstrap")
    w = np.asarray(weights)
    numerator = np.einsum("j,cjk,k->c", w, cov, w)
    denominator = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    cluster_t = np.array([numerator[idx].sum() for idx in indices])
    cluster_u = np.array([denominator[idx].sum() for idx in indices])
    values = []
    # Configuration-count normalization cancels in the ratio, including uneven clusters.
    for offset in range(0, draws, 512):
        selected = rng.integers(len(names), size=(min(512, draws - offset), len(names)))
        t, u = cluster_t[selected].sum(1), cluster_u[selected].sum(1)
        keep = (u > 0) & (t >= 0)
        values.extend(np.sqrt(t[keep] / u[keep]).tolist())
    valid = np.array(values, float)
    failures = draws - len(valid)
    # A conditional-on-valid interval is a diagnostic, not a repaired unconditional CI.
    interval = np.quantile(valid, [alpha / 2, 1 - alpha / 2]).tolist() if len(valid) else None
    return {"method": "recipe_percentile_diagnostic", "draws": draws,
            "invalid_draws": failures, "invalid_fraction": failures / draws,
            "conditional_valid_interval": interval,
            "interval": interval if failures == 0 else None,
            "status": "uncalibrated" if failures == 0 else "undefined_draws_present"}


def folds_for(configs, nfolds, seed):
    recipes = sorted({c["recipe"] for c in configs})
    require(2 <= nfolds <= len(recipes), "Fold count exceeds available recipes")
    order = rng_for(seed, "recipe-folds").permutation(len(recipes))
    mapping = {recipes[int(i)]: n % nfolds for n, i in enumerate(order)}
    return np.array([mapping[c["recipe"]] for c in configs])
