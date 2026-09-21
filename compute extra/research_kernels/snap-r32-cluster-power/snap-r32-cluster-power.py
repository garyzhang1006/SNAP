"""R32: band-aware clustering, matched-step power, and an MMLU subject-level split control.

Three blocks named by the fourth blind meta-review, all exploratory and post hoc.

Block A, clustering. From the shipped per-configuration cross-half moments
(snap-r2-grouped C01 original split, margin and accuracy, full battery and
without BoolQ), the recipe-clustered wild bootstrap-t is reproduced, then the
same T_c and U_c get a size-band clustering (G=5) with Rademacher and with Webb
six-point weights, on theta and on log theta, a cluster-robust t(4), and a
two-way recipe-by-band cluster-robust t whose variance is the recipe variance
plus the band variance minus the configuration-level variance, with the
degrees of freedom set to the smaller cluster count minus one.

Block B, matched-step power. The 33 configurations that share a final step
(snap-r21-matched-step per_config, matched flag) are re-estimated with their
24 recipe clusters to reproduce 1.082 with interval 0.121 to 1.530 on margins,
and a simulation with that exact design (33 configurations, the same recipe
labels, three runs, ten benchmarks) reports how often the wild recipe interval
excludes one when the truth is the margin population (rho 0.061, noise 0.73,
Lambda 1.2446) and the accuracy-like population (rho 0.018, noise 1.45), so a
reader can tell whether the subset refutes the effect or can't see it.

Block C, MMLU subject control. With MMLU's subject strata removed from a copy
of the manifest, so that MMLU scores as a plain item mean, the original item
split is re-estimated, then 40 splits that place whole subjects on one side
and 40 unstratified item re-splits are run, and the subject-level and
item-level distributions of the inflation factor and the off-diagonal
contribution are reported side by side. An item effect shared within a
subject and repeated across halves would separate the two distributions.

Outputs: /kaggle/working/cluster_power.json plus the SNAP job directories.
"""
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")
SEED = 20260922
DRAWS = 4999
POWER_REPS = 2000
POWER_DRAWS = 999
SUBJECT_SPLITS = 200
BANDS = ["150M", "300M", "530M", "750M", "1B"]
POPULATIONS = {"margin_like": {"rho": 0.061, "noise_sd": 0.73}, "accuracy_like": {"rho": 0.018, "noise_sd": 1.45},
               "null_margin_noise": {"rho": 0.0, "noise_sd": 0.73}, "null_accuracy_noise": {"rho": 0.0, "noise_sd": 1.45}}


def find(name, contains=""):
    hits = [p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._") and contains in str(p)]
    if not hits:
        sys.exit(f"{name} with {contains!r} not found under /kaggle/input")
    return sorted(hits)[0]


shutil.copytree(find("run_two_gpus.py").parent, W / "snap_compute", ignore=shutil.ignore_patterns("__pycache__", "._*"))
PKG = W / "snap_compute"
shutil.copytree(find("pyproject.toml").parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
for f in ("snap_adapter.py",):
    hits = [p for p in Path("/kaggle/input").rglob(f) if not p.name.startswith("._")]
    assert len({hashlib.sha256(h.read_bytes()).hexdigest() for h in hits}) == 1, (f, [str(h) for h in hits])
    shutil.copy(hits[0], W / f)
from seednoise.inference import _theta, cluster_se, cluster_t_interval, wild_bootstrap_t  # noqa: E402


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, (np.integer, np.bool_)):
        return o.item()
    return o


def dump(summary):
    (W / "cluster_power.json").write_text(json.dumps(clean(summary), indent=1))


def sqrt_or_nan(x):
    return float(np.sqrt(x)) if np.isfinite(x) and x >= 0 else float("nan")


def as_row(iv):
    return {"lo": iv.lo, "hi": iv.hi, "se": iv.se, "method": iv.method}


WEBB = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])


