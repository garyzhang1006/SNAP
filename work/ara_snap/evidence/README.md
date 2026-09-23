# Evidence Index

Paper table and figure numbers come from `deliverables/main.aux`; supplement numbers from `deliverables/supplement_extended.aux`. Seven supplement tables duplicate paper tables cell for cell (checked by diffing the LaTeX tabulars) and are indexed under the paper number: supplement Tables 1, 2, 6, 10, 14, 15, 21 equal paper Tables 5, 6, 7, 8, 9, 10, 12. Supplement Table 16 repeats Table 8's five original models with parameter counts and is kept as its own file.

## Tables (paper)
| File | Source | Claims | Description |
|------|--------|--------|-------------|
| [tables/table1_primary_inflation.md](tables/table1_primary_inflation.md) | Table 1, §4.1 | C02, C03, C05 | Raw and auxiliary-contrast inflation, K_eff, sigma_agg on both scales |
| [tables/table2_registered_heldout_test.md](tables/table2_registered_heldout_test.md) | Table 2, §4.2 | C07, C08 | Registered held-out test (fails) and same-scope original battery |
| [tables/table3_wrong_call_rates.md](tables/table3_wrong_call_rates.md) | Table 3, §4.5 | C18 | Wrong-call rates under independence and corrected rules on real recipe pairs |
| [tables/table4_notation.md](tables/table4_notation.md) | Table 4, Appendix A.2 | C01 | Notation (non-result; routed also to concepts.md) |
| [tables/table5_truncation_subsets.md](tables/table5_truncation_subsets.md) | Table 5, Appendix B.1 | C13 | Estimates on checkpoint-schedule subsets |
| [tables/table6_reliability_by_trait.md](tables/table6_reliability_by_trait.md) | Table 6, Appendix B.2 | C05 | Per-trait cross-half reliability and formats |
| [tables/table7_inflation_by_size.md](tables/table7_inflation_by_size.md) | Table 7, Appendix C | C04, C19 | Inflation by model size band |
| [tables/table8_prediction_error.md](tables/table8_prediction_error.md) | Table 8, Appendix C | C17 | Five-fold prediction MSE for six covariance models |
| [tables/table9_interval_coverage.md](tables/table9_interval_coverage.md) | Table 9, Appendix C | C09, C01 | Coverage and bias of five interval constructions in twelve populations |
| [tables/table10_competence_adjustments.md](tables/table10_competence_adjustments.md) | Table 10, Appendix C | C12 | Competence-proxy adjustments, observed and simulated |
| [tables/table11_external_seed_panel.md](tables/table11_external_seed_panel.md) | Table 11, Appendix C | C16 | External random-seed panel inflation |
| [tables/table12_battery_size_curve.md](tables/table12_battery_size_curve.md) | Table 12, Appendix C | C07 | Battery-size curves of original-benchmark subsets at four scopes |
| [tables/table13_compute_budget.md](tables/table13_compute_budget.md) | Table 13, Appendix D.4 | none (provenance) | Planned compute budget |

## Tables (extended supplement)
| File | Source | Claims | Description |
|------|--------|--------|-------------|
| [tables/supp_table3_planning_power.md](tables/supp_table3_planning_power.md) | Supplement Table 3 | C14 | Planning SE, MDE and power at N = 85 |
| [tables/supp_table4_planning_checks.md](tables/supp_table4_planning_checks.md) | Supplement Table 4 | C12, C14, C15 | Gates G0 to G8 with outcomes |
| [tables/supp_table5_prediction_scorecard.md](tables/supp_table5_prediction_scorecard.md) | Supplement Table 5 | C14, C11, C15, C16 | Eleven planning predictions scored |
| [tables/supp_table7_scoring_scale.md](tables/supp_table7_scoring_scale.md) | Supplement Table 7 | C05, C06 | Margin inflation after item-level transforms |
| [tables/supp_table8_accuracy_point_calculations.md](tables/supp_table8_accuracy_point_calculations.md) | Supplement Table 8 | C18 | sigma_agg, K_eff, P_flip at 300M |
| [tables/supp_table9_null_sensitivity.md](tables/supp_table9_null_sensitivity.md) | Supplement Table 9 | C01, C09, C10, C12 | Null and sensitivity simulations N1 to N6 |
| [tables/supp_table11_trait_removal.md](tables/supp_table11_trait_removal.md) | Supplement Table 11 | C04, C06 | Benchmark removal on both scales with sigma_agg |
| [tables/supp_table12_fixed_k_subsets.md](tables/supp_table12_fixed_k_subsets.md) | Supplement Table 12 | C04, C06 | Equal-weight subsets by battery size |
| [tables/supp_table13_adjacent_checkpoint.md](tables/supp_table13_adjacent_checkpoint.md) | Supplement Table 13 | C13 | Selected versus previous shared checkpoint |
| [tables/supp_table16_five_fold_prediction.md](tables/supp_table16_five_fold_prediction.md) | Supplement Table 16 | C17 | Five original prediction models with parameter counts |
| [tables/supp_table17_gain_simulator.md](tables/supp_table17_gain_simulator.md) | Supplement Table 17 | C12 | Gain-simulator excess shares |
| [tables/supp_table18_recipe_subset_sweep.md](tables/supp_table18_recipe_subset_sweep.md) | Supplement Table 18 | C14 | Exhaustive seventeen-recipe subset sweep |
| [tables/supp_table19_registered_rule_power.md](tables/supp_table19_registered_rule_power.md) | Supplement Table 19 | C07 | Simulated pass rate of the registered rule |
| [tables/supp_table20_heldout_leave_one_task_out.md](tables/supp_table20_heldout_leave_one_task_out.md) | Supplement Table 20 | C08 | Held-out estimates with one task removed |

