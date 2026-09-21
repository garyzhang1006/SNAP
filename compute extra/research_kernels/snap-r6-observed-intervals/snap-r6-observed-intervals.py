"""What every interval construction says about the observed population, rather than about simulations.

Design fixed before running (2026-09-15, written 22:45 EDT). The coverage work compares six interval
constructions on simulated populations. A reader wants to know what they say about the data in hand, so
this run applies all of them to the 125 shipped configurations, for margins and for accuracy, on the full
ten-benchmark battery and on the nine-benchmark battery that drops BoolQ. Wild intervals use 9,999 draws
rather than the shipped 4,999, and each one is repeated over twenty bootstrap seeds so the Monte Carlo
spread of the endpoints is visible beside the endpoints themselves. Nothing here is a coverage claim. It
reports how much the reported interval would move under each construction, which is the quantity a
reader needs when a construction that we didn't pre-register turns out to cover better.
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

from scipy.stats import t as student_t  # noqa: E402
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import cluster_t_interval, wild_bootstrap_t  # noqa: E402
from seednoise.population import Phenotype, Population  # noqa: E402

def _wild(T, U, cluster, n_boot=4999, alpha=0.05, seed=0, weights="rademacher", cr3=False):
    """Wild cluster bootstrap-t, copied from the shipped estimator with two options added."""
    T, U = np.asarray(T, float), np.asarray(U, float)
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    sU = float(np.sum(U))
    th = float(np.sum(T)) / sU
    r = T - th * U
    if cr3:
        u_g = np.bincount(inv, weights=U, minlength=G)
        h = np.clip(u_g / sU, 0.0, 0.99)
        r = r / (1.0 - h)[inv]
    e = np.bincount(inv, weights=r, minlength=G)
    se = float(np.sqrt(np.sum(e ** 2))) / sU
    rng = np.random.default_rng(seed)
    if weights == "rademacher":
        v = rng.choice([-1.0, 1.0], size=(n_boot, G))
    elif weights == "mammen":
        p5 = np.sqrt(5.0)
        lo, hi = -(p5 - 1) / 2, (p5 + 1) / 2
        v = np.where(rng.random((n_boot, G)) < (p5 + 1) / (2 * p5), lo, hi)
    else:
        w6 = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])
        v = w6[rng.integers(0, 6, size=(n_boot, G))]
    vb = v[:, inv]
    Tb = th * U + vb * r
    th_b = Tb.sum(axis=1) / sU
    rb = Tb - th_b[:, None] * U
    eb = np.zeros((n_boot, G))
    np.add.at(eb, (np.arange(n_boot)[:, None], np.broadcast_to(inv, vb.shape)), rb)
    se_b = np.sqrt((eb ** 2).sum(axis=1)) / sU
    ok = se_b > 0
    tb = ((th_b[ok] - th) / se_b[ok])
    tb = tb[np.isfinite(tb)]
    if tb.size < max(100, int(0.9 * n_boot)):
        return float("nan"), float("nan")
    lo_q, hi_q = np.percentile(tb, [100 * (1 - alpha / 2), 100 * (alpha / 2)])
    lo, hi = th - lo_q * se, th - hi_q * se
    return (float(np.sqrt(lo)) if lo >= 0 else float("nan"),
            float(np.sqrt(hi)) if hi >= 0 else float("nan"))


def _cluster_t_cr1(T, U, cluster, alpha=0.05):
    keys, inv = np.unique(np.asarray(cluster), return_inverse=True)
    G = keys.size
    sU = float(np.sum(U))
    th = float(np.sum(T)) / sU
    e = np.bincount(inv, weights=np.asarray(T, float) - th * np.asarray(U, float), minlength=G)
    se = float(np.sqrt(G / (G - 1.0) * np.sum(e ** 2))) / sU
    crit = float(student_t.ppf(1 - alpha / 2, G - 1))
    lo, hi = th - crit * se, th + crit * se
    return (float(np.sqrt(lo)) if lo >= 0 else float("nan"),
            float(np.sqrt(hi)) if hi >= 0 else float("nan"))



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


N_BOOT, N_SEED = 9999, 20
BOOLQ = [j for j, t in enumerate(TR) if "boolq" in t.lower()]
assert len(BOOLQ) == 1, BOOLQ
FULL = list(range(len(TR)))
DROP = [j for j in FULL if j not in BOOLQ]
report = {"design": __doc__, "traits": TR, "n_boot": N_BOOT, "n_seed": N_SEED, "batteries": {}}
for label, idx in (("full", FULL), ("without_boolq", DROP)):
    for name in ("margin", "accuracy"):
        t1 = time.time()
        sub = restrict(pop, name, idx)
        est = estimate(sub, name, check=False)
        T, U, recipe = est.T, est.U, sub.recipe
        cell = {"lambda_hat": float(est.lambda_hat), "n_traits": len(idx)}
        shipped = wild_bootstrap_t(T, U, recipe, n_boot=4999, seed=0)
        cell["shipped"] = [float(shipped.lo), float(shipped.hi)]
        for method, kw in (("wild_rademacher", {}), ("wild_mammen", {"weights": "mammen"}),
                           ("wild_webb", {"weights": "webb"}), ("wild_cr3", {"cr3": True})):
            ends = np.array([_wild(T, U, recipe, n_boot=N_BOOT, seed=s, **kw) for s in range(N_SEED)])
            cell[method] = {"lo": float(np.mean(ends[:, 0])), "hi": float(np.mean(ends[:, 1])),
                            "lo_sd": float(np.std(ends[:, 0], ddof=1)), "hi_sd": float(np.std(ends[:, 1], ddof=1)),
                            "width": float(np.mean(ends[:, 1] - ends[:, 0])),
                            "excludes_one": bool(np.mean(ends[:, 0]) > 1.0 or np.mean(ends[:, 1]) < 1.0)}
        lo, hi = _cluster_t_cr1(T, U, recipe)
        cell["cluster_t_cr1"] = {"lo": float(lo), "hi": float(hi), "width": float(hi - lo),
                                 "excludes_one": bool(lo > 1.0 or hi < 1.0)}
        ct = cluster_t_interval(T, U, recipe)
        cell["cluster_t"] = {"lo": float(ct.lo), "hi": float(ct.hi), "width": float(ct.hi - ct.lo),
                             "excludes_one": bool(ct.lo > 1.0 or ct.hi < 1.0)}
        for form in ("centred", "restricted"):
            res = invert(T, U, recipe, form=form)
            cell[f"inversion_{form}"] = {"kind": res["kind"], "lambda_sets": res["lambda_sets"],
                                         "excludes_one": not any(a <= 1.0 and (b is None or 1.0 <= b)
                                                                 for a, b in res["lambda_sets"])}
        report["batteries"][f"{label}/{name}"] = cell
        print(f"[{label}/{name}] {time.time() - t1:.0f}s {json.dumps(cell)}", flush=True)

report["wall_seconds"] = time.time() - t0
(W / "r6_observed_intervals.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
