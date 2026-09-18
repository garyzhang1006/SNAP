#!/usr/bin/env bash
# Upload code and kernels to Kaggle, check status, and fetch outputs.
# Credentials come from the Kaggle CLI's own config (~/.kaggle/kaggle.json or
# KAGGLE_USERNAME/KAGGLE_KEY in the environment); this script never reads or
# writes a token. Every kernel it pushes is private (is_private in its metadata).
#
#   tools/push.sh code                     create or version the snap-new-code dataset (common/ + config/)
#   tools/push.sh kernel kaggle/k00-env-probe
#   tools/push.sh kernel kaggle/k02-score/build/snap-new-k02-pilot
#   tools/push.sh status snap-new-k02-pilot
#   tools/push.sh output snap-new-k02-pilot outputs/k02-pilot
#
# Pushing a kernel starts it on Kaggle and spends quota; GPU kernels spend GPU hours.
set -euo pipefail

KAGGLE="${KAGGLE:-$(command -v kaggle || echo /Library/Frameworks/Python.framework/Versions/3.14/bin/kaggle)}"
USER_SLUG="garyzhang11111"
HERE="$(cd "$(dirname "$0")/.." && pwd)"

case "${1:-}" in
  code)
    stage="$HERE/kaggle/_stage/snap-new-code"
    rm -rf "$stage"
    mkdir -p "$stage"
    cp -R "$HERE/common" "$HERE/config" "$stage/"
    find "$stage" -name "__pycache__" -type d -prune -exec rm -rf {} +
    find "$stage" -name "._*" -delete
    cat > "$stage/dataset-metadata.json" <<EOF
{"title": "snap-new-code", "id": "$USER_SLUG/snap-new-code", "licenses": [{"name": "CC0-1.0"}]}
EOF
    if "$KAGGLE" datasets status "$USER_SLUG/snap-new-code" >/dev/null 2>&1; then
      "$KAGGLE" datasets version -p "$stage" -m "snap-new-code $(git -C "$HERE" rev-parse --short HEAD)" --dir-mode zip
    else
      "$KAGGLE" datasets create -p "$stage" --dir-mode zip
    fi
    echo "waiting for Kaggle to publish the new dataset version"
    check="$HERE/kaggle/_stage/check"
    rm -rf "$check"; mkdir -p "$check"
    for _ in $(seq 1 30); do
      sleep 20
      rm -f "$check/config.zip"
      "$KAGGLE" datasets download "$USER_SLUG/snap-new-code" -f config.zip -p "$check" --force >/dev/null 2>&1 || continue
      if python3 - "$check/config.zip" "$stage/config" <<'PY'
import sys, zipfile, hashlib, pathlib
z = zipfile.ZipFile(sys.argv[1]); src = pathlib.Path(sys.argv[2])
want = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in src.glob("*.json")}
got = {n.split("/")[-1]: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
sys.exit(0 if all(got.get(k) == v for k, v in want.items()) else 1)
PY
      then echo "published"; rm -rf "$check"; exit 0; fi
    done
    echo "the new version has not appeared after 10 minutes; check the dataset page before pushing kernels" >&2
    exit 1
    ;;
  kernel)
    dir="${2:?kernel directory}"
    test -f "$dir/kernel-metadata.json" || { echo "no kernel-metadata.json in $dir" >&2; exit 1; }
    grep -q '"is_private": true' "$dir/kernel-metadata.json" || { echo "$dir is not marked private; refusing" >&2; exit 1; }
    "$KAGGLE" kernels push -p "$dir"
    ;;
  status)
    "$KAGGLE" kernels status "$USER_SLUG/${2:?kernel slug}"
    ;;
  output)
    mkdir -p "${3:?destination directory}"
    "$KAGGLE" kernels output "$USER_SLUG/${2:?kernel slug}" -p "$3"
    ;;
  *)
    sed -n '2,13p' "$0"
    exit 1
    ;;
esac
