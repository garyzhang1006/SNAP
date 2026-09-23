"""SNAP inference: wild bootstrap, seed jackknife, deletion sensitivity, diagnostics, reading rules.

Stub distilled from the paper (Section 2.3, 4.2, 4.3, Appendix D.2) and the
released code (src/seednoise/inference.py, compute2/analysis/estimates.py).
Only numpy is used; the t quantile for the jackknife is passed in or taken
from the small table below.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from snap_estimator import CrossHalf, pooled_ratio

N_BOOT = 4999
BOOT_SEED = 0
# 0.975 quantiles of Student t, used by the delete-one-seed jackknife.
T975 = {2: 4.302653, 8: 2.306004, 24: 2.063899}


@dataclass
class Interval:
    point: float
    lo: float   # nan when the squared-ratio endpoint is negative (heuristic H06)
    hi: float
    method: str


def _sqrt_or_nan(x: float) -> float:
    return float(np.sqrt(x)) if np.isfinite(x) and x >= 0 else float("nan")


# -------------------------------------------------------------- wild bootstrap
def wild_bootstrap_t(T: np.ndarray, U: np.ndarray, cluster: np.ndarray,
                     n_boot: int = N_BOOT, seed: int = BOOT_SEED, alpha: float = 0.05) -> Interval:
    """Wild cluster bootstrap-t on theta = sum T / sum U, Rademacher signs per cluster.

    The denominator stays fixed at the observed sum U; each draw recomputes theta*
    and its studentising SE from the bootstrap residuals (heuristic H05).
    """
    keys, inv = np.unique(cluster, return_inverse=True)
    G = keys.size
    if G < 2:
        raise ValueError(f"{G} cluster(s): a clustered interval needs at least two")
    sU = float(U.sum())
    th = float(T.sum()) / sU
    r = T - th * U
    se = float(np.sqrt(np.sum(np.bincount(inv, weights=r) ** 2))) / sU
    rng = np.random.default_rng(seed)
    v = rng.choice([-1.0, 1.0], size=(n_boot, G))[:, inv]
    Tb = th * U + v * r
    th_b = Tb.sum(axis=1) / sU
    rb = Tb - th_b[:, None] * U
    eb = np.stack([np.bincount(inv, weights=row, minlength=G) for row in rb])
    se_b = np.sqrt((eb ** 2).sum(axis=1)) / sU
    ok = se_b > 0
    tb = (th_b[ok] - th) / se_b[ok]
    if tb.size < max(100, int(0.9 * n_boot)):
        raise RuntimeError(f"only {tb.size} of {n_boot} draws gave a finite t; cluster structure too degenerate")
    q_hi, q_lo = np.percentile(tb, [100 * (1 - alpha / 2), 100 * alpha / 2])
    return Interval(_sqrt_or_nan(th), _sqrt_or_nan(th - q_hi * se), _sqrt_or_nan(th - q_lo * se),
                    f"wild cluster bootstrap-t (G={G}, B={n_boot})")


# -------------------------------------------------------------- seed jackknife
def seed_jackknife(yA: np.ndarray, yB: np.ndarray, stats_fn, t_crit: float | None = None) -> Interval:
    """Delete-one-seed jackknife with t(R-1), formed on theta and square-rooted (heuristic H10).

    yA, yB: (N, R, K) with run index r meaning the same seed in every configuration.
    stats_fn: callable (yA, yB) -> CrossHalf, normally snap_estimator.cross_half_statistics.
    """
    R = yA.shape[1]
    th = pooled_ratio(stats_fn(yA, yB)).theta
    loo = np.array([pooled_ratio(stats_fn(np.delete(yA, r, 1), np.delete(yB, r, 1))).theta for r in range(R)])
    se = float(np.sqrt((R - 1) / R * np.sum((loo - loo.mean()) ** 2)))
    c = T975[R - 1] if t_crit is None else t_crit
    return Interval(_sqrt_or_nan(th), _sqrt_or_nan(th - c * se), _sqrt_or_nan(th + c * se),
                    f"delete-one-seed jackknife t({R - 1})")


def jackknife_logdiff(yA1, yB1, yA2, yB2, stats_fn, t_crit: float | None = None) -> tuple[float, float, float]:
    """Jackknife interval for log theta_within - log theta_cross on the same runs (rule R2).

    Population 1 is within-bank-1 (two halves of bank 1); population 2 is
    cross-bank (A = bank 1, B = bank 2). Halve the result for log Lambda.
    """
    R = yA1.shape[1]

    def diff(a1, b1, a2, b2):
        t1, t2 = pooled_ratio(stats_fn(a1, b1)).theta, pooled_ratio(stats_fn(a2, b2)).theta
        if t1 <= 0 or t2 <= 0:
            raise ValueError("a ratio is not positive; the log difference is undefined")
        return float(np.log(t1) - np.log(t2))

    full = diff(yA1, yB1, yA2, yB2)
    loo = np.array([diff(*(np.delete(x, r, 1) for x in (yA1, yB1, yA2, yB2))) for r in range(R)])
    se = float(np.sqrt((R - 1) / R * np.sum((loo - loo.mean()) ** 2)))
    c = T975[R - 1] if t_crit is None else t_crit
    return full, full - c * se, full + c * se


# ------------------------------------------------------- deletion sensitivity
def deletion_sensitivity(ch: CrossHalf, recipe: np.ndarray, size: np.ndarray) -> dict[str, dict]:
    """Recompute the pooled ratio and wild interval after deleting each recipe and each size band.

    Benchmark deletions need recomputed T and U (snap_estimator.drop_traits) and are
    done by the caller; report the spread beside the interval (heuristic H08).
    """
    out: dict[str, dict] = {}
    for label, groups in (("recipe", recipe), ("size", size)):
        for g in np.unique(groups):
            keep = groups != g
            est = pooled_ratio(ch, keep)
            iv = wild_bootstrap_t(ch.T[keep], ch.U[keep], recipe[keep])
            out[f"{label}={g}"] = {"lambda": est.lam, "lo": iv.lo, "hi": iv.hi}
    return out


# ----------------------------------------------------------------- diagnostics
def trait_permutation(yA: np.ndarray, yB: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Independent run-label permutation per configuration and trait, applied to both halves (heuristic H11)."""
    N, R, K = yA.shape
    pA, pB = yA.copy(), yB.copy()
    for c in range(N):
        for j in range(K):
            p = rng.permutation(R)
            pA[c, :, j], pB[c, :, j] = yA[c, p, j], yB[c, p, j]
    return pA, pB


# --------------------------------------------------------------- reading rules
def registered_heldout_rule(iv: Interval) -> bool:
    """Registered test: pass iff the lower 95% wild recipe-cluster limit exceeds one."""
    return bool(np.isfinite(iv.lo) and iv.lo > 1.0)


def rule_r1(jack: Interval) -> bool:
    """R1 (PolyPythias bank 1): pass iff the delete-one-seed jackknife lower endpoint exceeds one."""
    return bool(np.isfinite(jack.lo) and jack.lo > 1.0)


def rule_r2(cross: Interval, diff_lo: float, diff_hi: float) -> str:
    """R2 (disjoint bank): verdict on the shared-item explanation, as fixed before scoring."""
    cross_above = np.isfinite(cross.lo) and cross.lo > 1.0
    if cross_above and diff_lo <= 0.0 <= diff_hi:
        return "not supported"
    if diff_lo > 0.0 and np.isfinite(cross.hi) and cross.hi >= 1.0 and not cross_above:
        return "supported"
    return "undecided"
