"""The 66 released task names, the ten traits, and the item-id spaces.

A vendored copy of the constants in src/seednoise/data/datadecide.py, so the
GPU environment needs numpy only. analysis/estimates.py asserts that this copy
still equals the seednoise one before it reads any run, because the task order
is what assigns item ids and a drift between the two would misalign the banks.

Item ids. Bank 1 is the release's own item set and uses the release ids,
task_index * ITEM_STRIDE + doc_id, so a bank-1 item scored here carries the same
id as the same item in the reduced release runs. Bank 2 and the zero-shot bank
sit in their own id blocks (base 200 and 300 above the task index), so no bank
can ever be mistaken for another when files share a directory. The held-out
pipeline under compute extra uses base 100.
"""
from __future__ import annotations

TRAITS = ["arc_challenge", "arc_easy", "boolq", "csqa", "hellaswag", "mmlu",
          "openbookqa", "piqa", "socialiqa", "winogrande"]
TRAIT_INDEX = {t: i for i, t in enumerate(TRAITS)}

TASKS = [
    'arc_challenge', 'arc_easy', 'boolq',
    'csqa', 'hellaswag', 'mmlu_abstract_algebra',
    'mmlu_anatomy', 'mmlu_astronomy', 'mmlu_business_ethics',
    'mmlu_clinical_knowledge', 'mmlu_college_biology', 'mmlu_college_chemistry',
    'mmlu_college_computer_science', 'mmlu_college_mathematics', 'mmlu_college_medicine',
    'mmlu_college_physics', 'mmlu_computer_security', 'mmlu_conceptual_physics',
    'mmlu_econometrics', 'mmlu_electrical_engineering', 'mmlu_elementary_mathematics',
    'mmlu_formal_logic', 'mmlu_global_facts', 'mmlu_high_school_biology',
    'mmlu_high_school_chemistry', 'mmlu_high_school_computer_science', 'mmlu_high_school_european_history',
    'mmlu_high_school_geography', 'mmlu_high_school_government_and_politics', 'mmlu_high_school_macroeconomics',
    'mmlu_high_school_mathematics', 'mmlu_high_school_microeconomics', 'mmlu_high_school_physics',
    'mmlu_high_school_psychology', 'mmlu_high_school_statistics', 'mmlu_high_school_us_history',
    'mmlu_high_school_world_history', 'mmlu_human_aging', 'mmlu_human_sexuality',
    'mmlu_international_law', 'mmlu_jurisprudence', 'mmlu_logical_fallacies',
    'mmlu_machine_learning', 'mmlu_management', 'mmlu_marketing',
    'mmlu_medical_genetics', 'mmlu_miscellaneous', 'mmlu_moral_disputes',
    'mmlu_moral_scenarios', 'mmlu_nutrition', 'mmlu_philosophy',
    'mmlu_prehistory', 'mmlu_professional_accounting', 'mmlu_professional_law',
    'mmlu_professional_medicine', 'mmlu_professional_psychology', 'mmlu_public_relations',
    'mmlu_security_studies', 'mmlu_sociology', 'mmlu_us_foreign_policy',
    'mmlu_virology', 'mmlu_world_religions', 'openbookqa',
    'piqa', 'socialiqa', 'winogrande',
]
TASK_INDEX = {t: i for i, t in enumerate(TASKS)}
ITEM_STRIDE = 10_000_000

# Item counts of the release battery per trait, in TRAITS order. The bank-1
# builder asserts them; the bank-2 caps in config/banks.json must not exceed them.
RELEASE_ITEMS = {"arc_challenge": 1172, "arc_easy": 2376, "boolq": 3270, "csqa": 1221,
                 "hellaswag": 10042, "mmlu": 14042, "openbookqa": 500, "piqa": 1838,
                 "socialiqa": 1954, "winogrande": 1267}
RELEASE_TOTAL = 37_682

BANK_BASE = {"bank1": 0, "bank2": 200, "bank2zs": 300}


def trait_of_task(task: str) -> str:
    t = task.split("-")[0]
    return "mmlu" if t.startswith("mmlu") else t


def item_id(bank: str, task_index: int, doc_id: int) -> int:
    if bank not in BANK_BASE:
        raise KeyError(f"unknown bank {bank!r}; have {sorted(BANK_BASE)}")
    if not 0 <= int(doc_id) < ITEM_STRIDE:
        raise ValueError(f"doc_id {doc_id} is outside the item-id stride")
    return (BANK_BASE[bank] + int(task_index)) * ITEM_STRIDE + int(doc_id)
