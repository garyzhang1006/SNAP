"""R23: DataDecide checkpoint sensitivity, selected step against the previous shared step.

Builds snap-scores-v1 datasets from the shipped reduced runs (selected common
step) and from the R22 reductions at the previous step all seeds share, with
the same adapter and the same item split, then reruns C01 in split mode
"original" on both and applies the original interval machinery. It reports the
inflation estimate at the earlier step, a paired recipe-cluster bootstrap for
the difference, and the aggregate-score checkpoint shift in the form the
PolyPythias appendix uses (root-mean-square shift over the between-seed
standard deviation), plus the shift after removing each configuration's mean
progress. It stops if the selected steps in the shipped runs don't match the
common steps R22 recorded.
"""
import json, platform, shutil, subprocess, sys, time
from pathlib import Path

import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")


def find_all(name):
    return sorted(p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._"))


def find(name):
    hits = find_all(name)
    if not hits:
        sys.exit(f"{name} not found under /kaggle/input")
    return hits[0]


shutil.copytree(find("run_two_gpus.py").parent, W / "snap_compute", ignore=shutil.ignore_patterns("__pycache__", "._*"))
PKG = W / "snap_compute"
src = [p for p in find_all("pyproject.toml") if "seed-noise" in str(p)][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
for f in ("snap_adapter.py", "snap_intervals.py"):
    shutil.copy(find(f), W / f)

# Runs: shipped selected-step runs from the reduced-runs dataset, earlier-step runs from R22.
sel_files = [p for p in find_all("*.npz") if "runs_prev" not in str(p) and "__seed-" in p.name]
prev_files = [p for p in find_all("*.npz") if "runs_prev" in str(p)]
manifests = [json.load(open(p)) for p in find_all("prev_manifest_*.json")]
print(f"[inputs] selected {len(sel_files)} npz, previous {len(prev_files)} npz, {len(manifests)} manifests", flush=True)
assert len(sel_files) == 375, len(sel_files)
assert len(manifests) == 5 and all(not m["failures"] for m in manifests), [m["failures"] for m in manifests]
cells = {}
for m in manifests:
    for recipe, r in m["recipes"].items():
        for size, c in r["cells"].items():
            cells[(r.get("member_recipe", recipe), size)] = c


def key(name):
    recipe, size, seed, step = name[:-4].split("__")
    return recipe, size, int(seed.split("-")[1]), int(step.split("-")[1])


sel_keys = {key(p.name): p for p in sel_files}
for (recipe, size, seed, step) in sel_keys:
    c = cells[(recipe, size)]
    assert c["common_step"] == step, (recipe, size, seed, step, c["common_step"])
prev_keys = {key(p.name): p for p in prev_files}
have_prev = {(r, s) for (r, s, _, _) in prev_keys}
configs = sorted({(r, s) for (r, s, _, _) in sel_keys})
kept = [c for c in configs if c in have_prev and sum(1 for k in prev_keys if k[:2] == c) == 3]
dropped = [c for c in configs if c not in kept]
print(f"[configs] {len(configs)} selected, {len(kept)} with three previous-step runs, dropped {dropped}", flush=True)
gaps = {}
for (r, s) in kept:
    gaps.setdefault(s, []).append(cells[(r, s)]["gap"])

runs = {"sel": W / "runs_sel", "prev": W / "runs_prev_flat"}
for d in runs.values():
    d.mkdir(exist_ok=True)
for k, p in sel_keys.items():
    if k[:2] in kept:
        shutil.copy(p, runs["sel"] / p.name)
for k, p in prev_keys.items():
    if k[:2] in kept:
        shutil.copy(p, runs["prev"] / p.name)
data = W / "datasets"
for tag, d in runs.items():
    subprocess.check_call([sys.executable, str(W / "snap_adapter.py"), "--runs", str(d), "--out", str(data / tag)])
print(f"[adapter] done at {time.time() - t0:.0f}s", flush=True)


def run_c01(ds, out):
    cfg_path = W / "configs" / f"{out}.json"; cfg_path.parent.mkdir(exist_ok=True)
    cfg_path.write_text(json.dumps({"seed": 20260914, "dataset": ds, "split_mode": "original", "bootstrap_draws": 4999, "template_only": False}, indent=2))
    subprocess.check_call([sys.executable, str(PKG / "runs" / "C01.py"), "--config", str(cfg_path), "--out", str(W / "SNAP" / out)])
    subprocess.check_call([sys.executable, str(W / "snap_intervals.py"), "--c01", str(W / "SNAP" / out), "--dataset", ds,
                           "--out", str(W / "SNAP" / out / "original_intervals.json")])
    return json.load(open(W / "SNAP" / out / "original_intervals.json"))


def aggregate(ds_json):
    meta = json.load(open(ds_json))
    z = np.load(Path(ds_json).with_name(meta["arrays"]))
    w = np.asarray(meta["weights"], float)
    per_b = []
    for b in meta["benchmarks"]:
        x = z[b["key"]]  # (C, R, n)
        if "strata" in b:
            strata = np.array(b["strata"]); labels = sorted(set(strata.tolist()))
            per_b.append(np.mean([x[:, :, strata == s].mean(-1) for s in labels], axis=0))
        else:
            per_b.append(x.mean(-1))
    return meta, np.einsum("j,jcr->cr", w, np.stack(per_b))


results = {"kept_configs": len(kept), "dropped_configs": [list(c) for c in dropped],
           "gap_by_size": {s: {"min": int(min(g)), "median": float(np.median(g)), "max": int(max(g))} for s, g in gaps.items()},
           "phenotypes": {}}
rng = np.random.default_rng(0)
for phen in ("margin", "accuracy"):
    ds = {t: str(data / t / phen / "scores.json") for t in runs}
    iv = {t: run_c01(ds[t], f"C01_{phen}_{t}") for t in runs}
    meta_s, agg_s = aggregate(ds["sel"]); meta_p, agg_p = aggregate(ds["prev"])
    ids_s = [c["id"] for c in meta_s["configs"]]; ids_p = [c["id"] for c in meta_p["configs"]]
    assert ids_s == ids_p
    seeds_s = [[r["seed"] for r in c["runs"]] for c in meta_s["configs"]]; seeds_p = [[r["seed"] for r in c["runs"]] for c in meta_p["configs"]]
    assert seeds_s == seeds_p, "run order differs between the two datasets"
    # Paired recipe-cluster bootstrap of the inflation difference.
    TU = {}
    for t in runs:
        m = json.load(open(ds[t])); cov = np.load(W / "SNAP" / f"C01_{phen}_{t}" / "moments.npz")["covariance"]
        w = np.asarray(m["weights"], float)
        TU[t] = (np.einsum("j,cjk,k->c", w, cov, w), np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2)))
    recipe = np.array([c["recipe"] for c in meta_s["configs"]]); size = np.array([c["size"] for c in meta_s["configs"]])
    groups = sorted(set(recipe.tolist())); idx = [np.flatnonzero(recipe == g) for g in groups]
    lam = {t: float(np.sqrt(TU[t][0].sum() / TU[t][1].sum())) for t in runs}
    diffs = []
    for _ in range(4999):
        pick = np.concatenate([idx[i] for i in rng.integers(0, len(groups), len(groups))])
        th = {t: TU[t][0][pick].sum() / TU[t][1][pick].sum() for t in runs}
        if th["sel"] >= 0 and th["prev"] >= 0:
            diffs.append(np.sqrt(th["prev"]) - np.sqrt(th["sel"]))
    diffs = np.array(diffs)
    # Checkpoint shift of aggregate scores, per run.
    shift = agg_s - agg_p                                   # (C, 3)
    between_sd = float(np.sqrt(np.mean(agg_s.var(axis=1, ddof=1))))
    rms_shift = float(np.sqrt(np.mean(shift ** 2)))
    centred = shift - shift.mean(axis=1, keepdims=True)
    rms_centred = float(np.sqrt(np.mean(centred ** 2) * 3 / 2))  # ddof correction for removing one mean of three
    cs = agg_s - agg_s.mean(1, keepdims=True); cp = agg_p - agg_p.mean(1, keepdims=True)
    corr_within = float((cs * cp).sum() / np.sqrt((cs ** 2).sum() * (cp ** 2).sum()))
    by_size = {}
    for s in ("150M", "300M", "530M", "750M", "1B"):
        i = size == s
        if i.any():
            bsd = float(np.sqrt(np.mean(agg_s[i].var(axis=1, ddof=1))))
            by_size[s] = {"n": int(i.sum()), "between_sd": bsd, "rms_shift": float(np.sqrt(np.mean(shift[i] ** 2))),
                          "ratio": float(np.sqrt(np.mean(shift[i] ** 2)) / bsd),
                          "ratio_centred": float(np.sqrt(np.mean(centred[i] ** 2) * 3 / 2) / bsd),
                          "within_config_corr": float((cs[i] * cp[i]).sum() / np.sqrt((cs[i] ** 2).sum() * (cp[i] ** 2).sum()))}
    rank_same = float(np.mean([np.array_equal(np.argsort(agg_s[c]), np.argsort(agg_p[c])) for c in range(agg_s.shape[0])]))
    results["phenotypes"][phen] = {
        "lambda_selected": lam["sel"], "lambda_previous": lam["prev"], "intervals_selected": iv["sel"], "intervals_previous": iv["prev"],
        "difference_previous_minus_selected": lam["prev"] - lam["sel"],
        "difference_recipe_bootstrap_95": [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))],
        "difference_valid_draws": int(diffs.size),
        "between_seed_sd": between_sd, "rms_shift": rms_shift, "ratio_rms_shift_over_between_sd": rms_shift / between_sd,
        "rms_shift_centred": rms_centred, "ratio_centred": rms_centred / between_sd,
        "within_config_corr_selected_vs_previous": corr_within, "seed_order_unchanged_share": rank_same, "by_size": by_size}
    print(f"[{phen}] {json.dumps({k: v for k, v in results['phenotypes'][phen].items() if not k.startswith('intervals') and k != 'by_size'})}", flush=True)
    print(f"[{phen}/by_size] {json.dumps(by_size)}", flush=True)
    print(f"[{phen}/intervals] sel {json.dumps({k: iv['sel'][k] for k in ('lambda', 'wild')})} prev {json.dumps({k: iv['prev'][k] for k in ('lambda', 'wild')})}", flush=True)

results["wall_seconds"] = time.time() - t0
(W / "r23_prev_step.json").write_text(json.dumps(results, indent=1, default=lambda x: None if isinstance(x, float) and not np.isfinite(x) else x))
for d in list(runs.values()) + [W / "seed-noise"]:
    shutil.rmtree(d, ignore_errors=True)
for t in runs:
    for phen in ("margin", "accuracy"):
        (data / t / phen / "scores.npz").unlink(missing_ok=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
