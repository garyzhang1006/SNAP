# Experiments

Declarative verification plans. Design quantities (run counts, draw counts) are given where the paper fixes them; result values live in `evidence/`. Hardware for released-score analyses is CPU (Kaggle CPU kernels); scoring runs are listed per experiment.

## E01: Calibration simulations for the estimator and its intervals
- **Verifies**: C01, C09
- **Setup**:
  - Model: none (synthetic populations)
  - Hardware: Kaggle CPU and GPU kernels (Not specified per run in paper)
  - Dataset: Simulated populations with 125 configurations in 25 recipe clusters, three runs, ten benchmarks, released item counts; twelve populations in Table 9 (null at two noise levels, margin-like and accuracy-like covariance, one trait holding most of the trace, recipe-shared effects, Student t with 4 df, one dominant recipe, cross-half error correlation, higher covariance)
  - System: 2,000 replicates per population with 4,999 bootstrap draws; repeat at 10,000 replicates; N1 recovery grid at six effect sizes
- **Procedure**:
  1. Generate half scores from the measurement model with specified Sigma_E and item noise.
  2. Compute pooled Lambda-hat and the wild recipe-cluster bootstrap-t, cluster t(24), configuration percentile, recipe percentile and centred test-inversion intervals.
  3. Record mean bias and empirical coverage per population; sweep cross-half noise correlation and a scalar shared item effect.
- **Metrics**: Mean estimate minus true Lambda; coverage of nominal 95% intervals; recovery slope across effective coefficients.
- **Expected outcome**:
  - Under independent noise the mean estimate sits at one within Monte Carlo error.
  - Wild bootstrap-t coverage stays near nominal across populations, while the configuration percentile bootstrap undercovers under recipe-shared effects.
  - Cross-half error correlation biases the estimate downward, toward one.
- **Baselines**: Configuration percentile bootstrap; recipe percentile bootstrap; cluster t(24).
- **Dependencies**: none

## E02: Primary full-battery estimation on DataDecide
- **Verifies**: C02, C03, C05
- **Setup**:
  - Model: DataDecide OLMo-architecture runs, 25 recipes x {150M, 300M, 530M, 750M, 1B} x 3 replicates
  - Hardware: One Kaggle CPU core (no forward passes)
  - Dataset: Released per-item outputs, ten benchmarks, 37,682 items per run, largest checkpoint step common to all three runs per configuration
  - System: Frozen within-trait balanced split (master seed 20260101); wild recipe-cluster bootstrap-t, 4,999 Rademacher draws, bootstrap seed 0
- **Procedure**:
  1. Stream and reduce released tarballs to per-item margin and accuracy at the common step.
  2. Form half scores, centre across runs, compute T_c and U_c, pool and take the ratio.
  3. Report Lambda-hat, K_eff, sigma_agg and intervals on both score scales, raw and auxiliary contrast.
- **Metrics**: Lambda-hat (dimensionless), 95% interval, K_eff, sigma_agg (margin units or accuracy fraction).
- **Expected outcome**:
  - Margin inflation exceeds one with an interval excluding one.
  - Accuracy inflation is smaller than margin inflation and its interval may include one.
- **Baselines**: Independence (Lambda = 1); auxiliary-run contrast.
- **Dependencies**: E01

## E03: Composition and deletion sensitivity
- **Verifies**: C04, C05, C06
- **Setup**:
  - Model: As E02
  - Hardware: CPU kernels
  - Dataset: As E02
  - System: Wild interval recomputed after each deletion; 1,013 equal-weight subsets; 2,000 flat and near-flat Dirichlet weightings; BoolQ weight lowered in seven steps; item-count weighting
- **Procedure**:
  1. Delete each recipe, each recipe pair, each size band and each benchmark in turn and recompute the estimate and interval.
  2. Enumerate equal-weight benchmark subsets of two to ten benchmarks.
  3. Sweep benchmark weights over the simplex and along the BoolQ weight.
- **Metrics**: Estimate and interval per deletion; share of intervals excluding one; trace shares; sigma_agg.
- **Expected outcome**:
  - Benchmark removal moves the estimate more than recipe or size removal.
  - Removing the dominant-variance benchmark raises Lambda while lowering sigma_agg.
  - Margin intervals keep excluding one under most deletions; accuracy flips under some deletions.
- **Baselines**: Full ten-benchmark flat-weight estimate.
- **Dependencies**: E02

