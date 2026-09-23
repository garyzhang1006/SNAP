# Architecture: SNAP measurement pipeline

Data flows from released (or newly scored) per-item outputs to a battery-level inflation factor with intervals and rule verdicts. No model training occurs; DataDecide analyses need no inference, while the registered test and PolyPythias arms add a scoring stage.

```
[Item scoring] -> [Reduction] -> [Half split] -> [Centring] -> [Cross-half statistics]
                                                                   |
                                        [Pooled ratio] <-----------+
                                              |
                  +---------------+-----------+------------+-------------------+
                  |               |                        |                   |
          [Wild bootstrap]  [Seed jackknife]    [Deletion sensitivity]   [Diagnostics]
                  |               |                        |
                  +-------> [Reading rules] <--------------+
```

## Item scoring
- **Purpose**: Produce per-item log-likelihoods for gold and alternative answers.
- **Inputs**: Model checkpoints; request files (DataDecide release requests for bank 1; OLMES builds at a pinned commit for held-out tasks and bank 2).
- **Outputs**: Per-item per-byte margin m and correctness a (Equation 1).
- **Interactions**: Feeds Reduction. Skipped for the primary DataDecide analysis, which reads released item scores.
- **Key design choices**: Byte-identical prompts for bank 1; float32 (registered test, PolyPythias bank scoring) or fp16 (earlier transfer); cached scores checked against an uncached reference within 0.001 nats.

## Reduction
- **Purpose**: Stream released tarballs once and keep item identifier, margin and accuracy bit at the common checkpoint.
- **Inputs**: 122.9 GB of gzipped JSONL tarballs (25 recipe archives).
- **Outputs**: One NumPy array per run (about 48 MB total for 375 runs), 37,682 items per run.
- **Interactions**: Selects the largest step available for all three runs of a configuration (checkpoint index cached and re-checked).
- **Key design choices**: One sequential pass because gzipped tar members require reading from their starts.

## Half split
- **Purpose**: Assign each benchmark's items to halves A and B once.
- **Inputs**: Trait labels per item; optional passage/story groups.
- **Outputs**: Boolean half-A mask reused for every run in an arm.
- **Interactions**: Feeds Centring through half scores.
- **Key design choices**: Balanced within-trait permutation from master seed 20260101 (not an item-ID hash); passage-aware variant for BoolQ check and for the registered test; bank-1 versus bank-2 halves for R2.

## Centring
- **Purpose**: Remove configuration means before products.
- **Inputs**: Half scores y^A, y^B per configuration (R x K each).
- **Outputs**: Centred deviations d^A, d^B.
- **Interactions**: Implemented by projecting onto an orthonormal basis of mean-zero run contrasts; the auxiliary contrast uses only the two auxiliary runs.
- **Key design choices**: Runtime checks on basis row sums and invariance of sum T_c under a shared configuration shift.

## Cross-half statistics
- **Purpose**: Form T_c (aggregate covariance) and U_c (trace part) per configuration.
- **Inputs**: d^A, d^B.
- **Outputs**: Vectors T and U of length N.
- **Interactions**: Feeds Pooled ratio, Wild bootstrap, Seed jackknife and deletions.
- **Key design choices**: Symmetrised matrix estimate for diagnostics; the headline ratio uses the sums directly without correlation normalisation.

## Pooled ratio
- **Purpose**: Estimate theta = sum T / sum U, Lambda = sqrt(theta), K_eff = K/Lambda^2, r_E = (Lambda^2 - 1)/(K - 1).
- **Inputs**: T, U (optionally restricted to a subset of configurations or benchmarks).
- **Outputs**: Point estimates.
- **Key design choices**: Sums pooled before division to avoid unstable per-configuration denominators.

## Wild bootstrap
- **Purpose**: Nominal 95% interval clustered on the 25 recipes.
- **Inputs**: T, U, recipe labels.
- **Outputs**: Interval on theta, square-rooted.
- **Key design choices**: Rademacher weights per cluster, fixed observed denominator, studentised, 4,999 draws, seed 0; discarded zero-SE draws; missing endpoint when negative.

## Seed jackknife
- **Purpose**: Primary interval for PolyPythias (nine seeds, five size clusters).
- **Inputs**: Population with a common seed index across configurations.
- **Outputs**: Delete-one-seed t(8) interval on theta, square-rooted; jackknife of within-minus-cross log difference.

## Deletion sensitivity
- **Purpose**: Recompute estimate and interval after deleting each recipe, recipe pair, size band and benchmark, and across weightings.
- **Outputs**: Spread reported beside the interval, since the factor belongs to the battery.

## Diagnostics
- **Purpose**: Reliability, correlation matrices, cross-format diagnostic, permutation references, calibration simulations, prediction comparisons.
- **Outputs**: Exploratory descriptions; none enters the headline ratio.

## Reading rules
- **Purpose**: Mechanical verdicts fixed before scoring.
- **Inputs**: Primary intervals.
- **Outputs**: Registered held-out verdict (pass iff wild lower limit > 1); R1 verdict (pass iff jackknife lower limit > 1); R2 verdict (not supported / supported / undecided).
- **Key design choices**: The rules name the interval the verdict uses; other intervals are reported beside it.