def wild_t(T, U, cluster, weights="rademacher", log=False, n_boot=DRAWS, alpha=0.05, seed=SEED):
    """Wild cluster bootstrap-t on theta (or log theta) with Rademacher or Webb six-point cluster weights.

    Same imposed-null residual perturbation as seednoise.inference.wild_bootstrap_t; the
    Webb variant is the standard small-G repair for G near five, where Rademacher
    weights give only 2^G distinct draws.
    """
    T, U = np.asarray(T, float), np.asarray(U, float)
    if T.shape != U.shape or T.ndim != 1:
        raise ValueError(f"T {T.shape} and U {U.shape} must be matching 1-D arrays")
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    if G < 2:
        raise ValueError(f"{G} cluster(s): a clustered interval needs at least two")
    if n_boot < 199:
        raise ValueError(f"n_boot={n_boot}: too few draws for two-sided 95% tail quantiles")
    th = _theta(T, U)
    sU = float(np.sum(U))
    r = T - th * U
    se = cluster_se(T, U, cluster)
    rng = np.random.default_rng(seed)
    v = rng.choice([-1.0, 1.0], size=(n_boot, G)) if weights == "rademacher" else rng.choice(WEBB, size=(n_boot, G))
    vb = v[:, inv]
    Tb = th * U + vb * r
    th_b = Tb.sum(axis=1) / sU
    rb = Tb - th_b[:, None] * U
    eb = np.zeros((n_boot, G))
    np.add.at(eb, (np.arange(n_boot)[:, None], np.broadcast_to(inv, vb.shape)), rb)
    se_b = np.sqrt((eb ** 2).sum(axis=1)) / sU
    if log:
        ok = (se_b > 0) & (th_b > 0)
        tb = (np.log(th_b[ok]) - np.log(th)) / (se_b[ok] / th_b[ok])
    else:
        ok = se_b > 0
        tb = (th_b[ok] - th) / se_b[ok]
    tb = tb[np.isfinite(tb)]
    if tb.size < max(100, int(0.9 * n_boot)):
        raise RuntimeError(f"only {tb.size} of {n_boot} bootstrap draws produced a finite t")
    distinct = int(np.unique(np.round(tb, 12)).size)
    lo_q, hi_q = np.percentile(tb, [100 * (1 - alpha / 2), 100 * (alpha / 2)])
    if log:
        se_log = se / th
        lo, hi = th * np.exp(-lo_q * se_log), th * np.exp(-hi_q * se_log)
    else:
        lo, hi = th - lo_q * se, th - hi_q * se
    out = {"point": sqrt_or_nan(th), "lo": sqrt_or_nan(lo), "hi": sqrt_or_nan(hi), "se": float(se / (2 * np.sqrt(th))) if th > 0 else None,
           "finite_draws": int(tb.size), "distinct_t_values": distinct,
           "method": f"wild cluster bootstrap-t on {'log ' if log else ''}theta, {weights} weights (G={G})"}
    if log:
        out["nonpositive_theta_draws"] = int(np.sum(th_b <= 0))
    if weights == "rademacher" and G <= 6:
        out["note"] = f"{2 ** G} sign vectors only; the smallest two-sided randomisation p-value is {2 / 2 ** G:.4f}, so this interval is a foil for the Webb variant"
    return out


def twoway_cluster_t(T, U, recipe, band, alpha=0.05):
    """Two-way (recipe, band) cluster-robust t on theta: V = V_recipe + V_band - V_config, df = min(G) - 1."""
    from scipy import stats
    T, U = np.asarray(T, float), np.asarray(U, float)
    th = _theta(T, U)
    vr, vb_, vc = cluster_se(T, U, recipe) ** 2, cluster_se(T, U, band) ** 2, cluster_se(T, U, np.arange(T.size)) ** 2
    v = vr + vb_ - vc
    G = min(np.unique(recipe).size, np.unique(band).size)
    q = stats.t.ppf(1 - alpha / 2, G - 1)
    out = {"variance_recipe": float(vr), "variance_band": float(vb_), "variance_config": float(vc), "variance_twoway": float(v), "df": G - 1}
    if v <= 0:
        # Cameron, Gelbach and Miller's two-way variance can go negative; the fallback is the larger one-way variance.
        se = float(np.sqrt(max(vr, vb_)))
        out.update({"lo": sqrt_or_nan(th - q * se), "hi": sqrt_or_nan(th + q * se), "se": se, "branch": "fallback_max_oneway",
                    "method": f"two-way (recipe, band) variance not positive, interval from max(V_recipe, V_band) with t({G - 1})"})
        return out
    se = float(np.sqrt(v))
    out.update({"lo": sqrt_or_nan(th - q * se), "hi": sqrt_or_nan(th + q * se), "se": se, "branch": "twoway",
                "method": f"two-way (recipe, band) cluster-robust t({G - 1}) on theta"})
    return out


