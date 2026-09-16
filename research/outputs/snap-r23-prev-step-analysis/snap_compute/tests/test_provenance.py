import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from run import execute
from reduce_scores import reduce_choices, reduce_documents
from snap.core import write_json


class ProvenanceTests(unittest.TestCase):
    def test_proxy_rejects_losses_from_another_corpus(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "corpus.jsonl").write_text(json.dumps({"id": "doc", "text": "Actual document"}) + "\n")
            write_json(root / "layout.json", {"configs": [{"id": "c", "runs": [{"id": "r", "run_key": "R"}]}]})
            write_json(root / "losses.json", {"kind": "documents", "rows": [
                {"run_key": "R", "document_id": "doc", "document_hash": "WRONG_DOCUMENT_HASH", "target_tokens": 3, "nll_sum": 2.}]})
            script = Path(__file__).resolve().parents[1] / "make_proxy.py"
            p = subprocess.run([sys.executable, str(script), "--losses", str(root / "losses.json"),
                "--dataset", str(root / "layout.json"), "--corpus", str(root / "corpus.jsonl"), "--out", str(root / "proxy.json")],
                capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertFalse((root / "proxy.json").exists())

    def test_nonfinite_choice_loss_rejected(self):
        rows = [("r", {"nll_sum": loss, "metadata": {"benchmark": "b", "item_id": "i", "choice_index": i,
                 "choice_count": 2, "gold_index": 0, "normalizer": 1}}) for i, loss in enumerate([float("nan"), 1.])]
        with self.assertRaises(ValueError):
            reduce_choices(rows)

    def test_invalid_document_count_rejected(self):
        with self.assertRaises(ValueError):
            reduce_documents([("r", {"nll_sum": 1., "target_tokens": -1,
                                     "metadata": {"document_id": "d", "document_hash": "h"}})])

    def test_unowned_output_directory_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(root / "config.json", {"inputs": []})
            write_json(root / "output" / "old_result.json", {"old": True})
            with self.assertRaises(ValueError):
                execute("C00", root / "config.json", root / "output")


if __name__ == "__main__":
    unittest.main()
