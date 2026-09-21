"""R31 identification checks on the matched 37,682-item universe: attribute-oriented item splits and a seed-matched paired interval.

Question. The cross-half estimate is identified only up to an item effect that
is shared across benchmarks and repeated across halves. A random split carries
any such component equally in both halves. This kernel splits every task's
items by an attribute a run-level item effect could follow (prompt length,
gold answer position) and orients every benchmark the same way, so the two
halves are no longer exchangeable with respect to an effect tied to that
attribute. The quantity that can carry a cross-benchmark shared effect is the
off-diagonal sum of the cross-half covariance, so the kernel reports the
off-diagonal contribution and the per-benchmark diagonal under each split, and
the inflation factor beside them, with and without BoolQ.

Reference. Each structured split is compared with a permutation null that
shuffles the same labels within each stratum, so every permuted partition has
the same per-stratum half sizes as the structured one. The shift is reported
in units of that null's spread and in units of the wild cluster standard error
of the original estimate. A doc-id parity split is the exchangeable control,
and the BoolQ passage-group split from r2 is the second control, since BoolQ's
length split is close to a passage split.

Limits, written into the output. A within-benchmark run-by-attribute
interaction or a per-half scale difference moves the inflation factor through
its denominator without any cross-benchmark effect, which is why the
off-diagonal contribution is the reported target. A scalar item effect uniform
over every item enters every partition identically and is not identified by
any of this. Everything here is exploratory and post hoc on the same runs and
items that produced the published estimate.

Second block. The seed-matched paired-difference ratio over same-size recipe
pairs, reported in the appendix as a median without an interval, gets a
recipe-cluster (dyadic) percentile bootstrap over 4,999 draws after the kernel
asserts that it reproduces the appendix's counts and medians.

Outputs: /kaggle/working/structured_splits.json and the SNAP job directories.
"""
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")
SEED = 20260921
DRAWS = 4999
PERMS = 60
TRAITS = ["arc_challenge", "arc_easy", "boolq", "csqa", "hellaswag", "mmlu", "openbookqa", "piqa", "socialiqa", "winogrande"]
PUBLISHED_PAIRS = {"margin": {"total": 1500, "positive": 1445, "strict": 1379, "median": 1.024, "median_strict": 1.027},
                   "accuracy": {"total": 1500, "positive": 1222, "strict": 919, "median": 1.081, "median_strict": 1.079}}


def find(name):
    hits = [p for p in Path("/kaggle/input").rglob(name) if not p.name.startswith("._")]
    if not hits:
        sys.exit(f"{name} not found under /kaggle/input")
    return hits[0]


shutil.copytree(find("run_two_gpus.py").parent, W / "snap_compute", ignore=shutil.ignore_patterns("__pycache__", "._*"))
PKG = W / "snap_compute"
shutil.copytree(find("pyproject.toml").parent, W / "seed-noise", ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(W / "seed-noise")])
for f in ("snap_adapter.py", "snap_intervals.py", "r9_pairs.py", "requests_audit.py"):
    hits = [p for p in Path("/kaggle/input").rglob(f) if not p.name.startswith("._")]
    assert len({hashlib.sha256(h.read_bytes()).hexdigest() for h in hits}) == 1, (f, [str(h) for h in hits])
    shutil.copy(hits[0], W / f)
sys.path.insert(0, str(W))
from requests_audit import ITEM_STRIDE, TASK_INDEX, trait_of  # noqa: E402

docs = json.load(open(find("doc_tables.json")))
assert sum(len(t) for t in docs.values()) == 37682, sum(len(t) for t in docs.values())
boolq_groups = json.load(open(find("boolq_groups_from_requests.json")))
assert set(boolq_groups) == {"boolq"} and len(boolq_groups["boolq"]) == 3270

