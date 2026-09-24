# ARS deep-research fact-check, 2026-09-24

External factual claims in deliverables/main.tex, checked against primary abstracts fetched from the arXiv export API today and against the earlier literature audit (research/R13_literature_audit.md). Run in session with no agents.

| Claim in main.tex | Source | Verdict |
|---|---|---|
| DataDecide has 25 data recipes, sizes up to 1B and three replicates | 2504.11393 abstract ("25 corpora", "model sizes up to 1B", "3 random seeds") | Supported |
| PolyPythias trains nine seeds at 14M, 31M, 70M, 160M and 410M, 45 runs, with the seed setting initialisation and data order | 2503.09543 abstract ("45 new training runs", "9 new seeds across 5 model sizes, from 14M to 410M", "initialisation and data order") | Supported |
| Heineman et al. relate signal and noise to decision accuracy, with noise measured across checkpoints | 2508.13144 abstract (noise is "sensitivity to random variability between training steps", decisions at small scale) | Supported; the paper now attributes the 1.104 to our recomputation |
| Jordan (2024) finds accuracy deviations nearly independent across shifted ImageNet test sets | 2304.01910, Appendix C, Figure 10, where the largest cross-set R^2 is 0.14 (R13 audit) | Supported |
| Auxiliary runs below 1B stop at 25% of the 1B budget, seed labels {2,14,15} and {2,4,5} | DataDecide release metadata, read in earlier rounds from the released checkpoint index | Supported by release files, not by the abstract |

Verdict: no unsupported external claim found.
