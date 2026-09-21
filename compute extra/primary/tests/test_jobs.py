import tempfile
from pathlib import Path
import unittest

import numpy as np

from make_demo import make_demo
from run import execute
from snap.core import read_json, write_json
from snap.jobs import prediction_rows


class JobTests(unittest.TestCase):
    def test_cpu_jobs_and_resume_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_demo(Path(tmp) / "demo")
            entries = []
            # C02 runs this suite; including it here would recursively invoke itself.
            for job in [f"C{i:02d}" for i in range(11) if i != 2]:
                output = root / "outputs" / job
                result = execute(job, root / f"{job}.json", output)
                self.assertIsInstance(result, dict)
                manifest = read_json(output / "manifest.json")
                self.assertEqual(manifest["status"], "FINISHED_UNCHECKED")
                entries.append({"job": job, "path": str(output), "config_hash": manifest["config_hash"]})
            write_json(root / "C11.json", {"required_outputs": entries})
            final = execute("C11", root / "C11.json", root / "outputs" / "C11")
            self.assertEqual(final["status"], "artifact_integrity_verified")
            execute("C01", root / "C01.json", root / "outputs" / "C01")
            write_json(root / "outputs" / "C01" / "result.json", {"corrupt": True})
            with self.assertRaisesRegex(ValueError, "Changed completed artifact"):
                execute("C01", root / "C01.json", root / "outputs" / "C01")

    def test_changed_config_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_demo(tmp)
            execute("C01", root / "C01.json", root / "result")
            cfg = read_json(root / "C01.json")
            cfg["seed"] = 999
            write_json(root / "C01.json", cfg)
            with self.assertRaisesRegex(ValueError, "different code/inputs/configuration"):
                execute("C01", root / "C01.json", root / "result")

    def test_training_prediction_does_not_use_heldout_covariance(self):
        configs = [{"id": str(i), "recipe": str(i), "size": 1} for i in range(4)]
        cov = np.tile(np.eye(2), (4, 1, 1))
        folds = np.array([0, 0, 1, 1])
        before = prediction_rows(cov, configs, [.5, .5], folds)
        cov[:2] *= 100
        after = prediction_rows(cov, configs, [.5, .5], folds)
        for x, y in zip(before[:8], after[:8]):
            self.assertEqual(x["prediction"], y["prediction"])
            self.assertNotEqual(x["target_raw_variance_moment"], y["target_raw_variance_moment"])


if __name__ == "__main__":
    unittest.main()
