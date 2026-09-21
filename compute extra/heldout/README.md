# new code: held-out scoring on Kaggle

This folder holds everything the GPU plan needs. One pipeline scores 375 DataDecide checkpoints on four held-out tasks and runs the pre-registered Λ̂ test from `PROTOCOL_heldout.md`. A separate CPU-only kernel reanalyses decisions on the shipped reduced runs. All compute runs on Kaggle, and nothing in this folder is meant to run models locally. The two local tools, `tools/make_shards.py` and `tools/freeze.py`, only read and write JSON.

Hugging Face needs no token, since all 125 `allenai/DataDecide-*` model repositories and the eval-instances release download anonymously. The Kaggle CLI uses its own credentials in `~/.kaggle/kaggle.json`, and no file here contains a token.

## Layout

| Path | What it is |
| --- | --- |
| `config/runs.json` | The 375 runs: recipe, size, seed, batch, step, hub repo and branch. Built by `config/make_runs.py` from the paper's reduction manifests, with every branch checked on the hub. |
| `config/tasks.json` | Held-out tasks, backups, the ARC-Easy verification task, seeds, scoring settings, pilot and scope rules. |
| `config/frozen.json` | Written by `tools/freeze.py` after k01. It doesn't exist until then. |
| `common/snapnew.py` | The request and score formats, alignment checks, and per-item margins. No torch. |
| `common/scorer.py` | OLMES-equivalent log-likelihood scoring with a packed context cache and a reference-path check. |
| `kaggle/k00-env-probe` | CPU. Logic tests, the OLMo install, a 150M checkpoint on CPU, cache versus reference, disk. |
| `kaggle/k01-requests` | CPU. Builds `requests.jsonl.gz` with OLMES at the pinned commit. |
| `kaggle/k02-score/k02-score-template.py` | The GPU scorer on two T4 cards. `tools/make_shards.py` turns it into the pilot and production kernels under `build/`. |
| `kaggle/k03-verify-release` | CPU. Checks the pilot against the release (seed-branch mapping and scorer fidelity), applies the backup rule, and writes `decision.json`. |
| `kaggle/k04-analyze-heldout` | CPU. Runs the held-out Λ̂ test with seednoise, plus the combined 14-trait and leave-one-task-out results. |
| `kaggle/k05-decision` | CPU. Wrong-call rates, power and the seed-count rule on the shipped runs, plus a figure. |
| `tools/push.sh` | Wraps the Kaggle CLI to push code and kernels, check status and fetch outputs. |
| `PROTOCOL_heldout.md` | The pre-registration. |

## Budget

These GPU figures are projections from the PolyPythias job's measured T4 throughput, and the pilot replaces them with measured numbers:

| Step | Hardware | Hours |
| --- | --- | --- |
| k00, k01, k03, k04 | CPU | under 1 each; k03 downloads the 4.9 GB c4 release tarball |
| k05 | CPU | a few |
| k02 pilot | 2x T4 | about 1 |
| k02 production, all 375 runs | 2x T4 | about 30 to 35 session hours |
| k02 production, 530M to 1B only | 2x T4 | about 15 |

Kaggle gives about 30 GPU hours a week and caps a session at 9 hours, which is why production is split into shards of at most 8.4 hours. `config/tasks.json` switches to the 530M to 1B scope whenever the pilot projects more than 30 session hours for the full scope, so with the estimate above the fallback is the likely outcome. If you want the full scope across two quota weeks, raise `fallback_if_projected_t4_hours_above` before step 2, because changing it after the freeze counts as a protocol change.

## Run order

Every `push.sh kernel` starts a Kaggle job. Nothing has been pushed yet, and each push needs your go-ahead.

1. Push the code, then probe the environment on CPU.
   ```bash
   tools/push.sh code
   ```
   ```bash
   tools/push.sh kernel kaggle/k00-env-probe
   ```
   Check that `probe_report.json` shows `all_ok: true`. If the OLMo import fails against the Kaggle image, fix the install lines in k00 and in the k02 template together, because they must stay identical.

2. Build the requests and freeze them.
   ```bash
   tools/push.sh kernel kaggle/k01-requests
   ```
   ```bash
   tools/push.sh output snap-new-k01-requests outputs/k01
   ```
   Read `outputs/k01/requests_summary.json` and confirm the item counts, the choice counts and that no context is longer than about 8,000 characters. Then freeze:
   ```bash
   python3 tools/freeze.py outputs/k01/requests_summary.json
   ```
   Commit `config/frozen.json` and push the code again (`tools/push.sh code`), since k02 reads the freeze from the dataset.

3. Pilot on GPU, about 1 hour.
   ```bash
   python3 tools/make_shards.py pilot
   ```
   ```bash
   tools/push.sh kernel kaggle/k02-score/build/snap-new-k02-pilot
   ```
   `shard_report.json` should list 6 runs done with none failed. The `mode` in each timing entry should be `packed`. `reference` still gives correct numbers, only about 3 to 5 times slower.

4. Verify against the release on CPU.
   ```bash
   tools/push.sh kernel kaggle/k03-verify-release
   ```
   ```bash
   tools/push.sh output snap-new-k03-verify-release outputs/k03
   ```
   `decision.json` must show `seed_branch_mapping_verified: true`. If a hub run matches a different release seed, fix `SEED_BRANCH` in `config/make_runs.py`, rebuild `runs.json`, push the code and rerun the pilot. If no seed matches, the scorer or prompts differ from OLMES, and production must not start. Read `comparisons` first.

5. Production on GPU.
   ```bash
   tools/push.sh output snap-new-k02-pilot outputs/k02-pilot
   ```
   ```bash
   python3 tools/make_shards.py production --pilot-report outputs/k02-pilot/shard_report.json --decision outputs/k03/decision.json
   ```
   Read `kaggle/k02-score/build/plan.json` for the scope, the shard count and the projected hours. Then push `snap-new-k02-s01`, `s02` and so on, one at a time, within the weekly quota. A shard that reports `not_started` runs needs a follow-up shard with those runs.

6. Run the held-out test on CPU. `make_shards.py production` already added every shard to k04's kernel sources.
   ```bash
   tools/push.sh kernel kaggle/k04-analyze-heldout
   ```
   `heldout_results.json` holds `verdict` (PASS or FAIL under the protocol rule) and every reported number, and `heldout_table.csv` has them in table form.

k05 needs none of the steps above and can run at any time:
```bash
tools/push.sh kernel kaggle/k05-decision
```

## What is and isn't verified

The only local checks were `py_compile` on every Python file and a JSON parse of the configs. None of the kernels has run yet. k00 exists to catch environment problems on CPU before any GPU hour is spent, and k03 exists to catch a wrong seed mapping or a scorer mismatch before production. The seed-to-branch mapping stays an assumption until k03 passes.
