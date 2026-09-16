"""Data-integrity checks over the package itself, which fail loudly when a contract slips.

Every check reads files rather than recomputing science, so this suite is fast enough to run before a
commit. The manifest hash check samples by default and takes --full to verify all 375 files, because
this filesystem reads at roughly a tenth of a second per file.
"""
import csv, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ["research/manifest.csv", "research/protocol.md", "research/claims.csv",
            "research/LEDGER.md", "research/R1_estimand.md", "research/kernel_status.tsv",
            "research/results/simulation_cells.csv", "research/results/index.csv",
            "research/figures/make_prediction_figure.py",
            "deliverables/main.tex", "deliverables/appendix_a.tex",
            "deliverables/appendices_bcd.tex", "deliverables/references.tex",
            "deliverables/figures/prediction.pdf"]
SEEDS_BELOW_1B, SEEDS_1B = {"2", "14", "15"}, {"2", "4", "5"}


def test_required_paths_exist():
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    assert not missing, missing


def test_manifest_shape():
    rows = list(csv.DictReader((ROOT / "research/manifest.csv").open()))
    assert len(rows) == 375, len(rows)
    assert len({r["run_id"] for r in rows}) == 375
    assert len({r["config_id"] for r in rows}) == 125
    assert len({r["reduction_sha256"] for r in rows}) == 375
    for r in rows:
        allowed = SEEDS_1B if r["size"] == "1B" else SEEDS_BELOW_1B
        assert r["seed"] in allowed, (r["run_id"], r["seed"])
        assert r["hf_revision"].startswith(f"step{r['selected_step']}-seed-"), r["hf_revision"]


def test_manifest_hashes(full=False):
    rows = list(csv.DictReader((ROOT / "research/manifest.csv").open()))
    runs = ROOT / "research/outputs/snap-r6-perm-seeds/runs"
    sample = rows if full else rows[::25]
    for r in sample:
        data = (runs / r["reduction_file"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == r["reduction_sha256"], r["run_id"]
        assert len(data) == int(r["reduction_bytes"]), r["run_id"]
    print(f"   checked {len(sample)} of {len(rows)} reduction hashes")


def test_results_index_matches_disk():
    rows = list(csv.DictReader((ROOT / "research/results/index.csv").open()))
    assert rows, "index is empty"
    for r in rows[::40]:
        p = ROOT / r["file"]
        assert p.exists(), r["file"]
        assert p.stat().st_size == int(r["bytes"]), r["file"]


def test_simulation_cells_are_probabilities():
    rows = list(csv.DictReader((ROOT / "research/results/simulation_cells.csv").open()))
    assert len(rows) > 200, len(rows)
    for r in rows:
        cov = float(r["coverage"])
        assert 0.0 <= cov <= 1.0, r
        assert int(r["replicates"]) >= 500, r
        for field in ("excludes_one_rate", "undefined_or_unbounded"):
            if r[field] not in ("", "None"):
                assert 0.0 <= float(r[field]) <= 1.0, (field, r)


def test_claims_point_at_real_artifacts():
    rows = list(csv.DictReader((ROOT / "research/claims.csv").open()))
    assert rows, "claims.csv is empty"
    for r in rows:
        assert r["evidence_label"] in {"OBSERVED", "REPORTED", "PROPOSED", "INFERRED"}, r
        assert r["claim_id"] and r["status"], r


def test_kernel_status_has_no_silent_failures():
    lines = [l.split("\t") for l in
             (ROOT / "research/kernel_status.tsv").read_text(errors="replace").splitlines()]
    states = {}
    for parts in lines:
        if len(parts) >= 2:
            states.setdefault(parts[1], []).append(parts[0])
    unknown = set(states) - {"COMPLETE", "ERROR", "CANCEL", "CANCEL_REQUESTED",
                             "CANCEL_ACKNOWLEDGED", "status"}
    assert not unknown, unknown
    # A kernel that failed and was repushed carries both rows, so the last state is the one that
    # counts, and no number in the package may come from a kernel whose last state is not COMPLETE.
    last = {}
    for parts in lines:
        if len(parts) >= 2 and parts[0] != "kernel":
            last[parts[0]] = parts[1]
    indexed = {r["kernel"] for r in
               csv.DictReader((ROOT / "research/results/index.csv").open())}
    bad = sorted(k for k in indexed if last.get(k, "COMPLETE") != "COMPLETE")
    assert not bad, bad
    print(f"   kernel states {({k: len(v) for k, v in states.items()})}")


if __name__ == "__main__":
    full = "--full" in sys.argv
    failures = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_"):
            continue
        try:
            fn(full) if name == "test_manifest_hashes" else fn()
            print("ok", name)
        except AssertionError as exc:
            failures += 1
            print("FAIL", name, exc)
    sys.exit(1 if failures else 0)