summary = {"seed": SEED, "draws": DRAWS, "blocks": {}}

# Block A: clustering alternatives on the shipped moments.
block_a = {}
for phen in ("margin", "accuracy"):
    for ds, job in (("full", "original"), ("noboolq", "noboolq_original")):
        meta = json.load(open(find("scores.json", f"datasets/{ds}/{phen}/")))
        cov = np.load(find("moments.npz", f"C01_{phen}_{job}/"))["covariance"]
        w = np.asarray(meta["weights"], float)
        T = np.einsum("j,cjk,k->c", w, cov, w)
        U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
        recipe = np.array([c["recipe"] for c in meta["configs"]])
        band = np.array([c["size"] for c in meta["configs"]])
        assert T.size == 125 and set(band) == set(BANDS), (T.size, set(band))
        cell = {"lambda": sqrt_or_nan(_theta(T, U)),
                "recipe_wild": as_row(wild_bootstrap_t(T, U, recipe, n_boot=DRAWS, seed=0)),          # seed 0 reproduces the shipped interval
                "recipe_wild_new_seed": as_row(wild_bootstrap_t(T, U, recipe, n_boot=DRAWS, seed=SEED)),
                "recipe_cluster_t": as_row(cluster_t_interval(T, U, recipe)),
                "band_cluster_t": as_row(cluster_t_interval(T, U, band)),
                "band_wild_rademacher": wild_t(T, U, band),
                "band_wild_webb": wild_t(T, U, band, weights="webb"),
                "band_wild_webb_log": wild_t(T, U, band, weights="webb", log=True),
                "recipe_wild_webb": wild_t(T, U, recipe, weights="webb"),
                "twoway_cluster_t": twoway_cluster_t(T, U, recipe, band),
                "cluster_se": {"recipe": cluster_se(T, U, recipe), "band": cluster_se(T, U, band), "config": cluster_se(T, U, np.arange(T.size))}}
        block_a[f"{phen}/{ds}"] = cell
        print(f"[A {phen}/{ds}] lambda {cell['lambda']:.4f} recipe_wild {cell['recipe_wild']['lo']:.4f}-{cell['recipe_wild']['hi']:.4f} "
              f"band_webb {cell['band_wild_webb']['lo']}-{cell['band_wild_webb']['hi']} twoway {cell['twoway_cluster_t']['lo']}-{cell['twoway_cluster_t']['hi']}", flush=True)
expected = {"margin": (1.1429001912272698, 1.3376841038790925), "accuracy": (0.992604456794931, 1.1566521851337639)}
for phen, (lo, hi) in expected.items():
    got = block_a[f"{phen}/full"]["recipe_wild"]
    assert abs(got["lo"] - lo) < 1e-6 and abs(got["hi"] - hi) < 1e-6, (phen, got, lo, hi)
block_a["reproduction"] = "recipe wild intervals match snap-r2-grouped to 1e-6 on both scales"
summary["blocks"]["A_clustering"] = block_a
dump(summary)

