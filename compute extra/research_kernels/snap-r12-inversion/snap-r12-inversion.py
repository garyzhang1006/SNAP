"""R12 addition: PolyPythias transport intervals under the cluster test-inversion construction.

Design fixed before running (2026-09-15, written 19:08 EDT). The manuscript reports configuration-bootstrap
intervals for the PolyPythias rescore, and the three-size accuracy interval has no defined lower endpoint.
With three or five configurations of nine runs, each configuration is its own cluster, so the centred and
restricted inversions of snap-r6-fieller use t(2) and t(4) critical values. Estimates must reproduce
snap-r12-analysis (margin 1.41372 and 1.26199, accuracy 2.28589 and 1.71085), and the configuration
bootstrap (4,999 draws, seed 0) is recomputed beside them. Per-configuration T and U are saved.
"""
import json, platform, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")
src = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")][0]
shutil.copytree(src.parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])

from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import config_bootstrap  # noqa: E402
from scipy.stats import t as student_t  # noqa: E402

DD = {"margin": 1.243949911719114, "accuracy": 1.0783733870898093}
arm2 = [p for p in Path("/kaggle/input").rglob("arm2__*.npz") if "runs-arm2" in str(p)]
assert len(arm2) == 45
report = {"design": __doc__, "transport": {}}
runs_dir = W / "arm2"; runs_dir.mkdir(exist_ok=True)
for p in arm2:
    shutil.copy(p, runs_dir / p.name)
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



for label, sizes in (("three_sizes", ["70m", "160m", "410m"]), ("five_sizes", ["14m", "31m", "70m", "160m", "410m"])):
    pop, info = build_population(runs_dir, TRAITS, n_runs=9, sizes=sizes)
    cell = {"N": pop.N, "R": pop.R}
    for name in ("margin", "accuracy"):
        e = estimate(pop, name, check=False)
        cl = np.arange(pop.N)
        row = {"Lambda": float(e.lambda_hat), "T": e.T.tolist(), "U": e.U.tolist(),
               "centred": invert(e.T, e.U, cl, form="centred"), "restricted": invert(e.T, e.U, cl, form="restricted")}
        iv = config_bootstrap(e.T, e.U, n_boot=4999, seed=0)
        row["config"] = [float(iv.lo), float(iv.hi)]
        cell[name] = row
    report["transport"][label] = cell
    print(f"[{label}] {json.dumps(cell)}", flush=True)
report["wall_seconds"] = time.time() - t0
(W / "r12_inversion.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True); shutil.rmtree(runs_dir, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
