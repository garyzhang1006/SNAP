# Supplement Table 11 - Trait-removal estimates

**Source**: Table 11 of the extended supplement, Extended Supplement to "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (supplement_extended_body.tex, "Recipe, size, and trait sensitivity", label tab:original10)
**Caption**: Trait-removal estimates across all 125 configurations on both score scales, with wild recipe-cluster intervals over 4,999 draws. Each removal row uses the nine remaining traits with equal weights of one ninth, and the final row uses all ten traits. The columns sigma_agg and sigma_ind give the aggregate and independence standard deviations in units of 10^-3, so the weighted trace equals sigma_ind^2 and the weighted off-diagonal sum equals sigma_agg^2 - sigma_ind^2.
**Extraction type**: raw_table
**Status**: exploratory

| Removed trait | Lambda_M | Interval | sigma_agg (M) | sigma_ind (M) | Lambda_A | Interval | sigma_agg (A) | sigma_ind (A) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BoolQ | 1.786 | [1.689, 1.877] | 5.16 | 2.89 | 1.558 | [1.412, 1.687] | 3.26 | 2.09 |
| WinoGrande | 1.246 | [1.144, 1.340] | 6.36 | 5.11 | 1.102 | [1.023, 1.178] | 5.87 | 5.32 |
| HellaSwag | 1.244 | [1.142, 1.338] | 6.35 | 5.10 | 1.076 | [0.992, 1.153] | 5.69 | 5.29 |
| PIQA | 1.243 | [1.139, 1.340] | 6.35 | 5.10 | 1.073 | [0.988, 1.150] | 5.69 | 5.30 |
| MMLU | 1.205 | [1.103, 1.300] | 6.13 | 5.09 | 1.068 | [0.984, 1.143] | 5.66 | 5.30 |
| ARC-Challenge | 1.195 | [1.113, 1.272] | 6.08 | 5.09 | 1.039 | [0.952, 1.116] | 5.47 | 5.27 |
| OpenBookQA | 1.178 | [1.092, 1.257] | 5.97 | 5.07 | 1.074 | [0.992, 1.150] | 5.66 | 5.27 |
| ARC-Easy | 1.161 | [1.089, 1.228] | 5.81 | 5.01 | 1.046 | [0.957, 1.126] | 5.43 | 5.19 |
| Social IQa | 1.139 | [1.068, 1.205] | 5.68 | 4.99 | 1.032 | [0.950, 1.109] | 5.41 | 5.24 |
| CommonsenseQA | 1.096 | [1.054, 1.137] | 4.99 | 4.55 | 1.014 | [0.936, 1.086] | 5.15 | 5.08 |
| None | 1.244 | [1.143, 1.338] | 5.72 | 4.59 | 1.078 | [0.993, 1.157] | 5.14 | 4.77 |
