# compute2 results

Every number below is exploratory and post hoc with respect to the paper's registration; the reading rules were fixed in README.md before any run was scored.

## Verification gate

Not run: reduced/verify has no runs

## PolyPythias, nine seeds per size at one matched step, the paper's items and prompts

Items 37682, final step 143000, split seednoise.halves.split_items(seed=20260101).

### Within bank 1 (the paper's design on the replicate family)

| battery | phenotype | contrast | Lambda | K_eff | primary interval | wild (recipe/size) | cluster t | config boot |
|---|---|---|---|---|---|---|---|---|
| full | margin | all | 1.302 | 5.897 | [0.921, 1.595] | [nan, 2.063] | [0.826, 1.646] | [1.045, 1.506] |
| full | accuracy | all | 1.481 | 4.557 | [0.561, 2.019] | [nan, 2.523] | [nan, 2.159] | [0.933, 1.976] |
| no_boolq | margin | all | 2.273 | 1.743 | [1.553, 2.814] | [1.917, 2.580] | [1.938, 2.564] | [1.394, 2.369] |
| no_boolq | accuracy | all | 2.500 | 1.440 | [2.367, 2.625] | [2.473, 2.526] | [2.415, 2.581] | [nan, 4.253] |

Per size (one configuration, nine seeds, jackknife):

| size | margin Lambda | jackknife | accuracy Lambda | jackknife |
|---|---|---|---|---|
| 14m | 1.203 | [nan, 2.284] | 1.029 | [0.464, 1.379] |
| 31m | 1.096 | [0.802, 1.327] | 1.142 | [0.990, 1.276] |
| 70m | 1.198 | [nan, 1.737] | 2.353 | [nan, 3.902] |
| 160m | 0.997 | [nan, 1.465] | 0.815 | [0.474, 1.050] |
| 410m | 1.576 | [0.841, 2.064] | 2.140 | [1.444, 2.659] |

### Cross-bank (A = every bank-1 item, B = every bank-2 item, same runs)

| battery | phenotype | contrast | Lambda | K_eff | primary interval | wild (recipe/size) | cluster t | config boot |
|---|---|---|---|---|---|---|---|---|
| full | margin | all | 1.293 | 5.984 | [0.920, 1.580] | [nan, 2.148] | [0.731, 1.676] | [1.016, 1.522] |
| full | accuracy | all | 1.530 | 4.272 | [0.441, 2.118] | [nan, 2.787] | [nan, 2.317] | [0.870, 2.109] |
| no_boolq | margin | all | 2.301 | 1.700 | [1.370, 2.951] | [1.782, 2.722] | [1.841, 2.683] | [1.240, 2.427] |
| no_boolq | accuracy | all | 2.570 | 1.363 | [2.191, 2.900] | [2.461, 2.674] | [2.391, 2.737] | [1.142, 2.631] |

### Within bank 2 (halves of the disjoint items)

| battery | phenotype | contrast | Lambda | K_eff | primary interval | wild (recipe/size) | cluster t | config boot |
|---|---|---|---|---|---|---|---|---|
| full | margin | all | 1.286 | 6.049 | [0.911, 1.573] | [nan, 2.167] | [0.651, 1.698] | [0.993, 1.535] |
| full | accuracy | all | 1.590 | 3.954 | [0.334, 2.224] | [nan, 3.105] | [nan, 2.472] | [0.820, 2.215] |
| no_boolq | margin | all | 2.309 | 1.687 | [1.137, 3.062] | [1.554, 2.872] | [1.693, 2.793] | [1.001, 2.486] |
| no_boolq | accuracy | all | 2.613 | 1.318 | [2.393, 2.816] | [2.342, 2.859] | [2.131, 3.020] | [nan, 2.836] |

Within-bank-1 minus cross-bank, delete-one-seed jackknife:

- margin, full battery: 0.015 [-0.035, 0.065] on log theta (halve for log Lambda)
- margin, without BoolQ: -0.024 [-0.184, 0.135] on log theta (halve for log Lambda)
- accuracy, full battery: -0.064 [-0.174, 0.045] on log theta (halve for log Lambda)
- accuracy, without BoolQ: -0.055 [-0.266, 0.156] on log theta (halve for log Lambda)

Cross-format not run: reduced/pythia_bank2zs_final has no runs

Curve not run: reduced/pythia_bank1_curve has no runs

## DataDecide, 375 runs, bank 1 from the release and bank 2 scored here

Not run: reduced/datadecide_bank2 has no runs

## Verdicts under the pre-specified reading rules

```json
{
 "V0_verification": {
  "pass": null,
  "status": "not run",
  "rule": "every verify run reproduces the release margins within the nats thresholds and agrees on correctness for at least the threshold fraction of items"
 },
 "R1_pythia_replicates_margin": {
  "lambda": 1.3022243165382272,
  "lo": 0.9206589861012651,
  "hi": 1.5949806809105547,
  "interval": "delete-one-seed jackknife t(8)",
  "pass": false,
  "rule": "nine-seed PolyPythias at one matched step, jackknife lower endpoint above one"
 },
 "R1_pythia_replicates_accuracy": {
  "lambda": 1.4814118469703015,
  "lo": 0.5605288217300143,
  "hi": 2.018655384333315,
  "interval": "delete-one-seed jackknife t(8)",
  "pass": false,
  "rule": "nine-seed PolyPythias at one matched step, jackknife lower endpoint above one"
 },
 "R2_pythia_identification_margin": {
  "cross_lambda": 1.2927062502373492,
  "cross_lo": 0.9203132984532629,
  "cross_hi": 1.5796209455105017,
  "within_minus_cross_log_theta": 0.014671851506020128,
  "diff_lo": -0.03519325515121176,
  "diff_hi": 0.06453695816325201,
  "shared_item_explanation": "undecided",
  "rule": "cross-bank interval above one and the within-minus-cross difference including zero rejects the item explanation; a positive difference interval with a cross-bank interval covering one supports it"
 },
 "R2_pythia_identification_accuracy": {
  "cross_lambda": 1.529946907717057,
  "cross_lo": 0.4412188509576661,
  "cross_hi": 2.1182070263375032,
  "within_minus_cross_log_theta": -0.06447490050772009,
  "diff_lo": -0.17391558798775664,
  "diff_hi": 0.04496578697231646,
  "shared_item_explanation": "undecided",
  "rule": "cross-bank interval above one and the within-minus-cross difference including zero rejects the item explanation; a positive difference interval with a cross-bank interval covering one supports it"
 }
}
```
