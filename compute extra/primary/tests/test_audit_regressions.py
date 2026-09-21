import tempfile
from pathlib import Path
import unittest

from make_demo import make_demo
from run import execute
from snap.core import load_dataset, read_json, split_halves, write_json
from snap.jobs import c05, c08, c11


class AuditRegressions(unittest.TestCase):
    def test_fractional_half_labels_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_demo(tmp)
            meta, arrays = load_dataset(root / "scores.json")
            meta["benchmarks"][0]["original_half"][0] = .4
            with self.assertRaises(ValueError):
                split_halves(meta, arrays, mode="original")

    def test_missing_group_ids_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_demo(tmp)
            meta, arrays = load_dataset(root / "scores.json")
            meta["benchmarks"][0]["group_ids"][0] = None
            with self.assertRaises(ValueError):
                split_halves(meta, arrays, mode="group")

    def test_duplicate_benchmark_array_key_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_demo(tmp)
            meta = read_json(root / "scores.json")
            meta["benchmarks"][1]["key"] = meta["benchmarks"][0]["key"]
            write_json(root / "scores.json", meta)
            with self.assertRaises(ValueError):
                load_dataset(root / "scores.json")

    def test_cached_audit_rechecks_upstream_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_demo(tmp)
            execute("C01", root / "C01.json", root / "C01")
            manifest = read_json(root / "C01" / "manifest.json")
            write_json(root / "C11.json", {"required_outputs": [
                {"job": "C01", "path": str(root / "C01"), "config_hash": manifest["config_hash"]}]})
            execute("C11", root / "C11.json", root / "C11")
            write_json(root / "C01" / "result.json", {"corrupt": True})
            with self.assertRaises(ValueError):
                execute("C11", root / "C11.json", root / "C11")

    def test_audit_requires_hashed_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(root / "manifest.json", {"job": "C01", "status": "FINISHED_UNCHECKED", "config_hash": "x", "artifacts": {}})
            write_json(root / "result.json", {"T": 123})
            with self.assertRaises(ValueError):
                c11({"required_outputs": [{"path": str(root), "job": "C01", "config_hash": "x"}]}, root)

    def test_simulation_resume_rejects_changed_unit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_demo(tmp)
            execute("C05", root / "C05.json", root / "output")
            unit = next((root / "output").glob("cell_*.json"))
            value = read_json(unit)
            value["estimate"] = 999.
            write_json(unit, value)
            manifest = read_json(root / "output" / "manifest.json")
            manifest["status"] = "FAILED"
            write_json(root / "output" / "manifest.json", manifest)
            with self.assertRaises(ValueError):
                execute("C05", root / "C05.json", root / "output")

    def test_empty_campaigns_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                c05({"cells": [], "replicate_stop": 2}, root)
            write_json(root / "pairs.json", {"schema": "snap-pairs-v1", "pairs": []})
            with self.assertRaises(ValueError):
                c08({"pairs": str(root / "pairs.json")}, root)

    def test_fractional_simulation_dimensions_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                c05({"cells": [{"runs": 2.5, "recipes": 2, "sizes": 1, "benchmarks": 2}],
                     "replicate_stop": 1, "bootstrap_draws": 20, "seed": 1}, Path(tmp))


if __name__ == "__main__":
    unittest.main()