## E04: Registered held-out test on four unseen tasks
- **Verifies**: C07, C08
- **Setup**:
  - Model: DataDecide runs at 530M, 750M and 1B (225 runs, 75 configurations)
  - Hardware: 205 runs on Kaggle T4 cards; last 20 at 1B on three RTX 3090 cards
  - Dataset: SciQ, MedMCQA, and multiple-choice DROP and CoQA, 1,000 items each, built with OLMES at a pinned commit; passage- or story-sharing items kept in one half
  - System: float32 weights, transformers 4.57.1, 6,000-token cap; torch 2.10.0 (T4 image) and 2.14.0 (3090s); wild recipe-cluster bootstrap-t, 4,999 draws
- **Procedure**:
  1. Register task list, replacement rule, statistic, interval, pass rule and scope rule before production scores.
  2. Apply the replacement rule on pilot 1B accuracy (below chance plus 0.02 triggers replacement).
  3. Score all runs in scope, check each against a reference path within 0.001 nats.
  4. Compute held-out margin inflation and its interval; compare to the original ten benchmarks on the same runs.
- **Metrics**: Held-out Lambda-hat and lower 95% limit; interval width; accuracy inflation; leave-one-task-out estimates.
- **Expected outcome**:
  - Registered prediction: the lower 95% limit of held-out margin inflation exceeds one.
  - The original ten benchmarks on the same runs pass the rule.
- **Baselines**: Original ten benchmarks at the same scope; four-benchmark subsets of the original battery.
- **Dependencies**: E02

## E05: Item-dependence checks
- **Verifies**: C10
- **Setup**:
  - Model: As E02
  - Hardware: Kaggle CPU kernels
  - Dataset: BoolQ passages recovered from release request files; 37,682 items in 66 groups
  - System: 50 paired passage-aware re-splits; 2,000 within-group item permutations; 200 re-drawn splits; scalar item-effect sweep with 2,000 replicates per share; cross-half noise correlation sweep with 1,000 replicates per value
- **Procedure**:
  1. Assign whole BoolQ passages to halves and compare with item-level splits.
  2. Permute run deviations across items within each group, separately for every run, and recompute.
  3. Simulate a scalar item effect shared across benchmarks and repeated across halves at increasing shares.
- **Metrics**: Change in Lambda-hat; permutation tail fraction; share reproducing the observed estimate.
- **Expected outcome**:
  - Passage-aware splitting moves estimates within re-split variation.
  - Item-level permutation accounts for a small part of the estimate.
  - A benchmark-wide shared item effect can reproduce the observed value only at a sizable share.
- **Baselines**: Frozen item-level split.
- **Dependencies**: E02

## E06: Covariance structure by scoring format
- **Verifies**: C11
- **Setup**:
  - Model: As E02
  - Hardware: CPU
  - Dataset: Nine margin traits with positive variance (WinoGrande excluded); formats MC, cloze, yes/no
  - System: Masked cross-format diagnostic; two-correlation fit with leave-one-benchmark-out re-estimation
- **Procedure**:
  1. Estimate the cross-half correlation matrix and average within and across formats.
  2. Compute the diagnostic retaining only cross-format off-diagonal pairs.
  3. Replace correlations by two block values, keep seed variances, predict full and deletion estimates.
- **Metrics**: Mean within/cross-format correlation; diagnostic Lambda; absolute prediction error per deletion.
- **Expected outcome**:
  - Within-format correlations exceed cross-format correlations.
  - The cross-format diagnostic falls toward one.
  - A two-parameter fit approximates observed deletions.
- **Baselines**: Full-matrix estimate; equal-variance fit.
- **Dependencies**: E02, E03

## E07: Gain and competence adjustments
- **Verifies**: C12
- **Setup**:
  - Model: As E02 (250 run contrasts)
  - Hardware: CPU
  - Dataset: As E02
  - System: Regression $y_{crj}=\alpha_{cj}+\beta_j x^{(-j)}_{cr}+\gamma_j s_{cr}+u_{crj}$; shipped, shrunken, factor and clipped-drop proxies; simulations under independent, common and matched covariance (300 replicates)
- **Procedure**:
  1. Adjust each benchmark's run contrast for gain and a leave-one-benchmark-out competence proxy.
  2. Audit proxy input shares and split-half signal.
  3. Apply each adjustment to simulated populations with no competence variable.
- **Metrics**: Adjusted Lambda-hat; proxy split-half correlation; simulated reference means and percentiles.
- **Expected outcome**:
  - Planned prediction: gain adjustment leaves most of the accuracy excess.
  - Diagnostic expectation: if proxies average the same seed deviations they adjust, adjusted estimates move toward or below one even without a competence mechanism.
