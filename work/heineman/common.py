import numpy as np


def lam(S):
    """Inflation of the equal-weight average's SD over its independence SD: sqrt(1'S1 / tr S)."""
    tr = np.trace(S)
    tot = S.sum()
    if tr <= 0 or tot <= 0:
        return float("nan")
    return float(np.sqrt(tot / tr))


def within_cov(block, detrend):
    """Pooled covariance of checkpoint-to-checkpoint deviations inside one run.

    block has shape (W, K): W consecutive checkpoints by K tasks. Demeaning removes the
    run's level; detrending also removes a straight-line drift over the window, so what is
    left is the step-to-step wiggle Heineman et al. call noise.
    """
    W = block.shape[0]
    t = np.arange(W, dtype=float)
    if detrend:
        A = np.column_stack([np.ones(W), t])
        coef, *_ = np.linalg.lstsq(A, block, rcond=None)
        resid = block - A @ coef
        dof = W - 2
    else:
        resid = block - block.mean(0)
        dof = W - 1
    return resid.T @ resid, dof


def pct(a, q):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    return float(np.percentile(a, q)) if a.size else float("nan")
