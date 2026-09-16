import unittest

import numpy as np

from snap.core import cluster_bootstrap, folds_for, moments, rng_for, split_halves, summarize


class MomentTests(unittest.TestCase):
    def test_hand_calculation_and_shared_shift(self):
        a = np.array([[[0., 0.], [2., 4.]]])
        expected = np.array([[[2., 4.], [4., 8.]]])
        np.testing.assert_allclose(moments(a, a), expected)
        np.testing.assert_allclose(moments(a + 123, a - 78), expected)
        self.assertAlmostEqual(summarize(expected, [.5, .5])["lambda_squared"], 1.8)

    def test_symmetry_and_run_reordering(self):
        rng = rng_for(0, "test")
        a, b = rng.normal(size=(2, 7, 3, 4))
        np.testing.assert_allclose(moments(a, b), moments(b, a))
        np.testing.assert_allclose(moments(a[:, ::-1], b[:, ::-1]), moments(a, b))

    def test_negative_moments_not_clipped(self):
        result = summarize(-np.eye(2), [.5, .5])
        self.assertIsNone(result["lambda"])
        self.assertEqual(result["negative_diagonal_count"], 2)
        self.assertLess(result["T"], 0)

    def test_diagonal_reference(self):
        self.assertEqual(summarize(np.diag([2., 7.]), [.5, .5])["lambda"], 1)

    def test_cluster_bootstrap_preserves_identical_clusters(self):
        cov = np.tile(np.eye(2), (6, 1, 1))
        result = cluster_bootstrap(cov, ["a", "a", "b", "b", "c", "c"], [.5, .5], 50, 1)
        self.assertEqual(result["interval"], [1., 1.])

    def test_undefined_draws_do_not_become_ci(self):
        cov = np.tile(-np.eye(2), (3, 1, 1))
        result = cluster_bootstrap(cov, ["a", "b", "c"], [.5, .5], 20, 1)
        self.assertIsNone(result["interval"])
        self.assertEqual(result["invalid_fraction"], 1)

    def test_group_integrity_and_reproducibility(self):
        meta = {"benchmarks": [{"name": "task", "item_ids": list("abcdef"),
                                "group_ids": ["p", "p", "q", "q", "r", "r"]}]}
        data = [np.arange(12).reshape(1, 2, 6)]
        a, b, assignment = split_halves(meta, data, 1, mode="group")
        h = assignment[0]["half"]
        self.assertEqual(h[0], h[1])
        self.assertEqual(h[2], h[3])
        self.assertEqual(h[4], h[5])
        np.testing.assert_equal(a, split_halves(meta, data, 1, mode="group")[0])
        self.assertEqual(a.shape, (1, 2, 1))

    def test_cross_stratum_group_rejected(self):
        meta = {"benchmarks": [{"name": "task", "item_ids": list("abcd"),
                  "group_ids": ["p", "q", "p", "q"], "strata": ["x", "x", "y", "y"]}]}
        with self.assertRaisesRegex(ValueError, "crosses strata"):
            split_halves(meta, [np.zeros((1, 2, 4))], mode="group")

    def test_recipe_folds_do_not_leak_sizes(self):
        configs = [{"recipe": r} for r in ["a", "a", "b", "b", "c", "c"]]
        folds = folds_for(configs, 3, 99)
        self.assertEqual(folds[0], folds[1])
        self.assertEqual(len(set(folds)), 3)

    def test_monte_carlo_unbiased_moment_under_declared_model(self):
        rng = rng_for(93, "unbiased")
        truth = np.array([[1., .4], [.4, 2.]])
        latent = rng.multivariate_normal([0, 0], truth, size=(30000, 3))
        a = latent + rng.normal(size=latent.shape)
        b = latent + rng.normal(size=latent.shape)
        np.testing.assert_allclose(moments(a, b).mean(0), truth, atol=.03)


if __name__ == "__main__":
    unittest.main()
