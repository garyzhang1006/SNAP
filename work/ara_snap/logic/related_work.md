# Related Work

Typed blocks for works with a specific technical relation; the rest of the 53-entry bibliography follows as brief entries. DOIs are given only where the bibliography provides an arXiv identifier; otherwise "Not specified in paper".

## RW01: Magnusson et al., 2025 (DataDecide)
- **DOI**: arXiv:2504.11393
- **Type**: imports
- **Delta**:
  - What changed: Uses DataDecide's released per-item outputs (25 recipes, five sizes with three replicates, ten benchmarks) as the primary population; reads the release's request text byte for byte for bank 1.
  - Why: The only released suite with matched replicates and per-item outputs at these sizes.
- **Claims affected**: C02, C03, C04, C05, C06, C07, C13
- **Adopted elements**: Runs, benchmarks, checkpoint index, request files, auxiliary-run schedule.

## RW02: van der Wal et al., 2025 (PolyPythias)
- **DOI**: arXiv:2503.09543
- **Type**: imports
- **Delta**:
  - What changed: Scores nine seeds at five sizes on the paper's battery as a second family with a clean seed design.
  - Why: DataDecide lacks a replicate design where the seed is a clean rerun.
- **Claims affected**: C15, C20, C21
- **Adopted elements**: 45 checkpoints at step 143,000.

## RW03: Heineman et al., 2025 (Signal and noise)
- **DOI**: arXiv:2508.13144
- **Type**: extends
- **Delta**:
  - What changed: They measure per-benchmark signal and noise and relate the ratio to decision accuracy; this paper estimates covariance between benchmarks and uses their released random-seed panels as an external check.
  - Why: Per-benchmark noise omits off-diagonal terms of the average's variance.
- **Claims affected**: C16, C18
- **Adopted elements**: External seed panel (initialisation and data-order runs).

## RW04: Bouthillier et al., 2021
- **DOI**: Not specified in paper
- **Type**: extends
- **Delta**:
  - What changed: They derive variance inflation from correlated repeated trainings of one pipeline on one task; this paper applies covariance accounting across benchmarks within a replicate run.
  - Why: Benchmark averages combine correlated run deviations across tasks.
- **Claims affected**: C02
- **Adopted elements**: Variance-inflation framing.

## RW05: Spearman, 1904; Cronbach, 1951
- **DOI**: Not specified in paper
- **Type**: imports
- **Delta**:
  - What changed: The cross-half identity follows split-half repeated-measurement ideas, applied to run deviations across benchmarks rather than items of one test; Cronbach motivates the 50 re-splits (N3).
  - Why: Disjoint halves cancel item-sampling noise in cross products.
- **Claims affected**: C01, C10
- **Adopted elements**: Split-half construction.

## RW06: Searle et al., 1992
- **DOI**: Not specified in paper
- **Type**: imports
- **Delta**:
  - What changed: Variance-component moment estimation; explains negative moment estimates when the true component lies near zero.
  - Why: Justifies keeping negative-diagonal benchmarks.
- **Claims affected**: C01, C02
- **Adopted elements**: Moment estimation of variance components.

## RW07: Martin and Eaves, 1977; Cheverud, 1988
- **DOI**: Not specified in paper
- **Type**: extends
- **Delta**:
  - What changed: Quantitative-genetics covariance structure used as an analogy (between-configuration R_P versus within-configuration R_E); Cheverud's genetic-phenotypic correlation comparison motivates the phenotypic plug-in, which fails here.
  - Why: Tests whether cheap between-configuration correlation predicts run correlation.
- **Claims affected**: C17
- **Adopted elements**: P2 plug-in baseline.

## RW08: Cameron et al., 2008; MacKinnon and Webb, 2017
- **DOI**: Not specified in paper
- **Type**: imports
- **Delta**:
  - What changed: Wild cluster bootstrap-t for few clusters applied to a ratio of pooled moments with a fixed denominator.
  - Why: 25 recipe clusters.
- **Claims affected**: C02, C09
- **Adopted elements**: Rademacher wild cluster bootstrap-t.

## RW09: Bell and McCaffrey, 2002
- **DOI**: Not specified in paper
- **Type**: bounds
- **Delta**:
  - What changed: Few-cluster bias concerns; the paper notes the bootstrap-t addresses them without guaranteeing coverage at 25 clusters; CR3 correction examined in simulation.
  - Why: Coverage check.
- **Claims affected**: C09, C19
- **Adopted elements**: Leverage/CR3-style correction as a comparator.

## RW10: Cheverud, 2001; Nyholt, 2004; Li and Ji, 2005
- **DOI**: Not specified in paper
- **Type**: baseline
- **Delta**:
  - What changed: They count effective independent tests from correlation eigenvalues to adjust thresholds; this paper converts a noise covariance into an effective benchmark count for a fixed battery.
  - Why: Different target (variance of an average, not test multiplicity).
