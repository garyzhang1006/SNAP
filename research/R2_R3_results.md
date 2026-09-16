# R2 and R3 results (OBSERVED on Kaggle, 2026-09-15)

Kernels: `snap-r3-requests-audit` v2 (10:30 EDT), `snap-r2-grouped` v1 (10:34 EDT, 128 s). Outputs under `research/outputs/`. Comparison set and weighting were frozen in `R1_estimand.md` before any grouped number was opened.

## Passage recovery

The release's own `requests/boolq-requests.jsonl.gz` carries each item's passage inside `doc.query`. All 3,270 BoolQ passages match google/boolq validation exactly at the same native_id, so the earlier index join and the request-file join give the same partition: 2,938 passages, group sizes {1: 2692, 2: 197, 3: 27, 4: 13, 5: 7, 7: 1, 9: 1}, 578 items in shared passages. The passage-aware split assigns whole passages to halves and averages questions, so half sizes are unequal by a few items.

## Comparison set on the 37,682-item universe

Intervals: wild is the original wild cluster bootstrap-t over 25 recipes, ct is cluster-robust t(24), cfg is the configuration percentile bootstrap, rp is the snap_compute recipe percentile diagnostic. All 4,999 draws. BoolQ diagonal and trace are cross-half covariance units of the score scale.

| phenotype | split | Lambda | wild | ct | cfg | rp | BoolQ diag | trace | off-diag aggregate | sigma_agg |
|---|---|---|---|---|---|---|---|---|---|---|
| margin | original | 1.2439 | 1.1429 to 1.3377 | 1.1473 to 1.3336 | 1.0694 to 1.4255 | 1.1344 to 1.3221 | 1.4337e-3 | 2.111e-3 | 1.156e-5 | 5.716e-3 |
| margin | item (seed 20260914) | 1.2456 | 1.1437 to 1.3400 | 1.1486 to 1.3356 | 1.0701 to 1.4266 | 1.1364 to 1.3242 | 1.4340e-3 | 2.106e-3 | 1.162e-5 | 5.717e-3 |
| margin | group (BoolQ passages) | 1.2475 | 1.1466 to 1.3408 | 1.1512 to 1.3369 | 1.0713 to 1.4290 | 1.1387 to 1.3250 | 1.4235e-3 | 2.096e-3 | 1.166e-5 | 5.711e-3 |
| margin | no BoolQ, original | 1.7856 | 1.6891 to 1.8765 | 1.7101 to 1.8581 | 1.6749 to 1.8617 | 1.6437 to 1.8375 | none | 6.776e-4 | 1.831e-5 | 5.165e-3 |
| accuracy | original | 1.0784 | 0.9926 to 1.1567 | 0.9975 to 1.1536 | 0.9755 to 1.1824 | 1.0029 to 1.1550 | 1.9188e-3 | 2.274e-3 | 3.704e-6 | 5.142e-3 |
| accuracy | item | 1.0838 | 0.9934 to 1.1635 | 0.9979 to 1.1633 | 0.9825 to 1.1902 | 1.0034 to 1.1658 | 1.9166e-3 | 2.239e-3 | 3.907e-6 | 5.128e-3 |
| accuracy | group | 1.0971 | 1.0068 to 1.1769 | 1.0108 to 1.1770 | 0.9957 to 1.2031 | 1.0174 to 1.1794 | 1.8951e-3 | 2.217e-3 | 4.514e-6 | 5.166e-3 |
| accuracy | no BoolQ, original | 1.5578 | 1.4119 to 1.6870 | 1.4153 to 1.6884 | 1.3984 to 1.7217 | 1.4232 to 1.7013 | none | 3.549e-4 | 6.251e-6 | 3.261e-3 |

Trace shares on the original split: margin BoolQ 0.679, csqa 0.206, socialiqa 0.047, arc_easy 0.039; accuracy BoolQ 0.844, csqa 0.081, arc_easy 0.040. The no-BoolQ values 1.786 and 1.558 equal the draft's leave-one-trait-out numbers (REPORTED there as 1.786 and 1.558), so that sweep is now reproduced with the same intervals to three decimals (draft 1.689 to 1.877 and 1.412 to 1.687).

## Fifty repeated splits (C03, seed 20260914)