# Attribute labels per item. Side 0 is long / goldA / even for every task, so orientation is fixed across benchmarks.
AXES = ("length", "gold", "parity")
side = {a: {} for a in AXES}
axis_report = {}
for task, table in docs.items():
    trait = trait_of(task)
    chars = np.array([v["stem_chars"] for v in table.values()], float)
    cut = float(np.median(chars))
    counts = {a: [0, 0] for a in AXES}
    gold_hist = {}
    for d, v in table.items():
        item = str(TASK_INDEX[task] * ITEM_STRIDE + int(d))
        n_choices = len(v["choice_hashes"]) or 2          # WinoGrande ships no choice hashes and has two options
        gold = int(v["gold"]) - (1 if task == "winogrande" else 0)
        assert 0 <= gold < n_choices, (task, d, v["gold"], n_choices)
        gold_hist[str(gold)] = gold_hist.get(str(gold), 0) + 1
        labels = {"length": 0 if v["stem_chars"] > cut else 1,
                  "gold": 0 if gold < n_choices / 2 else 1,
                  "parity": 0 if int(d) % 2 == 0 else 1}
        for a, s in labels.items():
            side[a].setdefault(trait, {})[item] = s
            counts[a][s] += 1
    for a in AXES:
        assert min(counts[a]) > 0, (task, a, counts[a])
    axis_report[task] = {"median_stem_chars": cut, "gold_positions": gold_hist,
                         **{a: {"side0": counts[a][0], "side1": counts[a][1]} for a in AXES}}
for a in AXES:
    assert sorted(side[a]) == sorted(TRAITS), sorted(side[a])
print(f"[labels] built at {time.time() - t0:.0f}s", flush=True)

runs = W / "runs"; runs.mkdir(exist_ok=True)
n = 0
for p in sorted(Path("/kaggle/input").rglob("*.npz")):
    if p.name.startswith("._") or "moments" in p.name or "scores" in p.name:
        continue
    shutil.copy(p, runs / p.name); n += 1
assert n == 375, n
data = W / "datasets"
subprocess.check_call([sys.executable, str(W / "snap_adapter.py"), "--runs", str(runs), "--out", str(data / "plain")])
subprocess.check_call([sys.executable, str(W / "snap_adapter.py"), "--runs", str(runs), "--out", str(data / "noboolq"), "--exclude", "boolq"])
(W / "groups_passage.json").write_text(json.dumps(boolq_groups))
subprocess.check_call([sys.executable, str(W / "snap_adapter.py"), "--runs", str(runs), "--out", str(data / "passage"),
                       "--groups", str(W / "groups_passage.json")])
print(f"[adapter] done at {time.time() - t0:.0f}s", flush=True)


def run_job(job, cfg, out, quiet=False):
    cfg_path = W / "configs" / f"{out}.json"; cfg_path.parent.mkdir(exist_ok=True)
    cfg_path.write_text(json.dumps({**cfg, "template_only": False}, indent=2))
    t1 = time.time()
    subprocess.check_call([sys.executable, str(PKG / "runs" / f"{job}.py"), "--config", str(cfg_path), "--out", str(W / "SNAP" / out)],
                          stdout=subprocess.DEVNULL if quiet else None)
    if not quiet:
        print(f"[{job}] {out} in {time.time() - t1:.0f}s", flush=True)
    return json.load(open(W / "SNAP" / out / "result.json"))


def intervals(out, ds):
    path = W / "SNAP" / out / "original_intervals.json"
    subprocess.check_call([sys.executable, str(W / "snap_intervals.py"), "--c01", str(W / "SNAP" / out), "--dataset", ds, "--out", str(path)])
    return json.load(open(path))


def oriented_manifest(src_manifest, dst_manifest, assign):
    """Write a copy of a snap-scores-v1 manifest whose original_half follows the given item -> side map.

    The score archive and its hash are untouched, so the loader's archive check still passes.
    """
    meta = json.load(open(src_manifest))
    for b in meta["benchmarks"]:
        m = assign[b["name"]]
        missing = [i for i in b["item_ids"] if i not in m]
        assert not missing, (b["name"], len(missing), missing[:3])
        b["original_half"] = [int(m[i]) for i in b["item_ids"]]
        assert set(b["original_half"]) == {0, 1}, b["name"]
    meta["arrays"] = str(Path(src_manifest).parent / meta["arrays"]) if not Path(meta["arrays"]).is_absolute() else meta["arrays"]
    Path(dst_manifest).parent.mkdir(parents=True, exist_ok=True)
    with open(dst_manifest, "w") as fh:
        json.dump(meta, fh)
    return meta