- **Claims affected**: C03
- **Adopted elements**: Effective-count framing.

## RW11: Madaan et al., 2024; Reimers and Gurevych, 2017; Zhou et al., 2020
- **DOI**: arXiv:2406.10229 (Madaan); others Not specified in paper
- **Type**: extends
- **Delta**:
  - What changed: They report seed-related variability of scores per benchmark or score distributions; Zhou's Spearman matrix averages checkpoints across seeds; this paper adds covariance between benchmark-specific run deviations.
  - Why: Off-diagonal terms enter aggregate variance.
- **Claims affected**: C02
- **Adopted elements**: none

## RW12: Jordan, 2024
- **DOI**: Not specified in paper
- **Type**: extends
- **Delta**:
  - What changed: Separates example-specific training variance from distribution-level variation and compares accuracies across related evaluation sets (shifted versions of one benchmark); this paper targets covariance across different benchmarks.
  - Why: Item-general versus fixed-bank distinction.
- **Claims affected**: C01
- **Adopted elements**: none

## RW13: Dodge et al., 2020
- **DOI**: arXiv:2002.06305
- **Type**: extends
- **Delta**:
  - What changed: They examine whether favourable initialisations transfer across tasks and compare four GLUE rankings across seeds without a covariance matrix.
  - Why: This paper estimates the covariance matrix itself.
- **Claims affected**: C02
- **Adopted elements**: none

## RW14: Schaeffer et al., 2023
- **DOI**: Not specified in paper
- **Type**: bounds
- **Delta**:
  - What changed: Discontinuous metrics change apparent trends; accuracy thresholds the margin at zero, so both scales are reported.
  - Why: Score-scale dependence of inflation.
- **Claims affected**: C05
- **Adopted elements**: Two-scale reporting.

## RW15: Kish, 1965
- **DOI**: Not specified in paper
- **Type**: imports
- **Delta**:
  - What changed: Design effect 1 + (m - 1) rho_ICC used for planning (1.60) and numerator-based design effects (2.06, 1.26).
  - Why: Planning power.
- **Claims affected**: C14
- **Adopted elements**: Design effect formula.

## RW16: Karamcheti et al., 2021 (Mistral)
- **DOI**: Not specified in paper (URL https://crfm.stanford.edu/2021/08/26/mistral.html)
- **Type**: bounds
- **Delta**:
  - What changed: Considered as a source of held-out loss for a competence covariate; lacks a per-run benchmark battery.
  - Why: Needed an independent competence measurement.
- **Claims affected**: C12
- **Adopted elements**: none

## Remaining citations (background, excluded populations, comparison)
- Sellam et al., 2022 (MultiBERTs): 25 seeds of one configuration; excluded population.
- McCoy et al., 2020: 100 BERT fine-tuning runs from one checkpoint; excluded population.
- Biderman et al., 2023 (Pythia): size ladder without seed replicates; excluded.
- Team OLMo et al., 2025 (arXiv:2501.00656): OLMo-2 checkpoints lack replicates at matched steps; excluded.
- Hagmann et al., 2023: scalar variance components for nondeterminism.
- Bui et al., 2025 (arXiv:2503.07329); Hochlehnert et al., 2025: fine-tuning and decoding seeds, differ from pretraining-run variation.
- Dufour et al., 2026 (arXiv:2606.20536): training versus sampling variation in generative-model evaluation.
- Miller, 2024 (arXiv:2411.00640): item-level uncertainty for one model.
- Zhao et al., 2026 (arXiv:2605.20798): per-task tests without cross-task covariance.
- Haupt et al., 2026 (arXiv:2605.30916): per-item variation on PolyPythias.
- Dehghani et al., 2021 (arXiv:2107.07002); Demšar, 2006; Dror et al., 2017; Card et al., 2020; Gorman and Bedrick, 2019; Burnell et al., 2023: benchmark selection, inference, power, split dependence, per-instance reporting.
- Henderson et al., 2018; Agarwal et al., 2021: resample runs within tasks, whereas SNAP preserves paired run effects across benchmarks.
- Hardy et al., 2026 (arXiv:2605.25272); Kohli, 2026 (arXiv:2605.29800); Messing, 2026 (arXiv:2604.11581); Sha and Zhao, 2026 (arXiv:2603.29357): dependence across models, judges or prompts.
- Brown, 1910; Spearman, 1910: Spearman-Brown formula shares the form 1 + (k - 1) rho, but for parallel items.
- Campbell and Fiske, 1959: multitrait-multimethod; no benchmark here appears in multiple formats.
- Brennan, 2001: generalizability theory framework.
- Hofmann et al., 2025 (arXiv:2509.11106); Kipnis et al., 2025 (arXiv:2407.12844): ability structures across models.
- Hedges et al., 2010: dependent effect sizes without a complete covariance matrix.
