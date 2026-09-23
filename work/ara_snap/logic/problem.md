# Problem Specification

## Observations

### O1: Independence-based standard errors omit off-diagonal covariance
- **Statement**: For an equally weighted average of K benchmarks, independent run deviations give variance K^-2 tr(Sigma_E); covariance adds off-diagonal terms. In simulation with margin-like covariance, an independence-based comparison declares a difference in 0.113 of replicates with a true gap of zero, against a nominal 0.05.
- **Evidence**: §1 (Introduction); Appendix C "Observed gaps and predicted rank reversals".
- **Implication**: A benchmark-average comparison's error control depends on the unmeasured cross-benchmark run covariance.

### O2: Item-sampling noise contaminates naive run covariance
- **Statement**: A benchmark score from a finite item set carries item-dependent error, and with R = 3 replicate runs the raw cross-benchmark sample covariance mixes run covariance with item noise; raw cross-half products without centring contain squared configuration means that the analysis record reports can inflate the ratio by roughly three orders of magnitude.
- **Evidence**: §2.1-2.2; Appendix D.7 "Centring through run contrasts".
- **Implication**: An estimator must cancel item noise and configuration means before products are formed.

### O3: Released DataDecide runs provide replicates but with a confounded seed design
- **Statement**: DataDecide supplies 25 data recipes at 150M, 300M, 530M, 750M and 1B with three replicates each (375 runs, 125 configurations). The seed controls initialisation and data order together; auxiliary replicates below 1B stop at 25 percent of the 1B compute budget; in 26 configurations (one at 530M, 25 at 750M) the largest final step exceeds the smallest by more than a factor of 1.5; only 33 configurations share a final step. Seed labels are {2,14,15} below 1B and {2,4,5} at 1B, shared across every recipe inside a size band.
- **Evidence**: §3; Appendix B.1 (Table 5); Appendix C "Recipe, size and trait sensitivity" (band-shared seed label).
- **Implication**: The estimand is covariance among released runs at the selected steps, not a seed-only covariance.

### O4: Margins and accuracy respond differently to confidence changes
- **Statement**: Per-benchmark reliability averages 0.652 on margins and 0.324 on accuracy; seven accuracy and three margin benchmarks fall below 0.50; under a Gaussian location model the accuracy-to-margin noise ratio per unit squared sensitivity is p(1-p)/phi(z0)^2, about 1.66 at p = 0.35 with minimum pi/2.
- **Evidence**: §2.3 (Equation 7); §4.1; Appendix B.2 (Table 6).
- **Implication**: The two score scales need separate estimates; accuracy carries little seed signal at benchmark level.

### O5: One benchmark dominates the covariance trace
- **Statement**: BoolQ contributes 68% of the margin covariance trace and 84% of the accuracy trace; its margin seed variance is 1.43 x 10^-3 against 4.34 x 10^-4 for the next-largest trait.
- **Evidence**: §4.1; Appendix C "Associations with scoring format"; supplement Table 11.
- **Implication**: Any inflation factor is a property of the chosen battery and its variance weights.

### O6: Estimated run correlations follow scoring format
- **Statement**: Across nine defined margin traits, correlations average 0.624 within formats (sixteen pairs) and 0.007 across formats (twenty pairs).
- **Evidence**: §4.4; Appendix C "Associations with scoring format" and "A two-correlation fit".
- **Implication**: Format and task content are confounded here since each benchmark has one format.

### O7: Prior work does not estimate cross-benchmark run covariance
- **Statement**: Among the studies the authors located, none estimates the covariance of run noise between benchmarks or an effective benchmark count from that covariance; related work measures per-benchmark seed variance, variance sources within one task, or effective test counts for thresholds.
- **Evidence**: §5 (Related work); Appendix B.7.
- **Implication**: The target quantity and its estimator are the paper's contribution.

### O8: Planning artefacts lack corroborated provenance
- **Statement**: The analysis plan's claimed date (September 5, 2026) lacks an independent timestamp, no original file was supplied, the planned eight/seventeen recipe screening split was never formed, and the registered protocol's commit times are not independently corroborated.
- **Evidence**: §1; §3; Appendix B.4; Reproducibility statement.
- **Implication**: Only the registered held-out test (and the two PolyPythias rules) are read as confirmatory; everything else is exploratory.

## Gaps

