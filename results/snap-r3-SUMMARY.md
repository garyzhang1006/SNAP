# snap-r3 CPU kernels for the round 2 NEEDS-EXPERIMENT items R2-02, R2-26, R2-43

All three ran on Kaggle CPU on 2026-09-23, private, with enable_gpu false and enable_tpu false, from garyzhang11111/seed-noise-src (seednoise at SNAP 6cfedee) and garyzhang11111/seed-noise-reduced-runs (375 runs). Each script asserts the paper's margin Lambda 1.24395 before it computes anything. Each results folder holds the fetched JSON, the Kaggle log, and a copy of the pushed script and kernel-metadata.json (sources in work/kaggle/snap-r3-<item>/). Every number below is copied from the fetched files.

## R2-02: cross-format diagnostic under a uniform shared item component (done)

Kernel garyzhang11111/snap-r3-r2-02, COMPLETE. File results/snap-r3-r2-02/r2_02_shared_component_crossformat.json.
Injection model (stored in the JSON as `injection_model`): this is the snap-r6-sharednoise generator. Per-half item noise on trait k is sigma_k (sqrt(q) f + sqrt(1-q) z_k), where f is one scalar per run that all ten benchmarks share and that is identical in both halves. The shared term adds q sigma_j sigma_k to every cross-half covariance entry, diagonal included. sigma_k^2 is the per-half item noise from `seednoise.reliability.variance_components(pop, name).noise2`. The cross-format mask and T/U come from the r1_50 construction with `seednoise.estimator.half_projections`, and the unmasked T and U are asserted equal to `estimate()`. Intervals come from `seednoise.inference.wild_bootstrap_t` (4,999 draws, 25 recipes).

| reading | margin | accuracy |
|---|---|---|
| observed cross-format (reproduces r2-r1-50) | 0.9212 [0.8007, 1.0347] | 0.9652 [0.8484, 1.0634] |
| explain: the uniform component carries the whole observed excess, with no off-diagonal seed covariance; implied share q* | 1.4225 | 0.0526 |
| explain: induced cross-format diagnostic | 1.1133 (excluded: true) | 1.0469 (excluded: false) |
| explain: equal-pair-weight check sqrt(1 + 0.6 (Lambda^2 - 1)) | 1.1526 | 1.0477 |
| q = 0.124 with no seed covariance: full-matrix Lambda | 1.0236 | 1.1766 |
| q = 0.124 with no seed covariance: cross-format diagnostic | 1.0104 (excluded: false) | 1.1074 (excluded: true) |
| q = 0.124 added to observed T and U: full-matrix Lambda | 1.2612 | 1.2329 |
| q = 0.124 added: cross-format diagnostic, wild | 0.9330 [0.8079, 1.0500] | 1.0724 [0.9725, 1.1615] |

Bears on main.tex Sec 2 "Cross-format covariances alone give inflation 0.921 \ci{0.801}{1.035} ... which constrains a uniform component of that size", and on the matching sentence in the limitations paragraph.

Finding: the 0.124 share came from simulated noise (0.73 on a unit-variance latent), and it doesn't transfer to the released margin noise scales. On the released per-half item noise, which is small relative to the seed variance for margins (BoolQ has v 9.75e-6 against Sigma_E 1.43e-3), a 0.124 share lifts margin Lambda only to 1.024. To reproduce 1.244 the share would have to be 1.42, which is above one and so not attainable. Suppose a uniform component did carry the whole margin excess. It would push the cross-format diagnostic to 1.113, and the observed interval [0.801, 1.035] excludes that value. So the paper can say the interval excludes the value that explanation implies. It shouldn't describe "a uniform component of that size (0.124)" as the one being excluded, because at 0.124 the induced value of 1.010 sits inside the interval. On accuracy the explaining share is 0.053, which induces 1.047, and the interval [0.848, 1.063] does not exclude it.

## R2-26: split-half against the analytic diagonal correction (done)