| phenotype | mode | mean Lambda | sd | min | max | BoolQ diag mean (sd) |
|---|---|---|---|---|---|---|
| margin | item | 1.2459 | 0.0017 | 1.2427 | 1.2500 | 1.42598e-3 (9.4e-6) |
| margin | group | 1.2457 | 0.0015 | 1.2429 | 1.2487 | 1.42638e-3 (6.8e-6) |
| accuracy | item | 1.0828 | 0.0081 | 1.0631 | 1.0984 | 1.90029e-3 (2.0e-5) |
| accuracy | group | 1.0827 | 0.0093 | 1.0590 | 1.0972 | 1.89746e-3 (2.0e-5) |

Paired group minus item over the same 50 split seeds: margin mean -0.0002 (sd 0.0017), accuracy mean -0.0001 (sd 0.0060). Split spread is algorithmic sensitivity of one estimate, not population uncertainty.

## What R2 establishes

Passage sharing in BoolQ produces no detectable difference between item-level and passage-level halves. The BoolQ diagonal moves by 0.03 percent (margin) and 0.15 percent (accuracy) between the two split rules, and Lambda moves by less than one twentieth of its recipe-cluster standard error. The single grouped accuracy split at 1.0971 sits at the top of the 50-split range (max 1.0972), so it is a split draw and not a passage effect. The draft's statements that shared passages "bias the covariance estimate" and that the analysis "hasn't reconstructed passage groups" are both superseded: the groups are reconstructed from official provenance, and the bias is bounded below the split-to-split spread. The original 1.244 and 1.078 stand as the primary estimates on the frozen split. The BoolQ dominance of the trace (0.68 and 0.84) is unchanged and remains a composition sensitivity, not a leakage artefact. `snap-r2-group-sim` reports what passage-level run interaction the design could have detected.

## R3 inventory (doc-level stems from the request files)

Cross-trait shared stems: 2 (arc_challenge and arc_easy 1, arc_easy and mmlu 1). Within-trait docs in repeated stems: piqa 62 of 1,838 (max repeat 4), socialiqa 48 of 1,954, hellaswag 45 of 10,042 (max 3), mmlu college_physics 36 of 102, mmlu high_school_psychology 22 of 545, arc_easy 10 of 2,376, mmlu nutrition 10 of 306 (max 6), arc_challenge 4, openbookqa 4, winogrande 0, csqa 0. Repeated MMLU stems are generic question texts ("Which of the following is true?") with different choices, so they are distinct items sharing a stem string, not a shared passage. No grouping is applied outside BoolQ. Given the null BoolQ result at 578 shared-passage items, the smaller inventories elsewhere cannot move the estimate detectably, and the manuscript reports the inventory as a limitation rather than a repair.

## Detectability simulation (`snap-r2-group-sim`, OBSERVED, complete 11:15 EDT, 2,355 s)

`r2_group_sim.py`, 500 replicates per cell, seed 20260915, 125 configurations, 3 runs, 10 traits, BoolQ trace share 0.68, rho 0.061, BoolQ item-noise sd 4 against run-effect sd 4.37, observed passage histogram {1: 2692, 2: 197, 3: 27, 4: 13, 5: 7, 7: 1, 9: 1}. Truth Lambda 1.1519.

| tau (run-by-passage sd) | item Lambda mean (sd) | group Lambda mean (sd) | item diag relative bias | group diag relative bias | paired group minus item mean (sd) |
|---|---|---|---|---|---|
| 0.0 | 1.1508 (0.0447) | 1.1530 (0.0459) | +0.0021 | +0.0022 | +0.0022 (0.0330) |
| 0.5 | 1.1506 (0.0454) | 1.1504 (0.0471) | +0.0010 | +0.0009 | -0.0002 (0.0341) |
| 1.0 | 1.1523 (0.0440) | 1.1540 (0.0445) | -0.0090 | -0.0091 | +0.0017 (0.0331) |
| 2.0 | 1.1513 (0.0465) | 1.1505 (0.0446) | -0.0056 | -0.0055 | -0.0008 (0.0334) |
| 4.0 | 1.1557 (0.0454) | 1.1550 (0.0428) | -0.0028 | -0.0033 | -0.0007 (0.0355) |

Monte Carlo standard error of each paired mean is about 0.0015, so no cell separates the two split rules. Arithmetic on the histogram explains why: under a random item split the expected number of same-passage question pairs straddling the halves is (197*1 + 27*3 + 13*6 + 7*10 + 21 + 36)/2 = 241.5, against 1635^2 = 2.67 million cross-half pairs, so the leaked covariance is tau^2 * 9.0e-5, which at tau = 4 is 1.4e-3 against a BoolQ diagonal of 19.1, or 0.008 percent. The empirical null in the comparison table is what this structure implies, and the manuscript says so (appendix A). R2 is VERIFIED without qualification.
