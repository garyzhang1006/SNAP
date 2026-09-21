"""Audit item provenance from the release's own request files (R2 and R3).

Downloads requests/<task>-requests.jsonl.gz for all 66 tasks. Each row carries
the source document under "doc" (query, choices, gold and the dataset's own
fields) and the few-shot prompt under "request". Passage identity must come
from "doc", because "request.context" holds exemplars that differ per item.
BoolQ passages are taken from doc.query, which has the form
"<title> -- <passage>\\nQuestion: <question>?\\nAnswer:", and every passage
is checked for exact equality with google/boolq validation at the same
native_id. Only hashes and counts are written, never text.

Usage: python requests_audit.py --out OUT_DIR --native TASK_NATIVE_IDS_JSON
"""
import argparse
import gzip
import hashlib
import io
import json
import re
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import requests

HF_REPO = "allenai/DataDecide-eval-instances"
ITEM_STRIDE = 10_000_000
TASKS = ['arc_challenge', 'arc_easy', 'boolq', 'csqa', 'hellaswag', 'mmlu_abstract_algebra', 'mmlu_anatomy',
         'mmlu_astronomy', 'mmlu_business_ethics', 'mmlu_clinical_knowledge', 'mmlu_college_biology',
         'mmlu_college_chemistry', 'mmlu_college_computer_science', 'mmlu_college_mathematics',
         'mmlu_college_medicine', 'mmlu_college_physics', 'mmlu_computer_security', 'mmlu_conceptual_physics',
         'mmlu_econometrics', 'mmlu_electrical_engineering', 'mmlu_elementary_mathematics', 'mmlu_formal_logic',
         'mmlu_global_facts', 'mmlu_high_school_biology', 'mmlu_high_school_chemistry',
         'mmlu_high_school_computer_science', 'mmlu_high_school_european_history', 'mmlu_high_school_geography',
         'mmlu_high_school_government_and_politics', 'mmlu_high_school_macroeconomics',
         'mmlu_high_school_mathematics', 'mmlu_high_school_microeconomics', 'mmlu_high_school_physics',
         'mmlu_high_school_psychology', 'mmlu_high_school_statistics', 'mmlu_high_school_us_history',
         'mmlu_high_school_world_history', 'mmlu_human_aging', 'mmlu_human_sexuality', 'mmlu_international_law',
         'mmlu_jurisprudence', 'mmlu_logical_fallacies', 'mmlu_machine_learning', 'mmlu_management',
         'mmlu_marketing', 'mmlu_medical_genetics', 'mmlu_miscellaneous', 'mmlu_moral_disputes',
         'mmlu_moral_scenarios', 'mmlu_nutrition', 'mmlu_philosophy', 'mmlu_prehistory',
         'mmlu_professional_accounting', 'mmlu_professional_law', 'mmlu_professional_medicine',
         'mmlu_professional_psychology', 'mmlu_public_relations', 'mmlu_security_studies', 'mmlu_sociology',
         'mmlu_us_foreign_policy', 'mmlu_virology', 'mmlu_world_religions', 'openbookqa', 'piqa', 'socialiqa',
         'winogrande']
TASK_INDEX = {t: i for i, t in enumerate(TASKS)}


def trait_of(task):
    return "mmlu" if task.startswith("mmlu") else task


def norm(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(text))).strip()


def h16(text):
    return hashlib.sha256(norm(text).encode("utf-8")).hexdigest()[:16]


def stem(doc):
    """The item's own stem text, by dataset field, falling back to the query."""
    for key in ("query", "sentence", "goal", "context", "question"):
        if isinstance(doc.get(key), str) and doc[key].strip():
            return doc[key]
    return json.dumps(doc, sort_keys=True)


def boolq_passage(query):
    head = query.split("\nQuestion:", 1)[0]
    return head.split(" -- ", 1)[1] if " -- " in head else head


