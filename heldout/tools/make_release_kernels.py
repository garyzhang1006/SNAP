"""Split the release extraction across CPU kernels, one slice of recipes each.

  python3 tools/make_release_kernels.py --slices 4 --skip c4

Each kernel downloads its own recipe tarballs, pulls the verification task's
predictions out of them, and writes release_arc.npz. Kaggle runs five CPU
kernels at once, so slicing turns a serial 24-tarball download into a handful of
parallel ones. The slices are contiguous over the sorted recipe list so a rerun
of one slice is reproducible.

Nothing here contacts Kaggle. tools/push.sh uploads what this writes.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
USER = "garyzhang11111"
MARKER = 'RECIPES = ["c4"]  # replaced by tools/make_release_kernels.py'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slices", type=int, default=4)
    ap.add_argument("--skip", nargs="*", default=["c4"], help="recipes already extracted")
    args = ap.parse_args()

    runs = json.loads((HERE / "config" / "runs.json").read_text())["runs"]
    recipes = sorted({r["recipe"] for r in runs} - set(args.skip))
    assert recipes, "every recipe is in --skip"
    template = (HERE / "kaggle" / "k03a-release-arc" / "k03a-release-arc.py").read_text()
    assert template.count(MARKER) == 1, "recipe marker missing from k03a"

    build = HERE / "kaggle" / "k03a-release-arc" / "build"
    per = -(-len(recipes) // args.slices)
    for i in range(args.slices):
        chunk = recipes[i * per:(i + 1) * per]
        if not chunk:
            continue
        slug = f"snap-new-k03a-r{i + 1:02d}"
        d = build / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{slug}.py").write_text(template.replace(MARKER, f"RECIPES = {json.dumps(chunk)}"))
        (d / "kernel-metadata.json").write_text(json.dumps({
            "id": f"{USER}/{slug}", "title": slug, "code_file": f"{slug}.py", "language": "python",
            "kernel_type": "script", "is_private": True, "enable_gpu": False, "enable_tpu": False,
            "enable_internet": True,
            "dataset_sources": [f"{USER}/snap-new-code", f"{USER}/seed-noise-src"],
            "competition_sources": [], "kernel_sources": [], "model_sources": []}, indent=1) + "\n")
        print(f"wrote {d} with {len(chunk)} recipes: {chunk}")


if __name__ == "__main__":
    main()
