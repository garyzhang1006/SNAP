# R8 and R9 results (OBSERVED on Kaggle, 2026-09-15)

Kernel `snap-r8-prediction` v2 (pushed 10:50 EDT, complete 10:53 EDT, 116 s CPU). Inputs: snap-compute-src v5 and seed-noise-reduced-runs, adapter on the original split (seed 20260914), C01 with 0 bootstrap draws, C07 with 5 recipe folds and 2,000 paired recipe-resampling draws, `r9_pairs.py`, C08. Outputs under `research/outputs/snap-r8-prediction/SNAP/`. The C01 point estimates match the frozen split (1.243950 margin, 1.078373 accuracy).

## C07 operational prediction comparison

C07 predicts each held-out configuration's raw aggregate variance moment T_c from a covariance matrix fitted on the other four recipe folds, with four methods: diagonal (independence), full, rank_one_offdiagonal, and shrink_50. It differs from the draft's Table 2 experiment, which gives every model the held-out marginal seed standard deviations and scores log aggregate standard deviation. The job labels itself "not the original conditional log-SD prediction experiment" and sets uncertainty_calibrated false.

| phenotype | diagonal | full | rank-one | shrink 50 |
|---|---|---|---|---|
| margin MSE | 5.006e-9 | 5.030e-9 | 5.031e-9 | 4.964e-9 |
| margin paired diff vs diagonal, 95% | | -1.49e-10 to 7.84e-10 | -1.64e-10 to 9.48e-10 | -2.25e-10 to 2.16e-10 |
| accuracy MSE | 1.722e-9 | 1.821e-9 | 1.813e-9 | 1.762e-9 |
| accuracy paired diff vs diagonal, 95% | | -1.53e-11 to 4.04e-10 | -2.94e-11 to 3.75e-10 | -3.47e-11 to 1.78e-10 |

Zero invalid bootstraps. Every paired interval includes zero, so no covariance model has a detectable advantage over independence when the target is the noisy three-run variance moment of a held-out configuration. This neither confirms nor overturns the draft's log-SD ranking (rank-one 0.0057 versus independence 0.0358 on margins), which conditions on held-out marginal variances and has no paired interval. The manuscript reports both, distinguished by target.

## C08 seed-aligned pair decisions (R9)

`r9_pairs.py` builds 1,500 same-size recipe pairs per phenotype from the C01 moments: variance_a and variance_b are the three-run mean variances T_c/3, covariance_ab is the seed-matched cross-configuration covariance of the centred aggregate deviations, observed_gap is the difference of full-battery means.

| phenotype | defined pairs | feasible | median independence sd | median paired sd | median ratio | 5th to 95th pct ratio | share cov > 0 | median 2cov/sum |
|---|---|---|---|---|---|---|---|---|
| margin | 1,445 of 1,500 | 1,257 | 0.00310 | 0.00307 | 1.024 | 0.391 to 1.401 | 0.489 | -0.023 |
| accuracy | 1,222 of 1,500 | 668 | 0.00398 | 0.00388 | 1.081 | 0.360 to 1.621 | 0.493 | -0.038 |

Undefined pairs have a negative three-run variance estimate on one side. Pairs whose observed gap is inside 1.96 paired standard deviations: 282 of 1,445 (margin) and 259 of 1,222 (accuracy); inside 1.96 independence standard deviations: 307 and 260. Seed-matched replicates across recipes share no detectable run noise (median covariance near zero, half the pairs positive), so matching seeds across configurations neither reduces nor inflates the comparison noise in the median, while individual pairs vary by a factor of about 0.4 to 1.6 because three-run variance estimates are noisy. The C08 job labels its output "descriptive uncertainty arithmetic ... no true-gap or ranking-error guarantee".
