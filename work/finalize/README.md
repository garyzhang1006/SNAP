# Filling the PolyPythias results into the paper

Rule one (bank one, 45 runs) can be filled once both joshkerr1111 kernels finish. Rule two can't: it needs
`pythia_bank2_final`, bank two scored on the same 45 runs, and no kernel has scored it. Until it is, every
`\Rtwocase` branch and the cross-bank values stay pending, and the build with rule one filled and rule two
pending ends its main text on page 10 because it prints all three rule-two variants.

1. Download both kernels' `scores/pythia_bank1_final/*.npz` from joshkerr1111 into `results/pythia-bank1-josh/{a,b}/`.
2. Stage the 45 files. The script copies only, checks five sizes by nine seeds, and writes `MANIFEST.sha256`:

   ```bash
   python work/finalize/collect_scores.py --out work/finalize/stage results/pythia-bank1-partial results/pythia-bank1-josh
   ```

3. Upload `work/finalize/stage` as the private dataset `garyzhang11111/snap-pythia-bank1-scores`, then push
   `work/finalize/kernel` (CPU only, `enable_gpu` false). It rebuilds bank one at commit 6cfedee, checks the
   frozen hash and every score file against the manifest, and runs `reduce.py` and `analysis/estimates.py` unchanged.
4. Download the kernel's `results/` folder to `results/pythia-bank1-final/` and fill the paper:

   ```bash
   python work/finalize/fill_pending.py --results results/pythia-bank1-final
   ```

   This writes `deliverables/pythia_values.tex`, which sets `\Ronecase` from `verdicts.json` and gives each
   `\res{key}{label}` slot its value. It stops rather than fill if any run is missing or a point estimate or
   upper endpoint is undefined, and it also stops if any size's own estimate is undefined, since the per-size sentence then needs new wording. An undefined lower endpoint prints as n/a, as the per-size table already does.
5. Rebuild and run the six-build page check.

Tested on 2026-09-23 with deliberately fake fixture values in the scratchpad (rule one pass and fail, rule two
in each verdict, rule two absent, undefined lower endpoint). The filled builds end on page 9 when both rules
are decided. `estimates.py` was smoke-tested on an empty input to confirm the command line and imports.
