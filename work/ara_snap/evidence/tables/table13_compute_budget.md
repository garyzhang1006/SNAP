# Table 13 - Planned compute budget

**Source**: Table 13 in "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (appendices_bcd.tex, Appendix D.4, label tab:original15)
**Caption**: Compute budget reported in the planning document for both analysis arms. These figures describe the plan rather than measured costs for every listed operation.
**Extraction type**: raw_table (plan, not measurement; measured costs in src/environment.md)

| Operation | Budget | Scope |
| --- | --- | --- |
| Arm 2 held-out bits per byte | 6.0 GPU hours | 27 runs, 4,755 items |
| Calibration simulations N1, N5, N6 | 1.0 GPU hours | 2,000 replicates, six effects |
| 160M checkpoint check | 0.5 GPU hours | Adjacent checkpoints |
| Contingency | 2.5 GPU hours | Reserved capacity |
| Total GPU | 10.0 GPU hours | Planned total |
| Streaming and reduction | 18 CPU hours | 122.9 GB, one pass |
| Estimation, bootstrap, permutation | 7 CPU hours | Includes 200 planned splits |
