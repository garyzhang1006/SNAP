# Derived subset from Figure 2 - Cross-half correlation estimates and eigenvalue spectra (summary values only)

**Source**: Figure 2 in "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (appendices_bcd.tex, Appendix C "Associations with scoring format", label fig:covariance, figures/covariance.pdf)
**Caption**: Cross-half correlation estimates across the 125 configurations, margins on the left and accuracy in the centre, with undefined variances shown in grey and eigenvalue spectra on the right. The accuracy estimate has a negative eigenvalue, and its spectrum is a diagnostic of the moment estimate rather than a valid population correlation spectrum. PR is the spectral participation ratio, 3.57 on the nine margin traits and 3.62 on the eight accuracy traits after clipping that eigenvalue.
**Extraction type**: derived_subset (summary statistics stated in caption and prose; per-cell correlation values are Not available from provided input because the figure is a PDF heatmap and the text does not list the cells)
**Axes**: Heatmaps: X and Y = benchmark; colour = estimated correlation. Spectrum: X = eigenvalue index; Y = eigenvalue.

| Quantity | Margin (nine traits) | Accuracy (eight traits) | Source location |
| --- | --- | --- | --- |
| Spectral participation ratio | 3.57 | 3.62 after clipping (3.12 before) | Figure 2 caption; supplement "Relation to prior measurement work" |
| Leading eigenvalue | 4.33 | 3.85 | supplement prose |
| Negative eigenvalue | none (nine positive) | -0.55 | Appendix C |
| Correlation range | -0.157 to 0.802 | -0.216 to 1.296 (maximum for ARC-Easy and MMLU) | supplement prose; Appendix C |
| Mean within-format correlation (16 pairs) | 0.624 | Not specified in paper | §4.4; Appendix C |
| Mean cross-format correlation (20 pairs) | 0.007 | Not specified in paper | §4.4; Appendix C |
| ARC pair correlation | 0.801 | Not specified in paper | Appendix C |
| Undefined entries (ordered off-diagonal) | 18 | 34 | Appendix C "Performance correlation as a noise proxy" |
