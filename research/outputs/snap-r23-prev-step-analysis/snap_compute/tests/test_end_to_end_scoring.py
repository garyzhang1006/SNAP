import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from snap.core import object_hash, read_json, sha256, write_json


@unittest.skipUnless(importlib.util.find_spec("torch") and importlib.util.find_spec("transformers"), "GPU libraries unavailable")
class EndToEndScoring(unittest.TestCase):
    def test_four_gpu_entry_paths_with_tiny_local_cpu_model(self):
        import torch
        from transformers import AutoModelForCausalLM, GPT2Config
        from run import execute
        from reduce_scores import load_rows, reduce_choices, reduce_documents

        torch.manual_seed(3)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            model_path = root / "model"
            model = AutoModelForCausalLM.from_config(GPT2Config(vocab_size=16, n_positions=16, n_embd=8, n_layer=1, n_head=1, bos_token_id=0, eos_token_id=0))
            model.save_pretrained(model_path)
            del model
            snapshot = object_hash({str(p.relative_to(model_path)): sha256(p) for p in sorted(model_path.rglob("*")) if p.is_file()})
            rows = [{"id": f"option-{i}", "input_ids": [1, 2, 3 + i], "target_mask": [False, False, True],
                     "metadata": {"document_id": "doc", "document_hash": "synthetic-doc-hash",
                                  "benchmark": "task", "item_id": "item", "choice_index": i,
                                  "choice_count": 2, "gold_index": 0, "normalizer": 1}} for i in range(2)]
            records = root / "records.jsonl"
            records.write_text("".join(json.dumps(row) + "\n" for row in rows))
            for job in ("G00", "G01", "G02", "G03"):
                spec = {"run_key": "synthetic-run", "model_id": str(model_path), "revision": "local",
                        "local_snapshot_hash": snapshot, "tokenizer_id": "synthetic-integer-tokenizer",
                        "tokenizer_revision": "synthetic-v1", "records": "records.jsonl",
                        "records_sha256": sha256(records), "expected_records": 2, "max_length": 16,
                        "records_kind": "documents" if job == "G01" else "choices"}
                write_json(root / f"{job}-models.json", {"models": [spec]})
                cfg = {"models": f"{job}-models.json", "protocol_reviewed": True, "protocol_source": "SYNTHETIC TEST",
                       "dtype": "float32", "device": "cpu", "synthetic_cpu_test": True,
                       "records_per_shard": 1, "reference_records": 2, "reference_abs_mean_nll_tolerance": 1e-6}
                write_json(root / f"{job}.json", cfg)
                result = execute(job, root / f"{job}.json", root / job)
                self.assertEqual(result["models"][0]["records"], 2)
                self.assertEqual(result["models"][0]["target_tokens"], 2)
                if job == "G01":
                    self.assertEqual(len(reduce_documents(load_rows([root / job]))), 1)
                else:
                    self.assertEqual(len(reduce_choices(load_rows([root / job]))), 1)
            # Simulate interruption after valid shards were written, then resume.
            manifest = read_json(root / "G02" / "manifest.json")
            manifest["status"] = "FAILED"
            write_json(root / "G02" / "manifest.json", manifest)
            resumed = execute("G02", root / "G02.json", root / "G02")
            self.assertEqual(resumed["models"][0]["load_seconds_this_attempt"], 0)


if __name__ == "__main__":
    unittest.main()
