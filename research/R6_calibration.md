# R6 interval calibration (OBSERVED on Kaggle, 2026-09-15)

Kernels `snap-r6-calibration-a` and `-b`, `r6_calibration.py`, 2,000 replicates per cell, 4,999 bootstrap draws, seed 20260915, 545 s and similar. Each replicate simulates 125 configurations (25 recipes by 5 sizes) with 3 runs and 10 benchmarks, forms two halves as run effect plus independent item noise, and scores four intervals against the population Lambda implied by the cell's run covariance. Monte Carlo standard error of a coverage near 0.95 is 0.005.

| cell | population | truth | mean estimate | bias | wild | cluster t | config pct | recipe pct |
|---|---|---|---|---|---|---|---|---|
| a0 | null, margin-like noise 0.73 | 1.000 | 0.9995 | -0.0005 | 0.953 | 0.946 | 0.948 | 0.936 |
| a1 | null, accuracy-like noise 1.45 | 1.000 | 0.9893 | -0.0107 | 0.943 (3 invalid) | 0.941 | 0.943 | 0.857 (184 invalid) |
| a2 | margin-like rho 0.061 | 1.2446 | 1.2452 | +0.0006 | 0.947 | 0.943 | 0.938 | 0.928 |
| a3 | accuracy-like rho 0.018 | 1.0780 | 1.0705 | -0.0075 | 0.943 | 0.940 | 0.942 | 0.910 (52 invalid) |
| a4 | margin-like, BoolQ share 0.68 | 1.1519 | 1.1513 | -0.0007 | 0.938 | 0.935 | 0.936 | 0.925 |
| a5 | accuracy-like, BoolQ share 0.84 | 1.0308 | 1.0311 | +0.0002 | 0.954 | 0.950 | 0.955 | 0.940 |
| b0 | recipe-shared run effects 0.5 | 1.2446 | 1.2414 | -0.0032 | 0.944 | 0.940 | 0.872 | 0.931 |
| b1 | Student t, 4 df | 1.2446 | 1.2441 | -0.0005 | 0.946 (4 invalid) | 0.930 | 0.943 | 0.926 |
| b2 | one recipe with 6x variance | 1.2446 | 1.2436 | -0.0009 | 0.930 | 0.910 | 0.931 | 0.912 |
| b3 | cross-half error correlation 0.1, margin-like | 1.2446 | 1.2302 | -0.0144 | 0.928 (upper miss 0.066) | 0.925 | 0.929 | 0.918 |
| b4 | cross-half error correlation 0.1, accuracy-like | 1.0780 | 1.0624 | -0.0155 | 0.946 | 0.941 | 0.943 | 0.933 |
| b5 | rho 0.2 | 1.6733 | 1.6709 | -0.0024 | 0.947 | 0.943 | 0.943 | 0.928 |

Median widths in the margin-like cell a2: wild 0.243, cluster t 0.237, config 0.230, recipe percentile 0.225.

## Reading

The wild cluster bootstrap-t used in the draft holds coverage between 0.928 and 0.954 across all twelve cells, and its misses are two-sided except under cross-half error correlation, where the estimator is biased downward and the interval misses above. The cluster-robust t(24) tracks it within 0.02 and drops to 0.910 with one dominant recipe. The configuration percentile bootstrap fails under recipe-shared run effects (0.872), which is why recipes and not configurations are the cluster. The snap_compute recipe-percentile diagnostic under-covers in every cell (0.857 to 0.940) and returns undefined draws in the accuracy-like noise cells, so it is a diagnostic and not a replacement. The draft's accuracy interval that excludes 1 under the recipe percentile (1.0029 to 1.1550) and includes 1 under the wild bootstrap (0.9926 to 1.1567) is an instance of this under-coverage, and the wild interval is the one to report. The C05 cells in the plan (rho 0, 0.1, 0.3, df 4, cross-half correlation 0.3) are covered by a0 to a3, b1, b3 to b5 except the correlation 0.3 case, which is outside the range the BoolQ passage check makes plausible. Positive cross-half error correlation of 0.1 shrinks Lambda by about 0.015, which bounds the direction of any residual item dependence: dependence pulls the estimate toward 1, not away from it.
