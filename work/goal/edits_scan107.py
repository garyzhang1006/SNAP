"""Scan 107: while/although/whereas down from 5.0 per thousand words, above the 21-paper corpus4
maximum of 3.32, by splitting contrast joins that carry two separate results."""
from pathlib import Path
P = Path(__file__).resolve().parents[2] / "deliverables" / "main.tex"
E = [
("is 1.244 \\ci{1.143}{1.338}, while accuracy gives 1.078 \\ci{0.993}{1.157} at the scored checkpoint (Table~\\ref{tab:primary}).",
 "is 1.244 \\ci{1.143}{1.338}. Accuracy gives 1.078 \\ci{0.993}{1.157} at the scored checkpoint, an interval that includes one (Table~\\ref{tab:primary})."),
("leaving the two targets nearly equal, while without BoolQ it is 0.578",
 "leaving the two targets nearly equal. Without BoolQ, however, it is 0.578"),
("stop short of their released final models while the auxiliary runs sit",
 "stop short of their released final models, but the auxiliary runs sit"),
("at the selected steps, while the auxiliary-run contrast (1.256 in Table~\\ref{tab:primary}) removes the batch component.",
 "at the selected steps. The auxiliary-run contrast (1.256 in Table~\\ref{tab:primary}) removes the batch component."),
("\\ci{1.412}{1.687}, while removing CommonsenseQA instead gives inflation estimates of 1.096 and 1.014.",
 "\\ci{1.412}{1.687}. Removing CommonsenseQA instead gives inflation estimates of 1.096 and 1.014."),
("Accuracy inflation is 1.220 \\ci{1.066}{1.359}, while the original ten give 1.097 on the same runs.",
 "Accuracy inflation is 1.220 \\ci{1.066}{1.359} against 1.097 for the original ten on the same runs."),
("to 1.090, while removing any other task leaves it between 1.120 and 1.213, and only the removal of DROP,",
 "to 1.090, and removing any other task leaves it between 1.120 and 1.213. Only the removal of DROP,"),
("\\ci{\\res{xlo}{lo}}{\\res{xhi}{hi}}, while the within-minus-cross difference in log squared inflation has an interval \\ci{\\res{dlo}{lo}}{\\res{dhi}{hi}} that includes zero, and its upper limit then bounds",
 "\\ci{\\res{xlo}{lo}}{\\res{xhi}{hi}}. The within-minus-cross difference in log squared inflation has an interval \\ci{\\res{dlo}{lo}}{\\res{dhi}{hi}} that includes zero, and its upper limit then bounds"),
("\\ci{\\res{xlo}{lo}}{\\res{xhi}{hi}} covering one, while the within-minus-cross difference",
 "\\ci{\\res{xlo}{lo}}{\\res{xhi}{hi}} covering one. The within-minus-cross difference"),
("\\ci{\\res{xlo}{lo}}{\\res{xhi}{hi}}, while the within-minus-cross difference in log squared inflation has interval \\ci{\\res{dlo}{lo}}{\\res{dhi}{hi}}. Bank two",
 "\\ci{\\res{xlo}{lo}}{\\res{xhi}{hi}}, and the within-minus-cross difference in log squared inflation has interval \\ci{\\res{dlo}{lo}}{\\res{dhi}{hi}}. Bank two"),
("a pattern our accuracy interval allows, while our margin covariance sits within formats.",
 "a pattern our accuracy interval allows. Our margin covariance, by contrast, sits within scoring formats."),
("on average, while the 33 configurations that share a final step give",
 "on average. The 33 configurations that share a final step give"),
("(Section~\\ref{sec:estimator}), while on accuracy such an effect could reproduce",
 "(Section~\\ref{sec:estimator}). On accuracy, however, such an effect could reproduce"),
("with a benchmark-removal check, while the split adds the item-general value",
 "with a benchmark-removal check. The split adds the item-general value"),
]
s = P.read_text()
for a, b in E:
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)
P.write_text(s)
print(len(E), "edits applied")
