# snap-r5 Kaggle results

## Shared-component bound: the largest uniform share the cross-format diagnostic allows (done)

Kernel garyzhang11111/snap-r5-shared-bound, COMPLETE (CPU, 24 s). File results/snap-r5-shared-bound/r5_shared_bound.json, script r5_shared_bound.py beside it. The setup, data sources, injection model and sums are copied verbatim from snap-r3-r2-02 (r2_02.py), and the recomputed observed cross-format values are asserted equal to the stored snap-r2-r1-50 values to 1e-9. The model assumes zero off-diagonal cross-benchmark seed covariance, so the shared share q gives Lambda(q) = sqrt(1 + N q A / sum U) and cross-format D(q) = sqrt(1 + N q C / sum U), and the largest admissible share at limit L is (L^2 - 1) sum U / (N C). Fractions of the excess are (Lambda(q) - 1) / (Lambda_obs - 1) on the Lambda scale and N q A / (sum T - sum U) on the covariance scale.

| quantity | margin | accuracy |
|---|---|---|
| observed full-matrix Lambda | 1.2439499117191137 | 1.0783733870898096 |
| observed cross-format, wild | 0.9211891046274687 [0.8006569396931505, 1.034729865199787] | 0.9651889498004318 [0.8483992935798912, 1.063438097874525] |
| share that explains the whole excess, q* | 1.4224827977168986 | 0.052558551570596315 |
| largest share with D(q) <= observed upper limit | 0.4198218091972702 | 0.07170458495558704 |
| Lambda that share alone produces | 1.077756576498004 | 1.1055435038866464 |
| fraction of excess, Lambda scale | 0.31873992472493123 | 1.3466752912656694 |
| fraction of excess, covariance scale | 0.29513313614132203 | 1.3642800802695998 |
| largest share at rounded limit (1.035 / 1.063) | 0.42314342456348747 | 0.07119428066518974 |
| Lambda at rounded limit | 1.0783494281476291 | 1.1048279987636431 |
| fraction of excess at rounded limit, Lambda scale | 0.3211701434753599 | 1.337545851419165 |
| largest share with D(q) <= observed point | 0.0 | 0.0 |
| implied cross-format seed covariance sum at q = 0 | -0.0003995979766877743 | -0.00019442583348349383 |
| implied cross-format seed covariance sum at the upper-limit share | -0.0005860970856482341 | -0.0005664525488702633 |

Bears on claim_audit CA2 and kill_argument KA1 (work/rebuttal/r5), and on main.tex Sec 2, "which constrains a uniform component of that size". Under zero seed covariance a uniform share of at most 0.420 survives the margin upper limit, and on its own that share produces margin Lambda 1.078, about 32 percent of the 0.244 excess (30 percent on the covariance scale), so the diagnostic rules out a shared component as the whole explanation but not as roughly a third of it. At the point estimate no positive share survives, because D(q) >= 1 for every q >= 0 and both observed points sit below 1, which already requires negative cross-format seed covariance under this model. On accuracy the bound doesn't bind, since the admissible share 0.0717 exceeds q* 0.0526 and would produce 1.106, more than the whole observed excess. All of these bounds fail if cross-format seed covariance is negative, which is the offset KA1 raises.
