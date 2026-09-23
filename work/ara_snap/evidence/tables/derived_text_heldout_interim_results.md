# Derived subset - Registered held-out test interim results and 750M-only run

**Source**: Derived from text of Appendix C "Registered held-out test" (appendices_bcd.tex, label app:heldout) and §4.2; no numbered source table
**Caption**: Held-out and original-battery estimates at the scopes that preceded the full-scope registered test, plus the exploratory 750M-only run, transcribed from prose. Configuration counts of 25 per size band and 50 for two sizes come from Appendix C (each band holds 25 configurations) and supplement Table 19.
**Extraction type**: derived_subset
**Derived from**: prose of Appendix C; complements `table2_registered_heldout_test.md`

| Scope | Configurations | Battery | Margin Lambda | Margin interval | Accuracy Lambda | Accuracy interval | Rule verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 530M alone (interim) | 25 | Held-out | 1.198 | [0.864, 1.454] | 1.373 | [1.138, 1.567] | fail |
| 530M and 750M | 50 | Held-out | 1.201 | [0.546, 1.616] | 1.327 | [1.153, 1.484] | fail |
| 530M and 750M | 50 | Original ten | 1.316 | [0.880, 1.637] | Not specified in paper | Not specified in paper | fail |
| 530M, 750M plus 18 recipes at 1B (second interim) | 68 | Held-out | 1.181 | [0.685, 1.552] | 1.262 | [1.084, 1.422] | fail |
| 530M, 750M plus 18 recipes at 1B (second interim) | 68 | Original ten | 1.174 | [0.954, 1.360] | Not specified in paper | Not specified in paper | not read |
| 18 scored 1B configurations alone | 18 | Held-out | 1.152 | [0.599, 1.516] | Not specified in paper | Not specified in paper | not read |
| 18 scored 1B configurations alone | 18 | Original ten | 0.947 | [0.295, 1.306] | Not specified in paper | Not specified in paper | not read |
| 750M alone (exploratory) | 25 | Held-out | 1.203 | [undefined, 1.828] | 1.299 | [0.959, 1.584] | not read |
| 750M alone (exploratory) | 25 | Original ten | 1.110 | [0.686, 1.407] | 0.987 | [0.310, 1.320] | not read |
| Held-out pooled with original ten, full scope | 75 | Fourteen tasks | 1.419 | [1.051, 1.714] | 1.240 | [0.986, 1.458] | not read |

Additional prose facts: pilot LogiQA-en mean accuracy 0.269 against a bar of 0.270, LSAT-LR 0.219 against 0.220 (chance 0.25 and 0.20); pilot binomial SE about 0.010; item-count cap of 1,000 per benchmark gives original-battery margin 1.218 [1.121, 1.309] against 1.247 [1.146, 1.342] uncapped; cap of 200 gives 1.179 [1.002, 1.337]; post hoc three-size curve four-benchmark median 1.172 with 5th/95th percentiles 0.979 and 1.485.
