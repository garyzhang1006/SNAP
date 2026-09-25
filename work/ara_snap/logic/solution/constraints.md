# Constraints and Limitations

## Boundary conditions of the estimator
- Identification requires zero-mean item errors with zero cross-half covariance; disjoint item identifiers alone don't establish it (shared passages, duplicate stems such as 62 of 1,838 PIQA items, and two stems shared across traits remain ungrouped outside BoolQ).
- A scalar item effect shared across benchmarks and repeated across halves enters the numerator whole and the denominator only a tenth; shares of 0.124 (margin) and 0.009 (accuracy) of item-noise variance reproduce the observed estimates. Unmeasured; a regression diagnostic has no power to separate it from seed covariance that follows item-noise scales.
- Unbiasedness of T_c and U_c does not carry over to their ratio or square root; either pooled sum can be nonpositive; a negative lower squared endpoint is recorded as missing (1B margin in Table 7).
- The largest discrepancy between opposite cross-half covariance entries is 2.44 bootstrap standard errors, which doesn't by itself establish leakage; the reduced item records carry 57 MMLU subject groups but only one group for each other trait.
- The covariance moment estimate need not be positive semidefinite; the accuracy correlation estimate is not a valid correlation matrix (entry 1.296, eigenvalue -0.55) and is kept unprojected.
- The inflation factor belongs to a fixed battery and weighting; benchmark-subset spreads describe this battery and do not sample a population of batteries.
- Lambda compares against independence at the battery's own marginal variances; K_eff is not a count of independent information sources.

## Design assumptions that the released runs can't be shown to satisfy
- Run effects are not i.i.d. within configurations: DataDecide seeds change initialisation and data order together, auxiliary runs below 1B use shortened schedules, and checkpoints differ in truncation (26 severely truncated configurations, 25 at 750M). The estimate is covariance among released runs at the selected steps.
- The release shares one seed label across all recipes in a size band; a band-shared run effect would break recipe clustering (coverage 0.821 at a quarter of latent variance, 0.580 at a half). Bounded at 0.044 of seed covariance on margins by a test with power 0.490 at the bound.
- Release provenance (tokeniser builds, harness revisions, auxiliary settings) is not audited independently.
- Format and content are confounded because each benchmark appears in one format.

## Statistical power limits
- Accuracy: at 125 configurations and three runs, a true ratio of 1.10 is detected in 0.135 of replicates; four fifths power needs between 500 and 1,000 configurations at six runs.
- Registered test: four 1,000-item tasks at three sizes give intervals 0.626 wide against 0.343 for the original ten; the rule reads the lower limit.
- PolyPythias: 40 within-configuration contrasts against 250 in DataDecide; on the synthetic population shipped with the code, this design returns estimates between 0.94 and 1.36 around a true 1.24.
- Single size bands: accuracy intervals cover only 0.707 at three runs on an accuracy-like population.
- Equicorrelated seed covariance at 125 configurations: three runs let the margin interval exclude one in 0.997 of replicates, while accuracy needs eight runs to reach 0.803.
- Realised linearised SEs (0.045 margins, 0.038 accuracy on the Lambda scale) are smaller than planning values (0.0935, 0.1232) by factors of 2.1 and 3.3, against about 1.21 expected from the larger configuration count alone; the paper does not compute power from the observed effect.

## Scope and provenance limits
- Every analysis apart from the registered held-out test and the two PolyPythias rules is exploratory; primary-analysis choices could see all 125 configurations.
- The planning document (claimed date September 5, 2026) has neither a supplied original file nor an independently corroborated date; its screening split (eight screening, seventeen estimation recipes) was never formed; the plan's proposed responses to gates G3 and G5 were not executed.
- The registered protocol's and the R1/R2 rules' commit times are not independently corroborated.
- The registered test was limited by GPU budget to 225 runs at 530M, 750M and 1B; a six-task secondary analysis was withdrawn.
- DataDecide was not scored on the second bank, so 1.244 is untested on fresh items and the shared-item check is unrun in the headline family. The compute2 README also plans rule R3 (headline on fresh items) and optional curve and zero-shot arms; the paper reports none of them.
- R1 and R2 results: Not available: scoring in progress.
- The PolyPythias transfer, five-size rescore and checkpoint results come from earlier execution records not rerun in this revision; the loss-proxy rescoring was not run.
- A competence adjustment needs a measurement outside the benchmark scores (held-out loss); DataDecide fields inspected don't supply it, although all 375 runs reach public commits with weights.
- An independence approximation used outside the studied battery can understate uncertainty; a correction transferred between batteries holds nominal size only within about 0.05 of the source ratio.

## Numerical and hardware constraints
- Derived quantities use unrounded estimates; recomputation from printed three-decimal values can differ in the last digit.
- Bootstrap draws come from NumPy's default generator, whose stream is tied to the NumPy version (2.0.2).
- Changing the scoring token budget changes batch grouping and can shift floating-point results (0.6 percent inflation shift in the transport rescore); a Turing-versus-Ada comparison changed 18 of 4,755 accuracy bits.

## Disclosures stated by the paper
- AI use statement: generative AI tools were used only to polish wording, find related work, and give minor help with analysis code.
- Ethics statement: the study analyses released model outputs with no new participant recruitment or data collection; derived artifacts must retain source attribution and licensing requirements.
