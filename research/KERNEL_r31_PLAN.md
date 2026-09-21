# Kernel r31: attribute-oriented item splits and a seed-matched paired interval

Written 2026-09-21 after the third blind panel (4/4/4, meta 4) named identification of the shared item component as the first of two evidence items that move the paper from 4 to 5. Nothing here has run. The kernel needs the user's explicit approval before it is pushed, per the standing no-local-compute and Kaggle-approval rules. A first draft that used the library's `group` split mode was refuted before any run (the mode flips each stratum's orientation by a coin toss, and the inflation factor moves through its denominator under any attribute split), and this version is the repaired design.

## What it computes

`compute extra/research_kernels/snap-r31-structured-splits/` is a private CPU kernel on the same inputs as `snap-r2-grouped` (the `snap-compute-src` dataset, the 375 reduced runs, and the `snap-r3-requests-audit` output that carries `doc_tables.json` with prompt length and gold position for all 37,682 items and the BoolQ passage groups).

Three attribute splits per task, written into each dataset manifest as `original_half` so that side 0 is the same attribute in every benchmark and every MMLU subject:

- `length`: items above the task's median prompt length on side 0.
- `gold`: gold answer in the first half of the answer positions on side 0 (BoolQ yes, WinoGrande option 1).
- `parity`: even document id on side 0, the exchangeable control.

For each split, score scale and battery (full and without BoolQ) it reports the inflation factor with its wild recipe interval, the per-benchmark diagonal, the off-diagonal contribution to the aggregate variance, the per-benchmark half sizes, and the shift from the original split in units of the wild standard error. The reference for each split is a permutation null of 60 partitions that shuffle the same side labels within each stratum, so every null partition has the same per-stratum half sizes as the structured one, and the kernel reports z scores and percentiles against that null for both the inflation factor and the off-diagonal contribution. The BoolQ passage-group split from r2 runs as a second control, since BoolQ's length split is close to its passage split.

Reading rule, written into the output: the quantity that can carry a cross-benchmark shared item effect is the off-diagonal contribution, and a shift in the inflation factor alone can come from a within-benchmark run-by-attribute interaction or a per-half scale difference. A scalar item effect uniform over every item is not identified by any partition. The permutation z is conditional on the fixed runs and items and carries no run-level sampling uncertainty.

Second block: the seed-matched paired-difference ratio over same-size recipe pairs. The kernel first asserts that it reproduces the appendix (1,500 pairs, 1,445 margin and 1,222 accuracy pairs with a positive paired-difference variance, medians 1.024 and 1.081, stricter subsets 1.027 and 1.079 over 1,379 and 919 pairs) and then runs a dyadic recipe-cluster percentile bootstrap of the lower weighted median over 4,999 draws, pairs weighted by the product of the two recipes' draw counts, with the estimand, the 25-cluster caveat and the unresampled within-pair noise stated in the output.

## Cost

`snap-r2-grouped` ran the adapter and a handful of C01 jobs in about two minutes. This kernel runs the adapter three times, 16 bootstrapped C01 jobs, and 720 unbootstrapped C01 jobs for the permutation nulls at about one to two seconds each, so under thirty minutes on a CPU kernel, no GPU.

## Launch (after approval)

```bash
kaggle kernels push -p "compute extra/research_kernels/snap-r31-structured-splits"
```

Pull the output into `research/outputs/snap-r31-structured-splits/` and read `structured_splits.json`. Every number is exploratory and post hoc, and no evidence label in the paper moves on it.
