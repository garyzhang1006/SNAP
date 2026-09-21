import importlib.util
import math
from types import SimpleNamespace
import unittest

from snap.gpu import token_windows, validate_record


class WindowTests(unittest.TestCase):
    def test_every_target_once(self):
        for n in range(2, 40):
            for stride in (1, 3, 6):
                selected = []
                for begin, ids, mask in token_windows(list(range(n)), 7, stride):
                    self.assertFalse(mask[0])
                    selected.extend(begin + i for i, yes in enumerate(mask) if yes)
                self.assertEqual(selected, list(range(1, n)))

    def test_unscorable_first_token_rejected(self):
        with self.assertRaisesRegex(ValueError, "First token"):
            validate_record({"id": "x", "input_ids": [1, 2], "target_mask": [True, True]}, 4)


@unittest.skipUnless(importlib.util.find_spec("torch"), "PyTorch unavailable")
class LikelihoodTests(unittest.TestCase):
    def test_uniform_logits_exact_mask_count(self):
        import torch
        from snap.gpu import loss_for_record

        class UniformModel(torch.nn.Module):
            def get_input_embeddings(self):
                return SimpleNamespace(num_embeddings=7)

            def forward(self, input_ids, use_cache=False):
                return SimpleNamespace(logits=torch.zeros((*input_ids.shape, 7)))

        record = {"id": "uniform", "input_ids": [0, 1, 2, 3, 4], "target_mask": [False, True, False, True, True]}
        row = loss_for_record(UniformModel(), record, "cpu", 10, chunk_tokens=1)
        self.assertEqual(row["target_tokens"], 3)
        self.assertAlmostEqual(row["nll_sum"], 3 * math.log(7), places=6)

    def test_target_shift_against_direct_reference(self):
        import torch
        from snap.gpu import loss_for_record

        class FixedModel(torch.nn.Module):
            def get_input_embeddings(self):
                return SimpleNamespace(num_embeddings=3)

            def forward(self, input_ids, use_cache=False):
                return SimpleNamespace(logits=torch.tensor([[[2., 1., 0.], [0., 2., 1.], [1., 0., 2.]]]))

        record = {"id": "shift", "input_ids": [0, 1, 2], "target_mask": [False, True, True]}
        row = loss_for_record(FixedModel(), record, "cpu", 4)
        expected = -torch.log_softmax(torch.tensor([2., 1., 0.]), 0)[1] - torch.log_softmax(torch.tensor([0., 2., 1.]), 0)[2]
        self.assertAlmostEqual(row["nll_sum"], expected.item(), places=6)


if __name__ == "__main__":
    unittest.main()
