"""SNAP cross-half estimator: half split, centring, cross-half statistics, pooled ratio.

Stub distilled from the paper (Section 2, Algorithm 1, Appendix A and D) and the
released package (src/seednoise/estimator.py, halves.py). Item scoring and
reduction of released tarballs happen upstream; this module starts from
per-item scores already reduced to arrays.

Shapes: N configurations, R replicate runs, K benchmarks (traits), I items.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

MASTER_SEED = 20260101  # frozen half split (paper, reproducibility statement)


# ---------------------------------------------------------------- item scoring
def per_byte_margin(gold_loglik: np.ndarray, gold_bytes: np.ndarray,
                    alt_loglik: np.ndarray, alt_bytes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Item scoring output to margin and accuracy (Equation 1).

    gold_loglik, gold_bytes: (I,) summed log-likelihood and byte length of the gold answer.
    alt_loglik, alt_bytes: (I, V) for the V alternatives (pad missing with -inf / 1).
    Returns (m, a): per-byte margin and correctness, with a zero margin counted incorrect.
    """
    m = gold_loglik / gold_bytes - np.max(alt_loglik / alt_bytes, axis=1)
    return m, (m > 0).astype(float)


# ------------------------------------------------------------------ half split
def half_split(trait: np.ndarray, K: int, seed: int = MASTER_SEED) -> np.ndarray:
    """Balanced random half split within each trait; returns the boolean mask of half A.

    Split within trait so both halves cover every benchmark; reuse the same mask
    for every run of an arm (heuristic H03).
    """
    rng = np.random.default_rng(seed)
    mask = np.zeros(trait.shape[0], dtype=bool)
    for j in range(K):
        idx = np.flatnonzero(trait == j)
        if idx.size < 2:
            raise ValueError(f"trait {j} has {idx.size} items and can't be split into two halves")
        mask[rng.permutation(idx)[: idx.size // 2]] = True
    return mask


def half_split_grouped(trait: np.ndarray, group: np.ndarray, K: int, seed: int = MASTER_SEED) -> np.ndarray:
    """Passage-aware half split: every item sharing a passage/story lands in one half (heuristic H04).

    Half sizes then differ by a few items, so the equal-half derivation holds only approximately.
    """
    rng = np.random.default_rng(seed)
    mask = np.zeros(trait.shape[0], dtype=bool)
    for j in range(K):
        idx = np.flatnonzero(trait == j)
        groups = np.unique(group[idx])
        chosen = set(rng.permutation(groups)[: groups.size // 2].tolist())
        mask[idx] = np.isin(group[idx], list(chosen))
    return mask


def half_scores(item_scores: np.ndarray, trait: np.ndarray, mask_a: np.ndarray, K: int,
                subject: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Trait scores on each half for one run: (K,), (K,).

    item_scores: (I,) margins or accuracy bits. MMLU is macro-averaged over its
    subjects when `subject` is given (subject id per item, -1 elsewhere).
    """
    out = []
    for half in (mask_a, ~mask_a):
        y = np.empty(K)
        for j in range(K):
            sel = half & (trait == j)
            if subject is not None and np.any(subject[sel] >= 0):
                subs = np.unique(subject[sel])
                y[j] = np.mean([item_scores[sel & (subject == s)].mean() for s in subs])
            else:
                y[j] = item_scores[sel].mean()
        out.append(y)
    return out[0], out[1]


# -------------------------------------------------------------------- centring
def contrast_basis(R: int) -> np.ndarray:
    """Orthonormal basis of mean-zero run contrasts, shape (R-1, R) (heuristic H02).

    Each row annihilates the all-ones vector, so projecting raw or centred scores
    gives the same result; W.T @ W equals the centring matrix I - J/R.
    """
    H = np.eye(R) - np.ones((R, R)) / R
    u, _, _ = np.linalg.svd(H)
    W = u[:, : R - 1].T
    assert np.allclose(W @ np.ones(R), 0.0), "centring basis rows must sum to zero"
    return W


def centring(y: np.ndarray, W: np.ndarray) -> np.ndarray:
    """Centring by projection. y: (N, R, K) half scores -> (N, R-1, K) contrasts.

    Cross products of contrasts sum to the centred cross products d^A d^B over runs.
    For the auxiliary-run contrast (heuristic H12) pass W with a single row that
    contrasts the two auxiliary runs.
    """
    return np.einsum("qr,nrk->nqk", W, y)


# -------------------------------------------------------- cross-half statistics
@dataclass
class CrossHalf:
    """Per-configuration cross-half statistics T_c and U_c (Equation 4)."""
    T: np.ndarray  # (N,)  estimates K^-2 1' Sigma_E,c 1
    U: np.ndarray  # (N,)  estimates K^-2 tr Sigma_E,c
    K: int
    R: int


def cross_half_statistics(yA: np.ndarray, yB: np.ndarray, W: np.ndarray | None = None) -> CrossHalf:
    """T_c = (R-1)^-1 sum_r g^A g^B,  U_c = (K^2 (R-1))^-1 sum_{j,r} d^A d^B.

    yA, yB: (N, R, K) half scores for the same runs and trait order. For R2's
    cross-bank estimate pass bank-1 trait scores as yA and bank-2 scores as yB.
    """
    N, R, K = yA.shape
    W = contrast_basis(R) if W is None else W
    dA, dB = centring(yA, W), centring(yB, W)
    df = W.shape[0]  # R-1 for the full basis, 1 for a single contrast
    gA, gB = dA.mean(axis=2), dB.mean(axis=2)
    T = (gA * gB).sum(axis=1) / df
    U = (dA * dB).sum(axis=(1, 2)) / (K ** 2 * df)
    return CrossHalf(T=T, U=U, K=K, R=R)


def sigma_e_matrix(yA: np.ndarray, yB: np.ndarray) -> np.ndarray:
    """Symmetrised run-covariance estimate (Appendix A.3), (K, K); need not be PSD."""
    N, R, K = yA.shape
    W = contrast_basis(R)
    dA, dB = centring(yA, W), centring(yB, W)
    S = np.einsum("nqj,nqk->jk", dA, dB)
    return (S + S.T) / (2 * N * (R - 1))


# ---------------------------------------------------------------- pooled ratio
@dataclass
class PooledRatio:
    theta: float      # Lambda^2
    lam: float        # Lambda-hat, nan when theta < 0
    k_eff: float      # K / Lambda^2
    rbar_e: float     # (Lambda^2 - 1) / (K - 1)


def pooled_ratio(ch: CrossHalf, keep: np.ndarray | None = None) -> PooledRatio:
    """Pool sums across configurations before the ratio (heuristic H01).

    keep: optional boolean mask over configurations, used by deletion sensitivity
    and by the subset estimator Lambda_S = sqrt(sum_S T / sum_S U).
    """
    T, U = (ch.T, ch.U) if keep is None else (ch.T[keep], ch.U[keep])
    sU = float(U.sum())
    if sU <= 0:
        raise ValueError(f"pooled denominator {sU:.3e} is not positive; Lambda is undefined for this subset")
    theta = float(T.sum()) / sU
    lam = float(np.sqrt(theta)) if theta >= 0 else float("nan")
    k_eff = ch.K / theta if theta > 0 else float("nan")
    rbar = (theta - 1.0) / (ch.K - 1) if ch.K > 1 else float("nan")
    return PooledRatio(theta=theta, lam=lam, k_eff=k_eff, rbar_e=rbar)


def drop_traits(yA: np.ndarray, yB: np.ndarray, drop: list[int]) -> tuple[np.ndarray, np.ndarray]:
    """Deletion sensitivity helper: remove benchmarks, keeping equal weights on the rest."""
    keep = [j for j in range(yA.shape[2]) if j not in set(drop)]
    return yA[:, :, keep], yB[:, :, keep]
