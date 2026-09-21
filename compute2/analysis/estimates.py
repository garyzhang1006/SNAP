"""Every estimate compute2 produces, from the reduced runs, with the paper's estimator.

  python analysis/estimates.py --reduced reduced --release-runs data/release_runs --out results

Reads whichever jobs have been reduced and writes one JSON per analysis under
results/, then results/verdicts.json with the pre-specified reading rules
applied (README, "Reading rules"). Nothing here is fitted or tuned; the
estimator, the half split and the intervals are the seednoise functions the
paper used, imported from src/, and this file only assembles populations from
different item banks:

  within-bank   half A and half B are two halves of one bank (the paper's design)
  cross-bank    A is every item of bank 1 and B is every item of bank 2, so
                nothing about a specific item, passage or near-duplicate can
                sit in both factors of the cross product
  cross-format  A is bank 1 (five-shot) and B is the zero-shot bank

Intervals. DataDecide populations use the paper's wild cluster bootstrap-t over
the 25 recipes. PolyPythias populations have nine replicate seeds and at most
five size clusters, so the primary interval there is a delete-one-seed
jackknife with t(8) critical values, formed on theta and square-rooted, and the
size-cluster wild bootstrap is reported beside it as the thin-cluster check.
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE.parent / "common"))

import tasks66  # noqa: E402
from seednoise.data import datadecide as dd  # noqa: E402
from seednoise.estimator import correlation, estimate, sigma_e  # noqa: E402
from seednoise.halves import MASTER_SEED, split_items  # noqa: E402
from seednoise.inference import _theta, cluster_t_interval, config_bootstrap, wild_bootstrap_t  # noqa: E402
from seednoise.phenotypes import half_scores  # noqa: E402
from seednoise.population import ACCURACY, MARGIN, Phenotype, Population  # noqa: E402
from seednoise.store import load_run  # noqa: E402

K = len(tasks66.TRAITS)
N_BOOT = 4999
BOOT_SEED = 0
PAPER = {"margin": 1.244, "accuracy": 1.078}
SIZE_ORDER = ["14m", "31m", "70m", "160m", "410m", "150M", "300M", "530M", "750M", "1B"]


def check_constants():
    if list(dd.TASKS) != tasks66.TASKS or list(dd.TRAITS) != tasks66.TRAITS or dd.ITEM_STRIDE != tasks66.ITEM_STRIDE:
        raise SystemExit("common/tasks66.py no longer matches src/seednoise/data/datadecide.py; item ids would misalign")


# -- loading -------------------------------------------------------------------


def load_dir(path):
    path = Path(path)
    out = {}
    for f in sorted(path.glob("*.npz")):
        if f.name.endswith(".partial.npz"):
            continue
        items, meta = load_run(f)
        out[f.stem] = (items, meta)
    return out


def run_key_of(meta):
    return (str(meta["recipe"]).lower(), str(meta["size"]), int(meta["seed"]), int(meta["step"]))


def same_item_set(runs):
    ref = None
    for name, (items, _) in runs.items():
        if ref is None:
            ref = items.item_id
        elif not np.array_equal(items.item_id, ref):
            raise ValueError(f"{name} is on a different item set from the first run; the bank is not one item set")
    return ref


# -- splits and trait scores ---------------------------------------------------


def split_by_group(group, seed):
    """Balanced random half inside every task group, so a small MMLU subject
    keeps items on both sides. Returns the mask of half A."""
    rng = np.random.default_rng(seed)
    mask = np.zeros(group.shape[0], dtype=bool)
    for g in np.unique(group):
        idx = np.flatnonzero(group == g)
        if idx.size < 2:
            raise ValueError(f"group {g} has {idx.size} item, which cannot be split")
        mask[rng.permutation(idx)[: idx.size // 2]] = True
    return mask


def trait_scores(items, mask=None):
    if mask is None:
        mask = np.ones(items.n_items, dtype=bool)
    return half_scores(items, mask, K)


# -- populations ---------------------------------------------------------------


def assemble(cells, cluster_of, size_of):
    """cells: {config key: [(meta, (mA, aA), (mB, aB)), ...]} with equal run counts.
    cluster_of(key) and size_of(key) give the labels the intervals use."""
    keys = sorted(cells)
    counts = {len(v) for v in cells.values()}
    if len(counts) != 1:
        raise ValueError(f"configurations carry different run counts {sorted(counts)}")
    R = counts.pop()
    if R < 2:
        raise ValueError("a configuration needs at least two runs")
    N = len(keys)
    mA = np.zeros((N, R, K)); aA = np.zeros((N, R, K)); mB = np.zeros((N, R, K)); aB = np.zeros((N, R, K))
    gain = np.zeros((N, R)); batch = np.zeros((N, R), dtype=np.int64)
    clusters = sorted({cluster_of(k) for k in keys})
    sizes = sorted({size_of(k) for k in keys}, key=lambda z: SIZE_ORDER.index(z) if z in SIZE_ORDER else 999)
    recipe = np.zeros(N, dtype=np.int64); size = np.zeros(N, dtype=np.int64)
    for c, key in enumerate(keys):
        rows = sorted(cells[key], key=lambda t: t[0]["batch"])
        recipe[c], size[c] = clusters.index(cluster_of(key)), sizes.index(size_of(key))
        for r, (meta, (m_a, a_a), (m_b, a_b)) in enumerate(rows):
            mA[c, r], aA[c, r], mB[c, r], aB[c, r] = m_a, a_a, m_b, a_b
            gain[c, r] = meta["gain"]
            batch[c, r] = meta["batch"]
    pop = Population({MARGIN: Phenotype(MARGIN, mA, mB), ACCURACY: Phenotype(ACCURACY, aA, aB)},
                     gainA=gain, gainB=gain, batch=batch, recipe=recipe, size=size, traits=list(tasks66.TRAITS),
                     config_ids=[list(k) if isinstance(k, tuple) else [k] for k in keys])
    return pop, {"clusters": clusters, "sizes": sizes}


def drop_traits(pop, names):
    keep = [j for j, t in enumerate(pop.traits) if t not in set(names)]
    ph = {k: Phenotype(k, v.A[:, :, keep], v.B[:, :, keep]) for k, v in pop.phenotypes.items()}
    return Population(ph, pop.gainA, pop.gainB, pop.batch, pop.recipe, pop.size,
                      [pop.traits[j] for j in keep], pop.config_ids, None)


def sub_runs(pop, keep):
    ph = {k: Phenotype(k, v.A[:, keep, :], v.B[:, keep, :]) for k, v in pop.phenotypes.items()}
    return Population(ph, pop.gainA[:, keep], pop.gainB[:, keep], pop.batch[:, keep], pop.recipe, pop.size,
                      pop.traits, pop.config_ids, pop.n_items)


# -- intervals -----------------------------------------------------------------


def _sqrt(x):
    return float(np.sqrt(x)) if np.isfinite(x) and x >= 0 else float("nan")


def seed_jackknife(pop, name, which="all"):
    """Delete-one-replicate jackknife on theta = sum T / sum U, t(R-1) critical
    values, endpoints square-rooted. Run index r must mean the same seed in
    every configuration, which the assembler guarantees through the batch
    labels and this function checks."""
    if not np.all(pop.batch == pop.batch[0]):
        raise ValueError("batch labels differ across configurations, so run index is not a seed; no seed jackknife")
    est = estimate(pop, name, which, check=False)
    th = _theta(est.T, est.U)
    R = pop.R
    thetas = []
    for r in range(R):
        keep = [i for i in range(R) if i != r]
        e = estimate(sub_runs(pop, keep), name, which, check=False)
        thetas.append(_theta(e.T, e.U))
    thetas = np.asarray(thetas, dtype=float)
    se = float(np.sqrt((R - 1) / R * np.sum((thetas - thetas.mean()) ** 2)))
    crit = float(student_t.ppf(0.975, R - 1))
    return {"point": _sqrt(th), "lo": _sqrt(th - crit * se), "hi": _sqrt(th + crit * se),
            "se_theta": se, "method": f"delete-one-seed jackknife t({R - 1})", "n_seeds": R,
            "leave_one_out_lambda": [_sqrt(x) for x in thetas]}


def all_intervals(pop, name, which="all", jackknife=False):
    est = estimate(pop, name, which)
    T, U = est.T, est.U
    out = {"lambda": est.lambda_hat, "k_eff": est.k_eff, "rbar_e": est.rbar_e, "N": pop.N, "R": pop.R, "K": pop.K,
           "n_clusters": pop.n_clusters, "contrast": which,
           "sum_T": float(T.sum()), "sum_U": float(U.sum())}
    try:
        out["wild"] = wild_bootstrap_t(T, U, pop.recipe, n_boot=N_BOOT, seed=BOOT_SEED).as_row()
    except Exception as e:  # thin clusters: the error is the result
        out["wild"] = {"error": f"{type(e).__name__}: {e}"}
    try:
        out["cluster_t"] = cluster_t_interval(T, U, pop.recipe).as_row()
    except Exception as e:
        out["cluster_t"] = {"error": f"{type(e).__name__}: {e}"}
    out["config_boot"] = config_bootstrap(T, U, n_boot=N_BOOT, seed=BOOT_SEED).as_row()
    if jackknife:
        try:
            out["jackknife"] = seed_jackknife(pop, name, which)
        except Exception as e:
            out["jackknife"] = {"error": f"{type(e).__name__}: {e}"}
    return out


def primary(row, kind):
    """The interval the reading rules use: jackknife for PolyPythias, wild for DataDecide."""
    key = "jackknife" if kind == "pythia" else "wild"
    iv = row.get(key, {})
    return iv if "lo" in iv else {"lo": float("nan"), "hi": float("nan"), "point": row["lambda"]}


def cluster_boot_logdiff(T1, U1, T2, U2, cluster, n_boot=N_BOOT, seed=BOOT_SEED):
    """Percentile cluster bootstrap of log(theta_1) - log(theta_2), the two
    ratios recomputed on the same resampled clusters so the difference carries
    the shared sampling."""
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    members = [np.flatnonzero(inv == g) for g in range(G)]
    rng = np.random.default_rng(seed)
    d = np.full(n_boot, np.nan)
    for b in range(n_boot):
        idx = np.concatenate([members[g] for g in rng.integers(0, G, G)])
        t1, t2 = _theta(T1[idx], U1[idx]), _theta(T2[idx], U2[idx])
        if t1 > 0 and t2 > 0:
            d[b] = np.log(t1) - np.log(t2)
    ok = d[np.isfinite(d)]
    th1, th2 = _theta(T1, U1), _theta(T2, U2)
    point = float(np.log(th1) - np.log(th2)) if th1 > 0 and th2 > 0 else float("nan")
    if ok.size < max(100, int(0.9 * n_boot)):
        return {"point_log_theta_diff": point, "error": f"only {ok.size} of {n_boot} draws had both ratios positive"}
    lo, hi = np.percentile(ok, [2.5, 97.5])
    return {"point_log_theta_diff": point, "lo": float(lo), "hi": float(hi), "draws_defined": int(ok.size),
            "method": f"cluster percentile bootstrap (G={G}) of log theta difference; halve for log Lambda"}


def jackknife_logdiff(pop1, pop2, name):
    """Delete-one-seed jackknife of log(theta_1) - log(theta_2) for two
    populations on the same runs."""
    if pop1.R != pop2.R or not np.all(pop1.batch == pop2.batch):
        raise ValueError("the two populations do not share their runs")
    R = pop1.R

    def logdiff(p1, p2):
        e1, e2 = estimate(p1, name, "all", check=False), estimate(p2, name, "all", check=False)
        t1, t2 = _theta(e1.T, e1.U), _theta(e2.T, e2.U)
        return float(np.log(t1) - np.log(t2)) if t1 > 0 and t2 > 0 else float("nan")

    full = logdiff(pop1, pop2)
    loo = np.asarray([logdiff(sub_runs(pop1, [i for i in range(R) if i != r]),
                              sub_runs(pop2, [i for i in range(R) if i != r])) for r in range(R)])
    if not np.isfinite(loo).all() or not np.isfinite(full):
        return {"point_log_theta_diff": full, "error": "a leave-one-out ratio was not positive"}
    se = float(np.sqrt((R - 1) / R * np.sum((loo - loo.mean()) ** 2)))
    crit = float(student_t.ppf(0.975, R - 1))
    return {"point_log_theta_diff": full, "lo": full - crit * se, "hi": full + crit * se, "se": se,
            "method": f"delete-one-seed jackknife t({R - 1}) of log theta difference; halve for log Lambda"}


def matrix_block(pop, name):
    S = sigma_e(pop, name)
    C = correlation(S)
    return {"sigma_e": S.tolist(), "correlation": C.tolist(), "traits": pop.traits,
            "negative_diagonal": [pop.traits[j] for j in np.flatnonzero(np.diag(S) <= 0)]}


def full_block(pop, kind, which_list=("all",), matrix=True):
    """Both phenotypes, every contrast asked for, with and without BoolQ."""
    out = {"summary": pop.summary(), "config_ids": pop.config_ids}
    for battery, p in (("full", pop), ("no_boolq", drop_traits(pop, ["boolq"]))):
        out[battery] = {}
        for name in (MARGIN, ACCURACY):
            out[battery][name] = {w: all_intervals(p, name, w, jackknife=(kind == "pythia")) for w in which_list}
        if matrix:
            out[battery]["matrix"] = {name: matrix_block(p, name) for name in (MARGIN, ACCURACY)}
    return out


# -- the analyses --------------------------------------------------------------


def pythia_cells(runs, mask=None, mask_b=None, other=None, steps=None):
    """Cells keyed by (size, step). With other given, A comes from runs and B
    from other on matching keys (the cross-bank form); otherwise A and B are
    the two halves of runs."""
    cells = {}
    index_b = {run_key_of(m): (it, m) for it, m in other.values()} if other is not None else None
    for it, meta in runs.values():
        key = run_key_of(meta)
        if steps is not None and key[3] not in steps:
            continue
        if other is None:
            A, B = trait_scores(it, mask), trait_scores(it, ~mask if mask is not None else None)
        else:
            if key not in index_b:
                continue
            A, B = trait_scores(it, mask), trait_scores(index_b[key][0], mask_b)
        cells.setdefault((key[1], key[3]), []).append((meta, A, B))
    return cells


def analysis_pythia(reduced, results):
    final = load_dir(reduced / "pythia_bank1_final")
    if not final:
        return {"status": "not run", "reason": "reduced/pythia_bank1_final has no runs"}
    ref = same_item_set(final)
    first = next(iter(final.values()))[0]
    if ref.size != tasks66.RELEASE_TOTAL:
        raise SystemExit(f"pythia bank 1 holds {ref.size} items, the release battery is {tasks66.RELEASE_TOTAL}")
    mask = split_items(first.trait, K, seed=MASTER_SEED)          # the paper's split on the paper's items
    out = {"status": "ok", "items": int(ref.size), "split": f"seednoise.halves.split_items(seed={MASTER_SEED})"}
    steps = sorted({run_key_of(m)[3] for _, m in final.values()})
    if len(steps) != 1:
        raise SystemExit(f"pythia_bank1_final holds steps {steps}, expected one")
    cells = pythia_cells(final, mask)
    pop, labels = assemble(cells, cluster_of=lambda k: k[0], size_of=lambda k: k[0])
    out["final_step"] = steps[0]
    out["within_bank1"] = full_block(pop, "pythia")
    out["within_bank1"]["labels"] = labels
    # Per size: one configuration, nine seeds; the jackknife is the only interval.
    out["within_bank1_per_size"] = {}
    for key, rows in sorted(cells.items(), key=lambda kv: SIZE_ORDER.index(kv[0][0])):
        p, _ = assemble({key: rows}, cluster_of=lambda k: k[0], size_of=lambda k: k[0])
        out["within_bank1_per_size"][key[0]] = {
            name: {"lambda": estimate(p, name, "all", check=False).lambda_hat,
                   "jackknife": seed_jackknife(p, name)} for name in (MARGIN, ACCURACY)}

    # Cross-bank and within-bank-2 on the same runs.
    bank2 = load_dir(reduced / "pythia_bank2_final")
    if bank2:
        try:
            same_item_set(bank2)
            first2 = next(iter(bank2.values()))[0]
            mask2 = split_by_group(first2.group, seed=MASTER_SEED)
            cross = pythia_cells(final, mask=None, mask_b=None, other=bank2)
            within2 = pythia_cells(bank2, mask2)
            pc, _ = assemble(cross, cluster_of=lambda k: k[0], size_of=lambda k: k[0])
            p2, _ = assemble(within2, cluster_of=lambda k: k[0], size_of=lambda k: k[0])
            out["cross_bank"] = full_block(pc, "pythia", matrix=True)
            out["within_bank2"] = full_block(p2, "pythia", matrix=False)
            out["within_bank2"]["items"] = int(first2.n_items)
            out["within_minus_cross"] = {
                name: {"full": jackknife_logdiff(pop, pc, name),
                       "no_boolq": jackknife_logdiff(drop_traits(pop, ["boolq"]), drop_traits(pc, ["boolq"]), name)}
                for name in (MARGIN, ACCURACY)}
            out["runs_matched"] = pc.N * pc.R
        except Exception as e:  # a partial arm must not take R1 down with it
            out["cross_bank"] = {"status": "error", "reason": f"{type(e).__name__}: {e}"}
            out["within_bank2"] = {"status": "error", "reason": f"{type(e).__name__}: {e}"}
            out.pop("within_minus_cross", None)
            out.pop("runs_matched", None)
    else:
        out["cross_bank"] = {"status": "not run", "reason": "reduced/pythia_bank2_final has no runs"}

    zs = load_dir(reduced / "pythia_bank2zs_final")
    if zs:
        try:
            same_item_set(zs)
            cf = pythia_cells(final, mask=None, mask_b=None, other=zs)
            pz, _ = assemble(cf, cluster_of=lambda k: k[0], size_of=lambda k: k[0])
            out["cross_format"] = full_block(pz, "pythia", matrix=False)
            out["within_minus_crossformat"] = {name: jackknife_logdiff(pop, pz, name) for name in (MARGIN, ACCURACY)}
        except Exception as e:
            out["cross_format"] = {"status": "error", "reason": f"{type(e).__name__}: {e}"}
            out.pop("within_minus_crossformat", None)
    else:
        out["cross_format"] = {"status": "not run", "reason": "reduced/pythia_bank2zs_final has no runs"}

    # The curve across training, every configuration at one matched step.
    curve = load_dir(reduced / "pythia_bank1_curve")
    if curve:
        try:
            both = dict(final); both.update(curve)
            same_item_set(both)
            cells_all = pythia_cells(both, mask)
            pool, labels_c = assemble(cells_all, cluster_of=lambda k: k[0], size_of=lambda k: k[0])
            out["curve"] = {"pooled_over_steps": full_block(pool, "pythia", matrix=False), "labels": labels_c,
                            "per_step": {}, "per_size_step": {}}
            for step in sorted({k[1] for k in cells_all}):
                sub = {k: v for k, v in cells_all.items() if k[1] == step}
                ps, _ = assemble(sub, cluster_of=lambda k: k[0], size_of=lambda k: k[0])
                out["curve"]["per_step"][str(step)] = {
                    name: {"lambda": estimate(ps, name, "all", check=False).lambda_hat,
                           "jackknife": seed_jackknife(ps, name),
                           "no_boolq_lambda": estimate(drop_traits(ps, ["boolq"]), name, "all", check=False).lambda_hat}
                    for name in (MARGIN, ACCURACY)}
            for key, rows in sorted(cells_all.items(), key=lambda kv: (SIZE_ORDER.index(kv[0][0]), kv[0][1])):
                p, _ = assemble({key: rows}, cluster_of=lambda k: k[0], size_of=lambda k: k[0])
                out["curve"]["per_size_step"][f"{key[0]}@{key[1]}"] = {
                    name: estimate(p, name, "all", check=False).lambda_hat for name in (MARGIN, ACCURACY)}
        except Exception as e:
            out["curve"] = {"status": "error", "reason": f"{type(e).__name__}: {e}"}
    else:
        out["curve"] = {"status": "not run", "reason": "reduced/pythia_bank1_curve has no runs"}
    return out


def datadecide_join(release, scored):
    """Match release reduced runs (bank 1) to the scored bank-2 runs by recipe,
    size, seed and step; the recipe spelling differs in case for two recipes."""
    idx = {run_key_of(m): (it, m) for it, m in release.values()}
    matched, missing, step_mismatch = {}, [], []
    for name, (it, m) in scored.items():
        key = run_key_of(m)
        if key in idx:
            matched[name] = (idx[key], (it, m))
        else:
            near = [k for k in idx if k[:3] == key[:3]]
            (step_mismatch if near else missing).append({"run": name, "release_steps": [k[3] for k in near]})
    return matched, missing, step_mismatch


def analysis_datadecide(reduced, release_dir, results):
    scored = load_dir(reduced / "datadecide_bank2")
    if not scored:
        return {"status": "not run", "reason": "reduced/datadecide_bank2 has no runs"}
    if release_dir is None or not Path(release_dir).exists():
        return {"status": "not run", "reason": "no release reduced runs (--release-runs); run fetch_release.sh"}
    release = load_dir(release_dir)
    same_item_set(release)
    same_item_set(scored)
    first1 = next(iter(release.values()))[0]
    first2 = next(iter(scored.values()))[0]
    if first1.n_items != tasks66.RELEASE_TOTAL:
        raise SystemExit(f"release runs hold {first1.n_items} items, expected {tasks66.RELEASE_TOTAL}")
    mask1 = split_items(first1.trait, K, seed=MASTER_SEED)
    mask2 = split_by_group(first2.group, seed=MASTER_SEED)
    matched, missing, step_mismatch = datadecide_join(release, scored)
    out = {"status": "ok", "release_runs": len(release), "scored_runs": len(scored), "matched_runs": len(matched),
           "unmatched": missing, "step_mismatch": step_mismatch, "bank2_items": int(first2.n_items)}

    def cells_from(pairs, mode):
        cells = {}
        for (it1, m1), (it2, m2) in pairs:
            key = (str(m1["recipe"]).lower(), str(m1["size"]))
            if mode == "within1":
                A, B = trait_scores(it1, mask1), trait_scores(it1, ~mask1)
            elif mode == "within2":
                A, B = trait_scores(it2, mask2), trait_scores(it2, ~mask2)
            else:
                A, B = trait_scores(it1), trait_scores(it2)
            cells.setdefault(key, []).append((m2, A, B))
        # Cells with a different run count than three are dropped and reported, as build_population does.
        full = {k: v for k, v in cells.items() if len(v) == 3}
        dropped = [{"cell": list(k), "n_runs": len(v)} for k, v in cells.items() if len(v) != 3]
        return full, dropped

    pairs = list(matched.values())
    pops = {}
    for mode in ("within1", "cross", "within2"):
        cells, dropped = cells_from(pairs, mode)
        pop, labels = assemble(cells, cluster_of=lambda k: k[0], size_of=lambda k: k[1])
        pops[mode] = pop
        blk = full_block(pop, "datadecide", which_list=("all", "batch_free"))
        blk["dropped_cells"] = dropped
        blk["labels"] = labels
        out[{"within1": "within_bank1_reproduction", "cross": "cross_bank", "within2": "within_bank2"}[mode]] = blk
    # Paper reproduction check on the matched runs: only meaningful when all 125 cells are present.
    rep = out["within_bank1_reproduction"]["full"]
    out["reproduction"] = {
        "n_config": pops["within1"].N,
        "margin_lambda": rep[MARGIN]["all"]["lambda"], "accuracy_lambda": rep[ACCURACY]["all"]["lambda"],
        "paper": PAPER,
        "matches_paper": bool(pops["within1"].N == 125 and abs(rep[MARGIN]["all"]["lambda"] - PAPER["margin"]) < 0.005
                              and abs(rep[ACCURACY]["all"]["lambda"] - PAPER["accuracy"]) < 0.005),
        "note": "compared only when all 125 configurations are matched; the paper's 1.244 and 1.078 are on the full population"}
    out["within_minus_cross"] = {}
    out["within2_minus_cross"] = {}
    for name in (MARGIN, ACCURACY):
        e1 = estimate(pops["within1"], name, "all", check=False)
        ec = estimate(pops["cross"], name, "all", check=False)
        e2 = estimate(pops["within2"], name, "all", check=False)
        out["within_minus_cross"][name] = cluster_boot_logdiff(e1.T, e1.U, ec.T, ec.U, pops["cross"].recipe)
        out["within2_minus_cross"][name] = cluster_boot_logdiff(e2.T, e2.U, ec.T, ec.U, pops["cross"].recipe)
    # Per size band, cross-bank and within-bank-2, wild over the recipes inside the band.
    out["per_size"] = {}
    for mode in ("cross", "within2"):
        pop = pops[mode]
        for s, sname in enumerate(out["cross_bank"]["labels"]["sizes"]):
            idx = np.flatnonzero(pop.size == s)
            sub = pop.subset(idx)
            out["per_size"].setdefault(sname, {})[mode] = {
                name: all_intervals(sub, name, "all") for name in (MARGIN, ACCURACY)}

    zs = load_dir(reduced / "datadecide_bank2zs_1B")
    if zs:
        try:
            same_item_set(zs)
            m_zs, _, _ = datadecide_join(release, zs)
            cells, dropped = cells_from(list(m_zs.values()), "cross")
            if not cells:
                out["cross_format_1B"] = {"status": "not run", "reason": "no matched bank-1 x zero-shot cells with three runs"}
            else:
                pz, labels = assemble(cells, cluster_of=lambda k: k[0], size_of=lambda k: k[1])
                out["cross_format_1B"] = full_block(pz, "datadecide", which_list=("all", "batch_free"), matrix=False)
                out["cross_format_1B"]["dropped_cells"] = dropped
                # The 1B slice of within-bank-1 on the same cells, for the difference.
                keys1b = {tuple(c) for c in pz.config_ids}
                w1 = pops["within1"].subset(np.asarray([i for i, c in enumerate(pops["within1"].config_ids) if tuple(c) in keys1b]))
                e1, ez = estimate(w1, MARGIN, "all", check=False), estimate(pz, MARGIN, "all", check=False)
                out["cross_format_1B"]["within1_minus_crossformat_margin"] = cluster_boot_logdiff(e1.T, e1.U, ez.T, ez.U, pz.recipe)
        except Exception as e:  # a descriptive arm must not take R0, R2 and R3 down with it
            out["cross_format_1B"] = {"status": "error", "reason": f"{type(e).__name__}: {e}"}
    else:
        out["cross_format_1B"] = {"status": "not run", "reason": "reduced/datadecide_bank2zs_1B has no runs"}
    return out


def analysis_verify(reduced, release_dir, scores_dir, banks_cfg):
    """Bank-1 scores of the verify job against the release's per-item margins."""
    ver = load_dir(reduced / "verify")
    if not ver:
        return {"status": "not run", "reason": "reduced/verify has no runs"}
    if release_dir is None or not Path(release_dir).exists():
        return {"status": "not run", "reason": "no release reduced runs (--release-runs); run fetch_release.sh"}
    release = load_dir(release_dir)
    idx = {run_key_of(m): (it, m) for it, m in release.values()}
    thr = banks_cfg["verification"]
    out = {"status": "ok", "runs": {}, "thresholds": thr}
    all_pass = True
    for name, (it, meta) in ver.items():
        key = run_key_of(meta)
        if key not in idx:
            out["runs"][name] = {"error": "no release run with this recipe, size, seed and step"}
            all_pass = False
            continue
        rel = idx[key][0]
        pos = np.searchsorted(rel.item_id, it.item_id)
        ok = (pos < rel.item_id.size) & (rel.item_id[np.minimum(pos, rel.item_id.size - 1)] == it.item_id)
        if not ok.all():
            out["runs"][name] = {"error": f"{int((~ok).sum())} verify items are not release items"}
            all_pass = False
            continue
        d = np.abs(it.margin - rel.margin[pos])
        agree = float(np.mean(it.correct == rel.correct[pos]))
        per_task = {}
        for g in np.unique(it.group):
            sel = it.group == g
            per_task[tasks66.TASKS[int(g)]] = {"median_abs_diff": float(np.median(d[sel])),
                                               "p99_abs_diff": float(np.percentile(d[sel], 99)), "items": int(sel.sum())}
        row = {"items": int(d.size), "median_abs_diff_nats_per_byte": float(np.median(d)),
               "p99_abs_diff_nats_per_byte": float(np.percentile(d, 99)), "correct_agreement": agree,
               "mode": meta.get("mode"), "check_max_abs_diff_nats": meta.get("check_max_abs_diff_nats"),
               "per_task": per_task,
               "note": "release margins are stored as float16 in the reduced runs, so about 1e-3 of the difference is rounding"}
        row["pass"] = bool(row["median_abs_diff_nats_per_byte"] <= thr["pass_median_abs_diff_nats_per_byte"]
                           and row["p99_abs_diff_nats_per_byte"] <= thr["pass_p99_abs_diff_nats_per_byte"]
                           and row["correct_agreement"] >= thr["pass_correct_agreement"])
        all_pass &= row["pass"]
        out["runs"][name] = row
    out["pass"] = bool(all_pass and out["runs"])
    return out


