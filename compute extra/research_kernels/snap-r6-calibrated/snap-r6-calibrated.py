"""R6 iterated-bootstrap calibration of the shipped interval on the observed data.

Design fixed before running (2026-09-15, written 22:20 EDT). Two independent lines of evidence now say
the shipped wild interval undercovers. The twelve-population simulation puts its coverage between 0.933
and 0.953 at 10,000 replicates, and ten repeats of the seed-label permutation on these data put it
between 0.915 and 0.942 with a mean of 0.931. A reader is entitled to ask what the reported interval
becomes once that shortfall is corrected on the data itself rather than through a construction picked
in simulation. This run answers that with Beran prepivoting, which is the standard iterated bootstrap
calibration and needs no new modelling assumption. For each of 1,999 outer wild resamples it computes
the studentised statistic against the observed point, runs a second wild bootstrap of 1,999 draws
inside that resample, and records the fraction of inner statistics at or below the outer one. Those
prepivoted values have a uniform distribution when the studentised statistic is correctly calibrated,
so their empirical 2.5th and 97.5th percentiles give the levels the outer quantiles should be read at.
The calibrated interval reports those levels, the nominal levels they replace, and the implied coverage
of the shipped interval, for the full battery and for the battery without BoolQ on both scales. A
calibrated interval that still excludes one leaves the paper's margin conclusion standing under its own
measured miscalibration, and one that includes one is a finding the paper has to report.
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
runs_dir = W / "runs"; runs_dir.mkdir(exist_ok=True)
for p in sel:
    shutil.copy(p, runs_dir / p.name)

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import wild_bootstrap_t  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402


TR = list(TRAITS)
pop, info = build_population(runs_dir, TRAITS, n_runs=3)
print(f"[base] {json.dumps(info)}", flush=True)


def restrict(p, name, idx):
    ph = p.pheno(name)
    m = np.asarray(idx, int)
    sub = Phenotype(name, ph.A[:, :, m], ph.B[:, :, m])
    n_items = None if p.n_items is None else np.asarray(p.n_items)[m]
    return Population({name: sub}, p.gainA, p.gainB, p.batch, p.recipe, p.size,
                      [p.traits[j] for j in m], p.config_ids, n_items)


B1, B2, SEED = 1999, 1999, 20260926
BOOLQ = [j for j, t in enumerate(TR) if "boolq" in t.lower()]
assert len(BOOLQ) == 1, BOOLQ
FULL = list(range(len(TR)))
DROP = [j for j in FULL if j not in BOOLQ]


def _draw(rng, n, G):
    return rng.choice([-1.0, 1.0], size=(n, G))


def prepivot(T, U, cluster, b1=B1, b2=B2, seed=SEED):
    """Beran prepivoting of the wild cluster bootstrap-t, returning the prepivoted values."""
    T, U = np.asarray(T, float), np.asarray(U, float)
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G, sU = keys.size, float(np.sum(U))
    th = float(np.sum(T)) / sU
    r = T - th * U
    e = np.bincount(inv, weights=r, minlength=G)
    se = float(np.sqrt(np.sum(e ** 2))) / sU
    rng = np.random.default_rng(seed)
    v = _draw(rng, b1, G)[:, inv]
    Tb = th * U + v * r
    th_b = Tb.sum(axis=1) / sU
    rb = Tb - th_b[:, None] * U
    eb = np.zeros((b1, G))
    np.add.at(eb, (np.arange(b1)[:, None], np.broadcast_to(inv, v.shape)), rb)
    se_b = np.sqrt((eb ** 2).sum(axis=1)) / sU
    t_b = np.where(se_b > 0, (th_b - th) / np.where(se_b > 0, se_b, 1.0), np.nan)
    u = np.full(b1, np.nan)
    for b in range(b1):
        if not np.isfinite(t_b[b]):
            continue
        # Second-level resample drawn from resample b, whose own centre is th_b[b].
        w = _draw(rng, b2, G)[:, inv]
        Tc = th_b[b] * U + w * rb[b]
        th_c = Tc.sum(axis=1) / sU
        rc = Tc - th_c[:, None] * U
        ec = np.zeros((b2, G))
        np.add.at(ec, (np.arange(b2)[:, None], np.broadcast_to(inv, w.shape)), rc)
        se_c = np.sqrt((ec ** 2).sum(axis=1)) / sU
        ok = se_c > 0
        t_c = (th_c[ok] - th_b[b]) / se_c[ok]
        t_c = t_c[np.isfinite(t_c)]
        if t_c.size >= max(100, int(0.9 * b2)):
            u[b] = float(np.mean(t_c <= t_b[b]))
    return th, se, t_b, u


def lam(x):
    return float(np.sqrt(x)) if x >= 0 else None


report = {"design": __doc__, "traits": TR, "b1": B1, "b2": B2, "seed": SEED, "batteries": {}}
for label, idx in (("full", FULL), ("without_boolq", DROP)):
    for name in ("margin", "accuracy"):
        t1 = time.time()
        sub = restrict(pop, name, idx)
        est = estimate(sub, name, check=False)
        T, U, recipe = est.T, est.U, sub.recipe
        th, se, t_b, u = prepivot(T, U, recipe)
        tv = t_b[np.isfinite(t_b)]
        uv = u[np.isfinite(u)]
        q_lo, q_hi = (float(np.percentile(uv, 2.5)), float(np.percentile(uv, 97.5))) if uv.size else (np.nan, np.nan)
        # Uncalibrated equal-tailed bootstrap-t at the nominal 0.025 and 0.975 levels.
        n_lo, n_hi = np.percentile(tv, [97.5, 2.5])
        plain = [lam(th - n_lo * se), lam(th - n_hi * se)]
        c_lo, c_hi = np.percentile(tv, [100 * q_hi, 100 * q_lo])
        calib = [lam(th - c_lo * se), lam(th - c_hi * se)]
        shipped = wild_bootstrap_t(T, U, recipe, n_boot=4999, seed=0)
        cell = {"lambda_hat": float(est.lambda_hat), "n_traits": len(idx),
                "shipped": [float(shipped.lo), float(shipped.hi)],
                "uncalibrated": plain, "calibrated": calib,
                "nominal_levels": [0.025, 0.975], "calibrated_levels": [q_lo, q_hi],
                "implied_coverage_of_nominal": float(np.mean((uv > 0.025) & (uv < 0.975))) if uv.size else None,
                "n_prepivot_ok": int(uv.size), "n_outer_ok": int(tv.size),
                "width_plain": None if None in plain else plain[1] - plain[0],
                "width_calibrated": None if None in calib else calib[1] - calib[0],
                "calibrated_excludes_one": None if None in calib else bool(calib[0] > 1.0 or calib[1] < 1.0)}
        report["batteries"][f"{label}/{name}"] = cell
        print(f"[{label}/{name}] {time.time() - t1:.0f}s {json.dumps(cell)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_calibrated.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
