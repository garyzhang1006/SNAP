"""R7 whether the availability census the manuscript reports still holds a day later.

Design fixed before running (2026-09-16, written 18:30 EDT). The main text carries a hard count from a
network census, that 80 of the 125 model repositories answer an unauthenticated request with HTTP 401
while 40 resolve without one. Every other number in this paper comes from files that cannot change under
us, but that one describes a remote service whose gating a maintainer can flip at any time, and a
reviewer reading in three months may check it and find something else. A count that moves is not a
reason to drop the claim, since the paper's point is that provenance depends on a third party, but it is
a reason to know the drift rate rather than to assume none.
This run repeats the identical census, constructing the same repository names from the shipped reduced
runs crossed with all five size bands, issuing the same unauthenticated HEAD against each, and recording
the same status codes and branch lists. It fetches no weights, so it stays a network census rather than
compute. Agreement with the first census lets the manuscript report the count as stable across two
readings, and a difference gets reported as a difference with both dates named.
"""
import json, platform, re, sys, time
from pathlib import Path

t0 = time.time()
print("[env] python", sys.version.replace("\n", " "), platform.platform(), flush=True)
W = Path("/kaggle/working")
import requests
from huggingface_hub import HfApi

SIZES = ("150M", "300M", "530M", "750M", "1B")
API = "https://huggingface.co"


def recipes_present():
    """Every recipe name that appears in the shipped reduced runs, at any size."""
    names = set()
    for p in Path("/kaggle/input").rglob("*__*__seed-*.npz"):
        if p.name.startswith("._"):
            continue
        stem = p.name.split("__seed-")[0]
        parts = stem.rsplit("__", 1)
        if len(parts) == 2 and parts[1] in SIZES:
            names.add(parts[0])
    return sorted(names)


api = HfApi()
listed = []
try:
    for m in api.list_models(author="allenai", search="DataDecide"):
        listed.append(m.id)
    listing_ok = True
except Exception as exc:
    listing_ok = False
    listed = [f"{type(exc).__name__}: {exc}"[:300]]
print(f"[namespace] listing_ok {listing_ok} count {len(listed)}", flush=True)

RECIPES = recipes_present()
print(f"[recipes] {len(RECIPES)} {RECIPES}", flush=True)

report = {"design": __doc__, "sizes": list(SIZES), "recipes_present": RECIPES,
          "namespace_listing_ok": listing_ok, "namespace_repos": sorted(listed),
          "rows": [], "summary": {}}


def classify(code, body):
    """The distinction the manuscript sentence turns on, kept explicit rather than inferred."""
    if code == 200:
        return "resolves_anonymously"
    if code == 401:
        return "refuses_unauthenticated"
    if code == 403:
        return "forbidden_gated"
    if code == 404:
        return "does_not_exist"
    return f"http_{code}"


session = requests.Session()
counts = {}
for recipe in RECIPES:
    for size in SIZES:
        repo = f"allenai/DataDecide-{recipe}-{size}"
        row = {"recipe": recipe, "size": size, "repo": repo}
        if not re.fullmatch(r"[A-Za-z0-9._\-/]+", repo):
            row.update({"status": None, "classification": "invalid_repo_id",
                        "detail": "repo id carries a character the Hub forbids"})
        else:
            try:
                r = session.head(f"{API}/api/models/{repo}", timeout=60,
                                 allow_redirects=True)
                row["status"] = int(r.status_code)
                row["classification"] = classify(r.status_code, "")
                if r.status_code == 200:
                    try:
                        refs = session.get(f"{API}/api/models/{repo}/refs", timeout=60).json()
                        branches = sorted(b.get("name", "") for b in refs.get("branches", []))
                        row["branch_count"] = len(branches)
                        row["seed_branch_suffixes"] = sorted(
                            {b.split("-seed-", 1)[1] for b in branches if "-seed-" in b})
                    except Exception as exc:
                        row["branch_error"] = f"{type(exc).__name__}: {exc}"[:200]
            except Exception as exc:
                row.update({"status": None, "classification": "request_failed",
                            "detail": f"{type(exc).__name__}: {exc}"[:200]})
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1
        report["rows"].append(row)
        print(f"[{repo}] {row['classification']} status {row.get('status')} "
              f"branches {row.get('branch_count')}", flush=True)
        (W / "r7_availability_recheck.json").write_text(json.dumps(report, indent=1))

report["summary"] = {"total_repositories": len(report["rows"]), "by_classification": counts,
                     "recipes": len(RECIPES), "sizes": len(SIZES)}
report["wall_seconds"] = time.time() - t0
(W / "r7_availability_recheck.json").write_text(json.dumps(report, indent=1))
print(f"[summary] {json.dumps(counts)}", flush=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