# Block B: the matched-step subset and its power.
r21 = json.load(open(find("r21_matched_step.json")))
block_b = {}
for phen in ("margin", "accuracy"):
    rows = [p for p in r21["per_config"][phen] if p["matched"]]
    assert len(rows) == 33, len(rows)
    T = np.array([p["T"] for p in rows]); U = np.array([p["U"] for p in rows])
    recipe = np.array([p["id"].split("__")[0] for p in rows]); band = np.array([p["size"] for p in rows])
    n_recipes = np.unique(recipe).size
    est = {"n": 33, "recipes": int(n_recipes), "by_size": {s: int((band == s).sum()) for s in BANDS},
           "lambda": sqrt_or_nan(_theta(T, U)), "recipe_wild": as_row(wild_bootstrap_t(T, U, recipe, n_boot=DRAWS, seed=0)),
           "recipe_wild_other_seeds": {str(s): as_row(wild_bootstrap_t(T, U, recipe, n_boot=DRAWS, seed=s)) for s in (1, 2, 3, SEED)},
           "recipe_wild_webb": wild_t(T, U, recipe, weights="webb"),
           "cluster_sizes": {str(k): int(v) for k, v in zip(*np.unique(np.unique(recipe, return_counts=True)[1], return_counts=True))},
           "note": "the lower endpoint sits where theta_lo is near zero, so its square root moves by tenths across bootstrap seeds; seed 0 is the shipped draw"}
    print(f"[B {phen}] matched-step lambda {est['lambda']:.4f} wild {est['recipe_wild']['lo']}-{est['recipe_wild']['hi']}", flush=True)
    block_b[phen] = est
assert abs(block_b["margin"]["lambda"] - 1.082) < 1e-3 and abs(block_b["margin"]["recipe_wild"]["lo"] - 0.121) < 1e-3 \
    and abs(block_b["margin"]["recipe_wild"]["hi"] - 1.530) < 1e-3, block_b["margin"]
block_b["reproduction"] = "margin matched-step estimate and wild interval match appendices_bcd tab:truncation to 1e-3"

# Power at the matched design: same 33 configurations and recipe labels, simulated latent run effects plus item noise.
recipe = np.array([p["id"].split("__")[0] for p in r21["per_config"]["margin"] if p["matched"]])
k, r = 10, 3
rng = np.random.default_rng(SEED)
block_b["power"] = {}
for name, pop in POPULATIONS.items():
    truth = (1 - pop["rho"]) * np.eye(k) + pop["rho"] * np.ones((k, k))
    w = np.full(k, 1.0 / k)
    true_lambda = float(np.sqrt((w @ truth @ w) / ((w * w) @ np.diag(truth))))
    excl, widths, lows, undefined, raised, point = 0, [], [], 0, 0, []
    for rep in range(POWER_REPS):
        latent = rng.multivariate_normal(np.zeros(k), truth, size=(33, r))
        a = latent + rng.normal(size=latent.shape) * pop["noise_sd"]
        b = latent + rng.normal(size=latent.shape) * pop["noise_sd"]
        da, db = a - a.mean(1, keepdims=True), b - b.mean(1, keepdims=True)
        cross = np.einsum("crj,crk->cjk", da, db) / (r - 1)
        cov = (cross + cross.transpose(0, 2, 1)) / 2
        T = np.einsum("j,cjk,k->c", w, cov, w)
        U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
        point.append(sqrt_or_nan(_theta(T, U)))
        try:
            iv = wild_bootstrap_t(T, U, recipe, n_boot=POWER_DRAWS, seed=SEED + rep)
        except (RuntimeError, ValueError):
            raised += 1
            continue
        if not (np.isfinite(iv.lo) and np.isfinite(iv.hi)):
            undefined += 1
            continue
        excl += iv.lo > 1.0
        widths.append(iv.hi - iv.lo); lows.append(iv.lo)
    defined = POWER_REPS - undefined - raised
    block_b["power"][name] = {"true_lambda": true_lambda, "rho": pop["rho"], "noise_sd": pop["noise_sd"], "reps": POWER_REPS, "draws": POWER_DRAWS,
                              "undefined_intervals": undefined, "raised": raised,
                              "exclusion_rate_lower_above_one": excl / POWER_REPS,
                              "exclusion_rate_conditional_on_defined": excl / defined if defined else None,
                              "monte_carlo_se": float(np.sqrt(max(excl / POWER_REPS * (1 - excl / POWER_REPS), 1e-9) / POWER_REPS)),
                              "median_width": float(np.median(widths)) if widths else None,
                              "median_lower": float(np.median(lows)) if lows else None,
                              "point_estimate_mean": float(np.nanmean(point)), "point_estimate_sd": float(np.nanstd(point, ddof=1)),
                              "note": ("design is the 33 matched configurations with their 24 recipe clusters, 18 of them singletons; no recipe-shared or "
                                       "band-shared component, so the simulated variance is smaller than the real one and exclusion rates are upper "
                                       "bounds on power; an undefined lower endpoint counts as a non-exclusion; the null cells calibrate the size")}
    print(f"[B power {name}] true {true_lambda:.4f} exclusion {block_b['power'][name]['exclusion_rate_lower_above_one']} "
          f"undefined {undefined} median width {block_b['power'][name]['median_width']}", flush=True)
