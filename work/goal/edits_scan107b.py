"""Scan 107b: cross-reference density from 0.28 of sentences toward the corpus4 maximum of 0.22,
dropping pointers that repeat one a sentence away or aim at a float on the same page; three
agentless steps put in the passive, where corpus4 runs 2.2 to 10.3 per thousand words against 1.4."""
from pathlib import Path
P = Path(__file__).resolve().parents[2] / "deliverables" / "main.tex"
E = [
("Because the correction changes few calls on DataDecide's recipe comparisons (Section~\\ref{sec:prediction}), the",
 "Because the correction changes few calls on DataDecide's recipe comparisons, the"),
("and Section~\\ref{sec:family}'s cross-bank rule tests one tied to the item set in PolyPythias.",
 "and a cross-bank rule tests one tied to the item set in PolyPythias."),
("The auxiliary-run contrast (1.256 in Table~\\ref{tab:primary}) removes the batch component.",
 "The auxiliary-run contrast, at 1.256, removes the batch component."),
("Both rules of Section~\\ref{sec:family} were committed before either bank was scored.",
 "Both PolyPythias rules were committed before either bank was scored."),
("Full-battery margins exclude independence, while accuracy gives only a bound (Table~\\ref{tab:primary}).",
 "Full-battery margins exclude independence, while accuracy gives only a bound."),
("Its removal lowers the denominator of Equation~\\ref{eq:lambda} more than the numerator",
 "Its removal lowers the denominator of the ratio more than the numerator"),
("The BoolQ diagonal moves by 0.03\\% and 0.15\\% (Appendix~\\ref{app:derivations}).",
 "The BoolQ diagonal moves by 0.03\\% and 0.15\\% under the same reassignment."),
("depends on battery composition as the original does (Appendix~\\ref{app:heldout}).",
 "depends on battery composition as the original does."),
("Margin correlations track scoring format (Section~\\ref{sec:composition}), and cross-format inflation (Section~\\ref{sec:estimator}) is 0.921",
 "Margin correlations track scoring format, and cross-format inflation is 0.921"),
("give a margin interval too wide to test the full estimate (Section~\\ref{sec:data}).",
 "give a margin interval too wide to test the full estimate."),
("before implied cross-format inflation passes 1.035 (Section~\\ref{sec:estimator}).",
 "before implied cross-format inflation passes 1.035."),
("and the PolyPythias seeds avoid them by sharing one final step (Section~\\ref{sec:family}).",
 "and the PolyPythias seeds avoid them by sharing one final step."),
("and Section~\\ref{sec:composition} checks the one benchmark with documented shared passages by keeping each passage in one half.",
 "and we check the one benchmark with documented shared passages by keeping each passage in one half."),
# passives where the actor adds nothing
("We took the request text from the DataDecide release, and every prompt",
 "The request text was taken from the DataDecide release, and every prompt"),
("We dropped any item whose context matches a bank-one context or whose question appears among its own few-shot exemplars, and we capped each benchmark at 600 items apart from MMLU.",
 "Any item whose context matches a bank-one context or whose question appears among its own few-shot exemplars was dropped, and each benchmark apart from MMLU was capped at 600 items."),
("A wrong call here also counts genuine rank changes between sizes,",
 "A wrong call here, however, also counts genuine rank changes between sizes,"),
]
s = P.read_text()
for a, b in E:
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)
P.write_text(s)
print(len(E), "edits applied")
