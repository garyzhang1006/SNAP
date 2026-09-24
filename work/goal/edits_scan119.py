"""Scan 119: thirteen appendix ', while' joins rewritten, taking while/although/whereas from 3.83
toward the corpus4 maximum of 3.32 and 'however' from 0.06 to the corpus4 range (0.39 to 2.29)."""
from pathlib import Path
P = Path(__file__).resolve().parents[2] / "deliverables" / "appendices_bcd.tex"
E = [
(", while benchmark content and format remain confounded.", ". Benchmark content and format, however, remain confounded in this battery."),
("the ten-trait 1.244, while the corresponding accuracy values are 1.070 and 1.078.", "the ten-trait 1.244. The corresponding accuracy values are 1.070 and 1.078."),
("lowers the accuracy ratio to 1.279, while the margin ratio stays at 0.890.", "lowers the accuracy ratio to 1.279, and the margin ratio stays at 0.890."),
("(Appendix~\\ref{app:supplementary}), while one that follows scoring format stays unmeasured in DataDecide.", "(Appendix~\\ref{app:supplementary}). A component that follows scoring format, however, stays unmeasured in DataDecide."),
(", while the decomposition beats independence in 0.50 of splits.", ". The decomposition, however, beats independence in 0.50 of splits."),
("It beats the plug-in on every set, while the covariance term still hurts on five-size margins.", "It beats the plug-in on every set. The covariance term, however, still hurts on five-size margins."),
("exceed one under both seed mechanisms, while the unadjusted accuracy values lie near or below one.", "exceed one under both seed mechanisms. The unadjusted accuracy values, however, lie near or below one."),
("and still excludes one, while the matching accuracy interval runs", "and still excludes one. The matching accuracy interval, however, runs"),
("carry 1,000 items each, while the original benchmarks range from 500 to 14,042.", "carry 1,000 items each. The original benchmarks range from 500 to 14,042 items."),
("under Linux, while the scoring and calibration kernels ran on GPU cards.", "under Linux. The scoring and calibration kernels ran on GPU cards."),
("recomputes both sums, while ignoring recipe membership.", "recomputes both sums and ignores recipe membership."),
("Most items use one context, while WinoGrande uses one per choice.", "Most items use one context, but WinoGrande uses one per choice."),
("at the planned token budget, while the 16 GB T4 checkpoint check", "at the planned token budget, but the 16 GB T4 checkpoint check"),
]
s = P.read_text()
for a, b in E:
    assert s.count(a) == 1, (s.count(a), a[:70])
    s = s.replace(a, b)
P.write_text(s)
print(len(E), "edits")
