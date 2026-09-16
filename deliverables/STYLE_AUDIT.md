# Stop-slop and humanizer audit

The current revision contains 36 documented edits across two passes. `SNAP_style_pass_draft.zip` preserves the first pass, and `SNAP_editable_source.zip` contains the final revision. This audit is editorial material, not a research supplement.

## Assessment

The editorial score remains 47/50. It is a coarse, subjective judgment using stop-slop's five dimensions, not a percentage probability of human authorship. The edits improve particular passages without removing every reason for the existing deductions. No AI detector was run, and neither supplied skill defines or validates a test for “100% not AI.” This revision has known AI assistance, which remains disclosed in the paper.

| Dimension | Score | Evidence |
|---|---:|---|
| Directness | 10 | The abstract begins with the quantities needed to estimate uncertainty. The discussion states the BoolQ and schedule problems without generic setup sentences. |
| Rhythm | 9 | The discussion varies sentence length and clause structure. The numerical appendix still contains long sequences of result, comparison, and qualification. |
| Trust | 10 | Qualifications name the missing passage-aware check, unmatched schedules, and unmeasured paired error uncertainty. This score concerns how the prose treats readers, not independent validation of research claims. |
| Authenticity | 9 | The revision uses concrete study details and removes formulaic transitions. Repeated reporting constructions remain in the appendix, and there is no author-written comparison sample for assessing individual voice. |
| Density | 9 | Generic statements such as “This distinction concerns the estimand” now explain the exact difference. The retained planning history and sensitivity analyses still revisit some qualifications. |

## Audit between passes

The first pass left two generic discussion introductions and repeated benchmark-weighting language. The second pass revised those paragraphs while keeping their substantive qualifications. It also replaced the checkpoint paragraph's abstract opening with the named experiment and its comparison.

The literal phrase “rather than” decreased from 34 to 28 occurrences across manuscript source, “reported” from 44 to 41, capitalised “These” from 30 to 23, and capitalised “This” from 26 to 22. These counts document targeted changes, not a detector score or a word blacklist. The remaining occurrences require contextual judgment.

## Deliberate exceptions

Statistical adverbs remain where they carry meaning, including “approximately” for rounded quantities and “independently” for sampling assumptions. Equations and estimators can be grammatical subjects without inventing human agency. Scientific contrasts remain when they distinguish estimands, procedures, or assumptions. Published reference titles retain their wording. Removing these features indiscriminately would violate the humanizer instruction to preserve meaning.

The deterministic scan finds no prohibited prose punctuation or uncontracted negatives, and no prose segment shorter than the assumed eight-word minimum under its stated counting convention. This is full compliance with those checked mechanical constraints, not full compliance with every literal stop-slop instruction.

Displayed equations and all numeric table tokens are unchanged. The final PDF has eight main-text pages and 31 pages in total. It builds without unresolved references, font substitutions, missing characters, or overfull boxes.

## Complete edit record

### Edit 1, main.tex, pass 1

Before

> Benchmark averages reduce training variability according to the covariance between benchmark scores, which per-benchmark standard deviations leave unspecified.

After

> Estimating the run-to-run uncertainty of a benchmark average requires covariance between scores as well as their marginal variances.

### Edit 2, main.tex, pass 1

Before

> These inflation estimates depend on the chosen benchmark battery. Removing BoolQ raises the factors to 1.786 and 1.558, and shared passages remain an unresolved source of bias.

After

> Removing BoolQ raises the factors to 1.786 and 1.558, showing how much the full-battery estimates depend on its inclusion. Questions sharing a BoolQ passage can enter both item halves and bias the covariance estimate.

### Edit 3, main.tex, pass 1

Before

> These results support reporting replicate uncertainty and sensitivity to benchmark composition, while leaving a general independence approximation and a causal interpretation of margin covariance unresolved.

After

> We recommend reporting replicate uncertainty and sensitivity to benchmark composition, with passage dependence and score-scale mechanisms still unresolved.

### Edit 4, main.tex, pass 1

Before

> A benchmark average can hide uncertainty from the training runs behind its component scores.

After

> A benchmark average can change across training runs even when the evaluation items stay fixed.

### Edit 5, main.tex, pass 1

Before

> The construction uses the logic of repeated measurements and variance components, rather than a new identity for correlated averages.

After

> We adapt the established repeated-measurement construction to paired benchmark scores from replicate runs.

### Edit 6, main.tex, pass 1

Before

> The distinction between a seed effect and run variation matters in this population.

After

> Training conditions vary across the released runs in this population.

### Edit 7, main.tex, pass 1

Before

