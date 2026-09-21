"""CPU-only checks of the pieces that carry the numbers: the reduction matches
seednoise's reducer bit for bit, the reduced files load through seednoise, and
the analysis recovers a known inflation factor from synthetic banks."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "analysis"))

import bank  # noqa: E402
import estimates as est  # noqa: E402
import tasks66  # noqa: E402
from reduce import save_reduced  # noqa: E402
from seednoise.data import datadecide as dd  # noqa: E402
from seednoise.phenotypes import reduce_choices  # noqa: E402
from seednoise.store import load_run  # noqa: E402


def test_constants_match_seednoise():
    assert tasks66.TASKS == list(dd.TASKS)
    assert tasks66.TRAITS == list(dd.TRAITS)
    assert tasks66.ITEM_STRIDE == dd.ITEM_STRIDE
    assert sum(tasks66.RELEASE_ITEMS.values()) == tasks66.RELEASE_TOTAL


def fake_requests(rng, per_task=6):
    rows = []
    for task in ["arc_easy", "boolq", "mmlu_anatomy", "mmlu_virology", "winogrande"]:
        k = 2 if task in ("boolq", "winogrande") else 4
        for d in range(per_task):
            rows.append({"task": task, "task_index": tasks66.TASK_INDEX[task], "doc_id": d, "native_id": d,
                         "label": int(rng.integers(k)), "group": f"{task}:doc{d}", "context": f"Q{d}\nAnswer:",
                         "continuations": [" " + "x" * int(rng.integers(1, 6)) for _ in range(k)]})
    return rows


def test_per_item_matches_seednoise_reduce_choices(tmp_path):
    rng = np.random.default_rng(0)
    rows = fake_requests(rng)
    bank.validate_requests(rows)
    table = bank.choice_table(rows)
    sums = rng.normal(-20, 5, size=table["choice"].size)
    scores = dict(table, sum_logits=sums, meta=np.asarray(json.dumps({"x": 1})))
    got = bank.per_item(scores, rows, "bank1")
    # seednoise's reducer on the same per-byte scores and release ids.
    iid = table["task_index"] * tasks66.ITEM_STRIDE + table["doc_id"]
    trait = np.asarray([tasks66.TRAIT_INDEX[tasks66.trait_of_task(tasks66.TASKS[t])] for t in table["task_index"]])
    ref = reduce_choices(iid, trait, sums / table["num_bytes"], table["is_gold"], group=table["task_index"])
    assert np.array_equal(got["item_id"], ref.item_id)
    assert np.allclose(got["margin"], ref.margin)
    assert np.array_equal(got["correct"], ref.correct)
    assert np.array_equal(got["group"], ref.group)
    # Round trip through the reduced format and seednoise's loader.
    p = tmp_path / "r.npz"
    save_reduced(p, got, {"recipe": "c4", "size": "1B", "seed": 2, "step": 1, "batch": 0, "gain": -0.5})
    items, meta = load_run(p)
    assert items.n_items == ref.n_items and meta["size"] == "1B"
    assert np.array_equal(items.correct, ref.correct)
    # float16 storage, the paper's own schema: about three significant digits.
    assert np.allclose(items.margin, ref.margin, rtol=1e-3, atol=1e-3)


def test_bank_ids_never_collide():
    a = bank.item_id if hasattr(bank, "item_id") else tasks66.item_id
    b1 = tasks66.item_id("bank1", 65, 9_999_999)
    b2 = tasks66.item_id("bank2", 0, 0)
    assert b1 < b2
    assert tasks66.item_id("bank1", 1, 17) == tasks66.TASK_INDEX["arc_easy"] * tasks66.ITEM_STRIDE + 17


def test_split_by_group_balances_every_group():
    group = np.repeat(np.arange(5), [8, 9, 2, 40, 3])
    m = est.split_by_group(group, seed=1)
    for g in range(5):
        idx = group == g
        assert m[idx].sum() == idx.sum() // 2


# -- a synthetic population with a known inflation factor ----------------------


def synth_bank(rng, n_items_per_trait, base, run_effect, item_noise=1.0):
    """Per-item margins for one run on one bank: a trait-level run effect
    shared by every item of the trait, plus independent item noise."""
    ids, trait, group, margin = [], [], [], []
    for j, t in enumerate(tasks66.TRAITS):
        n = n_items_per_trait
        tasks = [k for k in tasks66.TASKS if tasks66.trait_of_task(k) == t]
        for i in range(n):
            task = tasks[i % len(tasks)]
            ids.append(tasks66.item_id(base, tasks66.TASK_INDEX[task], i // len(tasks)))
            trait.append(j)
            group.append(tasks66.TASK_INDEX[task])
            margin.append(run_effect[j] + item_noise * rng.normal())
    ids = np.asarray(ids); o = np.argsort(ids)
    return {"item_id": ids[o], "trait": np.asarray(trait)[o], "group": np.asarray(group)[o],
            "margin": np.asarray(margin)[o], "correct": np.asarray(margin)[o] > 0}


def make_population(root, rng, rbar, n_sizes=5, n_seeds=9, n_items=240, sd=0.3):
    K = len(tasks66.TRAITS)
    C = np.full((K, K), rbar); np.fill_diagonal(C, 1.0)
    L = np.linalg.cholesky(C)
    for s in range(n_sizes):
        size = ["14m", "31m", "70m", "160m", "410m"][s]
        mean = rng.normal(0, 2, size=K)
        for i, seed in enumerate(range(1, n_seeds + 1)):
            eff = mean + sd * (L @ rng.normal(size=K))
            for job, base in (("pythia_bank1_final", "bank1"), ("pythia_bank2_final", "bank2")):
                items = synth_bank(rng, n_items, base, eff)
                meta = {"recipe": "polypythias", "size": size, "seed": seed, "step": 143000, "batch": i, "gain": -1.0}
                save_reduced(root / job / f"polypythias__{size}__seed-{seed}__step-143000.npz", items, meta)


def _run_synthetic(tmp_path, monkeypatch, seed, rbar):
    root = tmp_path / f"s{seed}"
    make_population(root, np.random.default_rng(seed), rbar, n_items=400)
    # The release battery check is for real data; the synthetic bank is smaller.
    monkeypatch.setattr(tasks66, "RELEASE_TOTAL", 4000)
    monkeypatch.setattr(est, "N_BOOT", 99)
    res = est.analysis_pythia(root, root)
    assert res["status"] == "ok"
    return res


def test_analysis_recovers_known_lambda(tmp_path, monkeypatch):
    """Five sizes by nine seeds is a small design, so one draw can land 0.3
    from the truth; the check is calibration over four draws, which is what
    the jackknife interval claims to deliver."""
    K = len(tasks66.TRAITS)
    rbar = 0.06
    truth = float(np.sqrt(1 + (K - 1) * rbar))
    lam, cover, diff_cover = [], 0, 0
    for seed in (100, 101, 102, 103):
        res = _run_synthetic(tmp_path, monkeypatch, seed, rbar)
        w = res["within_bank1"]["full"]["margin"]["all"]
        c = res["cross_bank"]["full"]["margin"]["all"]
        lam += [w["lambda"], c["lambda"]]
        cover += w["jackknife"]["lo"] < truth < w["jackknife"]["hi"]
        d = res["within_minus_cross"]["margin"]["full"]
        diff_cover += d["lo"] <= 0.0 <= d["hi"]
        assert abs(w["lambda"] - c["lambda"]) < 0.15
    assert abs(np.mean(lam) - truth) < 0.2, (lam, truth)
    assert cover >= 3 and diff_cover >= 3, (cover, diff_cover)


def test_analysis_null_has_lambda_near_one(tmp_path, monkeypatch):
    lam = []
    for seed in (200, 201, 202):
        res = _run_synthetic(tmp_path, monkeypatch, seed, 0.0)
        lam.append(res["within_bank1"]["full"]["margin"]["all"]["lambda"])
    assert abs(np.mean(lam) - 1.0) < 0.15, lam


def _row(lam, lo, hi, key):
    return {"lambda": lam, key: {"lo": lo, "hi": hi, "method": key}}


def test_verdict_rules_on_fixed_inputs():
    py = {"status": "ok",
          "within_bank1": {"full": {"margin": {"all": _row(1.25, 1.10, 1.40, "jackknife")},
                                    "accuracy": {"all": _row(1.05, 0.95, 1.15, "jackknife")}}},
          "cross_bank": {"summary": {"N": 5}, "full": {"margin": {"all": _row(1.22, 1.08, 1.36, "jackknife")},
                                                 "accuracy": {"all": _row(1.00, 0.90, 1.10, "jackknife")}}},
          "within_minus_cross": {"margin": {"full": {"point_log_theta_diff": 0.02, "lo": -0.05, "hi": 0.09}},
                                 "accuracy": {"full": {"point_log_theta_diff": 0.10, "lo": 0.02, "hi": 0.18}}}}
    v = est.verdicts({"pythia": py, "verify": {"status": "ok", "pass": True}})
    assert v["R1_pythia_replicates_margin"]["pass"] is True
    assert v["R1_pythia_replicates_accuracy"]["pass"] is False
    assert v["R2_pythia_identification_margin"]["shared_item_explanation"] == "not supported"
    assert v["R2_pythia_identification_accuracy"]["shared_item_explanation"] == "supported"
    # An interval the thin-cluster code path could not compute never passes.
    py["within_bank1"]["full"]["margin"]["all"] = {"lambda": 1.3, "jackknife": {"error": "x"}}
    v = est.verdicts({"pythia": py})
    assert v["R1_pythia_replicates_margin"]["pass"] is False
    assert v["V0_verification"]["pass"] is None


def test_pack_respects_budget():
    pytest.importorskip("torch")
    import scorer
    encoded = [(list(range(n)), [[1, 2], [3]]) for n in (50, 40, 30, 20, 10)]
    batches = scorer.pack(list(range(5)), encoded, max_batch_tokens=120, max_items=8)
    assert [x for b in batches for x in b] == [0, 1, 2, 3, 4]
    for b in batches:
        L = max(len(encoded[i][0]) for i in b)
        assert len(b) * L <= 120 or len(b) == 1


class FakeTokenizer:
    """One token per character, so context arithmetic is visible in the test."""

    def encode(self, text, add_special_tokens=False):
        return [ord(c) for c in text]


def test_encode_requests_splits_per_choice_contexts():
    pytest.importorskip("torch")
    import scorer
    shared = {"task": "arc_easy", "doc_id": 1, "context": "Q1 Answer:", "continuations": [" a", " bb"], "label": 0}
    wino = {"task": "winogrande", "doc_id": 2, "context": "x so Sarah", "contexts": ["x so Sarah", "x so Maria"],
            "continuations": [" always won.", " always won."], "label": 1}
    units, owner, n_split = scorer.encode_requests(FakeTokenizer(), [shared, wino, shared])
    assert n_split == 1 and len(units) == 4
    assert owner == [[0], [1, 2], [3]]
    assert units[1][0] == [ord(c) for c in "x so Sarah"] and units[2][0] == [ord(c) for c in "x so Maria"]
    assert [len(u[1]) for u in units] == [2, 1, 1, 2]
    # Trailing whitespace migrates from the context into the continuation.
    ctx, cont = scorer.encode_pair(FakeTokenizer(), "Q Answer: ", "a")
    assert ctx == [ord(c) for c in "Q Answer:"] and cont == [ord(c) for c in " a"]


def test_validate_requests_checks_contexts():
    rng = np.random.default_rng(1)
    rows = fake_requests(rng)
    w = next(r for r in rows if r["task"] == "winogrande")
    w["contexts"] = [w["context"], w["context"] + " other"]
    bank.validate_requests(rows)
    w["contexts"] = [w["context"] + " other", w["context"]]
    with pytest.raises(ValueError):
        bank.validate_requests(rows)
    w["contexts"] = [w["context"]]
    with pytest.raises(ValueError):
        bank.validate_requests(rows)
