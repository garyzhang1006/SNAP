# Figure 1 - Inflation after removing each benchmark in turn

**Source**: Figure 1 in "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (main.tex, §4.1, label fig:composition, figures/composition.pdf)
**Caption**: Inflation after removing each benchmark in turn, with nominal 95% recipe-cluster intervals, from the trait-removal table of the extended supplement. The solid line marks one and the dashed line the full ten-benchmark estimate. On margins every removal leaves an interval that excludes one, and the estimate runs from 1.096 without CommonsenseQA to 1.786 without BoolQ.
**Extraction type**: raw_figure_data (values taken from the plotted source table, supplement Table 11, which the caption names as the figure's data; not read off pixels)
**Axes**: X = removed benchmark (categorical); Y = inflation Lambda (dimensionless), one panel per score scale; reference lines at 1 and at the full-battery estimate

| Removed benchmark | Margin Lambda | Margin interval | Accuracy Lambda | Accuracy interval |
| --- | --- | --- | --- | --- |
| BoolQ | 1.786 | [1.689, 1.877] | 1.558 | [1.412, 1.687] |
| WinoGrande | 1.246 | [1.144, 1.340] | 1.102 | [1.023, 1.178] |
| HellaSwag | 1.244 | [1.142, 1.338] | 1.076 | [0.992, 1.153] |
| PIQA | 1.243 | [1.139, 1.340] | 1.073 | [0.988, 1.150] |
| MMLU | 1.205 | [1.103, 1.300] | 1.068 | [0.984, 1.143] |
| ARC-Challenge | 1.195 | [1.113, 1.272] | 1.039 | [0.952, 1.116] |
| OpenBookQA | 1.178 | [1.092, 1.257] | 1.074 | [0.992, 1.150] |
| ARC-Easy | 1.161 | [1.089, 1.228] | 1.046 | [0.957, 1.126] |
| Social IQa | 1.139 | [1.068, 1.205] | 1.032 | [0.950, 1.109] |
| CommonsenseQA | 1.096 | [1.054, 1.137] | 1.014 | [0.936, 1.086] |
| Full battery (dashed line) | 1.244 | [1.143, 1.338] | 1.078 | [0.993, 1.157] |
