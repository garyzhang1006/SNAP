# snap-r2 CPU kernels for the round 1 NEEDS-EXPERIMENT items

All kernels ran on Kaggle CPU (enable_gpu false, enable_tpu false, private), 2026-09-23. Each results folder holds the fetched output, the Kaggle log, and a copy of the pushed script and kernel-metadata.json (sources in work/kaggle/snap-r2-<item>/). Every number below is copied from the fetched files. The DataDecide kernels install seednoise from garyzhang11111/seed-noise-src, read the 375 runs in garyzhang11111/seed-noise-reduced-runs, and assert the paper's margin Lambda 1.24395 before computing anything.

## R1-18: rule two operating characteristics (done)

Kernel garyzhang11111/snap-r2-r1-18, COMPLETE. File results/snap-r2-r1-18/r1_18_rule_two.json.
Setup: the r1_power.py model (nine seeds, five sizes, 4,000 replicates, seed 20260923) plus a bank two at one sixth of bank one's items. The verdicts come from SNAP 6cfedee compute2/analysis/estimates.py, using verdicts(), seed_jackknife() and jackknife_logdiff(). Vectorised copies of those functions produced the 4,000-replicate rates. In each scenario, the first 25 replicates also ran through the committed functions, with 0 label mismatches.

| scenario | not supported | supported | undecided | rule one pass |
|---|---|---|---|---|
| run covariance, true 1.2438, no shared item effect | 0.22575 | 0.013 | 0.76125 | 0.257 |
| independence, no shared item effect | 0.01075 | 0.015 | 0.97425 | 0.01375 |
| independence, shared-item share 0.124 | 0.01025 | 0.03275 | 0.957 | 0.039 |
| run covariance 1.244 plus share 0.124 | 0.20475 | 0.03225 | 0.763 | 0.31975 |

Supports: the R1-18 sentence at main.tex:213 about rule two's branch probabilities. When the effect is real and has no shared item component, rule two says "not supported" in about 0.23 of replicates and "undecided" in about 0.76. Under independence it reports "supported" in 0.015.
Caveats:
- On PolyPythias noise, a 0.124 share lifts the within-bank median only to 1.046 (cross 0.999), so that share doesn't reproduce 1.244 in this family. The 0.124 calibration came from DataDecide noise.
- Bank two is 6,808 against 37,682 items (R1-49), a ratio of 1/5.53, while the simulation used 1/6.

### R1-18b: the rule-one power figure in the paper (finding)

Kernel garyzhang11111/snap-r2-r1-18b, COMPLETE. File results/snap-r2-r1-18b/r1_18b_jackknife_recentring.json.
The kernel ran r1_power.py verbatim on the same draws. It reproduces pass_rate 0.356 and 5-95% 1.0258 to 1.4563. The recentred delete-one-seed jackknife that the committed seed_jackknife computes gives pass_rate_recentred_jackknife 0.2585 on those draws (null with a diagonal Sigma_E: 0.02625 for the r1_power jackknife, 0.0155 recentred).
r1_power.py drops a seed's term without recentring the remaining seeds, which understates the jackknife SE (median se_theta 0.2785 against 0.3197). The "0.356 of 4,000 replicates" at main.tex:213 therefore describes an approximation. The committed rule's power at a true 1.244 is about 0.26 (0.257 in R1-18, 0.2585 here). A separate issue: r1_power.py's rel vector is in table order (ARC-Easy first), while Sigma_E is in TRAITS order (arc_challenge first), so the reliabilities of the two ARC traits are swapped. This run kept that choice to stay comparable.

## R1-20: seed-mismatched recipe pairs (done)

Kernel garyzhang11111/snap-r2-r1-20, COMPLETE. File results/snap-r2-r1-20/r1_20_seed_mismatch.json.
Method: the k05-decision logic (seednoise.estimator.estimate leave-pair-out sigma_indep and sigma_agg, the 1B truth rule, a 2,000-draw recipe bootstrap). Each comparison sets one run against one run, with SE sqrt(2)*sigma. A seed-matched pair has i = j and a mismatched pair has i != j. Batch labels are identical across recipes in every size band (batch_check).
Independence-minus-corrected wrong-call rate, with the 95% recipe-bootstrap interval:

| phenotype, size | matched | mismatched | SD ratio matched/mismatched |
|---|---|---|---|
| margin 150M | 0.0041 [-0.0092, 0.0291] | 0.0027 [-0.0013, 0.0119] | 1.0234 |
| margin 300M | -0.0015 [-0.0115, 0.0086] | 0.0085 [-0.0030, 0.0336] | 0.9952 |
| margin 530M | 0.0193 [-0.0014, 0.0602] | 0.0160 [-0.0006, 0.0480] | 0.9282 |
| margin 750M | 0.0040 [-0.0026, 0.0182] | 0.0039 [-0.0004, 0.0137] | 1.0245 |
| accuracy 150M | -0.0008 [-0.0034, 0.0] | -0.0011 [-0.0037, 0.0] | 1.0146 |
| accuracy 300M | 0.0043 [-0.0017, 0.0158] | 0.0015 [-0.0023, 0.0073] | 1.0238 |
| accuracy 530M | 0.0117 [-0.0037, 0.0334] | 0.0038 [-0.0033, 0.0135] | 0.9727 |
| accuracy 750M | 0.0001 [-0.0099, 0.0102] | -0.0008 [-0.0066, 0.0040] | 1.0231 |

