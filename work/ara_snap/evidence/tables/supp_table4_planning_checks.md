# Supplement Table 4 - Planning checks, responses and outcomes

**Source**: Table 4 of the extended supplement, Extended Supplement to "Estimating Run-to-Run Covariance Across Language Model Benchmarks" (supplement_extended_body.tex, "Decision checks and deviations", label tab:original5)
**Caption**: Planning checks, proposed responses, and observed outcomes in the source analysis. The original assessment labels four checks as failures, while G2 uses a lower threshold that can't discriminate under its model.
**Extraction type**: raw_table

| Check | Condition and timing | Proposed response | Reported outcome |
| --- | --- | --- | --- |
| G0 | Outputs parse at the common step, day 1 | Drop unavailable cells, report reduced N if fewer than 70 estimation cells remain | Pass, all 125 cells |
| G1 | Accuracy power at r_E=0.115 at least 0.80, day 2 | Make accuracy secondary and report margin in the abstract | Pass, power 1.00 against an inflation of 1.427 at rho_g=0.73 |
| G2 | Median information ratio at least 1.4, day 2 | Remove comparative information claim | Ratio 1.61, threshold below the ratio's floor |
| G3 | Symmetric cross-half covariance and positive diagonal, day 3 | Split by source document, then report leakage if asymmetry persists | Fail, one negative margin diagonal and two accuracy diagonals |
| G4 | abs(Lambda-hat - 1) <= 0.02 under N1 and N2, day 4 | Subtract calibrated offset and report both estimates | Pass, offset at most 0.002 |
| G5 | N5 accounts for less than 50 percent of excess, day 5 | Lead with sharpness and report accuracy alone | Fail, default simulator share 0.61 |
| G6 | PolyPythias transport error within 20 percent, day 6 | Report transport failure and its ratio | Fail upward under the excess-ratio reading |
| G7 | Held-out loss available in metadata, day 1 | Use leave-one-trait-out competence covariate | Fail, no required field |
| G8 | Auxiliary-run Lambda >= 1+0.5(Lambda_full - 1), day 5 | Lead with auxiliary-run estimate if condition fails | Pass on both point estimates, margin 1.256 versus 1.122, intervals cross their boundaries |
