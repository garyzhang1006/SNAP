---
title: "Estimating Run-to-Run Covariance Across Language Model Benchmarks"
authors: ["Anonymous authors"]
year: 2026
venue: "ICLR 2027 (submission, under review)"
doi: "Not available from provided input (anonymous submission, no DOI or arXiv ID)"
ara_version: "1.0"
domain: "Machine learning evaluation methodology; statistical measurement of language model benchmarks"
keywords:
  - run-to-run variance
  - benchmark covariance
  - cross-half estimator
  - variance inflation
  - effective benchmark count
  - wild cluster bootstrap
  - DataDecide
  - PolyPythias
  - registered held-out test
  - language model evaluation
claims_summary:
  - "On per-byte margins over 375 DataDecide runs, the battery-average run standard deviation is 1.244 times the independence value, interval [1.143, 1.338] (exploratory)."
  - "On accuracy the interval [0.993, 1.157] includes one at a design with low power, so it is read as a bound of 1.157, not as independence."
  - "The registered held-out test on four unseen tasks fails its lower-limit rule at 1.217 [0.872, 1.498]; the original ten benchmarks on the same runs give 1.240 [1.054, 1.397]."
  - "BoolQ holds 68% of the margin covariance trace; removing it gives 1.786 [1.689, 1.877], so the factor belongs to the battery."
  - "On real recipe comparisons the covariance changes the wrong-call rate by at most 0.009, with every interval for that change reaching zero."
  - "PolyPythias replication (R1) and disjoint-bank shared-item check (R2) are pending: scoring in progress, no numbers or verdicts available."
abstract: "A run-to-run standard error for a benchmark average built from each benchmark's variance alone ignores the covariance between benchmark scores. The estimator SNAP splits each benchmark's items into two halves and takes cross-half products of run-centred scores so item-sampling noise drops out; the paper states the conditions for identifying run covariance and calibrates recipe-cluster intervals in simulation. Applied to 375 released DataDecide runs spanning 125 configurations and ten benchmarks, per-byte margins give a battery-average standard deviation 1.244 times the independent value (interval [1.143, 1.338], lower endpoint 1.095 under a test inversion added later), equivalent to 6.5 independent benchmarks of the same average variance, and every recipe, recipe-pair and benchmark deletion leaves an interval that excludes one. A second-family replication on PolyPythias and a disjoint item bank check are described with rules fixed before scoring; their results are pending in the source. BoolQ carries 68% of the margin covariance trace, and removing it leaves 1.786 across the nine remaining benchmarks. On accuracy the interval [0.993, 1.157] includes one under a low-powered design. A registered test on four unseen tasks fails its lower-limit rule at 1.217 with interval [0.872, 1.498], while on the same runs the original ten benchmarks give 1.240 with [1.054, 1.397]. Every other analysis is exploratory, no registration carries an independently corroborated timestamp, and on real recipe comparisons the covariance changes the wrong-call rate by at most 0.009. The paper recommends paired replicate scores across the chosen battery with a benchmark-removal check."
---

# Estimating Run-to-Run Covariance Across Language Model Benchmarks

## Overview

The paper defines SNAP (Seed Noise Across Phenotypes), a cross-half moment estimator of the covariance of run deviations between benchmarks, and summarises that covariance as an inflation factor Lambda: the ratio of the battery-average run standard deviation to the value independence would give at the same marginal variances. On 375 released DataDecide runs (25 recipes x 5 sizes x 3 replicates, ten benchmarks, 37,682 items), margin inflation is 1.244 with a recipe-cluster interval excluding one, accuracy inflation is 1.078 with an interval including one, and the size of the factor is set mostly by BoolQ. A registered test on four unseen tasks failed its rule. Apart from that registered test and two PolyPythias rules fixed before scoring (whose results are still pending in the source), every empirical analysis is labelled exploratory by the paper.

Source status caveat: `main.tex` section 4.3 ("A second family and a disjoint item bank") carries `\pending{...}` placeholders and `\outcome{...}` switches set to pending (`\Ronecase=0`, `\Rtwocase=0`). This ARA records R1 and R2 as pending/untested and does not choose an outcome.

## Layer Index

### Cognitive Layer (`/logic`)
| File | Description |
|------|-------------|
| [problem.md](logic/problem.md) | Observations O1-O8, gaps G1-G5, key insight, assumptions A1-A8 |
| [claims.md](logic/claims.md) | 21 claims (C01-C21), including 2 pending (C20, C21) and 2 refuted registered/planned predictions (C07, C14) |
| [concepts.md](logic/concepts.md) | 23 defined terms with notation and boundary conditions |
| [experiments.md](logic/experiments.md) | 16 declarative experiment plans (E01-E16), no numbers |
| [solution/architecture.md](logic/solution/architecture.md) | Component graph of the SNAP pipeline from item scores to verdicts |
| [solution/algorithm.md](logic/solution/algorithm.md) | Estimator equations, wild bootstrap-t, seed jackknife, R1/R2 rules, pseudocode, complexity |
| [solution/constraints.md](logic/solution/constraints.md) | Identification limits, design limits, provenance limits |
| [solution/heuristics.md](logic/solution/heuristics.md) | 14 implementation heuristics (H01-H14) |
| [related_work.md](logic/related_work.md) | 16 typed RW blocks covering 23 references, plus brief entries for the other 30 of the 53-entry bibliography |

### Physical Layer (`/src`)
| File | Description | Claims |
|------|-------------|--------|
| [configs/training.md](src/configs/training.md) | Estimation, bootstrap, simulation and scoring settings (no model training in this paper) | C02, C07, C09, C20, C21 |
| [configs/model.md](src/configs/model.md) | Model families, sizes, seeds, checkpoints and benchmark battery scored | C02, C07, C15, C20 |
| [execution/snap_estimator.py](src/execution/snap_estimator.py) | Cross-half T_c/U_c, pooled Lambda, K_eff, r_E, centring via run contrasts, split | C01, C02, C03 |
| [execution/snap_inference.py](src/execution/snap_inference.py) | Wild cluster bootstrap-t, delete-one-seed jackknife, registered and R1/R2 reading rules | C02, C07, C09, C20, C21 |
| [environment.md](src/environment.md) | Python/NumPy versions, hardware, pinned scoring stack, seeds | all |

### Exploration Graph (`/trace`)
| File | Description |
|------|-------------|
| [exploration_tree.yaml](trace/exploration_tree.yaml) | 35-node research DAG: 6 dead ends, 3 pivots, 8 decisions, 16 experiments (2 pending: R1, R2), 2 questions |

### Evidence (`/evidence`)
| File | Description |
|------|-------------|
| [README.md](evidence/README.md) | Index of 31 table files (13 paper tables, 14 supplement tables, 3 derived prose extractions, 1 pending placeholder) and 4 figure files (1 raw, 3 derived) |