## Tables (derived and pending)
| File | Source | Claims | Description |
|------|--------|--------|-------------|
| [tables/derived_text_heldout_interim_results.md](tables/derived_text_heldout_interim_results.md) | Appendix C prose, §4.2 | C07 | Interim held-out results that also failed; 750M-only run |
| [tables/derived_text_interval_constructions.md](tables/derived_text_interval_constructions.md) | §2.3, Appendix C prose | C02, C05, C09 | Full-battery intervals under nine constructions |
| [tables/derived_text_polypythias_transfer.md](tables/derived_text_polypythias_transfer.md) | Appendix C prose, §4.4 | C15, C17 | Earlier 4,755-item PolyPythias transfer and 160M checkpoint check |
| [tables/pending_sec4_3_second_family_results.md](tables/pending_sec4_3_second_family_results.md) | §4.3 (pending) | C20, C21 | Placeholder: every value "Not available: scoring in progress" |

## Figures
| File | Source | Claims | Description |
|------|--------|--------|-------------|
| [figures/figure1_benchmark_removal.md](figures/figure1_benchmark_removal.md) | Figure 1, §4.1 | C04, C06 | Single-benchmark removal estimates and intervals (data from supplement Table 11) |
| [figures/derived_from_figure2_covariance_summary.md](figures/derived_from_figure2_covariance_summary.md) | Figure 2, Appendix C | C11 | Summary statistics of the correlation heatmaps and spectra; per-cell values not available |
| [figures/derived_from_supp_figure1_calibration_recovery.md](figures/derived_from_supp_figure1_calibration_recovery.md) | Supplement Figure 1 | C01, C09 | N1 recovery means at six effect sizes; band endpoints not available |
| [figures/derived_from_supp_figure2_prediction_contrasts.md](figures/derived_from_supp_figure2_prediction_contrasts.md) | Supplement Figure 2 | C17 | Prediction contrasts whose values the prose states |

## Experiment to evidence map
| Experiment | Evidence files |
|------------|----------------|
| E01 | table9, supp_table9, derived_from_supp_figure1 |
| E02 | table1, derived_text_interval_constructions |
| E03 | supp_table11, supp_table12, figure1, table7, supp_table7 |
| E04 | table2, table12, supp_table19, supp_table20, derived_text_heldout_interim_results |
| E05 | supp_table9 (N3), prose of Appendix A.3 and C (no table) |
| E06 | derived_from_figure2, supp_table5 (prediction 9) |
| E07 | table10, supp_table17, supp_table4 (G5, G7) |
| E08 | table5, supp_table13 |
| E09 | supp_table18, supp_table3, supp_table4, supp_table5 |
| E10 | derived_text_polypythias_transfer |
| E11 | table11 |
| E12 | table8, supp_table16, derived_from_supp_figure2 |
| E13 | table3, supp_table8 |
| E14 | table7, derived_text_interval_constructions (size-band row) |
| E15 | pending_sec4_3_second_family_results (Not available: scoring in progress) |
| E16 | pending_sec4_3_second_family_results (Not available: scoring in progress) |
