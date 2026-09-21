from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from run import fingerprint
from snap.gpu import chunks_from_jsonl, validate_metadata


class RuntimeGuards(unittest.TestCase):
    def test_environment_changes_fingerprint(self):
        with patch("run.environment_identity", return_value={"numpy": "one"}):
            a = fingerprint({})[0]
        with patch("run.environment_identity", return_value={"numpy": "two"}):
            b = fingerprint({})[0]
        self.assertNotEqual(a, b)

    def test_fractional_shard_size_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "rows.jsonl"
            p.write_text("")
            with self.assertRaises(ValueError):
                list(chunks_from_jsonl(p, 1.5, 10))

    def test_metadata_rejects_invalid_choice_before_scoring(self):
        row = {"id": "r", "metadata": {"benchmark": "b", "item_id": "i", "choice_count": 2,
                                         "choice_index": 0, "gold_index": 3, "normalizer": 1}}
        with self.assertRaises(ValueError):
            validate_metadata(row, "choices")
        row["metadata"]["gold_index"] = 1
        row["metadata"]["normalizer"] = float("inf")
        with self.assertRaises(ValueError):
            validate_metadata(row, "choices")


if __name__ == "__main__":
    unittest.main()
