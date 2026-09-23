# Model and battery configuration

## DataDecide population
- **Value**: 25 data recipes x 5 sizes (150M, 300M, 530M, 750M, 1B) x 3 replicates = 375 runs in 125 configurations
- **Rationale**: Smaller released models lack the required per-item replicate coverage.
- **Search range**: Not applicable
- **Sensitivity**: medium (530M band removal gives the only failing deletion)
- **Source**: §1; §3

## DataDecide seed labels
- **Value**: {2, 14, 15} below 1B; {2, 4, 5} at 1B; the seed sets initialisation and data order together; one label shared across every recipe inside a size band
- **Rationale**: Release design.
- **Search range**: Not applicable
- **Sensitivity**: medium (band-shared effect bounded at 0.044)
- **Source**: §3; §6

## DataDecide auxiliary schedules
- **Value**: Auxiliary replicates below 1B stop at 25 percent of the 1B compute budget; selected step averages 41.5% of the 750M default final step (range 18% to 44%) and 87% at 530M (range 39% to 89%)
- **Rationale**: Release design.
- **Search range**: Not applicable
- **Sensitivity**: medium
- **Source**: §3; Appendix B.1

## Benchmark battery (K = 10)
- **Value**: ARC-Challenge (MC), ARC-Easy (MC), BoolQ (yes/no), CommonsenseQA (MC), HellaSwag (cloze), MMLU (MC, 57 subjects macro-averaged), OpenBookQA (MC), PIQA (cloze), Social IQa (MC), WinoGrande (cloze); 37,682 items per run; halves of 18,840 and 18,842 items
- **Rationale**: DataDecide's released battery.
- **Search range**: Subsets and weightings examined in Appendix C
- **Sensitivity**: high
- **Source**: §3; Table 6; Appendix B.2

## Held-out battery (registered test)
- **Value**: SciQ, MedMCQA, multiple-choice DROP, multiple-choice CoQA, 1,000 items each; replaced AGIEval LogiQA-en and LSAT-LR under the registered rule
- **Rationale**: Tasks outside the ten that shaped the estimator.
- **Search range**: Not applicable
- **Sensitivity**: high (CoQA removal 1.090)
- **Source**: §4.2; Appendix C

## PolyPythias population
- **Value**: GPT-NeoX, nine seeds at each of 14M, 31M, 70M, 160M, 410M; same code, data and hyperparameters; seed sets initialisation and data order; scored at shared final step 143,000 (45 runs)
- **Rationale**: Clean replicate design absent from DataDecide.
- **Search range**: Earlier transport used three planned sizes plus a five-size rescore on 4,755 items; 160M adjacent check at steps 143000 and 142000 on 1,800 items
- **Sensitivity**: Not available: scoring in progress (bank-1 full battery)
- **Source**: §3; §4.3; Appendix C "Transport to PolyPythias"

## Bank 1 and bank 2
- **Value**: Bank 1 = 37,682 items with DataDecide release request text; bank 2 = 6,808 disjoint items (see training.md)
- **Rationale**: R1 uses bank 1; R2 pairs bank 1 with bank 2.
- **Search range**: Not applicable
- **Sensitivity**: Not available: scoring in progress
- **Source**: §3; §4.3

## External panel
- **Value**: Heineman et al. (2025) single-configuration panels, ten initialisation runs or nine data-order runs, twenty checkpoints
- **Rationale**: External check on score-scale contrast.
- **Search range**: Not applicable
- **Sensitivity**: Not applicable
- **Source**: §4.4; Table 11
