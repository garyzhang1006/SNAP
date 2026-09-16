"""R6 addition: a cluster test-inversion interval for the pooled ratio, beside the shipped intervals.

Design fixed before running (2026-09-15, 18:15 EDT). The plan lists a ratio interval obtained by test
inversion as a candidate family when the denominator is uncertain, and R6 hasn't evaluated one.
For theta = Lambda squared, recipe cluster sums t_g = sum T_c and u_g = sum U_c, and z_g = t_g - theta u_g,
two statistics are inverted against the t(G-1) 97.5 percent point c.
  restricted  S(theta) = sum z_g / sqrt(sum z_g^2), the null-imposed form of the shipped cluster SE,
              which uses sum of squared cluster influences without a G/(G-1) factor.
  centred     S(theta) = sum z_g / sqrt(G/(G-1) sum (z_g - mean z)^2), a Fieller interval with the
              usual cluster-robust variance.
Each acceptance set {theta >= 0 : S(theta)^2 <= c^2} is a quadratic inequality, so it can be a bounded
interval, a ray, two rays, or all of [0, inf). Lambda endpoints are square roots of theta endpoints.
1. Observed data, 375 reduced runs, both phenotypes. Full battery, each size band, and each single
   benchmark removal, with 25 recipe clusters. Report the set type, endpoints, and the shipped
   cluster-t and wild bootstrap-t intervals (4,999 draws, seed 0) on the same T and U.
2. Coverage on the twelve R6 populations with the R6 generator copied verbatim, seed 20260915, rng
   [seed, cell index within its file, rep], 2,000 replicates, so each replicate reproduces the R6 data.
   The cluster-t interval is recomputed on each replicate and its coverage must equal the R6 summary.
   Record coverage, lower and upper misses, Monte Carlo SE, share of unbounded sets, and median width
   of bounded sets, and save every replicate's endpoints so the wild rows of R6 can be paired locally.
"""
import json, platform, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")


