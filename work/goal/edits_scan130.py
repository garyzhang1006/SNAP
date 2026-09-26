"""Scan 130: STE rule 3.7 active voice in the main text, plus the R6.2 split of the intro paragraph."""
from pathlib import Path
p = Path(__file__).resolve().parents[2] / "deliverables" / "main.tex"
t = p.read_text()
E = [
("weakens a comparison's error control. When the true", "weakens a comparison's error control.\n\nWhen the true"),
("Item-general covariance is estimated from two disjoint item halves per benchmark, where both half scores are centred across each configuration's replicate runs and their cross-half products are taken.",
 "We estimate item-general covariance from two disjoint item halves per benchmark, where we centre both half scores across each configuration's replicate runs and take their cross-half products."),
("unless a run effect is shared within a model size or item noise", "unless the runs of one model size share a run effect or item noise"),
("Items are averaged per benchmark, with MMLU macro-averaged over its 57 subjects, and we denote", "We average items per benchmark, with MMLU macro-averaged over its 57 subjects, and we denote"),
("This target is defined for a redrawn or extended item bank.", "This target applies to a redrawn or extended item bank."),
("Each benchmark's items are partitioned into disjoint halves with a frozen random seed, and that assignment is reused for its replicate runs. Each half score is centred across replicate runs, and we write",
 "We partition each benchmark's items into disjoint halves with a frozen random seed, and we reuse that assignment for its replicate runs. We centre each half score across replicate runs, and we write"),
("A format-following component is untested in DataDecide, and a cross-bank rule", "DataDecide can't test a format-following component, and a cross-bank rule"),
("Each is summed across configurations, and one sum is divided by the other to obtain", "We sum each across configurations, and we divide one sum by the other to obtain"),
("Nominal 95\\% wild cluster bootstrap-$t$ intervals are computed over the 25 recipe clusters,", "We compute nominal 95\\% wild cluster bootstrap-$t$ intervals over the 25 recipe clusters,"),
("In each configuration the largest checkpoint step that all three runs share is selected.", "In each configuration we select the largest checkpoint step that all three runs share."),
("The full estimate is interpreted as covariance among the released runs at the selected steps.", "We interpret the full estimate as covariance among the released runs at the selected steps."),
("The full battery is retained for the primary estimand with", "We retain the full battery for the primary estimand with"),
("and all 45 runs are scored at the shared final step 143,000 on all 37,682 items. The request text was taken from the DataDecide release,",
 "and we score all 45 runs at the shared final step 143,000 on all 37,682 items. We took the request text from the DataDecide release,"),
("Any item whose context matches a bank-one context or whose question appears among its own few-shot exemplars was dropped, and each benchmark apart from MMLU was capped at 600 items. Both PolyPythias rules were committed before either bank was scored.",
 "We dropped any item whose context matches a bank-one context or whose question appears among its own few-shot exemplars, and we capped each benchmark apart from MMLU at 600 items. We committed both PolyPythias rules before we scored either bank."),
("The 2,938 passages behind BoolQ's 3,270 questions were recovered from the release's request files, and when",
 "We recovered the 2,938 passages behind BoolQ's 3,270 questions from the release's request files, and when"),
("Five covariance models and an exploratory rescaled plug-in of observed score correlations were compared on five recipe folds,",
 "We compared five covariance models and an exploratory rescaled plug-in of observed score correlations on five recipe folds,"),
("reaches zero when nonpositive held-out variances are filled from training folds.", "reaches zero when we fill nonpositive held-out variances from training folds."),
("On real comparisons at each size below 1B, a pair of recipes was called when their aggregate gap exceeded two standard errors,",
 "On real comparisons at each size below 1B, we called a pair of recipes when their aggregate gap exceeded two standard errors,"),
("Each call was scored against the pair's ordering at 1B", "We scored each call against the pair's ordering at 1B"),
("The default 750M runs are scored at 41.5\\% of their final step on average.", "We score the default 750M runs at 41.5\\% of their final step on average."),
("Intervals are clustered on recipes, but the release shares", "We cluster intervals on recipes, but the release shares"),
]
for a, b in E:
    n = t.count(a)
    assert n == 1, (n, a[:70])
    t = t.replace(a, b)
p.write_text(t)
print(len(E), "edits applied")
