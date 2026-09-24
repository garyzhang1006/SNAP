"""ASD-STE100 pass on the main text: -ing verb forms, noun clusters over three words, phrasal verbs and
paragraphs over six sentences, with cuts of repeated numbers to hold the page-9 limit.
usage: python3 work/goal/edits_ste_main.py [--apply]"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[2] / "deliverables" / "main.tex"
E = [
    # abstract
    ("the ten-benchmark average's standard deviation in per-byte margin is",
     "the standard deviation of the ten-benchmark average in per-byte margin is"),
    ("Correcting for the covariance changes few of DataDecide's recipe orderings.",
     "A correction for the covariance changes few of DataDecide's recipe orderings."),
    ("A test on four held-out tasks that we fixed before scoring fails at 1.217",
     "A pre-specified test on four held-out tasks fails at 1.217"),
    ("{A second rule fixed before scoring passes, with", "{A second pre-specified rule passes, with"),
    ("{A second rule fixed before scoring also fails, since", "{A second pre-specified rule also fails, since"),
    ("We recommend reporting the replicate standard deviation of the battery average together with a benchmark-removal check",
     "We recommend that authors report the replicate standard deviation of the battery average with a benchmark-removal check"),
    # introduction
    ("Assuming independence drops the off-diagonal terms", "An independence assumption drops the off-diagonal terms"),
    ("(Appendix~\\ref{app:supplementary}). Figure~\\ref{fig:teaser} shows where that covariance sits in the DataDecide battery. Because the correction",
     "(Appendix~\\ref{app:supplementary}). Because the correction"),
    ("We estimate item-general covariance from two disjoint item halves per benchmark, centring both half scores across each configuration's replicate runs and taking their cross-half products. Under zero-mean item noise and conditional independence across halves, they estimate run covariance, including its diagonal.",
     "Figure~\\ref{fig:teaser} shows where that covariance sits in the DataDecide battery. We estimate item-general covariance from two disjoint item halves per benchmark, where we centre both half scores across each configuration's replicate runs and take their cross-half products. Under zero-mean item noise and conditional independence across halves, these products estimate run covariance with its diagonal."),
    ("Margins carry more seed signal, with per-benchmark reliability, the run variance's share of a benchmark half's replicate variance, averaging 0.652 against 0.324 for accuracy",
     "Margins carry more seed signal, since their per-benchmark reliability, the run variance's share of the replicate variance of one benchmark half, has a mean of 0.652 against 0.324 for accuracy"),
    ("Two rules fixed before scoring read the results, and in simulation", "Two pre-specified rules read the results, and in simulation"),
    ("This paper makes four contributions to measuring run covariance.", "This paper makes four contributions to the measurement of run covariance."),
    ("The split adds per-benchmark run variances net of item noise and a redrawn-bank target, untested on DataDecide. The two part ways when item noise is large, at 1.285 against 1.558 for accuracy without BoolQ (Section~\\ref{sec:estimator}).",
     "The split adds per-benchmark run variances net of item noise and a redrawn-bank target, untested on DataDecide, and its value parts from the replicate one when item noise is large, at 1.558 against 1.285 for accuracy without BoolQ (Section~\\ref{sec:estimator})."),
    # estimand
    ("by $y^{\\mathrm{marg}}$ and $y^{\\mathrm{acc}}$, calling each a trait.", "by $y^{\\mathrm{marg}}$ and $y^{\\mathrm{acc}}$ and call each a trait."),
    ("When deriving unbiasedness we assume", "For the unbiasedness derivation we assume"),
    ("We centre each half score across replicate runs, giving $d^H_{crj}", "We centre each half score across replicate runs and write $d^H_{crj}"),
    ("covers diagonal entries without requiring Gaussian run effects.", "covers diagonal entries and doesn't require Gaussian run effects."),
    ("with documented shared passages by keeping each passage in one half.", "with documented shared passages, where we keep each passage in one half."),
    ("We identify the estimate only up to a deviation tied to items that both halves share. Cross-format inflation",
     "We identify the estimate only up to a deviation tied to items that both halves share.\n\nCross-format inflation"),
    ("they can rise when removing a high-variance benchmark lowers", "they can rise when the removal of a high-variance benchmark lowers"),
    ("Subtracting item-sampling variance from the full-data diagonal instead needs",
     "A subtraction of item-sampling variance from the full-data diagonal instead needs"),
    ("and 0.186 of the accuracy one, leaving the two targets nearly equal.", "and 0.186 of the accuracy one, so the two targets are nearly equal."),
    ("In these populations finite-sample bias works against finding an excess.", "In these populations finite-sample bias makes an excess harder to find."),
    # data
    ("The auxiliary-run contrast, at 1.256, removes the batch component. Dropping the 26 severely truncated configurations removes the 750M band and one 530M configuration, giving margin inflation 1.276 (\\ci{1.114}{1.420}) and accuracy inflation 1.120 (\\ci{1.020}{1.208}), a subset we chose after seeing the full-sample estimates.",
     "The auxiliary-run contrast, at 1.256, removes the batch component. The 26 severely truncated configurations cover the 750M band and one 530M configuration, and without them margin inflation is 1.276 (\\ci{1.114}{1.420}) and accuracy inflation 1.120 (\\ci{1.020}{1.208}), a subset we chose after we saw the full-sample estimates."),
    ("share of the default final step (Appendix~\\ref{app:schedule}). At the adjacent earlier shared step",
     "share of the default final step (Appendix~\\ref{app:schedule}).\n\nAt the adjacent earlier shared step"),
    ("We retain the full battery for our primary estimand, including benchmarks with negative estimated diagonal covariance, since an unbiased moment estimate can be negative near zero and deleting such a benchmark would change the estimand.",
     "We retain the full battery for our primary estimand with the benchmarks whose estimated diagonal covariance is negative, since an unbiased moment estimate can be negative near zero and the deletion of such a benchmark would change the estimand."),
    ("with OLMES at a pinned commit, taking the train split for eight benchmarks", "with OLMES at a pinned commit, with the train split for eight benchmarks"),
    # results
    ("Accuracy carries little seed signal at the benchmark level, where reliability averages 0.324 against 0.652 on margins, and Table~\\ref{tab:original3} and Appendix~\\ref{app:supplementary} give the per-benchmark diagnostics, none of which enter the headline ratio because it uses covariance products directly.",
     "Table~\\ref{tab:original3} and Appendix~\\ref{app:supplementary} give the per-benchmark diagnostics, which don't enter the headline ratio because it uses covariance products directly."),
    ("averaging 0.624 within formats and 0.007 across them, excluding WinoGrande's undefined correlations",
     "with means of 0.624 within formats and 0.007 across them when we exclude WinoGrande's undefined correlations"),
    ("carries 68\\% of the margin covariance trace and 84\\% of the accuracy trace. Removing it raises margin inflation",
     "carries 68\\% of the margin covariance trace and 84\\% of the accuracy trace, and its removal raises margin inflation"),
    ("Removing CommonsenseQA instead gives inflation estimates", "The removal of CommonsenseQA instead gives inflation estimates"),
    ("off-diagonal terms involving BoolQ summing to about", "off-diagonal terms with BoolQ that sum to about"),
    ("Lowering BoolQ's weight from a tenth to 0.0867 already stops the accuracy interval including one",
     "A BoolQ weight of 0.0867 in place of a tenth already gives an accuracy interval that excludes one"),
    ("from the release's request files, and assigning each passage whole to one half changes the two estimates by $-0.0002$ and $-0.0001$ on average across fifty re-splits.",
     "from the release's request files, and when we assign each passage whole to one half, the two estimates change by $-0.0002$ and $-0.0001$ on average across fifty re-splits."),
    ("where the deletion of 530M gives \\ci{0.993}{1.338} and stops excluding one.", "where the deletion of 530M gives \\ci{0.993}{1.338}, an interval that includes one."),
    ("with a pre-specified rule replacing any task whose", "with a pre-specified rule that replaced any task whose"),
    ("Removing CoQA lowers held-out margin inflation to 1.090, and removing any other task leaves it between 1.120 and 1.213.",
     "Without CoQA, held-out margin inflation falls to 1.090, and without any other task it stays between 1.120 and 1.213."),
    ("Two rules fixed before scoring decide what the runs show.", "Two pre-specified rules decide what the 45 runs show."),
    ("The banks also differ in item count and exemplar overlap, and bank two draws most of its items from train splits, which pretraining data are more likely to contain. Any covariance these differences carry also enters the cross-bank estimate.",
     "Any covariance from the banks' other differences also enters the cross-bank estimate, since they differ in item count and exemplar overlap and bank two draws most of its items from train splits, which pretraining data are more likely to contain."),
    ("We simulated both rules after fixing them, drawing seed effects and item noise from the DataDecide margin fit",
     "We simulated both rules after we fixed them, with seed effects and item noise drawn from the DataDecide margin fit"),
    ("\\ci{\\res{xlo}{lo}}{\\res{xhi}{hi}} covering one.", "\\ci{\\res{xlo}{lo}}{\\res{xhi}{hi}} that covers one."),
    ("Margin correlations track scoring format, and cross-format inflation is 0.921 against 1.244 for the full matrix. Format and task content aren't separable in this battery. Setting within-format correlations to their mean of 0.624 and cross-format ones to 0.007, keeping benchmark seed variances, gives margin inflation of 1.285 against the observed 1.244 and 1.728 against 1.786 without BoolQ. The fit is in sample, and Appendix~\\ref{app:formatfit} checks it with each benchmark left out.",
     "Format and task content aren't separable in this battery. If we set within-format correlations to their mean of 0.624 and cross-format ones to 0.007 and keep the benchmark seed variances, margin inflation is 1.285 against the observed 1.244, and 1.728 against 1.786 without BoolQ. The fit is in sample, and Appendix~\\ref{app:formatfit} checks it with each benchmark held out."),
    ("on five recipe folds, fitting the run-covariance models off fold", "on five recipe folds and fit the run-covariance models off fold"),
    ("and an operational comparison refitting without held-out marginals", "and an operational comparison that refits without held-out marginals"),
    ("computed either under independence or with the estimated covariance, leaving the pair out of both estimates.",
     "computed either under independence or with the estimated covariance, and neither estimate uses the pair."),
    ("these rates aren't false-positive rates in the usual sense. On PolyPythias null seed pairs",
     "these rates aren't false-positive rates in the usual sense.\n\nOn PolyPythias null seed pairs"),
    ("0.016 for runs that don't, every interval reaching zero.", "0.016 for runs that don't, and every interval reaches zero."),
    # discussion
    ("Exploratory cuts excluding one, without BoolQ", "Exploratory cuts that exclude one, without BoolQ"),
    ("give a margin interval too wide to test the full estimate. Our populations stop at 1B",
     "give a margin interval too wide to test the full estimate.\n\nOur populations stop at 1B"),
    ("and we recommend reporting it with a benchmark-removal check.", "and we recommend that authors report it with a benchmark-removal check."),
]

t = P.read_text()
for old, new in E:
    n = t.count(old)
    if n != 1:
        sys.exit(f"expected one match, found {n}: {old[:80]}")
    t = t.replace(old, new)
if "--apply" in sys.argv:
    P.write_text(t)
print(f"{len(E)} edits {'applied' if '--apply' in sys.argv else 'checked'}")
