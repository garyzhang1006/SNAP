# Table 9 - Coverage of nominal 95 percent intervals in simulation

**Source**: Table 9 in "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (appendices_bcd.tex, Appendix C "Simulation and permutation calibration", label tab:coverage); identical to Table 14 of the extended supplement
**Caption**: Coverage of nominal 95 percent intervals across 2,000 simulated populations per cell. Bias is the mean estimate minus the population Lambda. Noise gives the item-noise standard deviation relative to unit run effects. Inversion is the centred cluster test-inversion interval, computed later on the same simulated moments. Every cell was afterwards repeated at 10,000 replicates, and the inversion range in the main text comes from that repeat, so it differs from this column by a few thousandths.
**Extraction type**: raw_table

| Population | Lambda | Bias | Wild | Cluster t | Config. | Recipe | Inversion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Null, noise 0.73 | 1.000 | 0.000 | 0.953 | 0.946 | 0.948 | 0.937 | 0.953 |
| Null, noise 1.45 | 1.000 | -0.011 | 0.943 | 0.941 | 0.943 | 0.857 | 0.946 |
| r_E=0.061, noise 0.73 | 1.245 | 0.001 | 0.947 | 0.943 | 0.938 | 0.929 | 0.948 |
| r_E=0.018, noise 1.45 | 1.078 | -0.007 | 0.943 | 0.940 | 0.942 | 0.910 | 0.945 |
| One trait with 0.68 of trace | 1.152 | -0.001 | 0.938 | 0.936 | 0.937 | 0.925 | 0.941 |
| One trait with 0.84 of trace | 1.031 | 0.000 | 0.954 | 0.950 | 0.955 | 0.940 | 0.957 |
| Recipe-shared run effects 0.5 | 1.245 | -0.003 | 0.944 | 0.940 | 0.872 | 0.931 | 0.947 |
| Student t, 4 df | 1.245 | 0.000 | 0.946 | 0.930 | 0.943 | 0.927 | 0.955 |
| One recipe at 6 times variance | 1.245 | -0.001 | 0.930 | 0.911 | 0.931 | 0.912 | 0.955 |
| Cross-half correlation 0.1, noise 0.73 | 1.245 | -0.014 | 0.928 | 0.926 | 0.930 | 0.918 | 0.932 |
| Cross-half correlation 0.1, noise 1.45 | 1.078 | -0.016 | 0.946 | 0.941 | 0.943 | 0.933 | 0.948 |
| r_E=0.2 | 1.673 | -0.002 | 0.947 | 0.943 | 0.943 | 0.928 | 0.948 |
