# Table 12 - Median margin inflation over subsets of the original ten benchmarks

**Source**: Table 12 in "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (appendices_bcd.tex, Appendix C "Registered held-out test", label tab:battery); identical to Table 21 of the extended supplement
**Caption**: Median margin inflation over subsets of the original ten benchmarks, with the share of subsets whose nominal 95% interval excludes one, at 530M and 750M, at 530M, 750M, and 1B, at 530M alone, and across all five sizes. Benchmark counts with more than 60 subsets use 60 sampled without replacement, and subsets whose bootstrap degenerates are left out of that share. The two-size rows were fixed before any 750M held-out score existed, the 530M rows came after the 530M interim result, and the three-size rows came after the full-scope result. These intervals use 1,999 wild draws, against 4,999 for the registered test.
**Extraction type**: raw_table

| Benchmarks | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 530M and 750M median | 1.010 | 1.143 | 1.213 | 1.288 | 1.142 | 1.206 | 1.210 | 1.259 | 1.316 |
| 530M and 750M share | 0.37 | 0.53 | 0.55 | 0.53 | 0.37 | 0.33 | 0.20 | 0.10 | 0.00 |
| 530M, 750M, and 1B median | 1.014 | 1.109 | 1.172 | 1.227 | 1.097 | 1.156 | 1.163 | 1.196 | 1.240 |
| 530M, 750M, and 1B share | 0.36 | 0.48 | 0.55 | 0.50 | 0.42 | 0.45 | 0.58 | 0.80 | 1.00 |
| 530M median | 1.019 | 1.133 | 1.244 | 1.317 | 1.296 | 1.368 | 1.377 | 1.439 | 1.514 |
| 530M share | 0.33 | 0.58 | 0.67 | 0.80 | 0.78 | 0.87 | 0.91 | 0.90 | 1.00 |
| All sizes median | 1.012 | 1.116 | 1.176 | 1.228 | 1.100 | 1.160 | 1.160 | 1.200 | 1.244 |
| All sizes share | 0.38 | 0.53 | 0.57 | 0.62 | 0.73 | 0.82 | 0.98 | 1.00 | 1.00 |
