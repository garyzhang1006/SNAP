"""snap-r2-r1-50 (CPU only): interval file for the cross-format masked-matrix diagnostic.

Paper: cross-format off-diagonal covariance alone gives margin diagnostic 0.921
with interval 0.801 to 1.035; accuracy 0.965 (0.848, 1.063); without BoolQ
1.006 (0.972, 1.039) against an unrestricted nine-trait 1.786 (1.689, 1.877)
(appendices_bcd.tex:128-130). The diagnostic keeps the diagonal and the 54 of 90
ordered off-diagonal pairs whose traits differ in format (MC: ARC-C, ARC-E,
CSQA, MMLU, OBQA, SIQA; cloze: HellaSwag, PIQA, WinoGrande; yes/no: BoolQ).

Per configuration, with seednoise at the paper's commit:
  pA, pB   seednoise.estimator.half_projections(half scores, contrast_basis(R))
  T_mask   (1/K^2) mean over contrast directions of sum_{j,k in mask} pA_j pB_k,
           which equals seednoise's own T (estimator._T_from) when the mask is all ones;
           the script asserts that identity before masking
  U        seednoise.estimator.estimate(...).U, unchanged
  point    sqrt(sum T_mask / sum U)
  interval seednoise.inference.wild_bootstrap_t(T_mask, U, recipe, 4999 draws, seed 0), the
           paper's primary interval, with cluster_t_interval and config_bootstrap beside it
           because the source of the published interval isn't on file
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

t0 = time.time()
W = Path("/kaggle/working")
Path("/kaggle/tmp").mkdir(parents=True, exist_ok=True)
sn = [p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._")]
assert sn, "seednoise source (garyzhang11111/seed-noise-src) is not attached"
sn_copy = Path("/kaggle/tmp") / "seed-noise"
shutil.rmtree(sn_copy, ignore_errors=True)
shutil.copytree(sn[0].parent, sn_copy, ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(sn_copy)])
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.estimator import contrast_basis, estimate, half_projections  # noqa: E402
from seednoise.inference import cluster_t_interval, config_bootstrap, wild_bootstrap_t  # noqa: E402
from seednoise.population import ACCURACY, MARGIN  # noqa: E402

shipped = [p for p in Path("/kaggle/input").rglob("*.npz")
           if "seed-noise-reduced-runs" in str(p) and not p.name.startswith("._")]
assert len(shipped) == 375, f"expected 375 shipped reduced runs, found {len(shipped)}"
run_dir = Path("/kaggle/tmp") / "runs_shipped"
shutil.rmtree(run_dir, ignore_errors=True)
run_dir.mkdir(parents=True)
for p in shipped:
    shutil.copy(p, run_dir / p.name)
pop, info = build_population(run_dir, TRAITS, n_runs=3)
lam = estimate(pop, MARGIN).lambda_hat
assert abs(lam - 1.24395) < 5e-4, f"shipped runs give Lambda {lam}, not the paper's 1.24395"

FORMAT = {"arc_challenge": "mc", "arc_easy": "mc", "boolq": "yesno", "csqa": "mc", "hellaswag": "cloze",
          "mmlu": "mc", "openbookqa": "mc", "piqa": "cloze", "socialiqa": "mc", "winogrande": "cloze"}
Wb = contrast_basis(pop.R)


def run(name, traits, cross_only):
    idx = [TRAITS.index(t) for t in traits]
    K = len(idx)
    ph = pop.pheno(name)
    pA, pB = half_projections(ph.A[:, :, idx], Wb), half_projections(ph.B[:, :, idx], Wb)
    ones = np.ones((K, K))
    T_all = np.einsum("ndj,ndk,jk->nd", pA, pB, ones).mean(axis=1) / K ** 2
    U = np.einsum("ndj,ndj->nd", pA, pB).mean(axis=1) / K ** 2
    fmt = [FORMAT[t] for t in traits]
    mask = np.array([[1.0 if (j == k or (fmt[j] != fmt[k] if cross_only else True)) else 0.0 for k in range(K)] for j in range(K)])
    Tm = np.einsum("ndj,ndk,jk->nd", pA, pB, mask).mean(axis=1) / K ** 2
    out = {"traits": traits, "retained_ordered_offdiag_pairs": int(mask.sum() - K), "ordered_offdiag_pairs": K * (K - 1),
           "point": float(np.sqrt(Tm.sum() / U.sum())) if Tm.sum() / U.sum() >= 0 else float("nan"),
           "full_matrix_lambda_recomputed": float(np.sqrt(T_all.sum() / U.sum())),
           "sum_T_mask": float(Tm.sum()), "sum_U": float(U.sum())}
    out["wild"] = wild_bootstrap_t(Tm, U, pop.recipe, n_boot=4999, seed=0).as_row()
    try:
        out["cluster_t"] = cluster_t_interval(Tm, U, pop.recipe).as_row()
    except Exception as ex:  # noqa: BLE001
        out["cluster_t"] = {"error": f"{type(ex).__name__}: {ex}"}
    out["config_boot"] = config_bootstrap(Tm, U, n_boot=4999, seed=0).as_row()
    return out, T_all, U


# The identity check: the unmasked recomputation must equal seednoise's own T and U.
for name in (MARGIN, ACCURACY):
    _, T_all, U = run(name, TRAITS, cross_only=False)
    e = estimate(pop, name, check=False)
    assert np.allclose(T_all, e.T, rtol=1e-10, atol=1e-18) and np.allclose(U, e.U, rtol=1e-10, atol=1e-18), f"{name}: recomputed T/U differ from seednoise"

nob = [t for t in TRAITS if t != "boolq"]
res = {}
for name in (MARGIN, ACCURACY):
    res[name] = {"cross_format_all_ten": run(name, TRAITS, True)[0],
                 "cross_format_no_boolq": run(name, nob, True)[0],
                 "unrestricted_no_boolq": run(name, nob, False)[0]}
    for k, v in res[name].items():
        print(f"[{name} {k}] {v['point']:.4f} wild [{v['wild']['lo']:.4f}, {v['wild']['hi']:.4f}] "
              f"pairs {v['retained_ordered_offdiag_pairs']}/{v['ordered_offdiag_pairs']} full {v['full_matrix_lambda_recomputed']:.5f}", flush=True)

out = {"results": res, "formats": FORMAT, "identity_check": "unmasked T and U equal seednoise.estimator.estimate T and U (rtol 1e-10)",
       "paper_values": {"margin": [0.921, 0.801, 1.035], "accuracy": [0.965, 0.848, 1.063],
                        "margin_no_boolq_cross": [1.006, 0.972, 1.039], "margin_no_boolq_unrestricted": [1.786, 1.689, 1.877]},
       "wall_seconds": time.time() - t0}
(W / "r1_50_crossformat_boot.json").write_text(json.dumps(out, indent=1, default=float))
print(f"[done] {time.time() - t0:.0f}s", flush=True)
