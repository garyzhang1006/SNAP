# Analysis protocol and amendment history

This file records what was decided, when it was decided, and what changed afterwards. It is the
protocol the reproducibility package refers to, and it is written so a reader can tell a decision fixed
in advance from a decision made after seeing a number. Labels follow the project convention, where
OBSERVED means read from code or data, REPORTED means carried from an earlier table, and PROPOSED means
planned but not executed.

## Scope and estimand

The estimand, what counts as random, the weighting, and the comparisons were frozen in
`research/R1_estimand.md` on 2026-09-15, before any grouped BoolQ estimate was opened. That file is the
controlling specification and this one does not restate it. The short version is that configurations are
fixed design cells at 25 recipes by 5 sizes, runs are random within a configuration at three per cell,
the recipe is the inference cluster, and the reported interval covers recipe resampling of the pooled
ratio with the item halves held fixed.

## Prospective stage that was planned and not run

The plan carried a screening split, where a subset of configurations would be analysed first and the
remainder held back for confirmation. We did not implement it, so the empirical study is exploratory
throughout, and the manuscript says so in its limitations rather than implying a confirmatory design.
This is a documented drop rather than a silent one.

## Decisions fixed before the result they govern

The half assignment is a frozen function of master seed 20260101 and the trait labels, so repeated
re-splits measure algorithmic sensitivity rather than sampling variation. The prediction comparison fixed
its eight paired contrasts and a practically meaningful difference of 0.005 in mean squared log error
before any contrast was computed. Every simulation kernel states its design in a docstring written
before the run, with the date and time of writing, and those docstrings are preserved inside each
kernel's own result file under the `design` key.

## Amendments, in the order they happened

The BoolQ repair moved from an item split to a passage split, because two questions on one passage break
the conditional independence the cross-half identity needs. The passage map covers 3,270 of 3,270
passages and the grouped estimate is reported as a sensitivity estimate beside the original.

The competence proxy was dropped rather than repaired. Variance flooring let one trait dominate the
adjustment, the repaired proxy's two item halves correlate at minus 0.086 on margins, and no defensible
proxy survived, so the mechanism claim was removed from the manuscript.

The interval construction was compared against seven alternatives, and the residual-scaled version is
better calibrated than the shipped one. We chose it after seeing four cells, so the paper reports the
shipped interval throughout and records the alternative as the better-calibrated option rather than
promoting it after the fact.

Two readings were retracted after larger runs contradicted them. The claim that the two sharing channels
partly cancel rested on a 0.012 gap at 4,000 replicates, which vanished at 12,000. The claim that flat
compound symmetry covers worse than a structured truth rested on a 0.011 gap at 4,000 replicates, and at
12,000 the ordering reversed to within 1.4 Monte Carlo standard errors. Both are stated in the appendix
as corrections rather than removed.

## Compute

Every number in this package comes from a Kaggle kernel or from the released reductions, and the
kernels are preserved under `research/kaggle/`, one directory per kernel with its script and metadata.
`research/kernel_status.tsv` records the terminal state and timing of each run, and `research/LEDGER.md`
records what each run showed and what the manuscript did about it.
