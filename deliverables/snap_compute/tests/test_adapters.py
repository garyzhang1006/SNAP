from pathlib import Path
import tempfile
import unittest

import numpy as np

from make_demo import make_demo
from pack_scores import pack
from reduce_scores import reduce_choices, reduce_documents
from snap.core import load_dataset, read_json, write_json
from run import execute


class AdapterTests(unittest.TestCase):
    def test_pack_shuffled_rows_and_reject_missing(self):
        layout = {"configs": [{"id": "c", "recipe": "r", "size": 1,
                               "runs": [{"id": "a", "run_key": "A"}, {"id": "b", "run_key": "B"}]}],
                  "benchmarks": [{"name": name, "key": name, "item_ids": ["x", "y"]} for name in ("t1", "t2")]}
        rows = [{"run_key": run, "benchmark": b, "item_id": item, "margin": i + j + k}
                for i, run in enumerate(("A", "B")) for j, b in enumerate(("t1", "t2")) for k, item in enumerate(("x", "y"))]
        with tempfile.TemporaryDirectory() as tmp:
            target = pack(layout, rows[::-1], "margin", Path(tmp) / "dataset")
            _, arrays = load_dataset(target)
            np.testing.assert_equal(arrays[0], [[[0, 1], [1, 2]]])
            with self.assertRaisesRegex(ValueError, "Missing or nonfinite"):
                pack(layout, rows[:-1], "margin", Path(tmp) / "incomplete")
            self.assertFalse((Path(tmp) / "incomplete").exists())
            with self.assertRaisesRegex(ValueError, "Duplicate score"):
                pack(layout, rows + rows[:1], "margin", Path(tmp) / "duplicate")

    def test_choice_margin_normalization_and_tie(self):
        def record(i, nll, divisor=1):
            return ("run", {"nll_sum": nll, "metadata": {"benchmark": "b", "item_id": "i",
                    "choice_index": i, "choice_count": 2, "gold_index": 1, "normalizer": divisor}})
        row = reduce_choices([record(0, 4), record(1, 2)])[0]
        self.assertEqual(row["margin"], 2)
        self.assertEqual(row["accuracy"], 1)
        row = reduce_choices([record(0, 4, 2), record(1, 2)])[0]
        self.assertTrue(row["exact_tie"])
        self.assertEqual(row["accuracy"], 0)
        with self.assertRaisesRegex(ValueError, "Incomplete choices"):
            reduce_choices([record(0, 4)])

    def test_document_aggregation_weights_targets(self):
        rows = [("r", {"nll_sum": loss, "target_tokens": n, "metadata": {"document_id": "d", "document_hash": "h"}})
                for loss, n in [(1., 1), (9., 3)]]
        result = reduce_documents(rows)[0]
        self.assertEqual(result["mean_nll"], 2.5)

    def test_missing_inputs_record_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(root / "config.json", {"dataset": "absent.json"})
            with self.assertRaises(FileNotFoundError):
                execute("C01", root / "config.json", root / "output")
            self.assertEqual(read_json(root / "output" / "manifest.json")["status"], "FAILED")

    def test_mismatched_checkpoint_metadata_excluded(self):
        from snap.jobs import c04
        with tempfile.TemporaryDirectory() as tmp:
            root = make_demo(tmp)
            meta = read_json(root / "scores.json")
            for c in meta["configs"]:
                c["runs"][2]["training_signature"] = "different"
            write_json(root / "scores.json", meta)
            result = c04({"dataset": str(root / "scores.json")}, root)
            self.assertEqual(result["included"], 0)
            self.assertTrue(result["status"].startswith("blocked"))


if __name__ == "__main__":
    unittest.main()