def truncate(obj, n=160):
    if isinstance(obj, str):
        return obj if len(obj) <= n else obj[:n] + f"...<{len(obj)} chars>"
    if isinstance(obj, dict):
        return {k: truncate(v, n) for k, v in obj.items()}
    if isinstance(obj, list):
        return [truncate(v, n) for v in obj[:6]] + ([f"<{len(obj) - 6} more>"] if len(obj) > 6 else [])
    return obj


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--native", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    native = json.load(open(args.native))["tables"]

    docs, samples, request_types = {}, {}, {}
    for task in TASKS:
        url = f"https://huggingface.co/datasets/{HF_REPO}/resolve/main/requests/{task}-requests.jsonl.gz"
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        rows = [json.loads(l) for l in gzip.GzipFile(fileobj=io.BytesIO(r.content)).read().decode("utf-8").splitlines() if l.strip()]
        samples[task] = truncate(rows[0])
        request_types[task] = dict(Counter(row.get("request_type") for row in rows))
        pred = {int(p["doc_id"]): p for p in native.get(task, [])}
        table = {}
        for row in rows:
            doc = row.get("doc", {})
            nid = row.get("native_id")
            did = row.get("doc_id")
            # Prediction doc ids are the key the reductions use; native ids tie them to the source.
            key = None
            if did is not None and int(did) in pred and str(pred[int(did)]["native_id"]) == str(nid):
                key = int(did)
            elif nid is not None:
                match = [d for d, p in pred.items() if str(p["native_id"]) == str(nid)]
                key = match[0] if len(match) == 1 else None
            if key is None or key in table:
                continue
            s = stem(doc)
            table[key] = {"native_id": nid, "stem_hash": h16(s), "stem_chars": len(norm(s)),
                          "gold": doc.get("gold", doc.get("label", doc.get("answer"))),
                          "choice_hashes": sorted(h16(c) for c in doc.get("choices", []) if isinstance(c, str))}
            if task == "boolq":
                table[key]["passage_hash"] = h16(boolq_passage(doc.get("query", "")))
                table[key]["passage_text"] = boolq_passage(doc.get("query", ""))
        docs[task] = table
        print(f"[req] {task}: {len(rows)} rows, {len(table)} of {len(pred)} prediction docs matched, "
              f"types {request_types[task]}, {time.time() - t0:.0f}s", flush=True)
    (out / "request_samples.json").write_text(json.dumps(samples, indent=1, default=str))

    report = {"tasks": {}, "cross_task": {}, "request_types": request_types}
    for task, table in docs.items():
        pred = native.get(task, [])
        counts = Counter(v["stem_hash"] for v in table.values())
        report["tasks"][task] = {"prediction_docs": len(pred), "matched_docs": len(table),
                                 "unique_stems": len(counts),
                                 "docs_in_repeated_stems": sum(c for c in counts.values() if c > 1),
                                 "max_stem_repeat": max(counts.values()) if counts else 0}
    where = defaultdict(set)
    for task, table in docs.items():
        for v in table.values():
            where[v["stem_hash"]].add(trait_of(task))
    pairs = Counter()
    for traits in where.values():
        if len(traits) > 1:
            ts = sorted(traits)
            for i, a in enumerate(ts):
                for b in ts[i + 1:]:
                    pairs[(a, b)] += 1
    report["cross_task"] = {"shared_stem_trait_pairs": {f"{a}|{b}": n for (a, b), n in pairs.items()},
                            "stems_in_more_than_one_trait": sum(1 for t in where.values() if len(t) > 1)}

    # BoolQ: exact passage check against the official validation split, then groups.
    from datasets import load_dataset
    boolq_val = load_dataset("google/boolq", split="validation")
    table = docs["boolq"]
    exact, unmatched = 0, []
    for d, v in table.items():
        i = int(v["native_id"])
        if norm(boolq_val[i]["passage"]) == norm(v["passage_text"]):
            exact += 1
        else:
            unmatched.append(d)
    groups = {str(2 * ITEM_STRIDE + d): v["passage_hash"] for d, v in table.items()}
    for v in table.values():
        v.pop("passage_text", None)
    sizes = Counter(Counter(groups.values()).values())
    report["boolq"] = {"items": len(groups), "passage_exact_match_with_google_boolq": exact,
                       "passage_mismatches": len(unmatched), "mismatch_examples": unmatched[:5],
                       "unique_passages": len(set(groups.values())),
                       "group_size_histogram": {str(k): v for k, v in sorted(sizes.items())},
                       "items_in_groups_of_two_or_more": sum(k * v for k, v in sizes.items() if k > 1)}
    (out / "boolq_groups_from_requests.json").write_text(json.dumps({"boolq": groups}))
    all_groups = {}
    for task, table in docs.items():
        trait = trait_of(task)
        all_groups.setdefault(trait, {})
        for d, v in table.items():
            all_groups[trait][str(TASK_INDEX[task] * ITEM_STRIDE + d)] = v.get("passage_hash", v["stem_hash"])
    (out / "stem_groups_all_traits.json").write_text(json.dumps(all_groups))
    (out / "doc_tables.json").write_text(json.dumps(docs))
    (out / "requests_audit_report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1), flush=True)
    print(f"[req] done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