Kernel garyzhang11111/snap-r3-r2-26, COMPLETE. File results/snap-r3-r2-26/r2_26_analytic_vs_split.json.
Split-half uses `seednoise.estimator.estimate(pop, name)`. The full bank uses `estimate` on a Population with A = B = full-bank scores from `seednoise.phenotypes.half_scores` with an all-True mask, which is the r2-r1-08 construction. The analytic correction subtracts sum_j v_cj / K^2 from T and U per configuration. v_cj is computed in the script (no committed function exists): (1/G_j^2) sum_g MS_g / n_g, where MS_g is the item-by-run interaction mean square inside each group and the MMLU groups match the half_scores macro-average. Intervals come from `wild_bootstrap_t` (4,999 draws, seed 0) and `cluster_t_interval`, both over 25 recipe clusters. Widths are on the Lambda scale.

| battery, phenotype | split-half (wild), width | analytic (wild), width | uncorrected full bank | wild width ratio analytic/split | cluster-t width ratio | cluster SE ratio (theta) |
|---|---|---|---|---|---|---|
| all ten, margin | 1.2439 [1.1429, 1.3377], 0.1948 | 1.2456 [1.1439, 1.3398], 0.1958 | 1.2375 | 1.0054 | 1.0066 | 1.0079 |
| all ten, accuracy | 1.0784 [0.9926, 1.1567], 0.1640 | 1.0819 [0.9942, 1.1623], 0.1681 | 1.0672 | 1.0246 | 1.0575 | 1.0606 |
| no BoolQ, margin | 1.7856 [1.6891, 1.8765], 0.1874 | 1.7919 [1.6994, 1.8782], 0.1788 | 1.7344 | 0.9539 | 0.9933 | 0.9968 |
| no BoolQ, accuracy | 1.5578 [1.4119, 1.6870], 0.2751 | 1.5948 [1.4500, 1.7214], 0.2714 | 1.2852 | 0.9865 | 0.9368 | 0.9596 |

The item-noise share removed from the full-bank diagonal is 0.037, 0.186, 0.092 and 0.578 in table order.
Bears on main.tex:35, "We adapt the repeated-measurement construction of quantitative genetics to this setting and call it SNAP", and on the R2-13 justification for splitting. The analytic correction reproduces the split-half point estimates within 0.002 on full-battery margins and within 0.004 on full-battery accuracy. Neither estimator is more efficient: the interval widths agree within about 6 percent in both directions, because recipe-level seed variation dominates the width and item noise barely contributes to it. The case for splitting therefore can't rest on precision. It has to rest on the split needing no model for the item-noise term, whereas the analytic version assumes item-by-run noise independent across items within a group.

## R2-43: the 0.008 band share and 0.044 bound (done, reproduced from committed code)

Kernel garyzhang11111/snap-r3-r2-43, COMPLETE. File results/snap-r3-r2-43/r2_43_band_share.json.
Source: SNAP 6cfedee, `compute extra/research_kernels/snap-r6-band-share/snap-r6-band-share.py`. Its `deviations`, `weighted_cross` and `band_statistic` functions and its 2,000-permutation null (seed 20260931) are copied verbatim. The share conversion comes from `snap-r6-share-power/snap-r6-share-power.py` (slope = total (1/25 - 1/625), q = (obs - null_mean)/slope, se = null_sd/slope, upper = q + 1.959964 se). The original run had stored the statistic but not the share. The ledger converted the share by hand (research/LEDGER.md, 2026-09-15 23:01 EDT). This kernel's observed statistic, total, null mean and null SD match the stored research/outputs/snap-r6-band-share/r6_band_share.json in all four cells (matches_stored_r6_statistics true).

| battery | share q | SE | 95% upper bound | permutation tail |
|---|---|---|---|---|
| full, margin | 0.00824 | 0.01815 | 0.04382 | 0.2830 |
| full, accuracy | -0.01565 | 0.02157 | 0.02663 | 0.7435 |
| without BoolQ, margin | 0.01970 | 0.01674 | 0.05252 | 0.1320 |
| without BoolQ, accuracy | 0.00671 | 0.02989 | 0.06528 | 0.3645 |

Bears on main.tex, "bounds that effect at 0.044 of the seed covariance on margins", and on appendices_bcd.tex, "the share comes to 0.008 on full-battery margins with a 95 percent upper bound of 0.044". Both printed values round correctly from 0.00824 and 0.04382, and they now have a stored output.
