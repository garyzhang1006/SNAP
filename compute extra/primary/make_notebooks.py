"""Generate one Kaggle notebook per job without submitting or executing anything."""
import argparse
from pathlib import Path

from snap.core import read_json, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    destination = Path(args.out)
    destination.mkdir(parents=True, exist_ok=True)
    for config in sorted((root / "configs").glob("*.json")):
        job = config.stem
        cells = [
            {"cell_type": "markdown", "metadata": {}, "source": [
                f"# SNAP {job}\nIndependent reference implementation. Read RUN_GUIDE.txt. Attach the package and required data privately. Edit the package path and configuration, then run. This notebook does not download research data or invent checkpoint identifiers.\n"]},
            {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
                "from pathlib import Path\nimport sys, json, subprocess\n",
                "print('Mounted inputs:', list(Path('/kaggle/input').iterdir()))\n",
                "PACKAGE = Path('/kaggle/input/REPLACE_WITH_ACTUAL_MOUNT/snap_compute')\n",
                "assert (PACKAGE / 'run.py').is_file(), 'Set PACKAGE to the extracted code directory'\n"]},
            {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
                "# Replace input paths with actual absolute Kaggle paths.\n",
                "# Keep template_only true until the configuration is filled and reviewed.\n",
                "CONFIG = " + repr(read_json(config)) + "\n"]},
            {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
                f"output = Path('/kaggle/working/SNAP_{job}')\n",
                f"config_path = Path('/kaggle/working/{job}.json')\n",
                "assert CONFIG.get('template_only') is False, 'Complete and review CONFIG first'\n",
                "config_path.write_text(json.dumps(CONFIG, indent=2))\n",
                f"subprocess.run([sys.executable, str(PACKAGE / 'runs/{job}.py'), '--config', str(config_path), '--out', str(output)], check=True)\n",
                "print((output / 'result.json').read_text())\n",
                "print('Save notebook outputs, retrieve them, then verify their manifests.')\n"]}
        ]
        for i, cell in enumerate(cells):
            cell["id"] = f"{job.lower()}-cell-{i}"
        write_json(destination / f"{job}.ipynb", {"cells": cells, "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4, "nbformat_minor": 5})


if __name__ == "__main__":
    main()