Supports: the R1-20 sentence for Sec 4.5, and it contradicts the seed-label explanation in R1-03 and R1-04. Seed-mismatched comparisons change the wrong-call rate no more than matched ones do, and every interval reaches zero. The matched-to-mismatched SD ratio of single-run deviation differences runs from 0.928 to 1.025, so shared seed labels cancel little. The main.tex:228 sentence ("suggests that most of the covariance cancels in such seed-matched gaps, which would explain the few changed calls") is not borne out and should be dropped or reversed.

## R1-08: fixed-bank inflation (done)

Kernel garyzhang11111/snap-r2-r1-08, COMPLETE. File results/snap-r2-r1-08/r1_08_fixed_bank.json.
Method: full-bank trait scores from seednoise.phenotypes.half_scores with an all-True mask, then a Population with A = B = full. seednoise.estimator.estimate gives lambda_hat, and seednoise.inference.wild_bootstrap_t (4,999 draws, 25 recipes) gives the interval.

| battery, phenotype | fixed bank (wild) | split-half SNAP (wild) |
|---|---|---|
| all ten, margin | 1.2375 [1.1370, 1.3313] | 1.2439 [1.1429, 1.3377] |
| all ten, accuracy | 1.0672 [0.9938, 1.1343] | 1.0784 [0.9926, 1.1567] |
| no BoolQ, margin | 1.7344 [1.5905, 1.8653] | 1.7856 [1.6891, 1.8765] |
| no BoolQ, accuracy | 1.2852 [1.1812, 1.3806] | 1.5578 [1.4119, 1.6870] |

Supports: the R1-08 sentence in Sec 2.1/2.2 naming the two estimands. On the released bank the replicate-SD inflation is 1.237 for margins and 1.067 for accuracy, close to the item-general values. They differ materially only for accuracy without BoolQ (1.285 against 1.558).

## R1-50: cross-format masked-matrix interval (done)

Kernel garyzhang11111/snap-r2-r1-50, COMPLETE. File results/snap-r2-r1-50/r1_50_crossformat_boot.json.
Method: T_mask from seednoise.estimator.half_projections and contrast_basis, which keeps the diagonal plus 54/90 cross-format ordered pairs. U comes from estimate. The interval is seednoise.inference.wild_bootstrap_t. The unmasked recomputation equals seednoise's T and U (asserted).
- margin: 0.9212, wild [0.8007, 1.0347]
- accuracy: 0.9652 [0.8484, 1.0634]
- margin without BoolQ: 1.0055 [0.9724, 1.0386]. Unrestricted nine-trait: 1.7856 [1.6891, 1.8765].

Supports: main.tex:220 and appendices_bcd.tex:128-130. All four published values reproduce to three decimals, so the interval now has a result file. The accuracy no-BoolQ cross-format value, 0.9720 [0.8223, 1.1011], is new.

## R1-49: enumeration and bank-two manifest (done)

Kernel garyzhang11111/snap-r2-r1-49, COMPLETE. Files results/snap-r2-r1-49/r1_49_enumeration.json, r1_49_bank2_manifest.json and bank2_requests.jsonl.gz.
- Enumeration: n_sets 1081575, estimator sqrt(sum T_c / sum U_c) with T and U from seednoise.estimator.estimate. Margins run from 1.0366622 to 1.3165447 and accuracy from 0.9634714 to 1.1913715. No set reaches the plan thresholds 1.349 and 1.40 (sets_reaching_threshold 0 for both). Supports main.tex:129 unchanged.
- Bank two, rebuilt with the committed builders at SNAP 6cfedee (build_bank1.py, then build_bank2.py with OLMES 5a51f502): items 6808, sha256 6190e0b24324ca357b3515206165acb6f024c310005d36fcf17fb2807cbc81d1.
  - Per trait: arc_challenge 600, arc_easy 600, boolq 600, csqa 600, hellaswag 600, mmlu 1508, openbookqa 500, piqa 600, socialiqa 600, winogrande 600.
  - Bank one: 37,682 items.
  - The largest drop is piqa, with 552 items whose context is in bank 1.
- Supports main.tex:45 and 135 ("6,808 items"). No earlier frozen hash exists anywhere in the repo or the SNAP release to compare against. This file is therefore a deterministic rebuild, not the original freeze.