def find_all(name):
    return sorted(p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._"))


src = [p for p in find_all("pyproject.toml") if "seed-noise" in str(p)][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
sel = [p for p in find_all("*.npz") if "__seed-" in p.name]
assert len(sel) == 375, len(sel)
runs = W / "runs"; runs.mkdir(exist_ok=True)
for p in sel:
    shutil.copy(p, runs / p.name)

from scipy.stats import t as student_t  # noqa: E402
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import cluster_t_interval, wild_bootstrap_t  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402

CELLS_A = [{"name": "null_margin_noise", "rho": 0.0, "noise_sd": 0.73}, {"name": "null_accuracy_noise", "rho": 0.0, "noise_sd": 1.45}, {"name": "margin_like", "rho": 0.061, "noise_sd": 0.73}, {"name": "accuracy_like", "rho": 0.018, "noise_sd": 1.45}, {"name": "margin_like_boolq_trace", "rho": 0.061, "noise_sd": 0.73, "trait_scales": [4.373213921133976, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, {"name": "accuracy_like_boolq_trace", "rho": 0.018, "noise_sd": 1.45, "trait_scales": [6.873863542433759, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}]
CELLS_B = [{"name": "margin_like_recipe_shared", "rho": 0.061, "noise_sd": 0.73, "recipe_shared": 0.5}, {"name": "margin_like_heavy_tails", "rho": 0.061, "noise_sd": 0.73, "student_df": 4}, {"name": "margin_like_one_dominant_recipe", "rho": 0.061, "noise_sd": 0.73, "recipe_variance_scales": [6.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, {"name": "margin_like_cross_half_error_corr_0.1", "rho": 0.061, "noise_sd": 0.73, "cross_half_error_correlation": 0.1}, {"name": "accuracy_like_cross_half_error_corr_0.1", "rho": 0.018, "noise_sd": 1.45, "cross_half_error_correlation": 0.1}, {"name": "rho_0.2_margin_noise", "rho": 0.2, "noise_sd": 0.73}]


def invert(T, U, cluster, alpha=0.05, form="restricted"):
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    t = np.bincount(inv, weights=np.asarray(T, float), minlength=G)
    u = np.bincount(inv, weights=np.asarray(U, float), minlength=G)
    c2 = float(student_t.ppf(1 - alpha / 2, G - 1)) ** 2
    a, b = t.sum(), u.sum()
    Stt, Stu, Suu = float(t @ t), float(t @ u), float(u @ u)
    if form == "restricted":
        m, k = 0.0, c2
    else:
        m, k = c2 / (G - 1), c2 * G / (G - 1)
    # (1 + m) (a - theta b)^2 - k (Stt - 2 theta Stu + theta^2 Suu) <= 0
    A = (1 + m) * b * b - k * Suu
    B = -2 * (1 + m) * a * b + 2 * k * Stu
    C = (1 + m) * a * a - k * Stt
    f = lambda th: A * th * th + B * th + C  # noqa: E731
    disc = B * B - 4 * A * C
    if abs(A) < 1e-300:
        roots = [] if abs(B) < 1e-300 else [-C / B]
    elif disc < 0:
        roots = []
    else:
        s = np.sqrt(disc); roots = sorted([(-B - s) / (2 * A), (-B + s) / (2 * A)])
    # Acceptance set on [0, inf): evaluate f between breakpoints.
    pts = sorted([0.0] + [r for r in roots if r > 0])
    segs = []
    edges = pts + [np.inf]
    for lo, hi in zip(edges[:-1], edges[1:]):
        mid = lo + 1.0 if not np.isfinite(hi) else 0.5 * (lo + hi)
        if f(mid) <= 0:
            segs.append([lo, hi])
    merged = []
    for s_ in segs:
        if merged and abs(merged[-1][1] - s_[0]) < 1e-15:
            merged[-1][1] = s_[1]
        else:
            merged.append(list(s_))
    if not merged:
        kind = "empty"
    elif len(merged) == 1 and np.isfinite(merged[0][1]):
        kind = "bounded"
    elif len(merged) == 1 and merged[0][0] == 0.0 and not np.isfinite(merged[0][1]):
        kind = "all"
    elif len(merged) == 1:
        kind = "ray"
    else:
        kind = "two_pieces"
    lam = [[float(np.sqrt(lo)), float(np.sqrt(hi)) if np.isfinite(hi) else None] for lo, hi in merged]
    return {"kind": kind, "lambda_sets": lam}


def covers(res, truth):
    return any(lo <= truth and (hi is None or truth <= hi) for lo, hi in res["lambda_sets"])


def r6_simulate(cell, rng):
    k, r = cell.get("benchmarks", 10), cell.get("runs", 3)
    recipes, sizes = cell.get("recipes", 25), cell.get("sizes", 5)
    rho = cell.get("rho", 0.0)
    scale = np.asarray(cell.get("trait_scales", [1.0] * k), float)
    truth = ((1 - rho) * np.eye(k) + rho * np.ones((k, k))) * np.outer(scale, scale)
    n = recipes * sizes
    recipe = np.repeat(np.arange(recipes), sizes)
    shared = cell.get("recipe_shared", 0.0)
    latent = np.sqrt(1 - shared) * rng.multivariate_normal(np.zeros(k), truth, size=(n, r))
    if shared > 0:
        latent += np.sqrt(shared) * np.repeat(rng.multivariate_normal(np.zeros(k), truth, size=(recipes, r)), sizes, axis=0)
    df = cell.get("student_df")
    if df:
        latent *= np.sqrt((df - 2) / rng.chisquare(df, size=(n, r, 1)))
    rs = cell.get("recipe_variance_scales")
    if rs:
        latent *= np.sqrt(np.asarray(rs, float))[recipe][:, None, None]
    noise = np.asarray(cell.get("noise_sd", 1.0), float) * np.ones(k)
    ec = cell.get("cross_half_error_correlation", 0.0)
    ea = rng.normal(size=latent.shape) * noise
    eb = ec * ea + np.sqrt(1 - ec ** 2) * rng.normal(size=latent.shape) * noise
    a, b = latent + ea, latent + eb
    w = np.full(k, 1.0 / k)
    da = a - a.mean(1, keepdims=True)
    db = b - b.mean(1, keepdims=True)
    cross = np.einsum("crj,crk->cjk", da, db) / (r - 1)
    cov = (cross + cross.transpose(0, 2, 1)) / 2
    T = np.einsum("j,cjk,k->c", w, cov, w)
    U = np.einsum("j,cj->c", w * w, np.diagonal(cov, axis1=1, axis2=2))
    true_lambda = float(np.sqrt((w @ truth @ w) / ((w * w) @ np.diag(truth))))
    return T, U, recipe, true_lambda


pop, _ = build_population(runs, TRAITS, n_runs=3)
assert pop.N == 125 and pop.K == 10
report = {"design": __doc__, "observed": {}, "coverage": {}}


def drop_trait(p, j):
    keep = [i for i in range(p.K) if i != j]
    ph = {k: Phenotype(v.name, v.A[:, :, keep], v.B[:, :, keep]) for k, v in p.phenotypes.items()}
    return Population(ph, p.gainA, p.gainB, p.batch, p.recipe, p.size, [p.traits[i] for i in keep], p.config_ids,
                      None if p.n_items is None else np.asarray(p.n_items)[keep])


def describe(p, name):
    e = estimate(p, name, check=False)
    row = {"N": int(p.N), "clusters": int(p.n_clusters), "lambda": float(e.lambda_hat)}
    for form in ("restricted", "centred"):
        row[form] = invert(e.T, e.U, p.recipe, form=form)
    ct = cluster_t_interval(e.T, e.U, p.recipe); wb = wild_bootstrap_t(e.T, e.U, p.recipe, n_boot=4999, seed=0)
    row["cluster_t"] = [ct.lo, ct.hi]; row["wild"] = [wb.lo, wb.hi]
    return row


for name in ("margin", "accuracy"):
    obs = {"full": describe(pop, name)}
    for s in np.unique(pop.size):
        obs[f"size_{int(s)}"] = describe(pop.subset(np.flatnonzero(pop.size == s)), name)
    for j, tr in enumerate(pop.traits):
        obs[f"drop_{tr}"] = describe(drop_trait(pop, j), name)
    report["observed"][name] = obs
    print(f"[observed {name}] full {json.dumps(obs['full'])}", flush=True)
    for k, v in obs.items():
        print(f"   {k} lam {v['lambda']:.4f} restricted {v['restricted']} centred {v['centred']} wild {v['wild']}", flush=True)

SEED, REPS = 20260915, 2000
for tag, cells in (("a", CELLS_A), ("b", CELLS_B)):
    for ci, cell in enumerate(cells):
        t1 = time.time(); rows = []
        for rep in range(REPS):
            rng = np.random.default_rng([SEED, ci, rep])
            T, U, recipe, truth = r6_simulate(cell, rng)
            row = {"rep": rep, "truth": truth}
            ct = cluster_t_interval(T, U, recipe)
            ok = bool(np.isfinite(ct.lo) and np.isfinite(ct.hi))
            row["cluster_t_covered"] = bool(ok and ct.lo <= truth <= ct.hi)
            for form in ("restricted", "centred"):
                res = invert(T, U, recipe, form=form)
                lo_all = min((s[0] for s in res["lambda_sets"]), default=None)
                row[form] = {**res, "covered": covers(res, truth),
                             "lower_miss": bool(res["lambda_sets"] and lo_all > truth),
                             "upper_miss": bool(res["kind"] == "bounded" and res["lambda_sets"][0][1] < truth)}
            rows.append(row)
        s = {"cell": f"{tag}{ci}", "name": cell["name"], "true_lambda": rows[0]["truth"], "reps": REPS,
             "cluster_t_coverage_recomputed": float(np.mean([r["cluster_t_covered"] for r in rows]))}
        for form in ("restricted", "centred"):
            cov = float(np.mean([r[form]["covered"] for r in rows]))
            widths = [r[form]["lambda_sets"][0][1] - r[form]["lambda_sets"][0][0] for r in rows if r[form]["kind"] == "bounded"]
            s[form] = {"coverage": cov, "mc_se": float(np.sqrt(cov * (1 - cov) / REPS)),
                       "lower_miss": float(np.mean([r[form]["lower_miss"] for r in rows])),
                       "upper_miss": float(np.mean([r[form]["upper_miss"] for r in rows])),
                       "share_unbounded": float(np.mean([r[form]["kind"] != "bounded" for r in rows])),
                       "kinds": {k: int(sum(r[form]["kind"] == k for r in rows)) for k in ("bounded", "ray", "two_pieces", "all", "empty")},
                       "median_width_bounded": float(np.median(widths)) if widths else None}
        report["coverage"][f"{tag}{ci}"] = s
        (W / f"rows_{tag}{ci}.json").write_text(json.dumps(rows))
        print(f"[cell {tag}{ci} {cell['name']}] {time.time() - t1:.0f}s {json.dumps(s)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_fieller.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
