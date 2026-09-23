# Claims

Status vocabulary: `supported` (evidence in the source backs the statement at the stated scope), `refuted` (a registered or planned test failed as written), `hypothesis` (stated but not resolved by the available evidence), `pending / untested` (the source describes the test but its results are not available). The paper labels every empirical analysis exploratory except the registered held-out test (C07) and the two PolyPythias rules fixed before scoring (C20, C21); each claim repeats its label.

## C01: Cross-half products identify item-general run covariance
- **Statement**: If item errors have conditional mean zero and zero covariance between halves A and B, and run effects within a configuration are i.i.d. with covariance Sigma_E,c, then E[d^A_crj d^B_crk] = (1 - 1/R) Sigma_E,c(j,k), diagonal included, without requiring Gaussian run effects; T_c and U_c then have expectations K^-2 1'Sigma_E,c 1 and K^-2 tr Sigma_E,c.
- **Status**: supported (derivation; the ratio and its square root are not unbiased)
- **Falsification criteria**: A counterexample population satisfying A1-A2 where the pooled moments are biased, or calibration simulations under independent noise returning mean inflation away from one beyond Monte Carlo error.
- **Proof**: [E01]
- **Evidence basis**: Derivation in Appendix A.3 (Equations 3-5 of the paper); under independent noise the calibration simulation returns mean inflation 1.0009 on margins and 1.0004 on accuracy; recovery slope 0.998 across effective coefficients from zero to 0.50 (supplement Table 9, §4.4).
- **Interpretation**: The target is covariance of run deviations that generalise across item halves; it can differ from the run variance of a fixed evaluation bank, and it is identified only up to any item effect shared across benchmarks and repeated across halves.
- **Dependencies**: none
- **Tags**: theory, identification, estimator, derivation

## C02: Margin inflation exceeds one on DataDecide
- **Statement**: On per-byte margins across 125 DataDecide configurations (375 runs, ten benchmarks), inflation is 1.244 with nominal 95% wild recipe-cluster interval [1.143, 1.338], which excludes one; a cluster test-inversion interval added later gives [1.095, 1.323].
- **Status**: supported (exploratory)
- **Falsification criteria**: A correct recomputation from the released per-item scores giving an interval that includes one, or evidence that the excess comes from a shared item effect (share near 0.124 of item-noise variance) rather than run covariance.
- **Proof**: [E02, E01]
- **Evidence basis**: Table 1 (raw margin row 1.244 [1.143, 1.338], K_eff 6.46, sigma_agg 0.00572); auxiliary contrast 1.256 [1.090, 1.400]; test inversion [1.095, 1.323] (§2.3, Appendix C); Beran prepivoting [1.151, 1.328]; residual-scaled wild [1.130, 1.349]; a separate Kaggle implementation reproduces primary estimates to three decimals; in 500 independent trait-specific run-label permutations none reaches the observed margin estimate and 0.028 reach the accuracy estimate (Appendix C "Permutation comparison").
- **Interpretation**: The battery-average spreads more across runs than independence predicts; the paper reads this as covariance among the released runs at the selected steps, not as seed-only covariance.
- **Dependencies**: C01
- **Tags**: headline, margin, DataDecide, exploratory

## C03: The ten-benchmark margin average behaves like 6.5 independent benchmarks
- **Statement**: At margin inflation 1.244, K_eff = K/Lambda^2 = 6.46 (reported as 6.5), with interval 5.6 to 7.7, relative to independent benchmarks of the same average variance; the effective covariance coefficient is 0.0608.
- **Status**: supported (exploratory)
- **Falsification criteria**: Same as C02, since K_eff is a deterministic transform of Lambda.
- **Proof**: [E02]
- **Evidence basis**: Table 1 (K_eff 6.46); §1 (interval 5.6 to 7.7); Appendix A.4 (r_E 0.0608 raw, 0.0695 gain-adjusted, 0.0641 auxiliary contrast).
- **Interpretation**: K_eff compares against independent benchmarks at the same average variance and does not count independent information sources; it differs from a spectral participation ratio (3.57 on nine margin traits).
- **Dependencies**: C02
- **Tags**: effective-count, margin, exploratory

