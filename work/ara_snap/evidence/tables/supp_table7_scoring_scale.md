# Supplement Table 7 - Margin inflation after item-level transformations

**Source**: Table 7 of the extended supplement, Extended Supplement to "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (supplement_extended_body.tex, "Scoring-scale interventions", label tab:scale)
**Caption**: Margin inflation after item-level transformations of the same saved margins, with wild recipe-cluster intervals over 4,999 draws. s_j is the pooled standard deviation of benchmark j's item margins.
**Extraction type**: raw_table
**Status**: exploratory

| Item score | Lambda-hat | Interval | Off-diagonal sum / trace | BoolQ trace share |
| --- | --- | --- | --- | --- |
| m | 1.244 | [1.143, 1.338] | 0.547 | 0.679 |
| 10m | 1.244 | [1.143, 1.338] | 0.547 | 0.679 |
| m/s_j | 1.182 | [1.094, 1.265] | 0.398 | 0.786 |
| min(max(m,-s_j),s_j)/s_j | 1.134 | [1.048, 1.213] | 0.287 | 0.827 |
| tanh(m/s_j) | 1.141 | [1.053, 1.222] | 0.301 | 0.822 |
| tanh(2m/s_j) | 1.120 | [1.032, 1.200] | 0.254 | 0.831 |
| sign(m) | 1.079 | [0.992, 1.158] | 0.164 | 0.844 |