> Our contribution is an explicit estimand, a cross-half covariance construction with stated assumptions, and an empirical account of its limits on released language model runs.

After

> We define the run covariance that cross-half products estimate and assess the assumptions required to interpret it in released language model runs.

### Edit 8, main.tex, pass 1

Before

> Calibration therefore checks the implemented estimator in specified populations, rather than proving an exact finite-sample null mean.

After

> We use calibration simulations to check finite-sample behaviour in specified populations, where the ratio and square-root transformations can introduce bias.

### Edit 9, main.tex, pass 1

Before

> This result weakens a claim that its upper endpoint excludes the planned substantive threshold.

After

> The excess lower-tail error makes the reported upper bound less reliable for comparison with the planned substantive threshold.

### Edit 10, main.tex, pass 1

Before

> The author-reported plan assigned eight recipes to screening and seventeen to estimation, but no stage of the pipeline drew that partition.

After

> The analysis plan assigned eight recipes to screening and seventeen to estimation, but we used all recipes without drawing that partition.

### Edit 11, main.tex, pass 1

Before

> We retain its thresholds as historical targets, not as evidence of preregistration.

After

> We report its thresholds as historical targets because their timing remains unverified.

### Edit 12, main.tex, pass 1

Before

> These outcomes describe sensitivity to simulator choices, not a causal interval for the fraction explained by sharpness.

After

> Changing the simulator changes the attributed share, and the simulations provide no identified causal fraction for sharpness.

### Edit 13, main.tex, pass 1

Before

> We therefore report the disagreement without selecting the result with a smaller tail probability.

After

> The permutation tail fraction and cluster interval answer different inferential questions, so we retain both results.

### Edit 14, main.tex, pass 1

Before

> Negative variance estimates are clipped before the model branch, while the target retains the original covariance contributions, introducing a further evaluation convention.

After

> The evaluation clips negative variance estimates before fitting any model, but retains the original covariance contributions in the target.

### Edit 15, main.tex, pass 1

Before

> These precedents motivate a narrower contribution than a first measurement of any cross-dataset training dependence.

After

> Our contribution concerns cross-half estimation of benchmark run covariance under explicit item-noise assumptions, building on those measurements of training dependence.

### Edit 16, main.tex, pass 1

Before

> The empirical results show why both the model and benchmark weights need attention.

After

> In DataDecide, the estimated covariance depends on benchmark weights and on whether scores use margins or accuracy.

### Edit 17, main.tex, pass 1

Before

> The principal unresolved issues concern identification and inference.

After

> Several features of the released runs limit identification and inference.

### Edit 18, main.tex, pass 1

Before

> The present evidence supports a conditional description of this battery, while additional passage-aware splits and reproducible paired model comparisons are needed before recommending an independence approximation more broadly.

After

> Before recommending independence for other batteries, we need passage-aware splits and reproducible model comparisons that quantify uncertainty in paired prediction errors.

### Edit 19, appendix_a.tex, pass 1

Before

> The distinction between item-general variation and fixed-battery variation determines how a practitioner can use the estimate.

After

> The item-general estimate can differ from the run variance of a fixed evaluation bank.

### Edit 20, appendix_a.tex, pass 1

Before

> The independence assumption concerns item effects, rather than whether two identifiers differ.

After

> Different item identifiers can still refer to items with dependent errors.

### Edit 21, appendix_a.tex, pass 1

Before

> BoolQ is a specific unresolved case in this analysis.

After

> BoolQ requires a passage-aware check that the present analysis lacks.

### Edit 22, appendix_a.tex, pass 1

Before

> The reported permutation coverage of 0.925 on margins is a reason to qualify the nominal interval, rather than evidence that a bootstrap automatically resolves concentration.

After

> With reported margin coverage of 0.925 under permutation, the bootstrap leaves a measurable calibration error despite resampling the recipe clusters.

### Edit 23, appendix_a.tex, pass 1

Before

> The scale cancellation and minimum $\pi/2$ belong to that model, rather than arbitrary empirical margin distributions.

After

> Both the scale cancellation and minimum $\pi/2$ require the Gaussian location model used in this calculation.

### Edit 24, appendices_bcd.tex, pass 1

Before

> These restrictions concern the replication required for this estimator.

After

> We exclude these populations because they lack the matched replicates or item outputs required here.

### Edit 25, appendices_bcd.tex, pass 1

Before

> This distinction concerns the estimand, even where the underlying model panel overlaps.

After

> Their item-level estimates and our benchmark covariance therefore answer different questions using some of the same models.

### Edit 26, appendices_bcd.tex, pass 1

Before

> These examples involve related dependence calculations on different measurement axes.