def clean(o):
    """JSON-safe copy: numpy scalars to Python, non-finite floats to null."""
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, (np.integer, np.bool_)):
        return o.item()
    return o


def dump(summary):
    (W / "structured_splits.json").write_text(json.dumps(clean(summary), indent=1))


def stat(x, f):
    return float(f(x)) if x.size >= 2 else None


def permuted(assign, meta, rng):
    """Shuffle each benchmark's side labels within each stratum, keeping per-stratum half sizes."""
    out = {}
    for b in meta["benchmarks"]:
        ids = b["item_ids"]
        strata = np.asarray(b.get("strata", ["all"] * len(ids)))
        labels = np.array([assign[b["name"]][i] for i in ids])
        new = labels.copy()
        for s in sorted(set(strata.tolist())):
            idx = np.flatnonzero(strata == s)
            new[idx] = rng.permutation(labels[idx])
        out[b["name"]] = dict(zip(ids, new.tolist()))
    return out


def pick(result, iv):
    return {"lambda": result["lambda"], "status": result["status"], "T": result["T"], "U": result["U"],
            "offdiagonal_sum": iv["offdiagonal_sum"], "aggregate_offdiagonal_contribution": iv["aggregate_offdiagonal_contribution"],
            "diagonal": iv["diagonal"], "trace_shares": iv["trace_shares"], "wild": iv["wild"],
            "negative_diagonal_count": result["negative_diagonal_count"]}


def lower_median(x, w=None):
    x = np.asarray(x, float)
    w = np.ones_like(x) if w is None else np.asarray(w, float)
    o = np.argsort(x); x, w = x[o], w[o]
    c = np.cumsum(w)
    return float(x[np.searchsorted(c, 0.5 * c[-1])])


summary = {"seed": SEED, "draws": DRAWS, "permutations": PERMS, "axes": axis_report, "phenotypes": {},
           "limits": ["A within-benchmark run-by-attribute interaction or a per-half scale difference moves the inflation factor "
                      "through its denominator without any cross-benchmark effect, so read the off-diagonal contribution, not lambda.",
                      "A scalar item effect uniform over every item enters every partition identically and is not identified here.",
                      "Permutation z scores are conditional on the 375 runs and the 37,682 items and carry no run-level sampling "
                      "uncertainty; the shift in wild-se units is the comparable scale.",
                      "Everything is post hoc on the runs and items that produced the published estimate."]}
