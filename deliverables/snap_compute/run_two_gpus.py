"""Launch two ordinary scoring processes, wait for both, and verify model coverage."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

from run import resolved_config
from snap.core import read_json, require, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", choices=["G00", "G01", "G02", "G03"])
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    cfg = resolved_config(args.config)
    require(cfg.get("template_only") is False and cfg.get("protocol_reviewed") is True,
            "Complete and review the configuration before launching GPU workers")
    import torch
    require(torch.cuda.device_count() >= 2, "Two visible CUDA devices required")
    models = read_json(cfg["models"])["models"]
    require(len(models) >= 2, "Two workers need at least two model entries")
    root = Path(args.out).resolve()
    root.mkdir(parents=True, exist_ok=True)
    processes, logs = [], []
    try:
        for worker in range(2):
            worker_cfg = {**cfg, "workers": 2, "worker": worker, "device": "cuda:0"}
            config_path = root / f"worker{worker}.json"
            if config_path.exists():
                require(read_json(config_path) == worker_cfg, "Changed worker configuration; choose a new output root")
            else:
                write_json(config_path, worker_cfg)
            log = open(root / f"worker{worker}.log", "a", encoding="utf-8")
            logs.append(log)
            env = dict(os.environ)
            # Resolve from the parent's visible-device list if it was already restricted.
            visible = os.environ.get("CUDA_VISIBLE_DEVICES")
            env["CUDA_VISIBLE_DEVICES"] = visible.split(",")[worker] if visible else str(worker)
            processes.append(subprocess.Popen([sys.executable, str(Path(__file__).parent / "run.py"), args.job,
                                                "--config", str(config_path), "--out", str(root / f"worker{worker}")],
                                               env=env, stdout=log, stderr=subprocess.STDOUT))
        codes = [p.wait() for p in processes]
        require(codes == [0, 0], f"Worker exit codes {codes}; inspect logs and resume valid shards")
        completed = []
        for worker in range(2):
            result = read_json(root / f"worker{worker}" / "result.json")
            completed.extend(row["run_key"] for row in result["models"])
        expected = [m["run_key"] for m in models]
        require(len(completed) == len(set(completed)) and set(completed) == set(expected), "Worker coverage mismatch")
        write_json(root / "coverage.json", {"expected": expected, "completed": completed, "status": "coverage_verified_not_science_verified"})
        print(f"Both workers finished. Inspect {root / 'coverage.json'} and validate scoring outputs.")
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        for log in logs:
            log.close()


if __name__ == "__main__":
    main()