summary["blocks"]["B_matched_step"] = block_b
dump(summary)

# Block C: MMLU subject-level splits against unstratified item re-splits.
runs = W / "runs"; runs.mkdir(exist_ok=True)
n = 0
for p in sorted(Path("/kaggle/input").rglob("*.npz")):
    if p.name.startswith("._") or "moments" in p.name or "scores" in p.name:
        continue
    shutil.copy(p, runs / p.name); n += 1
assert n == 375, n
data = W / "datasets"
subprocess.check_call([sys.executable, str(W / "snap_adapter.py"), "--runs", str(runs), "--out", str(data / "plain")])
print(f"[adapter] done at {time.time() - t0:.0f}s", flush=True)


def run_job(job, cfg, out, quiet=False):
    cfg_path = W / "configs" / f"{out}.json"; cfg_path.parent.mkdir(exist_ok=True)
    cfg_path.write_text(json.dumps({**cfg, "template_only": False}, indent=2))
    subprocess.check_call([sys.executable, str(PKG / "runs" / f"{job}.py"), "--config", str(cfg_path), "--out", str(W / "SNAP" / out)],
                          stdout=subprocess.DEVNULL if quiet else None)
    return json.load(open(W / "SNAP" / out / "result.json"))


def write_manifest(meta, dst):
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w") as fh:
        json.dump(meta, fh)


def offdiag(result, weights):
    cov = np.asarray(result["covariance"], float)
    w = np.asarray(weights, float)
    return float(w @ cov @ w - (w * w) @ np.diag(cov))


