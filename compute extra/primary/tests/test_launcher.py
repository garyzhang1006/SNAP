import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from snap.core import read_json, write_json


@unittest.skipUnless(importlib.util.find_spec("torch"), "PyTorch unavailable")
class LauncherTests(unittest.TestCase):
    def test_two_process_configuration_and_coverage_with_mock_devices(self):
        import run_two_gpus
        calls = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            models = [{"run_key": f"r{i}"} for i in range(5)]
            write_json(root / "models.json", {"models": models})
            write_json(root / "config.json", {"template_only": False, "protocol_reviewed": True, "models": "models.json"})

            class CompletedProcess:
                def wait(self, timeout=None):
                    return 0

                def poll(self):
                    return 0

            def fake_popen(command, **kwargs):
                cfg = read_json(command[command.index("--config") + 1])
                output = Path(command[command.index("--out") + 1])
                calls.append((cfg["worker"], kwargs["env"]["CUDA_VISIBLE_DEVICES"]))
                selected = [m for i, m in enumerate(models) if i % cfg["workers"] == cfg["worker"]]
                write_json(output / "result.json", {"models": selected})
                return CompletedProcess()

            argv = ["run_two_gpus.py", "G01", "--config", str(root / "config.json"), "--out", str(root / "out")]
            with patch("sys.argv", argv), patch("torch.cuda.device_count", return_value=2), \
                 patch.dict("os.environ", {"CUDA_VISIBLE_DEVICES": "3,7"}), \
                 patch("run_two_gpus.subprocess.Popen", side_effect=fake_popen):
                run_two_gpus.main()
            self.assertEqual(calls, [(0, "3"), (1, "7")])
            result = read_json(root / "out" / "coverage.json")
            self.assertEqual(set(result["completed"]), {m["run_key"] for m in models})

    def test_no_cuda_does_not_launch(self):
        import run_two_gpus
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(root / "config.json", {"template_only": False, "protocol_reviewed": True})
            with patch("sys.argv", ["run_two_gpus.py", "G01", "--config", str(root / "config.json"), "--out", str(root / "out")]), \
                 patch("torch.cuda.device_count", return_value=0), patch("run_two_gpus.subprocess.Popen") as spawn:
                with self.assertRaisesRegex(ValueError, "Two visible"):
                    run_two_gpus.main()
                spawn.assert_not_called()


if __name__ == "__main__":
    unittest.main()
