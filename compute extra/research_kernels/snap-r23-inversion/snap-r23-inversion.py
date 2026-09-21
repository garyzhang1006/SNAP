"""R23 addition: checkpoint-sensitivity intervals under the cluster test-inversion construction.

Design fixed before running (2026-09-15, written 18:58 EDT). The abstract states that the accuracy interval
excludes one at the previous shared step on 123 configurations. snap-r6-fieller showed that test inversion
can move a margin lower endpoint by 0.048, so this kernel recomputes the four estimates of snap-r23 with
seednoise on the same 123 configurations and reports the wild bootstrap-t (4,999 draws, seed 0), the
cluster-robust t(24), and the centred and restricted inversion intervals of snap-r6-fieller at both steps.
The selected-step and previous-step estimates must match snap-r23 (margin 1.233 and 1.192, accuracy 1.082
and 1.130) to three decimals, and the kernel records the comparison either way.
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
from scipy.stats import t as student_t  # noqa: E402
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import estimate  # noqa: E402
from seednoise.inference import cluster_t_interval, wild_bootstrap_t  # noqa: E402

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
print(f"[configs] kept {len(kept)}", flush=True)
report = {"design": __doc__, "kept": len(kept), "reference": {"margin": [1.233, 1.192], "accuracy": [1.082, 1.130]}, "steps": {}}
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



for label, files in (("selected", {k: v for k, v in sel_keys.items() if k[:2] in set(kept)}),
                     ("previous", {k: v for k, v in prev_keys.items() if k[:2] in set(kept)})):
    d = W / f"runs_{label}"; d.mkdir(exist_ok=True)
    for p in files.values():
        shutil.copy(p, d / p.name)
    pop, _ = build_population(d, TRAITS, n_runs=3)
    assert pop.N == len(kept), (label, pop.N)
    report["steps"][label] = {}
    for name in ("margin", "accuracy"):
        e = estimate(pop, name, check=False)
        wb = wild_bootstrap_t(e.T, e.U, pop.recipe, n_boot=4999, seed=0)
        ct = cluster_t_interval(e.T, e.U, pop.recipe)
        row = {"lambda": float(e.lambda_hat), "clusters": int(pop.n_clusters), "wild": [wb.lo, wb.hi], "cluster_t": [ct.lo, ct.hi],
               "centred": invert(e.T, e.U, pop.recipe, form="centred"), "restricted": invert(e.T, e.U, pop.recipe, form="restricted")}
        report["steps"][label][name] = row
        print(f"[{label} {name}] {json.dumps(row)}", flush=True)
report["wall_seconds"] = time.time() - t0
(W / "r23_inversion.json").write_text(json.dumps(report, indent=1))
shutil.rmtree(W / "seed-noise", ignore_errors=True)
for label in ("selected", "previous"):
    shutil.rmtree(W / f"runs_{label}", ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
