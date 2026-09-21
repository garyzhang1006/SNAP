"""R7 what actually happens when you ask for these checkpoints, recorded one error at a time.

Design fixed before running (2026-09-16, written 11:35 EDT). The manuscript states that 85 of the 125
model repositories refuse an unauthenticated request for their weights. Two GPU runs have now attempted
75 branch loads across all 25 recipes at 150M, and not one of them returned HTTP 401. Every one of the 51
failures was a name that does not exist on the Hub, and the 24 successes downloaded and rescored with no
credential at all. Either the earlier audit measured something different from what the sentence claims,
or the sentence is wrong. A paper cannot carry a provenance claim that its own later runs contradict, so
this run settles it by recording the error rather than the count.
It enumerates every recipe present in the shipped reduced runs, crossed with all five size bands, and for
each one it asks the Hub three questions in order. It lists the allenai namespace for repositories whose
name contains DataDecide, so a missing identifier can be told apart from a name the release spells
differently. It then issues an unauthenticated HEAD against each constructed repository and records the
exact status code, and where a repository resolves it reads the branch list so the seed naming can be
confirmed without downloading weights. Nothing here loads a model or fetches a safetensors file, so it is
a network census rather than compute. The output is a table with one row per repository, carrying the
constructed name, the status code, the error class and the branches found, plus a summary that counts how
many refuse authentication, how many do not exist, and how many resolve anonymously. Whatever that table
says, the manuscript sentence gets rewritten to match it.
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
        (W / "r7_availability.json").write_text(json.dumps(report, indent=1))

report["summary"] = {"total_repositories": len(report["rows"]), "by_classification": counts,
                     "recipes": len(RECIPES), "sizes": len(SIZES)}
report["wall_seconds"] = time.time() - t0
(W / "r7_availability.json").write_text(json.dumps(report, indent=1))
print(f"[summary] {json.dumps(counts)}", flush=True)
print(f"[done] {time.time() - t0:.0f}s", flush=True)