for phen in ("margin", "accuracy"):
    block = {"battery": {}}
    for battery, dsdir in (("full", data / "plain"), ("noboolq", data / "noboolq")):
        plain = str(dsdir / phen / "scores.json")
        meta = json.load(open(plain))
        base = run_job("C01", {"seed": SEED, "dataset": plain, "split_mode": "original", "bootstrap_draws": DRAWS}, f"C01_{phen}_{battery}_original")
        base_iv = intervals(f"C01_{phen}_{battery}_original", plain)
        wild_se = base_iv["wild"].get("se")          # snap_intervals swallows a failed wild bootstrap into an error dict
        bb = {"original": pick(base, base_iv), "structured": {}}
        rng = np.random.default_rng([SEED, phen == "accuracy", battery == "noboolq"])
        for a in AXES:
            assign = {b["name"]: side[a][b["name"]] for b in meta["benchmarks"]}
            ds = str(data / f"{a}_{battery}" / phen / "scores.json")
            oriented_manifest(plain, ds, assign)
            r = run_job("C01", {"seed": SEED, "dataset": ds, "split_mode": "original", "bootstrap_draws": DRAWS}, f"C01_{phen}_{battery}_{a}")
            iv = intervals(f"C01_{phen}_{battery}_{a}", ds)
            lam_null, off_null, undefined = [], [], 0
            for k in range(PERMS):
                pds = str(data / f"{a}_{battery}_perm" / phen / f"scores_{k}.json")
                oriented_manifest(plain, pds, permuted(assign, meta, rng))
                pr = run_job("C01", {"seed": SEED, "dataset": pds, "split_mode": "original", "bootstrap_draws": 0}, f"perm_{phen}_{battery}_{a}_{k}", quiet=True)
                shutil.rmtree(W / "SNAP" / f"perm_{phen}_{battery}_{a}_{k}", ignore_errors=True)
                Path(pds).unlink(missing_ok=True)
                if pr.get("lambda") is None:
                    undefined += 1
                    continue
                lam_null.append(pr["lambda"])
                off = np.asarray(pr["covariance"], float)
                w = np.asarray(meta["weights"], float)
                off_null.append(float(w @ off @ w - (w * w) @ np.diag(off)))
            lam_null, off_null = np.array(lam_null, float), np.array(off_null, float)
            lam, offc = r["lambda"], iv["aggregate_offdiagonal_contribution"]
            sd_l, sd_o = stat(lam_null, lambda x: x.std(ddof=1)), stat(off_null, lambda x: x.std(ddof=1))
            entry = pick(r, iv)
            entry.update({
                "half_sizes": {b["name"]: [int(sum(1 for i in b["item_ids"] if assign[b["name"]][i] == s)) for s in (0, 1)] for b in meta["benchmarks"]},
                "shift_lambda_from_original": None if lam is None else lam - base["lambda"],
                "shift_lambda_in_wild_se": None if lam is None or not wild_se else (lam - base["lambda"]) / wild_se,
                "permutation_null": {"n": int(lam_null.size), "undefined": undefined,
                                     "lambda_mean": stat(lam_null, np.mean), "lambda_sd": sd_l,
                                     "offdiag_mean": stat(off_null, np.mean), "offdiag_sd": sd_o},
                "lambda_z_against_null": None if lam is None or not sd_l else (lam - lam_null.mean()) / sd_l,
                "lambda_null_percentile": None if lam is None or not lam_null.size else float((lam_null <= lam).mean()),
                "offdiag_z_against_null": None if not sd_o else (offc - off_null.mean()) / sd_o,
                "offdiag_null_percentile": None if not off_null.size else float((off_null <= offc).mean()),
                "granularity": f"percentiles move in steps of 1/{PERMS}; treat |z| above 3 as extrapolation"})
            bb["structured"][a] = entry
            print(phen, battery, a, "lambda", lam, "offdiag", offc, "z_lambda", entry["lambda_z_against_null"],
                  "z_off", entry["offdiag_z_against_null"], "in wild se", entry["shift_lambda_in_wild_se"], flush=True)
        if battery == "full":
            pds = str(data / "passage" / phen / "scores.json")
            r = run_job("C01", {"seed": 20260914, "dataset": pds, "split_mode": "group", "bootstrap_draws": DRAWS}, f"C01_{phen}_passage_group")
            iv = intervals(f"C01_{phen}_passage_group", pds)
            bb["boolq_passage_group_control"] = pick(r, iv)
            bb["boolq_passage_group_control"]["shift_lambda_from_original"] = r["lambda"] - base["lambda"]
            bb["boolq_passage_group_control"]["note"] = ("r2 seed 20260914; group mode re-randomises the nine non-BoolQ benchmarks' "
                                                        "halves as well, so the shift mixes that re-split with the BoolQ passage grouping")
        block["battery"][battery] = bb
    summary["phenotypes"][phen] = block
    dump(summary)

    # Seed-matched paired-difference ratio, reproduced against the appendix, then a dyadic recipe bootstrap of the median.
    plain = str(data / "plain" / phen / "scores.json")
    pairs_path = W / "SNAP" / f"pairs_{phen}.json"
    subprocess.check_call([sys.executable, str(W / "r9_pairs.py"), "--c01", str(W / "SNAP" / f"C01_{phen}_full_original"),
                           "--dataset", plain, "--out", str(pairs_path)])
    pairs = json.load(open(pairs_path))["pairs"]
    va = np.array([p["variance_a"] for p in pairs]); vb = np.array([p["variance_b"] for p in pairs])
    cab = np.array([p["covariance_ab"] for p in pairs])
    ra = [p["id"].split("|")[0] for p in pairs]; rb = [p["id"].split("|")[1] for p in pairs]
    recipes = sorted(set(ra) | set(rb))
    ia = np.array([recipes.index(x) for x in ra]); ib = np.array([recipes.index(x) for x in rb])
    paired_var = va + vb - 2 * cab
    indep = va + vb
    keep = (paired_var > 0) & (indep > 0)           # the appendix filter; pairs with a nonpositive independence sum are counted below
    strict = keep & (va > 0) & (vb > 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        ratio = np.where(keep, np.sqrt(np.abs(paired_var) / np.where(indep > 0, indep, 1.0)), np.nan)
    pub = PUBLISHED_PAIRS[phen]
    repro = {"pairs_total": int(len(pairs)), "positive_paired_variance": int(keep.sum()), "strict": int(strict.sum()),
             "median_positive": float(np.median(ratio[keep])), "median_strict": float(np.median(ratio[strict])),
             "percentiles_5_95_positive": [float(v) for v in np.percentile(ratio[keep], [5, 95])],
             "share_covariance_positive": float((cab > 0).mean()),
             "positive_paired_variance_with_nonpositive_independence": int(((paired_var > 0) & ~(indep > 0)).sum()),
             "recipes": len(recipes)}
    ok = (repro["pairs_total"] == pub["total"] and repro["positive_paired_variance"] == pub["positive"] and repro["strict"] == pub["strict"]
          and abs(repro["median_positive"] - pub["median"]) < 6e-4 and abs(repro["median_strict"] - pub["median_strict"]) < 6e-4)
    repro["reproduces_appendix"] = bool(ok)
    if not ok:
        block["seed_matched_paired"] = {"reproduction": repro, "reproduction_failed": True, "published": pub}
        dump(summary)
        raise AssertionError((repro, pub))
    rng = np.random.default_rng([SEED, 7, phen == "accuracy"])
    boot = {"positive_paired_variance": [], "strict": []}
    invalid = {"positive_paired_variance": 0, "strict": 0}
    for _ in range(DRAWS):
        mult = np.bincount(rng.integers(0, len(recipes), len(recipes)), minlength=len(recipes))
        w = (mult[ia] * mult[ib]).astype(float)
        for name, mask in (("positive_paired_variance", keep), ("strict", strict)):
            m = mask & (w > 0) & np.isfinite(ratio)
            if m.sum() < 2:
                invalid[name] += 1
                continue
            boot[name].append(lower_median(ratio[m], w[m]))
    block["seed_matched_paired"] = {
        "reproduction": repro,
        "point_lower_median": {"positive_paired_variance": lower_median(ratio[keep & np.isfinite(ratio)]),
                               "strict": lower_median(ratio[strict & np.isfinite(ratio)])},
        "recipe_bootstrap_median_interval": {k: [float(v) for v in np.percentile(np.array(b), [2.5, 97.5])] for k, b in boot.items()},
        "invalid_draws": invalid, "clusters": len(recipes), "draws": DRAWS,
        "estimand": "lower weighted median over recipe-pair ratios of paired-difference sd to independence sd, three-run means, five sizes held fixed; "
                    "the appendix's plain median (reproduction.median_positive) can sit above the lower median by under 0.001 on even-sized sets",
        "method": "dyadic recipe-cluster percentile bootstrap, pairs weighted by the product of the two recipes' draw counts, "
                  "self-pairs omitted, within-pair estimation noise in the variances not resampled, 25 clusters so the interval is anti-conservative"}
    print(phen, "paired", json.dumps(block["seed_matched_paired"]), flush=True)
    summary["phenotypes"][phen] = block
    dump(summary)

shutil.rmtree(runs, ignore_errors=True); shutil.rmtree(W / "seed-noise", ignore_errors=True)
for d in data.glob("*"):
    for phen in ("margin", "accuracy"):
        (d / phen / "scores.npz").unlink(missing_ok=True)
    if d.name.endswith("_perm"):
        shutil.rmtree(d, ignore_errors=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