## C04: Margin exclusion of one survives recipe, recipe-pair and benchmark deletion
- **Statement**: Recomputing the shipped margin interval after deleting each recipe, each recipe pair and each benchmark leaves an interval that excludes one every time; the only deletion that fails is the 530M size band, giving 1.178 with [0.993, 1.338].
- **Status**: supported (exploratory)
- **Falsification criteria**: Any recipe, recipe-pair or benchmark deletion yielding a margin interval that includes one.
- **Proof**: [E03]
- **Evidence basis**: Appendix C "Gain calibration and recipe split sensitivity"; recipe removal range 1.207 to 1.256; size removal 1.178 to 1.289; supplement Table 11 (every benchmark removal lower endpoint above one, minimum 1.054 without CommonsenseQA); simulation puts at least one band-deletion failure in 0.164 of populations whose full interval excludes one; flat-Dirichlet weight sweep leaves 0.817 of margin intervals excluding one.
- **Interpretation**: The margin verdict does not hinge on any single recipe or benchmark; it covers four fifths of the weight simplex and all of its neighbourhood.
- **Dependencies**: C02
- **Tags**: sensitivity, deletion, margin, exploratory

## C05: Accuracy gives a bound, not evidence of independence
- **Statement**: Accuracy inflation is 1.078 with interval [0.993, 1.157], which includes one; at this design a true ratio of 1.10 would be detected in 0.135 of replicates, so the primary analysis bounds accuracy inflation at 1.157 (r_E < 0.038, K_eff > 7.47).
- **Status**: supported (as a bound; exploratory)
- **Falsification criteria**: A correct recomputation with an interval excluding one at the full battery, or a power calculation showing high detection probability at 1.10.
- **Proof**: [E02, E03, E08]
- **Evidence basis**: Table 1 (accuracy raw 1.078 [0.993, 1.157], K_eff 8.60); §1 (power 0.135 at 1.10, simulation exclusion rate 0.111 at the fitted cell); interval stops including one under five of 25 recipe removals, removal of the 750M band, and removal of WinoGrande [1.023, 1.178] or BoolQ [1.412, 1.687]; lowering BoolQ's weight to 0.0867 stops the interval including one. Thresholding the saved margins item by item (sign score) gives 1.079 [0.992, 1.158], reproducing the accuracy figure (supplement Table 7).
- **Interpretation**: The accuracy conclusion is a knife edge in the weighting; the flat weighting is the conservative choice on accuracy (0.386 of flat-Dirichlet accuracy intervals exclude one).
- **Dependencies**: C01
- **Tags**: accuracy, power, bound, exploratory

## C06: BoolQ sets the magnitude and the factor belongs to the battery
- **Statement**: BoolQ contributes 68% of the margin and 84% of the accuracy covariance trace; removing it raises margin inflation to 1.786 [1.689, 1.877] and accuracy to 1.558 [1.412, 1.687] while lowering the aggregate standard deviation on both scales; removing CommonsenseQA gives 1.096 and 1.014.
- **Status**: supported (exploratory)
- **Falsification criteria**: Benchmark removal moving the estimate less than recipe or size removal, or BoolQ removal raising the aggregate standard deviation.
- **Proof**: [E03]
- **Evidence basis**: §4.1; Figure 1; supplement Table 11 (sigma_agg 5.72 to 5.16 x 10^-3 margins, 5.14 to 3.26 x 10^-3 accuracy); implied BoolQ off-diagonal terms about -0.15 of the margin trace and -0.06 of the accuracy trace; subsets with BoolQ average 0.115 lower margin inflation at two benchmarks and 0.596 lower at nine; supplement Table 12; with BoolQ removed every size band excludes one on margins (1.548, 1.864, 1.874, 1.888, 1.649 from 150M to 1B), which the paper reads as composition sensitivity reappearing at size resolution, not independent support.
- **Interpretation**: A larger factor can accompany a less variable average; the factor compares each battery with independence at its own marginal variances, and the benchmark-removal spread is not a distribution over benchmark collections.
- **Dependencies**: C02
- **Tags**: composition, BoolQ, battery-dependence, exploratory