block_c = {}
for phen in ("margin", "accuracy"):
    src = str(data / "plain" / phen / "scores.json")
    meta = json.load(open(src))
    meta["arrays"] = str(data / "plain" / phen / meta["arrays"])
    mm = [b for b in meta["benchmarks"] if b["name"] == "mmlu"][0]
    subjects = np.array(mm["strata"])
    labels = sorted(set(subjects.tolist()))
    assert len(labels) == 57, len(labels)
    for b in meta["benchmarks"]:
        b.pop("strata", None); b.pop("stratum_weights", None)
    base_path = str(data / "nostrata" / phen / "scores.json")
    write_manifest(meta, base_path)
    base = run_job("C01", {"seed": SEED, "dataset": base_path, "split_mode": "original", "bootstrap_draws": DRAWS}, f"C01_{phen}_nostrata_original")
    cell = {"stratified_original_lambda": block_a[f"{phen}/full"]["lambda"],
            "nostrata_original": {"lambda": base["lambda"], "offdiag": offdiag(base, meta["weights"]),
                                  "recipe_percentile_diagnostic": base["uncertainty"].get("interval"),
                                  "diagnostic_method": base["uncertainty"].get("method"), "invalid_fraction": base["uncertainty"].get("invalid_fraction")},
            "subject_splits": [], "item_resplits": []}
    rng = np.random.default_rng([SEED, phen == "accuracy"])
    n_items = len(mm["item_ids"])
    for k in range(SUBJECT_SPLITS):
        m = json.loads(json.dumps(meta))
        mmb = [b for b in m["benchmarks"] if b["name"] == "mmlu"][0]
        order = rng.permutation(len(labels))
        left = {labels[i] for i in order[:len(labels) // 2]}
        mmb["original_half"] = [0 if s in left else 1 for s in subjects.tolist()]
        pth = str(data / "subject" / phen / f"scores_{k}.json"); write_manifest(m, pth)
        rs = run_job("C01", {"seed": SEED, "dataset": pth, "split_mode": "original", "bootstrap_draws": 0}, f"subj_{phen}_{k}", quiet=True)
        cell["subject_splits"].append({"lambda": rs["lambda"], "offdiag": offdiag(rs, meta["weights"]), "side0_items": int(sum(1 - x for x in mmb["original_half"]))})
        shutil.rmtree(W / "SNAP" / f"subj_{phen}_{k}", ignore_errors=True); Path(pth).unlink(missing_ok=True)
        m = json.loads(json.dumps(meta))
        mmb = [b for b in m["benchmarks"] if b["name"] == "mmlu"][0]
        half = np.ones(n_items, int); half[rng.permutation(n_items)[:cell["subject_splits"][-1]["side0_items"]]] = 0
        mmb["original_half"] = half.tolist()
        pth = str(data / "item" / phen / f"scores_{k}.json"); write_manifest(m, pth)
        ri = run_job("C01", {"seed": SEED, "dataset": pth, "split_mode": "original", "bootstrap_draws": 0}, f"item_{phen}_{k}", quiet=True)
        cell["item_resplits"].append({"lambda": ri["lambda"], "offdiag": offdiag(ri, meta["weights"])})
        shutil.rmtree(W / "SNAP" / f"item_{phen}_{k}", ignore_errors=True); Path(pth).unlink(missing_ok=True)
    from scipy import stats
    for key in ("lambda", "offdiag"):
        s = np.array([x[key] for x in cell["subject_splits"] if x[key] is not None], float)
        i = np.array([x[key] for x in cell["item_resplits"] if x[key] is not None], float)
        pooled = np.sqrt((s.var(ddof=1) + i.var(ddof=1)) / 2) if s.size > 1 and i.size > 1 else np.nan
        ratio = float(s.var(ddof=1) / i.var(ddof=1)) if s.size > 1 and i.size > 1 and i.var(ddof=1) > 0 else None
        cell[f"{key}_comparison"] = {"subject_mean": float(s.mean()), "subject_sd": float(s.std(ddof=1)), "item_mean": float(i.mean()),
                                     "item_sd": float(i.std(ddof=1)),
                                     "variance_ratio_subject_over_item": ratio,
                                     "variance_ratio_upper_tail_p": float(stats.f.sf(ratio, s.size - 1, i.size - 1)) if ratio is not None else None,
                                     "difference_in_pooled_sd": float((s.mean() - i.mean()) / pooled) if np.isfinite(pooled) and pooled > 0 else None,
                                     "n_subject": int(s.size), "n_item": int(i.size),
                                     "reading": "a within-subject shared item effect widens the subject arm, so the variance ratio is primary and the mean shift secondary"}
    cell["note"] = ("MMLU scored as a plain item mean in every row of this block, so the nostrata baseline differs from the "
                    "stratum-weighted published estimate; in both arms only MMLU's halves change and the nine other benchmarks "
                    "keep their frozen original halves; each item re-split matches the side-0 item count of the subject split "
                    "drawn just before it, so the two arms differ in whether whole subjects move together and in the cluster-sampling "
                    "variance that unequal subject sizes add on their own; MMLU carries under one percent of the margin trace, so both "
                    "arms sit close to the baseline and any separation speaks to MMLU's internal item structure, not to the battery-level factor")
    block_c[phen] = cell
    print(f"[C {phen}] nostrata lambda {base['lambda']:.4f} subject {cell['lambda_comparison']} item {cell['offdiag_comparison']}", flush=True)
summary["blocks"]["C_mmlu_subject"] = block_c
dump(summary)
shutil.rmtree(runs, ignore_errors=True); shutil.rmtree(W / "seed-noise", ignore_errors=True)
# The plain archives stay on disk because every saved manifest in this block points at them by absolute path.
print(f"[done] {time.time() - t0:.0f}s", flush=True)
