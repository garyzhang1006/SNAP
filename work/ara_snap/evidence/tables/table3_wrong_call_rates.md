# Table 3 - Wrong-sign calls against the 1B ordering

**Source**: Table 3 in "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (main.tex, §4.5, label tab:decision)
**Caption**: Wrong-sign calls against the 1B ordering, as a share of calls on resolved pairs, under the independence and corrected rules. The call columns count calls on resolved pairs only, and the difference is the independence rate minus the corrected rate, with its recipe-bootstrap interval.
**Extraction type**: raw_table
**Status**: exploratory

| Score | Size | Calls, Indep. | Calls, Corrected | Wrong-call rate, Indep. | Wrong-call rate, Corrected | Difference |
| --- | --- | --- | --- | --- | --- | --- |
| Margin | 150M | 180 | 179 | 0.056 | 0.050 | [0.000, 0.022] |
| Margin | 300M | 184 | 178 | 0.060 | 0.051 | [-0.002, 0.049] |
| Margin | 530M | 181 | 169 | 0.061 | 0.059 | [-0.016, 0.022] |
| Margin | 750M | 173 | 169 | 0.029 | 0.030 | [-0.004, 0.000] |
| Accuracy | 150M | 217 | 215 | 0.069 | 0.070 | [-0.003, 0.000] |
| Accuracy | 300M | 214 | 212 | 0.051 | 0.052 | [-0.003, 0.000] |
| Accuracy | 530M | 223 | 218 | 0.067 | 0.064 | [-0.004, 0.024] |
| Accuracy | 750M | 201 | 200 | 0.045 | 0.045 | [-0.002, 0.001] |