After

> Those studies measure dependence across models, judges, or prompts, while we measure paired benchmark deviations across training runs.

### Edit 27, appendices_bcd.tex, pass 1

Before

> We retain the numerical results while distinguishing these qualifications from tests of verified prospective hypotheses.

After

> Table~\ref{tab:original6} retains the numerical outcomes and states where the assessment differs from the proposed criterion.

### Edit 28, appendices_bcd.tex, pass 1

Before

> The accuracy permutation result and the interval containing one should therefore remain separate reported findings.

After

> We report both accuracy results because the disagreement depends on their different randomisation and sampling assumptions.

### Edit 29, appendices_bcd.tex, pass 1

Before

> These quantities measure concentration of variance across traits, while the noise-correlation participation ratio of 3.57 measures concentration across matrix directions. They describe different aspects of the same battery's weighting.

After

> The first two ratios measure how strongly a few traits dominate variance, while the noise-correlation participation ratio of 3.57 measures concentration across matrix directions.

### Edit 30, appendices_bcd.tex, pass 1

Before

> Both preserve the qualitative finding of margin separation and accuracy non-separation from one.

After

> The margin interval excludes one, and the accuracy interval includes one.

### Edit 31, appendices_bcd.tex, pass 1

Before

> This search limitation leaves the gain interpretation unresolved and doesn't turn simulator shares into causal bounds.

After

> Without paired held-out loss and benchmark scores from the same runs, we can't use that release to identify the gain contribution.

### Edit 32, appendices_bcd.tex, pass 1

Before

> The external comparison remains suggestive rather than independent confirmation of the primary magnitude.

After

> We therefore use this panel to compare score scales, with the size of item-noise attenuation still unmeasured.

### Edit 33, appendices_bcd.tex, pass 1

Before

> The sweep addresses sensitivity to recipe selection for the reported estimator, while it can't restore the absent prospective screening separation or remove other analysis choices made with the data visible.

After

> The sweep measures sensitivity to recipe selection after the analysis choices were made, so it provides no check on choices that used the full dataset.

### Edit 34, main.tex, pass 2

Before

> SNAP estimates cross-half covariance under a measurement model that separates item-general run effects from item-dependent noise. In DataDecide, the estimated covariance depends on benchmark weights and on whether scores use margins or accuracy. Accuracy inflation is small for the full DataDecide battery, while a single benchmark removal produces a larger estimate. Margin covariance also changes with scoring format and gain simulation assumptions, so neither score scale supports an unqualified statement about independent benchmark noise.

After

> SNAP estimates cross-half covariance under a measurement model that separates item-general run effects from item-dependent noise. Accuracy inflation is small for the full DataDecide battery, but removing BoolQ raises the estimate. The margin estimate depends on scoring format and gain simulation assumptions. Together, these sensitivities leave insufficient evidence for a general approximation of independent benchmark noise.

### Edit 35, main.tex, pass 2

Before

> Several features of the released runs limit identification and inference. Shared BoolQ passages can bias the dominant diagonal term, common-step scoring leaves training-schedule differences, and the competence adjustment is dominated by variance flooring. The margin interval has imperfect coverage under the reported permutation reference, and prediction rankings lack paired uncertainty estimates. A held-out text loss would help assess score-scale mechanisms, but wouldn't by itself identify a causal competence component. The original screening split was never implemented, which leaves the empirical study exploratory throughout.

After

> Shared BoolQ passages can bias the dominant diagonal term, and common-step scoring leaves differences between training schedules. Variance flooring lets one benchmark dominate the competence adjustment, while held-out text loss would provide a separate measurement for assessing score-scale mechanisms. That measurement alone wouldn't identify a causal competence component. Inference also remains limited by imperfect margin coverage under permutation and missing paired uncertainty for prediction rankings. We used the full dataset without the planned screening split, so the empirical study remains exploratory throughout.

### Edit 36, main.tex, pass 2

Before

> The reported adjacent-checkpoint experiment also limits a seed-only interpretation. Across nine PolyPythias 160M runs, moving 1,000 steps changes aggregate scores by 0.89 between-seed standard deviations on margins and 1.57 on accuracy. This narrow experiment doesn't quantify the corresponding effect at DataDecide's selected steps, but demonstrates that checkpoint choice can matter at the scale of the variation under study.

After

> Checkpoint choice introduces another source of variation in the reported PolyPythias experiment. Across nine 160M runs, moving 1,000 steps changes aggregate scores by 0.89 between-seed standard deviations on margins and 1.57 on accuracy. Those changes are comparable to the between-seed variation, although their size at DataDecide's selected steps remains unmeasured.
