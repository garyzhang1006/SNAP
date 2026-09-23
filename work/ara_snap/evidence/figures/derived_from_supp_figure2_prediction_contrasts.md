# Derived subset from Supplement Figure 2 - Paired prediction differences for eight pre-fixed contrasts

**Source**: Figure 2 of the extended supplement (supplement_extended_body.tex, label fig:prediction, figures/prediction.pdf); cited in Appendix C "Paired uncertainty"
**Caption**: Paired prediction differences for the eight contrasts fixed before any of them was computed, in mean squared error of the log aggregate seed standard deviation. Black marks the recipe bootstrap, resampling all 25 recipes over 2,000 refitted draws, with the observed point estimate as the dot. Grey marks 1,000 fold repartitions of the same 25 recipes, with the partition median as the tick, so the two rows separate recipe sampling from fold assignment. The shaded band is the practically meaningful difference of 0.005 that we fixed beforehand, and a negative value favours the first model of the pair. Every interval is a 2.5 to 97.5 percentile range rather than a standard error, and no endpoint here is missing or clipped.
**Extraction type**: derived_subset (only the contrasts whose values the prose states; the remaining contrasts and all fold-repartition ranges are Not available from provided input)
**Axes**: X = difference in mean squared log error; Y = contrast

| Contrast | Scale | Point stated in prose | Recipe-bootstrap interval |
| --- | --- | --- | --- |
| P1 minus P0 | Margin | about -0.03 | [-0.058, -0.001] |
| P1G minus P0 | Margin | about -0.03 | [-0.059, -0.002] |
| P3 minus P0 | Margin | about -0.03 | [-0.060, -0.004] |
| P2R minus P0 | Margin | reported as -0.023 | [-0.059, 0.010] |
| P1 minus P3 | Margin | Not specified in paper | [-0.003, 0.012] |
| P3 minus P0 | Accuracy | Not specified in paper | [-0.017, 0.023] |

Fold-mean errors for each model are in `../tables/table8_prediction_error.md`. Partition facts from prose: independence never has the lowest margin error across 1,000 partitions; P1, P1G, P3 lowest in 27, 33, 33 percent; on accuracy P3 lowest in 55 percent and independence in 39 percent; partition medians 0.0438 (independence) and 0.0031 (P1) on margins.
