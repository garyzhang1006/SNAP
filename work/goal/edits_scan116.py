"""Scan 116: 23 appendix ', which' joins rewritten (participles, appositives, plain 'and'),
taking appendices_bcd.tex from 3.54 per thousand words toward the corpus4 maximum of 2.23.
One of them also carried a 'no X but Y' contrast, removed here."""
from pathlib import Path
P = Path(__file__).resolve().parents[2] / "deliverables" / "appendices_bcd.tex"
E = [
(", which reproduces the three figures", ", reproducing the three figures"),
("vary fine-tuning and decoding seeds, which differ from pretraining-run variation.", "vary fine-tuning and decoding seeds, a different source from pretraining-run variation."),
("on PolyPythias, which differs from the covariance of benchmark run effects.", "on PolyPythias, a quantity distinct from the covariance of benchmark run effects."),
("2.44 bootstrap standard errors, which doesn't by itself establish leakage.", "2.44 bootstrap standard errors, a size that doesn't by itself establish leakage."),
("falls below zero, which leaves its square-root endpoint unavailable.", "falls below zero and leaves its square-root endpoint unavailable."),
("give 1.803, which shows how much", "give 1.803, showing how much"),
("to nine decimal places, which checks the construction.", "to nine decimal places, a check on the construction."),
("held-out marginal seed standard deviations, which isolates the correlation component.", "held-out marginal seed standard deviations, isolating the correlation component."),
("mean squared log error, which corresponds to a 7 percent error", "mean squared log error, corresponding to a 7 percent error"),
("low true correlations, which is an assumption we haven't tested.", "low true correlations, an assumption we haven't tested."),
("under flat weights, which is the check that licenses the sweep.", "under flat weights, the check that licenses the sweep."),
("for accuracy, which moves no conclusion but erases the 0.011 of separation", "for accuracy. That moves no conclusion, although it erases the 0.011 of separation"),
("is 0.420, which carries 0.319 of the margin excess", "is 0.420, carrying 0.319 of the margin excess"),
("as its own cluster, which gives margin sets of", "as its own cluster, giving margin sets of"),
("changes that answer, which shows how much of the first comparison was target noise", "changes that answer and shows how much of the first comparison was target noise"),
("The 84 splits share runs, which makes these descriptive differences", "The 84 splits share runs, making these descriptive differences"),
("or uncertainty intervals, which limits comparison with", "or uncertainty intervals, limiting comparison with"),
("from 1.103 to 1.832, which suggests that a few runs dominate", "from 1.103 to 1.832, a sign that a few runs dominate"),
("within 0.004 of one, which doesn't establish absence", "within 0.004 of one. That doesn't establish absence"),
("at six runs, which is eight to sixteen times", "at six runs, eight to sixteen times"),
("for the 225 runs in scope, which triggered the scope rule.", "for the 225 runs in scope, and that estimate triggered the scope rule."),
("to within 0.0005, which it did.", "to within 0.0005, and it did."),
("changes batch grouping, which can affect floating-point results", "changes batch grouping and can affect floating-point results"),
]
s = P.read_text()
for a, b in E:
    assert s.count(a) == 1, (s.count(a), a[:70])
    s = s.replace(a, b)
P.write_text(s)
print(len(E), "edits")
