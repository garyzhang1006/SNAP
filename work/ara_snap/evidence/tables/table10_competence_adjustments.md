# Table 10 - Inflation after each competence adjustment

**Source**: Table 10 in "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (appendices_bcd.tex, Appendix C "Competence proxy audit and calibration", label tab:proxy); identical to Table 15 of the extended supplement
**Caption**: Inflation after each competence adjustment, observed and in simulated populations with 300 replicates each. Simulated columns give replicate means under independent seed deviations, a single common correlation whose population inflation equals each scale's observed value, and the nearest positive semidefinite matrix to the observed seed covariance.
**Extraction type**: raw_table
**Status**: exploratory; negative result (no mechanistic reading)

| Adjustment | Margin Observed | Margin Indep. | Margin Common | Margin Matched | Accuracy Observed | Accuracy Indep. | Accuracy Common | Accuracy Matched |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| None | 1.244 | 1.000 | 1.242 | 1.243 | 1.078 | 0.998 | 1.093 | 1.116 |
| Shipped, floored | 1.244 | 1.000 | 1.170 | 1.093 | 1.076 | 0.999 | 1.092 | 1.109 |
| Floored traits dropped | 0.890 | 1.001 | 0.948 | 0.889 | 1.008 | 0.999 | 1.083 | 1.079 |
| Shrunken, in sample | 0.732 | 1.002 | 0.876 | 0.747 | 1.019 | 0.999 | 1.061 | 1.050 |
| Shrunken, cross-fitted | 0.731 | 1.002 | 0.875 | 0.745 | 1.004 | 0.999 | 1.060 | 1.049 |