- **Baselines**: Unadjusted estimate; simulated populations.
- **Dependencies**: E02

## E08: Checkpoint schedule and truncation sensitivity
- **Verifies**: C05, C13
- **Setup**:
  - Model: DataDecide, 123 configurations with an earlier shared step (369 runs)
  - Hardware: CPU
  - Dataset: Same items, split and weights at the selected and previous shared step
  - System: Paired recipe bootstrap, 4,999 draws; subsets defined by checkpoint index
- **Procedure**:
  1. Re-reduce each run at the largest shared step below the selected step and recompute.
  2. Recompute on subsets: shared final step, without severe truncation, severe truncation only, different final steps.
  3. Correlate configuration influence with truncation share.
- **Metrics**: Lambda-hat at both steps; paired change interval; subset estimates; Spearman correlation.
- **Expected outcome**:
  - Margin conclusions hold across steps; the accuracy verdict can change with the scored checkpoint.
  - No detectable association between influence and truncation.
- **Baselines**: Selected-step full-sample estimate.
- **Dependencies**: E02

## E09: Planned partition enumeration and planning scorecard
- **Verifies**: C14
- **Setup**:
  - Model: As E02
  - Hardware: CPU (exact recipe sweep)
  - Dataset: All 1,081,575 seventeen-recipe subsets of 25 recipes
  - System: Subset estimator $\widehat\Lambda_S=\sqrt{\sum_{c\in S}T_c/\sum_{c\in S}U_c}$
- **Procedure**:
  1. Enumerate every admissible estimation subset and compute margin and accuracy estimates.
  2. Compare with the plan's thresholds and score each of the eleven planning predictions and nine gates.
- **Metrics**: Range and quantiles of subset estimates; count reaching thresholds.
- **Expected outcome**:
  - Planned prediction: estimates exceed the planning thresholds.
  - The sweep shows whether any subset could have reached them.
- **Baselines**: All-recipe estimate; reconstructed planned partition.
- **Dependencies**: E02

## E10: Earlier PolyPythias transfer
- **Verifies**: C15
- **Setup**:
  - Model: PolyPythias, nine seeds per size, three planned sizes plus 14M and 31M rescore, step 143,000
  - Hardware: Slurm cluster L40S 46 GB (planned arm); one T4 with 6,000-token cap for the rescore; repeat on two T4s
  - Dataset: Nested 4,755-item battery
  - System: fp16 teacher-forced zero-shot scoring; configuration bootstrap; centred test inversion with each configuration as its own cluster
- **Procedure**:
  1. Score all runs on the nested battery and compute inflation at three and five sizes.
  2. Compare with DataDecide on raw and excess scales.
- **Metrics**: Lambda-hat; configuration-bootstrap and inversion intervals.
- **Expected outcome**:
  - Planned: DataDecide R_E predicts PolyPythias aggregate SD within 20 percent.
  - With three or five configurations, intervals are expected to be wide.
- **Baselines**: DataDecide estimate.
- **Dependencies**: E02

## E11: External signal-and-noise panel
- **Verifies**: C16
- **Setup**:
  - Model: Released single-configuration random-seed panels of Heineman et al. (2025), ten initialisation runs or nine data-order runs
  - Hardware: CPU
  - Dataset: Twenty released checkpoints; eighteen bits-per-byte traits, eight accuracy-per-character traits
  - System: No cross-half correction (no per-item outputs)
- **Procedure**:
  1. Estimate inflation per checkpoint and average across checkpoints.
  2. Apply a leave-one-out adjustment using the mean deviation of the other traits.
- **Metrics**: Lambda, adjusted Lambda, r_E.
- **Expected outcome**:
  - Likelihood scales show more inflation than accuracy scales.
- **Baselines**: DataDecide score-scale contrast.
- **Dependencies**: none

## E12: Prediction of aggregate uncertainty
- **Verifies**: C17
- **Setup**:
  - Model: As E02; PolyPythias nine-seed configurations for single-configuration ratios
  - Hardware: CPU
  - Dataset: Five recipe folds; 84 three-of-nine run choices for PolyPythias
  - System: Models P0 independence, P1 rank-one, P1G rank-one plus gain, P2 phenotypic plug-in, P3 full covariance, P2R rescaled plug-in; paired recipe bootstrap with 2,000 refitted draws; practically meaningful difference fixed at 0.005
- **Procedure**:
  1. Fit each covariance model off fold, supply held-out marginal seed SDs, predict log aggregate SD.
  2. Compute paired differences for eight pre-fixed contrasts.
  3. Repeat operationally without held-out marginals; repeat on 1,000 fold partitions and simulated populations.
