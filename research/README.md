# Scientific package

This directory holds the research artifacts, separate from the editorial materials in `deliverables/`.
Everything here is generated from frozen results by a script in `research/tools/`, and no number in it
was typed by hand.

## What is where

`manifest.csv` maps all 375 released runs to their repository, branch, checkpoint step and reduction
file, with a SHA-256 and a byte count for each reduction and the access code the availability census
returned for that repository. `protocol.md` records the estimand decisions, the prospective stage we
planned and did not run, and every amendment in the order it happened. `claims.csv` links manuscript
claims to artifacts and generating commands. `results/` holds the frozen tables described below.
`figures/` holds the script that draws the paired-prediction exhibit from those results. `tests/` holds
executable checks. `kaggle/` holds one directory per kernel, each with the script that ran and its
metadata. `LEDGER.md` records what each run showed and what the manuscript did about it, and
`kernel_status.tsv` records each run's terminal state and wall time.

## Score-table contract

Each reduction is an `.npz` named `<recipe>__<size>__seed-<seed>__step-<step>.npz`, which is the key,
and its fields are the ones a replicator gets on disk rather than a description of an earlier stage.
`item_id` is an int64 index over the 37,682 items of the fixed bank, `trait` is an int8 in zero to nine
naming the benchmark, `group` is an int16 in zero to sixty five naming the scoring task inside that
benchmark, `margin` is a float16 per-byte log-likelihood margin, `correct` is the same 37,682 outcomes
packed into 4,711 bytes at one bit each, `n_items` repeats the count so a truncated file fails loudly,
and `meta` is a JSON string carrying recipe, size, seed, step, batch flag, gain and task count.

The item bank is fixed, so a missing item is an error rather than a missing value, and the loaders
assert the count on every file. Scores carry no sentinel for missing, since absence is not
representable. The margin is stored at half precision, which sets the meaningful resolution of any
single item and is the reason every reported quantity is an average over thousands of them. Benchmark
weights are flat at one tenth each, subjects inside MMLU are macro-averaged before the battery average,
and BoolQ questions stay question weighted even where whole passages are assigned to halves, which
leaves half means with unequal denominators by design.

## Estimate-table contract

`results/simulation_cells.csv` carries one row per kernel, cell and interval construction, with the
unrounded coverage, its Monte Carlo standard error, the exclusion rate for the value one, the share of
replicates whose interval is undefined or unbounded, the median width, the true ratio the cell was
generated at, the varied parameters as JSON, the replicate count and the seed. The `interval_status`
column distinguishes a cell where every replicate produced a bounded interval from one where some did
not, so an undefined interval is never encoded as a zero or folded into the coverage.

`results/index.csv` carries one row per result file with its path, byte count, SHA-256 and the terminal
state its monitor recorded, so any number in the paper can be traced to the bytes that produced it.

## Running the checks

```
python3 research/tests/test_identities.py
python3 research/tests/test_package.py          # add --full to hash all 375 reductions
```

The first suite checks the estimator's algebra against closed forms and needs only numpy. The second
checks the package contracts, that the manifest matches the files on disk, that every coverage figure
is a probability, and that no kernel finished in a state the ledger does not name.

## Reproducing a result

Each kernel in `research/kaggle/` runs unmodified on Kaggle with the released reductions attached as a
dataset, and writes one JSON whose `design` key holds the question the run was written to answer, dated
before the run. The intended path for a replicator is to rerun a kernel, compare its JSON against the
copy in `research/outputs/`, and then rerun `research/tools/make_results_tables.py`, which rebuilds both
tables from whatever result files are present.
