# Heuristics

## H01: Pool T_c and U_c across configurations before taking the ratio
- **Rationale**: Each configuration's denominator uses two replicate degrees of freedom and can approach zero or turn negative; averaging per-configuration ratios would give those unstable denominators disproportionate weight.
- **Sensitivity**: high
- **Bounds**: Requires a positive pooled denominator; pooling does not remove influence concentration (one recipe holds 0.520 of squared margin influence; removing it moves the estimate by 0.037).
- **Code ref**: [src/execution/snap_estimator.py]
- **Source**: §2.2; Appendix A.5

## H02: Centre through an orthonormal basis of mean-zero run contrasts
- **Rationale**: Raw cross-half products contain squared configuration means, which the analysis record reports can inflate the ratio by roughly three orders of magnitude; projecting onto contrasts enforces centring at the estimator input.
- **Sensitivity**: high
- **Bounds**: R >= 2 runs per configuration; runtime checks on basis row sums and invariance of sum T_c under a shared configuration shift.
- **Code ref**: [src/execution/snap_estimator.py]
- **Source**: Appendix D.3, D.7

## H03: Freeze a balanced within-trait split and reuse it for every run
- **Rationale**: Splitting within trait keeps both halves covering all ten traits (a pooled split could leave a 500-item benchmark unbalanced); reusing the assignment keeps runs comparable. Uses a seeded permutation rather than an item-ID hash.
- **Sensitivity**: low (fifty re-splits give standard deviations 0.002 margins and 0.008 accuracy)
- **Bounds**: Master seed 20260101; each trait needs at least two items; each arm has its own split.
- **Code ref**: [src/execution/snap_estimator.py]
- **Source**: Algorithm 1; Appendix D.1; `src/seednoise/halves.py`

## H04: Keep items that share a passage or story in one half
- **Rationale**: Shared passages can connect the halves and violate the cross-half independence assumption.
- **Sensitivity**: low on this battery (BoolQ passage-aware split moves estimates by -0.0002 and -0.0001 on average)
- **Bounds**: Half sizes then differ by a few items and the equal-half derivation holds only approximately; CoQA grouped into 479 stories for 1,000 items.
- **Code ref**: [src/execution/snap_estimator.py]
- **Source**: §4.1; Appendix A.3; Appendix C "Registered held-out test"

## H05: Wild cluster bootstrap-t with a fixed observed denominator
- **Rationale**: Few-cluster inference over 25 recipes; the studentised wild bootstrap covered 0.928 to 0.954 in simulation where the configuration percentile bootstrap fell to 0.872 under recipe-shared effects.
- **Sensitivity**: medium
- **Bounds**: 4,999 Rademacher draws, bootstrap seed 0; discard draws with zero bootstrap SE; require at least max(100, 0.9B) finite draws; coverage shortfall about 0.02 below nominal; fails under band-shared effects.
- **Code ref**: [src/execution/snap_inference.py]
- **Source**: §2.3; Appendix D.2; Table 9

## H06: Record a negative lower squared-ratio endpoint as missing
- **Rationale**: Square-root endpoints exist only for nonnegative squared-ratio endpoints; truncating at zero would misstate the interval.
- **Sensitivity**: low
- **Bounds**: Affects thin cells (1B margins in Table 7); alternative positive constructions (log-scale, cluster t) reported beside.
- **Code ref**: [src/execution/snap_inference.py]
- **Source**: Appendix D.2; Appendix C "Variation across model sizes"

## H07: Keep benchmarks with negative estimated diagonal covariance
- **Rationale**: An unbiased moment estimate can be negative near zero; deleting a benchmark after seeing its estimate changes both the selection rule and the estimand.
- **Sensitivity**: medium (standardised diagnostics that drop such traits give 1.803 on nine margin traits)
- **Bounds**: Applies to the primary estimand; correlation-normalised diagnostics necessarily omit such traits.
- **Code ref**: [src/execution/snap_estimator.py]
- **Source**: §3; Appendix A.3

## H08: Report benchmark-removal spread beside the interval
- **Rationale**: The factor belongs to the battery; benchmark removal moves the estimate more than recipe or size removal (1.096 to 1.786 on margins).
- **Sensitivity**: high
- **Bounds**: Descriptive; the ten benchmarks are not exchangeable draws, so jackknife composition scales are not validated intervals.
- **Code ref**: [src/execution/snap_inference.py]
- **Source**: Algorithm 1 step 7; §4.1; Appendix C "Recipe, size and trait sensitivity"

## H09: Score each configuration at the largest step common to all its runs
- **Rationale**: Aligns the observation step across replicates so that run deviations are compared at one checkpoint.
- **Sensitivity**: medium (accuracy verdict changes at the adjacent earlier step)
- **Bounds**: Leaves schedule differences within configurations (750M default runs at an average 41.5% of final step).
- **Code ref**: [src/execution/snap_estimator.py]
- **Source**: §3; Appendix B.1

## H10: Use a delete-one-seed jackknife with t(R-1) when clusters are few
- **Rationale**: For PolyPythias the nine seeds are the replicate unit and five size clusters are too few for the wild bootstrap.
- **Sensitivity**: medium
- **Bounds**: Requires the same seed index across configurations; eight degrees of freedom; results pending.
- **Code ref**: [src/execution/snap_inference.py]
- **Source**: §4.3; `compute2/analysis/estimates.py` (`seed_jackknife`)

## H11: Permute run labels independently per trait for the null reference
- **Rationale**: A joint permutation across traits preserves cross-trait pairing and can't produce the independence null; identity permutations remain valid members.
- **Sensitivity**: low
- **Bounds**: Conditional randomisation; requires exchangeability beyond zero mean covariance; E_pi of the squared ratio equals one, not of Lambda.
- **Code ref**: [src/execution/snap_inference.py]
- **Source**: Appendix A.6; Appendix D.3

## H12: Report an auxiliary-run contrast beside the three-run estimate
- **Rationale**: Removes the default-versus-auxiliary batch component that enters the three-run cross-trait products.
- **Sensitivity**: low on margins (1.256 against 1.244)
- **Bounds**: Doesn't remove differences shared with checkpoint schedules; wider intervals.
- **Code ref**: [src/execution/snap_estimator.py]
- **Source**: Table 1; Appendix B.4 (gate G8)

## H13: Clip negative held-out variance estimates before fitting prediction models, keep original targets
- **Rationale**: Covariance models need nonnegative marginals; the target retains the original covariance contributions so the comparison is not redefined.
- **Sensitivity**: medium (under training-fold fill the rank-one interval reaches zero)
- **Bounds**: Clipping touches two margin and five accuracy traits across folds; two alternative rules reported.
- **Code ref**: [src/execution/snap_inference.py]
- **Source**: Appendix C "Paired uncertainty"; "Transport to PolyPythias"

## H14: Apply a registered replacement rule as written, even at the margin of sampling error
- **Rationale**: Registration is only meaningful if its rules decide; both AGIEval tasks missed the chance-plus-0.02 bar by about a thousandth, inside the pilot's binomial SE of about 0.010, and were replaced by DROP and CoQA.
- **Sensitivity**: high for task identity (removing CoQA lowers held-out margin inflation to 1.090)
- **Bounds**: The rule, not the evidence, decided the swap.
- **Code ref**: [src/execution/snap_inference.py]
- **Source**: §4.2; Appendix C "Registered held-out test"