- **Metrics**: Mean squared error of log aggregate SD; paired difference intervals.
- **Expected outcome**:
  - Covariance models beat independence on margins when marginals are supplied.
  - No separation on accuracy or in the operational comparison.
- **Baselines**: Independence (P0).
- **Dependencies**: E02

## E13: Decision impact of covariance correction
- **Verifies**: C18
- **Setup**:
  - Model: As E02; simulated three-run designs
  - Hardware: CPU
  - Dataset: Same-size recipe pairs at 150M, 300M, 530M, 750M scored against the 1B ordering; 4,000 and 8,000 simulation replicates
  - System: Two-standard-error calling rule with SD estimated under independence or covariance, pair left out; recipe bootstrap of 2,000 draws
- **Procedure**:
  1. Simulate uncorrected, plug-in and oracle rules at a zero gap and at transferred target ratios.
  2. On real data, call pairs below 1B and score against resolved 1B orderings.
- **Metrics**: False-positive rate (simulation); wrong-sign call share and its change (real data).
- **Expected outcome**:
  - The correction restores nominal size in simulation when the ratio matches the source battery.
  - On real comparisons the change in wrong-call rate is small.
- **Baselines**: Independence rule.
- **Dependencies**: E02

## E14: Clustering sensitivity and band-shared run effect
- **Verifies**: C19
- **Setup**:
  - Model: As E02
  - Hardware: CPU
  - Dataset: As E02; 150 ARC-Easy documents rescored for seed matching
  - System: Batch-slot permutation null (2,000 permutations); size-band clustering; simulated band and recipe sharing sweeps at 4,000 to 12,000 replicates
- **Procedure**:
  1. Permute runs by batch slot within bands to bound the band-shared share.
  2. Simulate coverage under band-shared and recipe-shared effects.
  3. Recompute intervals with size-band clusters.
- **Metrics**: Shared-share point estimate and upper bound; coverage; test power.
- **Expected outcome**:
  - The band-shared share is small; coverage stays near nominal up to the bound.
- **Baselines**: Recipe-clustered wild interval.
- **Dependencies**: E01, E02

## E15: PolyPythias bank-1 replication (rule R1)
- **Verifies**: C20
- **Setup**:
  - Model: PolyPythias (GPT-NeoX), nine seeds at each of 14M, 31M, 70M, 160M, 410M, step 143,000 (45 runs)
  - Hardware: Kaggle T4 cards, float32, transformers 4.57.1
  - Dataset: Bank 1, the full 37,682-item battery with request text taken byte for byte from the DataDecide release
  - System: Paper's item split and phenotypes; delete-one-seed jackknife t(8) primary; wild, cluster t and configuration bootstrap reported alongside
- **Procedure**:
  1. Score all 45 runs; check cached scores against an uncached reference on 24 items within 0.001 nats.
  2. Compute margin and accuracy inflation, per-size jackknives, and the estimate without BoolQ.
  3. Apply R1: pass iff the jackknife lower endpoint exceeds one.
- **Metrics**: Lambda-hat, jackknife interval, per-size estimates.
- **Expected outcome**:
  - Rule fixed before scoring; the source states no expected direction beyond the rule. Evidence: Not available: scoring in progress.
- **Baselines**: DataDecide margin estimate.
- **Dependencies**: E02, E10

## E16: Disjoint item bank identification check (rule R2)
- **Verifies**: C21
- **Setup**:
  - Model: Same 45 PolyPythias runs as E15
  - Hardware: Kaggle T4 cards, float32, transformers 4.57.1
  - Dataset: Bank 2, 6,808 items from the same ten benchmarks, OLMES at the DataDecide commit, train split for eight benchmarks and validation for OpenBookQA and MMLU; items matching a bank-one context or appearing among their own few-shot exemplars dropped; capped at 600 per benchmark apart from MMLU
  - System: Half A = bank 1, half B = bank 2; delete-one-seed jackknife of the within-minus-cross log difference
- **Procedure**:
  1. Score all runs on bank 2 and compute the cross-bank estimate.
  2. Compute the within-minus-cross difference in log inflation and its jackknife interval.
  3. Apply R2: not supported / supported / undecided per the fixed rule.
- **Metrics**: Cross-bank Lambda-hat and interval; log difference interval.
- **Expected outcome**:
  - Rule fixed before scoring; no expected direction stated. Evidence: Not available: scoring in progress.
- **Baselines**: Within-bank-1 estimate on the same runs (E15).
- **Dependencies**: E15
