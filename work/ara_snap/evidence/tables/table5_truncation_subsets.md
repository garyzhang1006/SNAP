# Table 5 - Inflation on checkpoint-schedule subsets

**Source**: Table 5 in "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (appendices_bcd.tex, Appendix B.1, label tab:truncation); identical to Table 1 of the extended supplement
**Caption**: Inflation estimates on subsets defined by each configuration's checkpoint schedule, with wild cluster bootstrap-t intervals over 4,999 draws. Severe truncation means that the largest final step among the three runs exceeds the smallest by more than a factor of 1.5.
**Extraction type**: raw_table
**Status**: exploratory; subsets chosen after seeing full-sample estimates

| Subset | Configurations | Recipes | Margin | Accuracy |
| --- | --- | --- | --- | --- |
| All | 125 | 25 | 1.244 [1.143, 1.338] | 1.078 [0.993, 1.157] |
| Shared final step | 33 | 24 | 1.082 [0.121, 1.530] | 1.129 [0.769, 1.397] |
| Without severe truncation | 99 | 25 | 1.276 [1.114, 1.420] | 1.120 [1.020, 1.208] |
| Severe truncation only | 26 | 25 | 1.107 [0.692, 1.397] | 0.977 [0.357, 1.306] |
| Different final steps | 92 | 25 | 1.330 [1.024, 1.583] | 1.070 [0.956, 1.171] |