## C07: The registered held-out test fails its rule
- **Statement**: The registered rule (lower 95% limit of held-out margin inflation above one) fails on all 225 runs at 530M, 750M and 1B: held-out margin inflation is 1.217 with interval [0.872, 1.498]; the original ten benchmarks on the same runs give 1.240 with [1.054, 1.397] and pass, a comparison fixed before any held-out score existed.
- **Status**: refuted (registered prediction failed at its registered scope)
- **Falsification criteria**: Not applicable to a failed registered test; the verdict would change only if the registered computation were shown to be wrong.
- **Proof**: [E04]
- **Evidence basis**: Table 2; held-out interval 0.626 wide against 0.343 for the original; point estimates differ by 0.024; three earlier interim results also failed (530M alone 1.198 [0.864, 1.454]; two sizes 1.201 [0.546, 1.616]; two sizes plus 18 recipes at 1B 1.181 [0.685, 1.552]); simulated pass rate at this scope with four traits is 0.926 at a true 1.244 under margin-like noise and 0.524 under accuracy-like noise, and 0.262 at the post hoc noise level 2.00 (supplement Table 19).
- **Interpretation**: Interval width rather than the point gap decides the verdict; the later power calculation can't rescue the registered test.
- **Dependencies**: C02
- **Tags**: registered, held-out, negative-result, confirmatory

## C08: Held-out accuracy inflation excludes one (exploratory)
- **Statement**: On the four held-out tasks, accuracy inflation is 1.220 with interval [1.066, 1.359], above the 1.097 [0.922, 1.246] that the original ten give at the same scope; removing CoQA lowers held-out margin inflation to 1.090, while removing any other task leaves it between 1.120 and 1.213.
- **Status**: supported (exploratory)
- **Falsification criteria**: Recomputation at the same scope giving an accuracy interval that includes one.
- **Proof**: [E04]
- **Evidence basis**: Table 2 (held-out accuracy row); §4.2; supplement Table 20 (leave-one-task-out).
- **Interpretation**: The held-out estimate depends on battery composition as the original does.
- **Dependencies**: C07
- **Tags**: held-out, accuracy, exploratory

## C09: Wild recipe-cluster bootstrap-t intervals are near nominal in simulation
- **Statement**: Across twelve simulated populations (125 configurations, 25 recipe clusters, three runs, ten benchmarks), the wild cluster bootstrap-t covers 0.928 to 0.954 at 2,000 replicates, while the configuration percentile bootstrap drops to 0.872 under recipe-shared run effects; finite-sample bias understates rather than manufactures an excess.
- **Status**: supported
- **Falsification criteria**: Coverage well below 0.95 in populations resembling the data, or positive bias under null populations.
- **Proof**: [E01]
- **Evidence basis**: Table 9; 10,000-replicate repeat puts wild coverage 0.933 to 0.953 and centred inversion 0.935 to 0.956; cross-half error correlation 0.1 biases the estimate by -0.014 (margin-like) and -0.016 (accuracy-like); accuracy-like null bias -0.011; band-shared run effect at a quarter of latent variance takes margin coverage to 0.821 and at a half to 0.580; in two scenarios fitted to the observed data the wild interval holds 0.954 and 0.946 on margins (fitted to the same data, so not independent confirmation).
- **Interpretation**: The shortfall of about 0.02 belongs to the construction; the residual-scaled variant (0.943 to 0.958) was chosen after seeing four cells and is not shipped.
- **Dependencies**: C01
- **Tags**: calibration, coverage, simulation

## C10: Item-level sharing checks do not account for the margin excess, but a benchmark-wide shared item effect is unmeasured
- **Statement**: Assigning BoolQ's 2,938 passages whole to halves changes the estimates by -0.0002 (margin) and -0.0001 (accuracy) on average across fifty re-splits; a within-group item permutation puts item-level sharing at about 0.001 of the margin and 0.002 of the accuracy estimate. A scalar item effect shared across benchmarks and repeated across halves at shares 0.124 and 0.009 of item-noise variance would reproduce 1.244 and 1.078, and it has not been measured.
- **Status**: supported for the sub-benchmark checks; hypothesis (untested) for the benchmark-wide item effect
- **Falsification criteria**: A passage-aware or grouped split moving the estimate beyond re-split variation (SD 0.002 margin, 0.008 accuracy), or a direct measurement of the shared scalar item effect near 0.124.
- **Proof**: [E05]
- **Evidence basis**: §4.1; Appendix A.3 (passage-aware split 1.248 and 1.097 on one split; SDs 0.0017 and 0.0060); Appendix C calibration (2,000 permutations: 0.087 reach the margin estimate, 0.352 the accuracy estimate; share 0.05 reaches the observed margin in only 0.007 of replicates); cross-half noise correlation sweep -0.1 to 0.5 leaves mean margin estimate 0.997 to 1.001.
- **Interpretation**: The passage null follows from BoolQ's passage structure (about 240 same-passage pairs across halves out of about 2.7 million) rather than from a sensitive test; the disjoint-bank R2 check is the design that targets the remaining item effect.
- **Dependencies**: C01, C02
- **Tags**: identification, item-dependence, passage, exploratory

