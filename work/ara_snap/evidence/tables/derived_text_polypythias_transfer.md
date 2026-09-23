# Derived subset - Earlier PolyPythias transfer and adjacent-checkpoint results

**Source**: Derived from text of Appendix C "Transport to PolyPythias" and "Adjacent-checkpoint variation in PolyPythias" and §4.4; no numbered source table
**Caption**: Inflation estimates from the earlier nested 4,755-item PolyPythias battery (not the §4.3 bank-1 scoring, which is pending), transcribed from prose.
**Extraction type**: derived_subset
**Derived from**: prose; distinct from `pending_sec4_3_second_family_results.md`

| Analysis | Scale | Estimate | Configuration-bootstrap interval | Test-inversion set |
| --- | --- | --- | --- | --- |
| Source pipeline, three sizes | Margin | 1.40574 | Not specified in paper | Not specified in paper |
| Rescore, three sizes | Margin | 1.41372 | [0.939, 1.781] | [0, 2.106] |
| Rescore, five sizes | Margin | 1.26199 | [0.927, 1.537] | [0.519, 1.664] |
| Rescore, three sizes | Accuracy | 2.28589 | [undefined, 2.971] | unbounded |
| Rescore, five sizes | Accuracy | 1.71085 | [0.869, 2.428] | unbounded |
| DataDecide reference | Margin | 1.24395 | [1.143, 1.338] (wild) | [1.095, 1.323] |
| DataDecide reference | Accuracy | 1.07837 | [0.993, 1.157] (wild) | [0.995, 1.162] |

| 160M adjacent-checkpoint check (steps 143000 vs 142000, 1,800 items) | Margin | Accuracy |
| --- | --- | --- |
| Between-run SD | 0.00513 | 0.00451 |
| RMS checkpoint shift | 0.00456 | 0.00710 |
| Shift ratio | 0.890 | 1.573 |
| Final-preceding correlation | 0.573 | -0.070 |
| Ratio after removing shared change | 0.890 | 1.279 |

Excess ratios: 1.66323 (source pipeline, three sizes); 1.69592 (three sizes) and 1.07393 (five sizes) in the rescore. Out-of-sample single-configuration mean absolute log error on three-size margins: independence 0.339, plug-in 0.536, decomposition 0.512; accuracy 0.370, 0.447, 0.384.