# -- reading rules -------------------------------------------------------------


def verdicts(res):
    """The pre-specified rules from the README, applied mechanically."""
    v = {}
    ver = res.get("verify", {})
    v["V0_verification"] = {"pass": ver.get("pass"), "status": ver.get("status"),
                            "rule": "every verify run reproduces the release margins within the nats thresholds and agrees on correctness for at least the threshold fraction of items"}
    py = res.get("pythia", {})
    if py.get("status") == "ok":
        for name in (MARGIN, ACCURACY):
            row = py["within_bank1"]["full"][name]["all"]
            iv = primary(row, "pythia")
            v[f"R1_pythia_replicates_{name}"] = {
                "lambda": row["lambda"], "lo": iv["lo"], "hi": iv["hi"], "interval": iv.get("method"),
                "pass": bool(np.isfinite(iv["lo"]) and iv["lo"] > 1.0),
                "rule": "nine-seed PolyPythias at one matched step, jackknife lower endpoint above one"}
        if py.get("cross_bank", {}).get("summary"):
            for name in (MARGIN, ACCURACY):
                cross = py["cross_bank"]["full"][name]["all"]
                civ = primary(cross, "pythia")
                diff = py["within_minus_cross"][name]["full"]
                v[f"R2_pythia_identification_{name}"] = {
                    "cross_lambda": cross["lambda"], "cross_lo": civ["lo"], "cross_hi": civ["hi"],
                    "within_minus_cross_log_theta": diff.get("point_log_theta_diff"),
                    "diff_lo": diff.get("lo"), "diff_hi": diff.get("hi"),
                    "shared_item_explanation": ("not supported" if np.isfinite(civ["lo"]) and civ["lo"] > 1.0
                                                and "lo" in diff and diff["lo"] <= 0.0 <= diff["hi"]
                                                else "supported" if "lo" in diff and diff["lo"] > 0.0
                                                and np.isfinite(civ["hi"]) and civ["hi"] >= 1.0
                                                and not (np.isfinite(civ["lo"]) and civ["lo"] > 1.0)
                                                else "undecided"),
                    "rule": "cross-bank interval above one and the within-minus-cross difference including zero rejects the item explanation; a positive difference interval with a cross-bank interval covering one supports it"}
    dd_res = res.get("datadecide", {})
    if dd_res.get("status") == "ok":
        for name in (MARGIN, ACCURACY):
            w2 = dd_res["within_bank2"]["full"][name]["all"]
            iv = primary(w2, "datadecide")
            v[f"R3_datadecide_fresh_items_{name}"] = {
                "lambda": w2["lambda"], "lo": iv["lo"], "hi": iv["hi"], "interval": iv.get("method"),
                "pass": bool(np.isfinite(iv["lo"]) and iv["lo"] > 1.0),
                "rule": "within-bank-2 on the 375 runs, recipe-clustered wild lower endpoint above one"}
            cross = dd_res["cross_bank"]["full"][name]["all"]
            civ = primary(cross, "datadecide")
            diff = dd_res["within_minus_cross"][name]
            v[f"R2_datadecide_identification_{name}"] = {
                "cross_lambda": cross["lambda"], "cross_lo": civ["lo"], "cross_hi": civ["hi"],
                "within_minus_cross_log_theta": diff.get("point_log_theta_diff"),
                "diff_lo": diff.get("lo"), "diff_hi": diff.get("hi"),
                "shared_item_explanation": ("not supported" if np.isfinite(civ["lo"]) and civ["lo"] > 1.0
                                            and "lo" in diff and diff["lo"] <= 0.0 <= diff["hi"]
                                            else "supported" if "lo" in diff and diff["lo"] > 0.0
                                            and np.isfinite(civ["hi"]) and civ["hi"] >= 1.0
                                            and not (np.isfinite(civ["lo"]) and civ["lo"] > 1.0)
                                            else "undecided"),
                "rule": "as R2 for PolyPythias, with the recipe-clustered bootstrap"}
        v["R0_reproduction"] = dd_res["reproduction"]
    return v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reduced", default=str(HERE.parent / "reduced"))
    ap.add_argument("--scores", default=str(HERE.parent / "scores"))
    ap.add_argument("--release-runs", default=str(HERE.parent / "data" / "release_runs"),
                    help="the 375 reduced release runs from fetch_release.sh (bank 1 for DataDecide)")
    ap.add_argument("--out", default=str(HERE.parent / "results"))
    args = ap.parse_args()
    check_constants()
    reduced, out = Path(args.reduced), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    banks_cfg = json.loads((HERE.parent / "config" / "banks.json").read_text())
    res = {}
    for name, fn in (("verify", lambda: analysis_verify(reduced, args.release_runs, args.scores, banks_cfg)),
                     ("pythia", lambda: analysis_pythia(reduced, out)),
                     ("datadecide", lambda: analysis_datadecide(reduced, args.release_runs, out))):
        try:
            res[name] = fn()
        except Exception:
            res[name] = {"status": "error", "traceback": traceback.format_exc()[-4000:]}
        (out / f"{name}.json").write_text(json.dumps(res[name], indent=1, default=float))
        print(f"[analysis] {name}: {res[name].get('status')}", flush=True)
    v = verdicts(res)
    (out / "verdicts.json").write_text(json.dumps(v, indent=1, default=float))
    print(json.dumps(v, indent=1, default=float))


if __name__ == "__main__":
    main()