## C11: Margin covariance sits within scoring formats
- **Statement**: Estimated margin correlations average 0.624 within formats and 0.007 across them; the cross-format diagnostic gives 0.921 [0.801, 1.035] against 1.244 for the full matrix; a two-correlation fit with benchmark seed variances gives 1.285 against 1.244, and 1.728 against 1.786 without BoolQ, with every leave-one-benchmark-out prediction within 0.054 of the observed deletion.
- **Status**: supported (exploratory, in-sample)
- **Falsification criteria**: Cross-format off-diagonal covariance comparable to within-format covariance, or a two-correlation fit failing to approximate observed deletions.
- **Proof**: [E06]
- **Evidence basis**: §4.4; Appendix C "Associations with scoring format" (54 of 90 ordered off-diagonal pairs retained; accuracy diagnostic 0.965 [0.848, 1.063]; without BoolQ 1.006 [0.972, 1.039]) and "A two-correlation fit" (equal variances give 1.803; leave-one-out errors 0.024 to 0.054).
- **Interpretation**: Format and task content are not separable because each benchmark sits in one format; a practitioner could approximate inflation for a new battery from its formats and seed variances, untested on any other battery.
- **Dependencies**: C02, C06
- **Tags**: mechanism, format, exploratory

## C12: Gain and competence adjustments carry no mechanistic reading
- **Statement**: Gain adjustment leaves margin inflation at 1.275 (the plan predicted more than 0.70 of the accuracy excess surviving); the shipped competence proxy is degenerate, with WinoGrande supplying more than 99.99% of its squared standardised inputs; repaired proxies fall below one even in simulations without a separate competence variable.
- **Status**: supported (negative result; exploratory)
- **Falsification criteria**: A proxy with measurable split-half signal whose adjustment departs from simulations with no competence variable.
- **Proof**: [E07]
- **Evidence basis**: §4.4; Appendix C "Competence proxy audit and calibration" and Table 10 (shipped floored 1.244; floored traits dropped 0.890; shrunken cross-fitted 0.731; shipped proxy split-half correlation -0.086 margins, -0.072 accuracy); clipped-drop weighting 0.889 against a simulated fifth percentile of 0.908.
- **Interpretation**: Every proxy averages the same seed deviations it adjusts, so adjustment removes shared covariance by construction; a competence adjustment needs a measurement outside the benchmark scores, such as held-out loss.
- **Dependencies**: C02
- **Tags**: mediation, gain, competence-proxy, dead-end, exploratory

## C13: The accuracy bound depends on the scored checkpoint
- **Statement**: At the adjacent earlier shared checkpoint the accuracy interval is [1.044, 1.210] and excludes one; on the 123 configurations with both steps, the paired change in accuracy inflation is 0.048 [-0.022, 0.130]; dropping the 26 severely truncated configurations gives 1.276 [1.114, 1.420] on margins and 1.120 [1.020, 1.208] on accuracy; the 33 configurations sharing a final step give intervals including one on both scales.
- **Status**: supported (exploratory, subsets chosen after seeing full-sample estimates)
- **Falsification criteria**: Accuracy intervals at adjacent checkpoints agreeing in their inclusion of one.
- **Proof**: [E08]
- **Evidence basis**: §3; Table 5; supplement Table 13 (margin 1.233 to 1.192, change -0.041 [-0.078, 0.001]); influence-truncation Spearman -0.036 margins, 0.001 accuracy.
- **Interpretation**: The accuracy bound is conditional on the checkpoint scored; the checks can't see an offset shared by every configuration.
- **Dependencies**: C05
- **Tags**: checkpoint, truncation, accuracy, exploratory

## C14: The planned thresholds were unreachable and the screening split was never formed
- **Statement**: No seventeen-recipe estimation set reaches the plan's thresholds of 1.349 (margin) and 1.40 (accuracy): enumerating all 1,081,575 sets gives margin estimates 1.037 to 1.317 and accuracy 0.963 to 1.191; the planned screening split was never drawn, and every choice in the primary analysis could see all 125 configurations.
- **Status**: refuted (planning prediction 1 fails; the holdout design was not implemented)
- **Falsification criteria**: Not applicable; the enumeration is exhaustive.
- **Proof**: [E09]
- **Evidence basis**: §3; supplement Table 18 (reconstructed planned partition 1.199 and 1.099; subsets reaching threshold 0 and 0); supplement Table 5 (prediction scorecard).
- **Interpretation**: The retrospective calculation can't restore a holdout or undo choices made after viewing the data.
- **Dependencies**: C02, C05
- **Tags**: preregistration, planning, dead-end

