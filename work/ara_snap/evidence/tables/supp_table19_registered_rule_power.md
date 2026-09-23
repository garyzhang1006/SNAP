# Supplement Table 19 - Simulated pass rate of the registered rule

**Source**: Table 19 of the extended supplement, Extended Supplement to "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (supplement_extended_body.tex, "Registered held-out test", label tab:rulepower)
**Caption**: Simulated pass rate of the registered rule, a lower 95% wild bootstrap limit above one, by scope, item-noise level, and true held-out inflation, from a compound-symmetric generator with four traits, 25 recipe clusters, and three runs. Each cell uses 4,000 replicates, so its Monte Carlo error is at most 0.008. We fixed the design at noise 0.73, 1.00, and 1.45 before the 530M and 750M analysis ran, and added the rows at 2.00, 2.50, and 3.00 after seeing the observed interval width.
**Extraction type**: raw_table
**Status**: rows at noise 2.00, 2.50, 3.00 are post hoc

| Scope, configurations | Noise | 1.00 | 1.10 | 1.20 | 1.244 | 1.316 | 1.40 | 1.50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| One size, 25 | 0.73 | 0.011 | 0.088 | 0.318 | 0.454 | 0.681 | 0.884 | 0.974 |
| Two sizes, 50 | 0.73 | 0.016 | 0.180 | 0.600 | 0.785 | 0.945 | 0.995 | 1.000 |
| Three sizes, 75 | 0.73 | 0.019 | 0.258 | 0.792 | 0.926 | 0.992 | 1.000 | 1.000 |
| One size, 25 | 1.00 | 0.015 | 0.074 | 0.238 | 0.329 | 0.535 | 0.752 | 0.905 |
| Two sizes, 50 | 1.00 | 0.015 | 0.138 | 0.454 | 0.631 | 0.847 | 0.961 | 0.998 |
| Three sizes, 75 | 1.00 | 0.019 | 0.189 | 0.640 | 0.820 | 0.963 | 0.997 | 1.000 |
| One size, 25 | 1.45 | 0.020 | 0.057 | 0.142 | 0.192 | 0.324 | 0.488 | 0.683 |
| Two sizes, 50 | 1.45 | 0.017 | 0.083 | 0.259 | 0.371 | 0.581 | 0.794 | 0.943 |
| Three sizes, 75 | 1.45 | 0.022 | 0.110 | 0.368 | 0.524 | 0.754 | 0.923 | 0.991 |
| One size, 25 | 2.00 | 0.028 | 0.048 | 0.099 | 0.118 | 0.185 | 0.281 | 0.411 |
| Two sizes, 50 | 2.00 | 0.023 | 0.060 | 0.141 | 0.188 | 0.322 | 0.477 | 0.686 |
| Three sizes, 75 | 2.00 | 0.025 | 0.070 | 0.195 | 0.262 | 0.436 | 0.634 | 0.824 |
| One size, 25 | 2.50 | 0.027 | 0.039 | 0.073 | 0.083 | 0.119 | 0.168 | 0.242 |
| Two sizes, 50 | 2.50 | 0.024 | 0.050 | 0.092 | 0.115 | 0.189 | 0.280 | 0.438 |
| Three sizes, 75 | 2.50 | 0.028 | 0.053 | 0.123 | 0.162 | 0.255 | 0.381 | 0.548 |
| One size, 25 | 3.00 | 0.028 | 0.034 | 0.053 | 0.065 | 0.081 | 0.110 | 0.147 |
| Two sizes, 50 | 3.00 | 0.025 | 0.041 | 0.067 | 0.080 | 0.119 | 0.161 | 0.259 |
| Three sizes, 75 | 3.00 | 0.026 | 0.046 | 0.085 | 0.106 | 0.154 | 0.223 | 0.335 |
