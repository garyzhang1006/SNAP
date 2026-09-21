"""Run one named experiment. Relative configuration paths resolve from its file."""
import argparse
from contextlib import contextmanager
import importlib.metadata
import os
from pathlib import Path
import sys
import time
import traceback

from snap.core import object_hash, read_json, require, sha256, verify_artifacts, write_json
from snap.jobs import CPU_JOBS


PATH_KEYS = {"dataset", "external_dataset", "proxy", "pairs", "models"}


def resolved_config(path):
    path = Path(path).resolve()
    cfg = read_json(path)
    for key in PATH_KEYS & cfg.keys():
        cfg[key] = str((path.parent / cfg[key]).resolve())
    if "inputs" in cfg:
        cfg["inputs"] = [str((path.parent / p).resolve()) for p in cfg["inputs"]]
    for entry in cfg.get("required_outputs", []):
        entry["path"] = str((path.parent / entry["path"]).resolve())
    return cfg


def fingerprint(cfg):
    paths = [cfg[k] for k in PATH_KEYS & cfg.keys()] + cfg.get("inputs", [])
    inputs = {}
    for name in paths:
        p = Path(name)
        inputs[str(p)] = sha256(p) if p.is_file() else "MISSING"
        if p.is_file() and p.suffix == ".json":
            value = read_json(p)
            extra = [value["arrays"]] if "arrays" in value else []
            extra += [m["records"] for m in value.get("models", [])]
            for model in value.get("models", []):
                local = Path(model["model_id"])
                if local.is_dir():
                    for f in sorted(local.rglob("*")):
                        if f.is_file():
                            inputs[str(f.resolve())] = sha256(f)
            for relative in extra:
                q = (p.parent / relative).resolve()
                inputs[str(q)] = sha256(q) if q.is_file() else "MISSING"
    root = Path(__file__).parent
    code = {str(p.relative_to(root)): sha256(p) for p in sorted(root.rglob("*.py")) if "__pycache__" not in p.parts}
    return object_hash({"config": cfg, "inputs": inputs, "code": code, "environment": environment_identity()}), inputs, code


def environment_identity():
    versions = {}
    for package in ("numpy", "torch", "transformers", "tokenizers"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return {"python": sys.version, "packages": versions}


@contextmanager
def output_lock(out):
    # Advisory locks are released by the OS after crashes, unlike stale PID files.
    import fcntl
    with open(out / ".lock", "a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError(f"Another process owns {out}; give each worker a separate output directory") from error
        yield


def execute(job, config_path, output):
    cfg = resolved_config(config_path)
    require(not cfg.get("template_only", False), "Template only: supply actual inputs and set template_only=false")
    out = Path(output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    identity, inputs, code = fingerprint(cfg)
    with output_lock(out):
        manifest_path = out / "manifest.json"
        require(manifest_path.exists() or not [p for p in out.iterdir() if p.name != ".lock"],
                "Output contains unowned files without a manifest; use a new output directory")
        if manifest_path.exists():
            previous = read_json(manifest_path)
            require(previous["job"] == job and previous["config_hash"] == identity,
                    "Output belongs to different code/inputs/configuration; use a new output directory")
            if previous["status"] == "FINISHED_UNCHECKED":
                verify_artifacts(out, previous)
                # An audit is a fresh assertion about upstream files, never a cached fact.
                if job != "C11":
                    return read_json(out / "result.json")
        manifest = {"job": job, "config_hash": identity, "inputs": inputs, "code": code,
                    "status": "RUNNING", "started_unix": time.time(), "configuration": cfg,
                    "environment": environment_identity(),
                    "implementation": "independent reference, not original pipeline"}
        write_json(manifest_path, manifest)
        try:
            if job in CPU_JOBS:
                result = CPU_JOBS[job](cfg, out)
            else:
                from snap.gpu import run_gpu
                result = run_gpu(job, cfg, out)
            write_json(out / "result.json", result)
            manifest["status"] = "FINISHED_UNCHECKED"
            manifest["finished_unix"] = time.time()
            manifest["artifacts"] = {str(p.relative_to(out)): sha256(p) for p in sorted(out.rglob("*"))
                                     if p.is_file() and p.name not in ("manifest.json", ".lock") and not p.name.endswith(".tmp")}
            write_json(manifest_path, manifest)
            return result
        except Exception as error:
            manifest.update(status="FAILED", error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc())
            write_json(manifest_path, manifest)
            raise


def main(forced_job=None):
    parser = argparse.ArgumentParser(description=__doc__)
    if forced_job is None:
        parser.add_argument("job", choices=list(CPU_JOBS) + [f"G{i:02d}" for i in range(4)])
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    job = forced_job or args.job
    execute(job, args.config, args.out)
    print(f"{job}: FINISHED_UNCHECKED; inspect {Path(args.out).resolve() / 'result.json'}")


if __name__ == "__main__":
    main()