## C15: Earlier PolyPythias transfer is inconclusive
- **Statement**: PolyPythias gives margin inflation of 1.406 (1.40574) on the three planned sizes and 1.262 (1.26199) with configuration-bootstrap interval [0.927, 1.537] on a five-size rescore; accuracy is 1.711 [0.869, 2.428] and stays unbounded under test inversion.
- **Status**: hypothesis (intervals include one; not a replication)
- **Falsification criteria**: A PolyPythias interval excluding one below DataDecide's value, or a clean-seed replication (R1) passing or failing.
- **Proof**: [E10]
- **Evidence basis**: §4.4; Appendix C "Transport to PolyPythias" (4,755-item nested battery; inversion sets 0 to 2.106 at three sizes and 0.519 to 1.664 at five sizes; transport prediction G6 fails upward under the excess-ratio reading, a post hoc scale choice).
- **Interpretation**: Three or five configurations are too few to bound PolyPythias inflation; this motivated the full-battery second-family scoring in §4.3.
- **Dependencies**: C02
- **Tags**: transfer, PolyPythias, exploratory

## C16: An external seed panel shows the same score-scale contrast without confirming the estimand
- **Statement**: Released single-configuration panels from Heineman et al. (2025) give likelihood (bits-per-byte) inflation of 1.705 and 1.625 on eighteen traits and accuracy-per-character inflation of 0.989 and 0.868 on eight traits, without cross-half correction, intervals, or a matched trait count.
- **Status**: hypothesis (suggestive only)
- **Falsification criteria**: A corrected estimate on that panel reversing the score-scale ordering.
- **Proof**: [E11]
- **Evidence basis**: Table 11; §4.4.
- **Interpretation**: Suggests the same score-scale difference; planning prediction 7 lacks its required lower confidence limit.
- **Dependencies**: C02, C05
- **Tags**: external, score-scale, exploratory

## C17: Covariance models improve aggregate-SD prediction on margins only, with held-out marginals supplied
- **Statement**: Over five recipe folds with held-out marginal seed standard deviations supplied, rank-one, rank-one plus gain and full covariance models lower mean squared error of log aggregate standard deviation by about 0.03 from independence's 0.0358 on margins, with paired intervals excluding zero (the rank-one interval reaches zero under training-fold fill); on accuracy every difference interval includes zero; an operational comparison without held-out marginals separates no model from independence.
- **Status**: supported (exploratory)
- **Falsification criteria**: Margin difference intervals that include zero under the primary clipping rule.
- **Proof**: [E12]
- **Evidence basis**: Table 8 (independence 0.0358, rank-one 0.0057, rank-one plus gain 0.0063, plug-in 0.1073, full 0.0068, rescaled plug-in 0.0131 on margins); Appendix C "Paired uncertainty" (P1 [-0.058, -0.001], P1G [-0.059, -0.002], P3 [-0.060, -0.004]); out-of-sample single-configuration ratios on PolyPythias: mean absolute log error 0.339 independence, 0.536 plug-in, 0.512 decomposition; Frobenius distances between R_E and R_P of 5.59 (margins) and 6.49 (accuracy), 4.374 and 4.593 on jointly defined entries; mean defined R_E entries 0.281 and 0.273 against R_P means 0.750 and 0.754.
- **Interpretation**: The estimated ratio is a measurement of this battery and helps only where replicates are missing and the target battery's own ratio is close; the phenotypic plug-in fails on transfer of correlation structure.
- **Dependencies**: C02
- **Tags**: prediction, model-comparison, exploratory

