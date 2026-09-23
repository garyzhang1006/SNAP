# Derived subset - Full-battery intervals under alternative constructions

**Source**: Derived from text of §2.3 and Appendix C ("Simulation and permutation calibration", "Interval construction and cluster sensitivity", "Gain calibration and recipe split sensitivity"); no numbered source table
**Caption**: Observed-data intervals for the full ten-benchmark battery under each interval construction the paper reports, transcribed from prose.
**Extraction type**: derived_subset
**Derived from**: prose; the shipped row matches `table1_primary_inflation.md`

| Construction | Margin interval | Accuracy interval | Status |
| --- | --- | --- | --- |
| Wild recipe-cluster bootstrap-t, 4,999 draws (shipped) | [1.143, 1.338] | [0.993, 1.157] | primary |
| Wild, Rademacher, 9,999 draws over twenty seeds | [1.141, 1.339] | Not specified in paper | added later |
| Residual-scaled wild (leverage-corrected) | [1.130, 1.349] | [0.987, 1.163] | chosen after seeing four cells; not shipped |
| Centred cluster test inversion | [1.095, 1.323] | [0.995, 1.162] | added later |
| Beran prepivoting (1,999 x 1,999) | [1.151, 1.328] | [0.994, 1.161] | added later |
| Configuration percentile bootstrap (125 configurations) | [1.069, 1.426] | [0.976, 1.182] | ignores recipe dependence |
| Delete-one-recipe jackknife t(24) | [1.143, 1.345] | [0.998, 1.158] | reported |
| Size-band clusters (5) | [1.030, 1.426] | [0.961, 1.184] | sensitivity |
| Without BoolQ, restricted inversion (widest of eight) | [1.391, 1.840] | Not specified in paper | sensitivity |
