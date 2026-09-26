"""Scan 130b: the seven findings that survived two-vote refutation in workflow wf_db37aab1-60c."""
from pathlib import Path
p = Path(__file__).resolve().parents[2] / "deliverables" / "main.tex"
t = p.read_text()
E = [
("DataDecide can't test a format-following component, and a cross-bank rule",
 "We didn't test a format-following component in DataDecide, and a cross-bank rule"),
("We retain the full battery for the primary estimand with the benchmarks whose estimated diagonal covariance is negative, since",
 "The primary estimand keeps all ten benchmarks, even those whose estimated diagonal covariance is negative, since"),
("with a frozen random seed, and we reuse that assignment for its replicate runs. We centre each half score across replicate runs, and we write",
 "with a frozen random seed and reuse that assignment for its replicate runs, and we then centre each half score across those runs and write"),
("That is, in these populations finite-sample bias makes an excess harder to find.",
 "That is, in these populations the downward bias makes an excess harder to find."),
("both rules call 0.133 of margin pairs", "both standard errors, under independence and with the estimated covariance, call 0.133 of margin pairs"),
("gives that effect an anti-conservative upper bound of 0.044 of margin run covariance,",
 "gives that effect an upper bound of 0.044 of margin run covariance that can understate it,"),
("The held-out interval is also 0.626 wide against 0.343 for the original.",
 "The held-out interval is also 0.626 wide against 0.343 for the original, and the closer like-for-like reference is the four-benchmark subset row of Table~\\ref{tab:heldout}, with a median of 1.176, although it pools all five sizes where the held-out test uses three."),
]
for a, b in E:
    assert t.count(a) == 1, a[:60]
    t = t.replace(a, b)
p.write_text(t)
print(len(E), "edits applied")