### G1: No estimator of item-general run covariance between benchmarks
- **Statement**: Evaluation practice lacks a way to estimate the covariance of run deviations across benchmarks with item-sampling noise removed.
- **Caused by**: O1, O2, O7
- **Existing attempts**: Per-benchmark seed variance (Madaan et al., 2024; Reimers and Gurevych, 2017); variance-source accounting within one pipeline and task (Bouthillier et al., 2021); signal-to-noise per benchmark (Heineman et al., 2025); effective-test counts from correlation eigenvalues (Cheverud 2001; Nyholt 2004; Li and Ji 2005).
- **Why they fail**: They report marginal variances or count independent tests for threshold adjustment; none estimates the off-diagonal run covariance that enters the variance of a benchmark average.

### G2: Inference with few recipe clusters and ratio estimators
- **Statement**: The estimator is a ratio of pooled moments with 25 recipe clusters; interval validity is not guaranteed and the pooled denominator can be nonpositive.
- **Caused by**: O3
- **Existing attempts**: Few-cluster bootstrap literature (Cameron et al., 2008; MacKinnon and Webb, 2017; Bell and McCaffrey, 2002).
- **Why they fail**: No existing calibration for this specific statistic; coverage has to be checked by simulation.

### G3: Separation of run covariance from shared item effects
- **Statement**: Disjoint item identifiers do not guarantee independent item errors across halves; a scalar item effect shared across benchmarks and repeated across halves enters the numerator whole (share 0.124 of item variance would reproduce 1.244).
- **Caused by**: O2, O5
- **Existing attempts**: Passage-aware split for BoolQ; within-group item permutation.
- **Why they fail**: Both leave untouched an effect carried by every item of a benchmark; the disjoint-bank check (R2) that targets it is pending.

### G4: Generality beyond one battery and one model family
- **Statement**: The estimator and battery were developed on the same ten benchmarks and one family with a confounded seed design.
- **Caused by**: O3, O5, O8
- **Existing attempts**: Registered held-out test on four unseen tasks (failed its rule); earlier PolyPythias transfer (intervals include one); external signal-and-noise panel (no cross-half correction).
- **Why they fail**: Wide intervals at reduced scope, few configurations, or missing correction; the clean-seed second-family replication (R1) is pending.

### G5: Practical value of covariance correction is unquantified
- **Statement**: It is unclear whether a covariance correction changes decisions practitioners make on real recipe comparisons.
- **Caused by**: O1
- **Existing attempts**: Simulated correction of false-positive rates; flip-probability census.
- **Why they fail**: Simulated gains do not establish effects on real decisions; noisy observed gaps do not bound true small gaps.

## Key Insight
- **Insight**: Split each benchmark's items into two disjoint halves with a frozen assignment reused across runs, centre each half score across the replicate runs of a configuration, and take cross-half products. Under zero-mean item errors that are uncorrelated across halves, E[d^A_crj d^B_crk] = (1 - 1/R) Sigma_E,c(j,k), including the diagonal, so pooled cross-half sums give both the aggregate covariance (T_c) and its trace-only part (U_c), and their ratio gives the inflation factor without item-noise bias.
- **Derived from**: O2 (item noise is independent across disjoint halves under the stated assumptions), O3 (replicates exist within configurations).
- **Enables**: An item-general run-covariance estimate from released per-item scores with no model inference, an effective benchmark count, and recipe-cluster intervals.

## Assumptions
- A1: Run effects within a configuration are independent, identically distributed draws with covariance Sigma_E,c (the paper states it can't sustain this in full, because training schedules differ within the population).
- A2: Item errors have conditional mean zero and zero covariance between halves A and B across the relevant runs and benchmarks.
- A3: The battery of ten benchmarks with equal weights is the fixed target; benchmarks are not treated as draws from a population of benchmarks.
- A4: Recipe clusters are the independent sampling unit for intervals; a run effect following the size band would break this (bounded at 0.044 of seed covariance on margins by a permutation test with power 0.490 at the bound).
- A5: The released per-item outputs, the release's seed labelling and the documented settings of auxiliary runs are accurate (release provenance is not independently audited).
- A6: For the information-ratio calculation only, item margins follow a Gaussian location model.
- A7: The planned threshold values (1.349 margin, 1.40 accuracy) and gate definitions come from a planning document whose date is not independently corroborated.
- A8: For PolyPythias, the nine seeds are the replicate unit and each seed reruns one recipe with the same code, data and hyperparameters.
