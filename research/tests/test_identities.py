"""Mathematical checks of the estimator, run against closed forms rather than against saved output.

These are the checks that would catch a sign error or a lost divisor in a reimplementation, and they
need only numpy. A failure here means the estimator's algebra is wrong, not that a number moved.
"""
import numpy as np

K, RUNS, RECIPES, SIZES = 10, 3, 25, 5
W = np.full(K, 1.0 / K)


def theta_from_truth(truth, w=W):
    """The population ratio the estimator targets, which is the full form over the diagonal one."""
    return float(w @ truth @ w) / float((w * w) @ np.diag(truth))


def test_compound_symmetry_closed_form():
    """With flat weights, a compound-symmetric truth gives Lambda squared of 1 plus (k-1) rho."""
    for rho in (0.0, 0.018, 0.061, 0.25):
        truth = (1 - rho) * np.eye(K) + rho * np.ones((K, K))
        assert abs(theta_from_truth(truth) - (1 + (K - 1) * rho)) < 1e-12, rho


def test_independent_truth_gives_one():
    """A diagonal truth carries no dependence, so the ratio is exactly one at any scale."""
    truth = np.diag(np.linspace(0.5, 2.0, K))
    assert abs(theta_from_truth(truth) - 1.0) < 1e-12


def test_cross_half_estimator_is_unbiased_for_the_latent_covariance():
    """Averaging the cross-half product over many draws recovers the latent covariance, not the noise."""
    rho, noise, reps = 0.061, 0.73, 4000
    truth = (1 - rho) * np.eye(K) + rho * np.ones((K, K))
    rng = np.random.default_rng(12345)
    acc = np.zeros((K, K))
    for _ in range(reps):
        latent = rng.multivariate_normal(np.zeros(K), truth, size=RUNS)
        a = latent + rng.normal(size=latent.shape) * noise
        b = latent + rng.normal(size=latent.shape) * noise
        da, db = a - a.mean(0, keepdims=True), b - b.mean(0, keepdims=True)
        cross = da.T @ db / (RUNS - 1)
        acc += (cross + cross.T) / 2
    est = acc / reps
    # The item noise is independent across halves, so it cancels in expectation and only the latent
    # covariance survives, including on the diagonal where a within-half estimator would not.
    err = float(np.abs(est - truth).max())
    assert err < 0.08, err


def test_band_index_tiles_and_recipe_index_repeats():
    """Configuration c is recipe c // sizes and band c % sizes, which the shared-effect cells rely on."""
    n = RECIPES * SIZES
    band = np.arange(n) % SIZES
    recipe = np.arange(n) // SIZES
    assert len(np.unique(band)) == SIZES and len(np.unique(recipe)) == RECIPES
    for r in range(RECIPES):
        assert sorted(band[recipe == r].tolist()) == list(range(SIZES))


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
