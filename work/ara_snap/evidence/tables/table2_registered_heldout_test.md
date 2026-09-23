# Table 2 - The registered test at 530M, 750M and 1B

**Source**: Table 2 in "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (main.tex, §4.2, label tab:heldout)
**Caption**: The registered test at 530M, 750M, and 1B, with nominal 95% recipe-cluster intervals over 75 configurations. The auxiliary contrast compares the two auxiliary runs, the original rows read the released runs at the same sizes and were fixed before any held-out score existed, and the last row gives the median over 60 four-benchmark subsets of the original battery across all five sizes with their 5th and 95th percentiles, from the battery-size curve the protocol committed to.
**Extraction type**: raw_table
**Status**: Row 1 is the registered test (rule: lower limit > 1; FAILS). All other rows are comparisons; row 2 is exploratory.

| Battery | Score | Lambda-hat | Interval |
| --- | --- | --- | --- |
| Held-out, four tasks | Margin | 1.217 | [0.872, 1.498] |
| Held-out, four tasks | Accuracy | 1.220 | [1.066, 1.359] |
| Held-out, auxiliary contrast | Margin | 1.181 | [0.906, 1.410] |
| Original, ten benchmarks | Margin | 1.240 | [1.054, 1.397] |
| Original, ten benchmarks | Accuracy | 1.097 | [0.922, 1.246] |
| Original, auxiliary contrast | Margin | 1.273 | [0.738, 1.629] |
| Original, four-benchmark subsets, all sizes (percentiles) | Margin | 1.176 | [0.982, 1.476] |
