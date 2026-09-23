# Table 4 - Notation

**Source**: Table 4 in "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (appendix_a.tex, Appendix A.2, label tab:notation)
**Caption**: Notation for the cross-half construction and its empirical diagnostics. The coefficient r_E uses covariance normalisation, which differs from mean correlation under unequal marginal variances.
**Extraction type**: raw_table (non-result table; also routed to logic/concepts.md)

| Symbol | Meaning |
| --- | --- |
| c, r, j, i | Configuration, replicate run, benchmark, and item indices |
| N, R, K | Configuration, replicate, and benchmark counts, with values 125, 3, and 10 |
| Sigma_E,c, Sigma_E | Configuration covariance and its average across the design |
| R_E, R_P | Run-effect and between-configuration score correlation matrices |
| y^marg, y^acc | Mean per-byte margin and accuracy on the specified item set |
| d^H_crj, g^H_cr | Centred benchmark score and its benchmark average on half H |
| T_c, U_c | Cross-half aggregate covariance and its diagonal-only contribution |
| Lambda, r_E | Standard-deviation inflation and effective covariance coefficient |
| Lambda_M, Lambda_A | The same inflation computed on margins and on accuracy |
| K_eff | Independent-benchmark equivalent at the same marginal RMS deviation |
| sigma_agg, sigma_indep | Aggregate deviation with full covariance and under independence |
| rho_g, v-bar | Aggregate reliability and its scaled item-noise contribution |
| s_cr, x_cr^(-j) | Gain covariate and opposite-half competence proxy |
