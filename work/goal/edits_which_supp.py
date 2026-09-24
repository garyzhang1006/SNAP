"""Turn ', which is <noun phrase>' in the extended supplement into plain appositives, which lowers the
', which' rate and adds commas the user asked for. usage: python3 work/goal/edits_which_supp.py [--apply]"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[2] / "deliverables" / "supplement_extended_body.tex"
E = [
    (", which is the honest reason the paper draws", ", and that limit is why the paper draws"),
    ("at most 0.0032, which is small beside the target noise.", "at most 0.0032, a small gap beside the target noise."),
    ("0.0867, which is a reduction of about one seventh.", "0.0867, a reduction of about one seventh."),
    ("the same question, which is whether a correction", "the same question, namely whether a correction"),
    ("by 0.005 there, which is the price of", "by 0.005 there, the price of"),
    ("standard deviation, which is exactly what the ordinary normal calculation", "standard deviation, exactly what the ordinary normal calculation"),
    ("drawn from, which is the friendly case", "drawn from, the friendly case"),
    ("target of 1.10, which is its own neighbourhood.", "target of 1.10, its own neighbourhood."),
    ("0.946 and 0.970, which is above 0.95 in eleven", "0.946 and 0.970, above 0.95 in eleven"),
    ("0.928, which is the same shortfall the main text", "0.928, the same shortfall the main text"),
    ("toward one, which is the $-0.014$ bias", "toward one, the $-0.014$ bias"),
    ("near 0.009, which is about 1 percent of", "near 0.009, about 1 percent of"),
    ("particular runs, which is the channel a shared passage", "particular runs, the channel a shared passage"),
    ("on margins, which is further below one than", "on margins, further below one than"),
    ("in 21 cases, which is a further obstacle", "in 21 cases, a further obstacle"),
    ("each configuration, which is enough to measure", "each configuration, enough to measure"),
    ("by chance, which is a weaker statement than", "by chance, a weaker statement than"),
    (", which is how much data an effect of this size needs.", " about the amount of data an effect of this size needs."),
    ("at six runs, which is eight to sixteen times", "at six runs, eight to sixteen times"),
    ("0.356, which is the cost of that lost direction", "0.356, the cost of that lost direction"),
    ("margin, which is the cell the analytic version", "margin, the cell the analytic version"),
    ("0.973 to 1.175, which is wider than the recipe interval.", "0.973 to 1.175, wider than the recipe interval."),
    ("actually bound, which is the recipe channel.", "actually bound, the recipe channel."),
    ("matter here, which is the opposite of what", "matter here, the opposite of what"),
    ("0.018 of replicates, which is the false positive rate", "0.018 of replicates, the false positive rate"),
]
t = P.read_text()
for old, new in E:
    if t.count(old) != 1:
        sys.exit(f"expected one match, found {t.count(old)}: {old}")
    t = t.replace(old, new)
if "--apply" in sys.argv:
    P.write_text(t)
print(f"{len(E)} edits {'applied' if '--apply' in sys.argv else 'checked'}")
