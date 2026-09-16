import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from snap.core import object_hash, read_json, write_json


@unittest.skipUnless(importlib.util.find_spec("transformers") and importlib.util.find_spec("tokenizers"), "Tokenizer libraries unavailable")
class PreparationTests(unittest.TestCase):
    def test_actual_tokenizer_preparation_and_proxy_cli(self):
        from tokenizers import Tokenizer
        from tokenizers.models import WordLevel
        from tokenizers.pre_tokenizers import Whitespace
        from transformers import PreTrainedTokenizerFast

        package = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            backend = Tokenizer(WordLevel({"[UNK]": 0, "a": 1, "b": 2, "c": 3, "d": 4}, unk_token="[UNK]"))
            backend.pre_tokenizer = Whitespace()
            tokenizer = PreTrainedTokenizerFast(tokenizer_object=backend, unk_token="[UNK]")
            tokenizer.save_pretrained(root / "tokenizer")
            docs = root / "docs.jsonl"
            docs.write_text(json.dumps({"id": "d", "text": "a b c d a b c d"}) + "\n")
            def invoke(script, *args):
                result = subprocess.run([sys.executable, str(package / script), *map(str, args)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            invoke("prepare_text.py", "--documents", docs, "--tokenizer", root / "tokenizer", "--revision", "local",
                   "--max-length", 4, "--stride", 2, "--out", root / "text.jsonl")
            records = [json.loads(line) for line in (root / "text.jsonl").read_text().splitlines()]
            self.assertEqual(sum(sum(r["target_mask"]) for r in records), 7)
            choices = root / "choices.jsonl"
            choices.write_text("".join(json.dumps({"benchmark": "b", "item_id": "i", "choice_index": i,
                  "choice_count": 2, "gold_index": 0, "context": "a ", "continuation": continuation, "normalizer": 1}) + "\n"
                  for i, continuation in enumerate(("b", "c"))))
            invoke("prepare_choices.py", "--choices", choices, "--tokenizer", root / "tokenizer", "--revision", "local",
                   "--max-length", 4, "--out", root / "choices_tokens.jsonl")
            self.assertEqual(len((root / "choices_tokens.jsonl").read_text().splitlines()), 2)
            layout = {"configs": [{"id": "c", "runs": [{"id": "r", "run_key": "R"}]}]}
            write_json(root / "layout.json", layout)
            write_json(root / "losses.json", {"kind": "documents", "rows": [
                {"run_key": "R", "document_id": "d", "document_hash": object_hash("a b c d a b c d"), "nll_sum": 14., "target_tokens": 7}]})
            invoke("make_proxy.py", "--losses", root / "losses.json", "--dataset", root / "layout.json",
                   "--corpus", docs, "--out", root / "proxy.json")
            self.assertEqual(read_json(root / "proxy.json")["values"]["c"]["r"], 2)


if __name__ == "__main__":
    unittest.main()
