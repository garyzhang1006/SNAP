"""R20 part b: index the checkpoint steps in five DataDecide recipe tarballs.

Streams each recipe tarball from Hugging Face through gzip and records every
member name that matches recipe/size/seed-N/step-S.tar.gz, with its byte size.
Nothing is extracted and nothing is written to disk but the index. The member
pattern is the one seednoise.data.datadecide uses, copied verbatim, so the keys
match the reduced-run filenames.
"""
import json, platform, re, sys, tarfile, time, urllib.request
from pathlib import Path

RECIPES = ["dclm-baseline-50p-dolma1.7-50p", "dclm-baseline-75p-dolma1.7-25p", "dclm-baseline-top-10p", "dclm-baseline-top-20p", "dclm-baseline-top-fw-10p"]
HF_REPO = "allenai/DataDecide-eval-instances"
PAT = re.compile(r"^(?P<recipe>[^/]+)/(?P<size>[^/]+)/seed-(?P<seed>\d+)/step-(?P<step>\d+)\.tar\.gz$")
W = Path("/kaggle/working")
t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)


class Counting:
    def __init__(self, resp):
        self.resp, self.n = resp, 0
    def read(self, size=-1):
        b = self.resp.read(size)
        self.n += len(b)
        return b


def index(recipe, attempt):
    url = f"https://huggingface.co/datasets/{HF_REPO}/resolve/main/models/{recipe}.tar.gz"
    resp = urllib.request.urlopen(urllib.request.Request(url), timeout=300)
    total = int(resp.headers.get("Content-Length", 0))
    cr = Counting(resp)
    rows, t1, last = [], time.time(), 0
    with tarfile.open(fileobj=cr, mode="r|gz") as tf:
        for m in tf:
            k = PAT.match(m.name)
            if k:
                rows.append({"recipe": k["recipe"], "size": k["size"], "seed": int(k["seed"]), "step": int(k["step"]), "bytes": m.size})
            if cr.n - last > 500_000_000:
                last = cr.n
                print(f"  {recipe}: {cr.n / 1e9:.2f}/{total / 1e9:.2f} GB, {len(rows)} runs, {time.time() - t1:.0f}s", flush=True)
    # tarfile stops at the end-of-archive blocks and leaves the gzip trailer unread,
    # so drain the rest of the response before comparing against Content-Length.
    tar_bytes = cr.n
    while cr.read(1 << 20):
        pass
    return {"recipe": recipe, "url": url, "content_length": total, "bytes_read": cr.n, "bytes_read_by_tar": tar_bytes, "runs": rows,
            "seconds": time.time() - t1, "attempt": attempt}


out = {"part": "b", "recipes": {}, "failures": {}}
for recipe in RECIPES:
    for attempt in range(1, 4):
        try:
            r = index(recipe, attempt)
            assert r["content_length"] == 0 or r["bytes_read"] == r["content_length"], (r["bytes_read"], r["content_length"])
            out["recipes"][recipe] = r
            print(f"[{recipe}] {len(r['runs'])} runs, {r['bytes_read'] / 1e9:.2f} GB in {r['seconds']:.0f}s", flush=True)
            break
        except Exception as error:  # noqa: BLE001
            print(f"[{recipe}] attempt {attempt} failed: {type(error).__name__}: {error}", flush=True)
            out["failures"].setdefault(recipe, []).append(f"{type(error).__name__}: {error}")
            time.sleep(30)
    (W / "step_index_b.json").write_text(json.dumps(out, indent=1))
out["wall_seconds"] = time.time() - t0
(W / "step_index_b.json").write_text(json.dumps(out, indent=1))
print(f"[done] {len(out['recipes'])} of {len(RECIPES)} recipes indexed in {time.time() - t0:.0f}s", flush=True)
if len(out["recipes"]) < len(RECIPES):
    sys.exit(f"missing recipes: {sorted(set(RECIPES) - set(out['recipes']))}")