## C18: Covariance correction matters in simulation but barely changes real recipe decisions
- **Statement**: In simulation a scaled independence standard error with a ratio estimated on the same margin population returns the false-positive rate from 0.113 to 0.051, and transferred to a battery whose own ratio is 1.5 leaves it at 0.101; on real recipe comparisons at four sizes, the correction removes between 1 and 12 of 173 to 223 calls and changes the wrong-call rate by at most 0.009, from rates between 0.029 and 0.070, with every recipe-bootstrap interval for that change reaching zero.
- **Status**: supported (exploratory)
- **Falsification criteria**: Real recipe comparisons where the correction changes the wrong-call rate with an interval excluding zero.
- **Proof**: [E13]
- **Evidence basis**: Table 3; Appendix C "Observed gaps and predicted rank reversals" (oracle 0.050; 455 of 1,500 same-size gaps below the 5% flip threshold; sign-reversal probability about 0.246 against 0.229 for a half-point gap); across 1,445 same-size recipe pairs with positive margin paired-difference variance, the paired-difference SD has median ratio 1.024 to independence (5th to 95th percentiles 0.39 to 1.40); extra runs per model buy power, not size control (four fifths power at one aggregate SD needs 16 runs on margins and 20 on accuracy, against three shipped).
- **Interpretation**: A wrong call here also counts genuine rank changes between sizes, so these rates are not false-positive rates; the recommendation is paired replicate scores across the chosen battery with a benchmark-removal check.
- **Dependencies**: C02, C05
- **Tags**: decision-impact, practice, exploratory

## C19: A band-shared run effect is bounded but not excluded
- **Statement**: A batch-slot permutation null bounds a run effect shared across recipes within a size band at 0.044 of the seed covariance on margins (point share 0.008), where simulated coverage stays 0.941 at a share of 0.05; the test's power is only 0.490 at the bound; size-band clustering gives margin [1.030, 1.426] and accuracy [0.961, 1.184].
- **Status**: supported (exploratory; low-powered bound)
- **Falsification criteria**: A higher-powered test detecting band sharing above 0.044.
- **Proof**: [E14]
- **Evidence basis**: §6; Appendix C "Gain calibration and recipe split sensitivity" (recipe-clustered coverage 0.821 at a quarter and 0.580 at a half of latent variance; ARC-Easy rescoring matched seeds in all 24 cells at 150M and fifteen loaded at 1B).
- **Interpretation**: The recipe clustering is a precaution the data can neither confirm nor rule out; within a single size the evidence is weaker (1B margin cluster-t [0.811, 1.628]).
- **Dependencies**: C09
- **Tags**: clustering, band-shared-effect, exploratory

## C20: Second-family replication on PolyPythias (R1)
- **Statement**: Under rule R1 fixed before scoring, margin inflation across 45 PolyPythias runs (nine seeds at 14M, 31M, 70M, 160M and 410M, step 143,000, bank 1 of 37,682 items) passes when the delete-one-seed jackknife t(8) lower endpoint exceeds one.
- **Status**: pending / untested (source values are `\pending{R1 lambda}` with `\pending{lo}`, `\pending{hi}`; outcome switch `\Ronecase=0`)
- **Falsification criteria**: Jackknife lower endpoint at or below one fails R1. The paper's pre-written fail branch notes that 40 within-configuration contrasts (against 250 in DataDecide) give synthetic estimates between 0.94 and 1.36 around a true 1.24, so a failure would bound the effect more than show it absent.
- **Proof**: [E15]
- **Evidence basis**: Not available: scoring in progress.
- **Interpretation**: Not available: scoring in progress. No outcome is selected in this ARA.
- **Dependencies**: C01, C02, C15
- **Tags**: replication, PolyPythias, rule-fixed-before-scoring, pending

## C21: Disjoint-bank check against a shared item component (R2)
- **Statement**: With every bank-one item as half A and every bank-two item (6,808 items built with OLMES at the DataDecide commit) as half B on the same 45 PolyPythias runs, rule R2 rejects the shared-item explanation when the cross-bank interval sits above one and the jackknife interval for the within-minus-cross difference in log inflation includes zero; it supports the explanation when the difference is positive and the cross-bank interval covers one; any other pattern is undecided.
- **Status**: pending / untested (source values are `\pending{cross lambda}` with pending intervals; outcome switch `\Rtwocase=0`)
- **Falsification criteria**: As stated by the rule; the three verdicts (not supported, supported, undecided) are mutually exclusive.
- **Proof**: [E16]
- **Evidence basis**: Not available: scoring in progress.
- **Interpretation**: Not available: scoring in progress. The paper notes the two banks also differ in split, item count and exemplar overlap, and that DataDecide was not scored on bank two, leaving 1.244 untested on fresh items and the shared-item check unrun in the headline family.
- **Dependencies**: C01, C10, C20
- **Tags**: identification, disjoint-bank, rule-fixed-before-scoring, pending
