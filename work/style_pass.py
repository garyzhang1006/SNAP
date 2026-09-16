from pathlib import Path
import json
edits={
'main.tex':[
('Benchmark averages reduce training variability according to the covariance between benchmark scores, which per-benchmark standard deviations leave unspecified.','Estimating the run-to-run uncertainty of a benchmark average requires covariance between scores as well as their marginal variances.'),
('These inflation estimates depend on the chosen benchmark battery. Removing BoolQ raises the factors to 1.786 and 1.558, and shared passages remain an unresolved source of bias.','Removing BoolQ raises the factors to 1.786 and 1.558, showing how much the full-battery estimates depend on its inclusion. Questions sharing a BoolQ passage can enter both item halves and bias the covariance estimate.'),
('These results support reporting replicate uncertainty and sensitivity to benchmark composition, while leaving a general independence approximation and a causal interpretation of margin covariance unresolved.','We recommend reporting replicate uncertainty and sensitivity to benchmark composition, with passage dependence and score-scale mechanisms still unresolved.'),
('A benchmark average can hide uncertainty from the training runs behind its component scores.','A benchmark average can change across training runs even when the evaluation items stay fixed.'),
('The construction uses the logic of repeated measurements and variance components, rather than a new identity for correlated averages.','We adapt the established repeated-measurement construction to paired benchmark scores from replicate runs.'),
('The distinction between a seed effect and run variation matters in this population.','Training conditions vary across the released runs in this population.'),
('Our contribution is an explicit estimand, a cross-half covariance construction with stated assumptions, and an empirical account of its limits on released language model runs.','We define the run covariance that cross-half products estimate and assess the assumptions required to interpret it in released language model runs.'),
('Calibration therefore checks the implemented estimator in specified populations, rather than proving an exact finite-sample null mean.','We use calibration simulations to check finite-sample behaviour in specified populations, where the ratio and square-root transformations can introduce bias.'),
('This result weakens a claim that its upper endpoint excludes the planned substantive threshold.','The excess lower-tail error makes the reported upper bound less reliable for comparison with the planned substantive threshold.'),
('The author-reported plan assigned eight recipes to screening and seventeen to estimation, but no stage of the pipeline drew that partition.','The analysis plan assigned eight recipes to screening and seventeen to estimation, but we used all recipes without drawing that partition.'),
('We retain its thresholds as historical targets, not as evidence of preregistration.','We report its thresholds as historical targets because their timing remains unverified.'),
('These outcomes describe sensitivity to simulator choices, not a causal interval for the fraction explained by sharpness.','Changing the simulator changes the attributed share, and the simulations provide no identified causal fraction for sharpness.'),
('We therefore report the disagreement without selecting the result with a smaller tail probability.','The permutation tail fraction and cluster interval answer different inferential questions, so we retain both results.'),
('Negative variance estimates are clipped before the model branch, while the target retains the original covariance contributions, introducing a further evaluation convention.','The evaluation clips negative variance estimates before fitting any model, but retains the original covariance contributions in the target.'),
('These precedents motivate a narrower contribution than a first measurement of any cross-dataset training dependence.','Our contribution concerns cross-half estimation of benchmark run covariance under explicit item-noise assumptions, building on those measurements of training dependence.'),
('The empirical results show why both the model and benchmark weights need attention.','In DataDecide, the estimated covariance depends on benchmark weights and on whether scores use margins or accuracy.'),
('The principal unresolved issues concern identification and inference.','Several features of the released runs limit identification and inference.'),
('The present evidence supports a conditional description of this battery, while additional passage-aware splits and reproducible paired model comparisons are needed before recommending an independence approximation more broadly.','Before recommending independence for other batteries, we need passage-aware splits and reproducible model comparisons that quantify uncertainty in paired prediction errors.')],
'appendix_a.tex':[
('The distinction between item-general variation and fixed-battery variation determines how a practitioner can use the estimate.','The item-general estimate can differ from the run variance of a fixed evaluation bank.'),
('The independence assumption concerns item effects, rather than whether two identifiers differ.','Different item identifiers can still refer to items with dependent errors.'),
('BoolQ is a specific unresolved case in this analysis.','BoolQ requires a passage-aware check that the present analysis lacks.'),
('The reported permutation coverage of 0.925 on margins is a reason to qualify the nominal interval, rather than evidence that a bootstrap automatically resolves concentration.','With reported margin coverage of 0.925 under permutation, the bootstrap leaves a measurable calibration error despite resampling the recipe clusters.'),
('The scale cancellation and minimum $\\pi/2$ belong to that model, rather than arbitrary empirical margin distributions.','Both the scale cancellation and minimum $\\pi/2$ require the Gaussian location model used in this calculation.')],
'appendices_bcd.tex':[
('These restrictions concern the replication required for this estimator.','We exclude these populations because they lack the matched replicates or item outputs required here.'),
('This distinction concerns the estimand, even where the underlying model panel overlaps.','Their item-level estimates and our benchmark covariance therefore answer different questions using some of the same models.'),
('These examples involve related dependence calculations on different measurement axes.','Those studies measure dependence across models, judges, or prompts, while we measure paired benchmark deviations across training runs.'),
('We retain the numerical results while distinguishing these qualifications from tests of verified prospective hypotheses.','Table~\\ref{tab:original6} retains the numerical outcomes and states where the assessment differs from the proposed criterion.'),
('The accuracy permutation result and the interval containing one should therefore remain separate reported findings.','We report both accuracy results because the disagreement depends on their different randomisation and sampling assumptions.'),
('These quantities measure concentration of variance across traits, while the noise-correlation participation ratio of 3.57 measures concentration across matrix directions. They describe different aspects of the same battery\'s weighting.','The first two ratios measure how strongly a few traits dominate variance, while the noise-correlation participation ratio of 3.57 measures concentration across matrix directions.'),
('Both preserve the qualitative finding of margin separation and accuracy non-separation from one.','The margin interval excludes one, and the accuracy interval includes one.'),
('This search limitation leaves the gain interpretation unresolved and doesn\'t turn simulator shares into causal bounds.','Without paired held-out loss and benchmark scores from the same runs, we can\'t use that release to identify the gain contribution.'),
('The external comparison remains suggestive rather than independent confirmation of the primary magnitude.','We therefore use this panel to compare score scales, with the size of item-noise attenuation still unmeasured.'),
('The sweep addresses sensitivity to recipe selection for the reported estimator, while it can\'t restore the absent prospective screening separation or remove other analysis choices made with the data visible.','The sweep measures sensitivity to recipe selection after the analysis choices were made, so it provides no check on choices that used the full dataset.')]
}
record=[]
for name,changes in edits.items():
 p=Path('deliverables')/name;s=p.read_text()
 for old,new in changes:
  assert s.count(old)==1,(name,old);s=s.replace(old,new);record.append({'file':name,'before':old,'after':new})
 p.write_text(s)
Path('work/style_pass_edits.json').write_text(json.dumps(record,indent=2)+'\n')
print(len(record),'documented edits')
