# Estimation, inference and scoring configuration

The paper trains no models. "Training" settings here are the estimation, resampling, simulation and scoring settings that determine every reported number.

## Half-split master seed
- **Value**: 20260101
- **Rationale**: Makes the frozen balanced within-trait split reproducible from the repository alone.
- **Search range**: 50 item re-splits (primary run) and 200 re-drawn splits (permutation kernel) checked variation
- **Sensitivity**: low
- **Source**: Reproducibility statement; Appendix D.1; `src/seednoise/halves.py`

## Wild bootstrap draws
- **Value**: 4,999 Rademacher draws, bootstrap seed 0
- **Rationale**: Registered/shipped setting; a two-sided 95% bootstrap-t needs enough draws for tail quantiles.
- **Search range**: 1,999 draws for battery-size curves; 9,999 draws over twenty seeds for the eight-construction comparison
- **Sensitivity**: low
- **Source**: §2.3; Appendix D.2; Table 12 caption

## Recipe clusters
- **Value**: G = 25 (recipes); alternative 5 size-band clusters
- **Rationale**: Recipe is the designed exchangeable unit; five sizes of a recipe may share run structure.
- **Search range**: Size-band clustering and two-way clustering examined
- **Sensitivity**: medium
- **Source**: §2.3; Appendix C

## Minimum surviving bootstrap draws
- **Value**: max(100, 0.9B)
- **Rationale**: A draw with zero bootstrap SE has no finite studentised statistic.
- **Search range**: Not specified in paper
- **Sensitivity**: low
- **Source**: Appendix D.2

## Calibration replicates
- **Value**: 2,000 per population (repeat at 10,000); 4,000 or 8,000 in later sweeps; 300 for proxy simulations
- **Rationale**: Monte Carlo error about 0.005 on coverage at 2,000.
- **Search range**: 1,000 to 60,000 pooled replicates reported
- **Sensitivity**: low
- **Source**: §2.3; Appendix C; Table 9

## Permutation replicates
- **Value**: 500 (primary N2), 1,000 and 2,000 (repeats), 2,000 (item-group and batch-slot permutations)
- **Rationale**: Conditional randomisation references.
- **Search range**: As listed
- **Sensitivity**: low
- **Source**: Reproducibility statement; Appendix C

## Item re-splits
- **Value**: 50 (primary; 200 budgeted)
- **Rationale**: Measure re-split variation.
- **Search range**: 200 in the permutation kernel
- **Sensitivity**: low
- **Source**: Appendix D.4; Reproducibility statement

## Checkpoint rule
- **Value**: Largest step available for all three runs of a configuration
- **Rationale**: Aligns the observation step across replicates.
- **Search range**: Adjacent earlier shared step (123 configurations)
- **Sensitivity**: medium (accuracy)
- **Source**: §3; Appendix B.1

## Registered held-out rule
- **Value**: Pass iff lower 95% wild recipe-cluster limit of held-out margin inflation > 1; scope 530M, 750M, 1B; replacement if 1B pilot accuracy < chance + 0.02
- **Rationale**: Fixed before any production score existed.
- **Search range**: None (registered)
- **Sensitivity**: high
- **Source**: §4.2; Appendix C "Registered held-out test"

## PolyPythias rule R1
- **Value**: Delete-one-seed jackknife, t(8), pass iff lower endpoint > 1
- **Rationale**: Nine seeds are the replicate unit; five size clusters are too few for the wild bootstrap.
- **Search range**: None (fixed before scoring)
- **Sensitivity**: Not available: scoring in progress
- **Source**: §4.3; compute2/README.md

## PolyPythias rule R2
- **Value**: Half A = bank 1, half B = bank 2; reject shared-item explanation iff cross-bank interval above one and jackknife interval of within-minus-cross log difference includes zero; support iff difference positive and cross-bank interval covers one; otherwise undecided
- **Rationale**: Removes any component the two halves share only because they come from one item set.
- **Search range**: None (fixed before scoring)
- **Sensitivity**: Not available: scoring in progress
- **Source**: §4.3; compute2/README.md

## Scoring precision and batching (registered test and banks)
- **Value**: float32 weights; 6,000-token cap (registered test); transformers 4.57.1; reference check within 0.001 nats (24 items for bank scoring)
- **Rationale**: Batch grouping can change floating-point results.
- **Search range**: Earlier transport arm used fp16 with a 30,000-token cap (6,000 on a T4 rescore)
- **Sensitivity**: low (0.6 percent inflation shift from hardware and token budget change)
- **Source**: §4.2; Reproducibility statement; Appendix D.4

## Bank-2 construction
- **Value**: 6,808 items; OLMES at the DataDecide commit (5a51f502d463b8cdc4a2dcad7d7096c41ff1197e per compute2/config/banks.json); train split for eight benchmarks, validation for OpenBookQA and MMLU; cap 600 per benchmark except MMLU
- **Rationale**: Disjoint items for R2 within compute budget.
- **Search range**: Cap is a compute decision made before scoring
- **Sensitivity**: Not available: scoring in progress
- **Source**: §3; compute2/README.md; compute2/config/banks.json

## Planning thresholds (historical)
- **Value**: Lambda_M > 1.349, Lambda_A > 1.40; design effect 1.60 at rho_ICC 0.15; t(16) for seventeen estimation recipes; Lambda^2 = 1.819 at N = 85
- **Rationale**: From the planning document (uncorroborated date).
- **Search range**: Not applicable
- **Sensitivity**: Not applicable
- **Source**: §3; Appendix B.3-B.5; supplement Tables 3-5
