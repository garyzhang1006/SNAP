"""snap-r8-r5-09 (CPU only, exploratory): rule-one power with PolyPythias item noise.

Answers REBUTTAL_LOG R5-09 (academic_reviewer AR5): the rule-one power of snap-r2-r1-18 borrows item
noise from DataDecide margin reliabilities (appendices_bcd.tex, "item noise from its margin reliabilities
with WinoGrande's set to 0.5"), which may be optimistic for 14M to 70M models.

Everything below the noise block is results/snap-r2-r1-18/r1_18_rule_two.py unchanged: Sigma_E, the
draw, the recentred delete-one-seed jackknife, rule one (jackknife lower limit > 1), rule two, 4,000
replicates, seed 20260923 restarted per scenario, 25 replicates cross-checked against the committed
SNAP functions at commit 6cfedee. The one change is the per-trait reliability vector rel that sets the
item noise, noise_k = v_k (1 - rel_k) / rel_k, used exactly as r1_18 uses it.

Reliabilities are computed here, from the 45 PolyPythias runs (nine seeds at 14M, 31M, 70M, 160M, 410M,
step 143000) on the 4,755-item transfer battery written by snap-r12-polypythias, with the same seednoise
code as snap-r12-analysis: seednoise.reliability.variance_components(pop, "margin"), whose reliability
is sigma_E2 / (sigma_E2 + noise2) for one item half, the definition behind the DataDecide table that
r1_18's rel vector copies. Noise sources:
  datadecide_rel_original    r1_18's rel vector verbatim (anchor; must reproduce r1_18's rates)
  pp_pooled_4755             PolyPythias reliabilities pooled over the 45 runs, at 4,755-item halves
  pp_pooled_bank1            the same noise-to-seed ratios scaled by n_pp_k / n_bank1_k, the per-trait
                             item counts of the transfer battery and of bank one (the 37,682 DataDecide
                             items, counted from a shipped DataDecide reduced run), since item noise of a
                             trait mean scales with one over its item count
  pp_per_size_4755           per-size reliabilities, size c's noise in simulated size cluster c
  pp_per_size_bank1          per-size, scaled to bank-one item counts
A trait whose PolyPythias sigma_E2 or noise2 is not positive has no reliability in (0, 1); it gets 0.5,
r1_18's rule for WinoGrande, and is listed under "set_to_half". PolyPythias vectors follow the
seednoise TRAITS order; the anchor keeps r1_18's vector, which swaps the two ARC values.
"""
import importlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t

t0 = time.time()
W = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path(".")
REPS, CHECK, SIZES, R, K = 4000, 25, 5, 9, 10
SEED = 20260923
CRIT = float(student_t.ppf(0.975, R - 1))
SNAP_COMMIT = "6cfedee87ac52695f96665ecc0a62ecdc97e1c35"
PP_SIZES = ["14m", "31m", "70m", "160m", "410m"]
BANK1_ITEMS = 37682
# results/snap-r2-r1-18/r1_18_rule_two.json, for the anchor check
R1_18 = {"run_cov_1244_share0": {"not supported": 0.22575, "supported": 0.013, "undecided": 0.76125, "r1": 0.257},
         "independence_share0": {"not supported": 0.01075, "supported": 0.015, "undecided": 0.97425, "r1": 0.014}}

# ---- PolyPythias reliabilities (seednoise as in snap-r12-analysis) ------------------
Path("/kaggle/tmp").mkdir(parents=True, exist_ok=True)
src = sorted(p for p in Path("/kaggle/input").rglob("pyproject.toml") if "seed-noise" in str(p) and not p.name.startswith("._"))
assert src, "seednoise source (garyzhang11111/snap-compute-src) is not attached"
sn_copy = Path("/kaggle/tmp/seed-noise")
shutil.rmtree(sn_copy, ignore_errors=True)
shutil.copytree(src[0].parent, sn_copy, ignore=shutil.ignore_patterns("._*"))
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", str(sn_copy)])
from seednoise.build import build_population  # noqa: E402
from seednoise.data.datadecide import TRAITS  # noqa: E402
from seednoise.reliability import variance_components  # noqa: E402
from seednoise.store import load_run  # noqa: E402

arm2 = sorted(p for p in Path("/kaggle/input").rglob("arm2__*.npz") if "runs-arm2" in str(p) and not p.name.startswith("._"))
assert len(arm2) == 45, f"expected 45 PolyPythias transfer runs from snap-r12-polypythias, found {len(arm2)}"
runs_dir = Path("/kaggle/tmp/arm2")
shutil.rmtree(runs_dir, ignore_errors=True)
runs_dir.mkdir(parents=True)
for p in arm2:
    shutil.copy(p, runs_dir / p.name)
pop, info = build_population(runs_dir, TRAITS, n_runs=R, sizes=PP_SIZES)
assert pop.N == SIZES and pop.R == R and pop.K == K and not info["dropped_cells"], info
n_pp = np.asarray(pop.n_items, float)
assert int(n_pp.sum()) == 4755, f"transfer battery has {n_pp.sum()} items, not 4,755"

dd = sorted(p for p in Path("/kaggle/input").rglob("*.npz") if "seed-noise-reduced-runs" in str(p) and not p.name.startswith("._"))
assert dd, "DataDecide reduced runs (garyzhang11111/seed-noise-reduced-runs) are not attached"
dd_items, _ = load_run(dd[0])
n_bank1 = np.bincount(dd_items.trait, minlength=K)[:K].astype(float)
assert int(n_bank1.sum()) == BANK1_ITEMS, f"DataDecide run {dd[0].name} has {n_bank1.sum()} items, not {BANK1_ITEMS}"
scale_bank1 = n_pp / n_bank1


def rel_of(comp, scale):
    sig, nz = np.asarray(comp.sigma_e2, float), np.asarray(comp.noise2, float)
    ok = (sig > 0) & (nz > 0)
    rel = np.full(K, 0.5)
    rel[ok] = 1.0 / (1.0 + scale[ok] * nz[ok] / sig[ok])
    return rel, [TRAITS[j] for j in range(K) if not ok[j]]


def comp_row(comp):
    return {"sigma_e2": [float(x) for x in comp.sigma_e2], "noise2": [float(x) for x in comp.noise2],
            "reliability_raw": [float(x) for x in comp.reliability]}


size_of = [pop.config_ids[c][1] for c in range(pop.N)]
order = [size_of.index(z) for z in PP_SIZES]       # simulated size cluster c <- PolyPythias size PP_SIZES[c]
comp_pool = variance_components(pop, "margin")
comp_size = [variance_components(pop.subset([c]), "margin") for c in order]

# ---- r1_18_rule_two.py model, unchanged apart from rel --------------------------
S = np.array([[1.5434e-05,2.8509e-05,-1.5923e-05,6.3360e-05,3.2814e-07,1.1676e-05,1.4808e-05,-4.0919e-07,2.5973e-05,4.4317e-07],
 [2.8509e-05,8.2182e-05,-5.3772e-05,1.3961e-04,8.1074e-07,2.3456e-05,2.8577e-05,1.1207e-06,5.7357e-05,2.8235e-07],
 [-1.5923e-05,-5.3772e-05,1.4337e-03,-7.7178e-05,-2.4860e-06,-9.4041e-06,1.7853e-05,3.5287e-07,-1.9656e-05,-3.3875e-06],
 [6.3360e-05,1.3961e-04,-7.7178e-05,4.3401e-04,1.9061e-06,4.8008e-05,6.9736e-05,-1.1707e-07,1.6556e-04,-1.0158e-06],
 [3.2814e-07,8.1074e-07,-2.4860e-06,1.9061e-06,6.7365e-07,3.9806e-07,1.8321e-07,8.2570e-08,9.8076e-08,-2.3876e-09],
 [1.1676e-05,2.3456e-05,-9.4041e-06,4.8008e-05,3.9806e-07,1.4210e-05,1.0622e-05,-1.8317e-07,1.8578e-05,-8.8690e-08],
 [1.4808e-05,2.8577e-05,1.7853e-05,6.9736e-05,1.8321e-07,1.0622e-05,3.2552e-05,5.6932e-07,3.1616e-05,6.6854e-08],
 [-4.0919e-07,1.1207e-06,3.5287e-07,-1.1707e-07,8.2570e-08,-1.8317e-07,5.6932e-07,7.5772e-07,2.5154e-07,8.4758e-08],
 [2.5973e-05,5.7357e-05,-1.9656e-05,1.6556e-04,9.8076e-08,1.8578e-05,3.1616e-05,2.5154e-07,9.8193e-05,-9.0688e-07],
 [4.4317e-07,2.8235e-07,-3.3875e-06,-1.0158e-06,-2.3876e-09,-8.8690e-08,6.6854e-08,8.4758e-08,-9.0688e-07,1.5477e-07]])
rel_dd = np.array([0.927, 0.584, 0.993, 0.93, 0.757, 0.86, 0.392, 0.273, 0.888, 0.5])
v = np.clip(np.diag(S), 1e-9, None)
S = (S + S.T) / 2
w_, V_ = np.linalg.eigh(S)
S = (V_ * np.clip(w_, 0, None)) @ V_.T
L_obs = V_ * np.sqrt(np.clip(w_, 0, None))
L_ind = np.diag(np.sqrt(np.diag(S)))
true_obs = float(np.sqrt(S.sum() / np.trace(S)))
BANK2_RATIO = 6.0


def noise_of(rel):
    return v * (1 - rel) / rel


NOISE, NOISE_INFO = {}, {}
NOISE["datadecide_rel_original"] = noise_of(rel_dd)
NOISE_INFO["datadecide_rel_original"] = {"rel": rel_dd.tolist(), "set_to_half": ["winogrande (r1_18 rule)"]}
for scale_name, scale in (("4755", np.ones(K)), ("bank1", scale_bank1)):
    rel, flagged = rel_of(comp_pool, scale)
    NOISE[f"pp_pooled_{scale_name}"] = noise_of(rel)
    NOISE_INFO[f"pp_pooled_{scale_name}"] = {"rel": rel.tolist(), "set_to_half": flagged}
    rels = [rel_of(cs, scale) for cs in comp_size]
    NOISE[f"pp_per_size_{scale_name}"] = np.stack([noise_of(r_) for r_, _ in rels])[:, None, :]   # (SIZES, 1, K)
    NOISE_INFO[f"pp_per_size_{scale_name}"] = {"rel_by_size": {z: r_.tolist() for z, (r_, _) in zip(PP_SIZES, rels)},
                                               "set_to_half_by_size": {z: f for z, (_, f) in zip(PP_SIZES, rels)}}
for k_, info_ in NOISE_INFO.items():
    info_["noise_over_v_mean"] = float(np.mean(np.asarray(NOISE[k_]) / v))
    print(f"[noise {k_}] {json.dumps(info_)}", flush=True)


def draw(rng, L, share, noise):
    """One replicate: bank-one halves a, b and bank-one full / bank-two full, all (SIZES, R, K)."""
    e = np.einsum("jk,crk->crj", L, rng.normal(size=(SIZES, R, K)))
    u1 = rng.normal(size=(SIZES, R, 1))      # shared scalar, bank one, repeated in both halves
    u2 = rng.normal(size=(SIZES, R, 1))      # bank two's own scalar
    sh1 = u1 * np.sqrt(share * 2 * noise)
    ia = rng.normal(size=(SIZES, R, K)) * np.sqrt((1 - share) * 2 * noise)
    ib = rng.normal(size=(SIZES, R, K)) * np.sqrt((1 - share) * 2 * noise)
    a, b = e + sh1 + ia, e + sh1 + ib
    full1 = (a + b) / 2
    full2 = e + u2 * np.sqrt(share * BANK2_RATIO * noise) + rng.normal(size=(SIZES, R, K)) * np.sqrt((1 - share) * BANK2_RATIO * noise)
    return a, b, full1, full2


def theta(A, B):
    d = A - A.mean(1, keepdims=True)
    f = B - B.mean(1, keepdims=True)
    T = float((d.sum(-1) * f.sum(-1)).sum())
    U = float((d * f).sum())
    return T / U if U != 0 else float("nan")


def loo(A, B):
    return np.array([theta(np.delete(A, r, 1), np.delete(B, r, 1)) for r in range(R)])


def sq(x):
    return float(np.sqrt(x)) if np.isfinite(x) and x >= 0 else float("nan")


def jack(A, B):
    th, l = theta(A, B), loo(A, B)
    se = float(np.sqrt((R - 1) / R * np.sum((l - l.mean()) ** 2)))
    return {"point": sq(th), "lo": sq(th - CRIT * se), "hi": sq(th + CRIT * se)}


def logdiff(a, b, f1, f2):
    tw, tc = theta(a, b), theta(f1, f2)
    full = float(np.log(tw) - np.log(tc)) if tw > 0 and tc > 0 else float("nan")
    lw, lc = loo(a, b), loo(f1, f2)
    ok = (lw > 0) & (lc > 0)
    if not ok.all() or not np.isfinite(full):
        return {"point_log_theta_diff": full, "error": "a leave-one-out ratio was not positive"}
    l = np.log(lw) - np.log(lc)
    se = float(np.sqrt((R - 1) / R * np.sum((l - l.mean()) ** 2)))
    return {"point_log_theta_diff": full, "lo": full - CRIT * se, "hi": full + CRIT * se}


def verdict(civ, diff):
    clo, chi = civ["lo"], civ["hi"]
    if np.isfinite(clo) and clo > 1.0 and "lo" in diff and diff["lo"] <= 0.0 <= diff["hi"]:
        return "not supported"
    if "lo" in diff and diff["lo"] > 0.0 and np.isfinite(chi) and chi >= 1.0 and not (np.isfinite(clo) and clo > 1.0):
        return "supported"
    return "undecided"


# ---- the committed functions, for the per-replicate cross-check ------------------
# The pip-installed seednoise above served the reliabilities; SNAP's estimates.py must see SNAP's own copy.
for m in [m for m in sys.modules if m == "seednoise" or m.startswith("seednoise.")]:
    del sys.modules[m]
snap = Path("/kaggle/tmp/SNAP")
if not snap.exists():
    subprocess.check_call(["git", "clone", "-q", "https://github.com/garyzhang1006/SNAP.git", str(snap)])
subprocess.check_call(["git", "-C", str(snap), "checkout", "-q", SNAP_COMMIT])
sys.path[:0] = [str(snap / "src"), str(snap / "compute2" / "common"), str(snap / "compute2" / "analysis")]
importlib.invalidate_caches()
import estimates as E  # noqa: E402
from seednoise.population import ACCURACY, MARGIN, Phenotype, Population  # noqa: E402

assert str(snap) in (sys.modules["seednoise"].__file__ or ""), "SNAP's seednoise was not the one imported"


def pop_of(A, B):
    N = A.shape[0]
    return Population({MARGIN: Phenotype(MARGIN, A, B), ACCURACY: Phenotype(ACCURACY, A, B)},
                      batch=np.tile(np.arange(R), (N, 1)), recipe=np.arange(N), size=np.arange(N),
                      traits=[f"t{j}" for j in range(K)])


def committed(a, b, f1, f2):
    pw, pc = pop_of(a, b), pop_of(f1, f2)
    res = {"pythia": {"status": "ok",
                      "within_bank1": {"full": {n: {"all": {"lambda": float("nan"), "jackknife": E.seed_jackknife(pw, n)}} for n in (MARGIN, ACCURACY)}},
                      "cross_bank": {"summary": True, "full": {n: {"all": {"lambda": float("nan"), "jackknife": E.seed_jackknife(pc, n)}} for n in (MARGIN, ACCURACY)}},
                      "within_minus_cross": {n: {"full": E.jackknife_logdiff(pw, pc, n)} for n in (MARGIN, ACCURACY)}}}
    v_ = E.verdicts(res)
    return v_[f"R2_pythia_identification_{MARGIN}"], v_[f"R1_pythia_replicates_{MARGIN}"]


out = {"design": {"reps": REPS, "sizes": SIZES, "seeds": R, "traits": K, "bank2_item_ratio": 1 / BANK2_RATIO,
                  "seed": SEED, "t_crit": CRIT, "true_lambda_run_cov": true_obs, "snap_commit": SNAP_COMMIT,
                  "rule_source": "SNAP compute2/analysis/estimates.py verdicts(), seed_jackknife(), jackknife_logdiff()",
                  "base_script": "results/snap-r2-r1-18/r1_18_rule_two.py",
                  "changed": "item-noise reliability vector only (see noise_sources)"},
       "polypythias": {"runs": len(arm2), "configs": [list(map(str, c)) for c in pop.config_ids], "cluster_order": PP_SIZES,
                       "traits": list(TRAITS), "n_items_transfer": n_pp.tolist(), "n_items_bank1": n_bank1.tolist(),
                       "bank1_count_source": dd[0].name, "scale_bank1": scale_bank1.tolist(),
                       "pooled": comp_row(comp_pool), "per_size": {z: comp_row(c_) for z, c_ in zip(PP_SIZES, comp_size)}},
       "noise_sources": NOISE_INFO, "scenarios": {}}

for src_name, noise in NOISE.items():
    for cov_name, L in (("run_cov_1244_share0", L_obs), ("independence_share0", L_ind)):
        name = f"{src_name}/{cov_name}"
        rng = np.random.default_rng(SEED)
        labels, lam_w, lam_c, r1pass, dpt = [], [], [], [], []
        mism, checked = 0, 0
        for i in range(REPS):
            a, b, f1, f2 = draw(rng, L, 0.0, noise)
            jw, jc, d = jack(a, b), jack(f1, f2), logdiff(a, b, f1, f2)
            lab = verdict(jc, d)
            labels.append(lab)
            lam_w.append(jw["point"]); lam_c.append(jc["point"]); dpt.append(d["point_log_theta_diff"])
            r1pass.append(bool(np.isfinite(jw["lo"]) and jw["lo"] > 1.0))
            if i < CHECK:
                r2, r1 = committed(a, b, f1, f2)
                checked += 1
                if r2["shared_item_explanation"] != lab or r1["pass"] != r1pass[-1]:
                    mism += 1
        labels = np.array(labels)
        p1 = float(np.mean(r1pass))
        row = {"noise_source": src_name, "seed_covariance": cov_name, "shared_item_share": 0.0,
               "rule_one_pass_rate": p1, "rule_one_mc_se": float(np.sqrt(p1 * (1 - p1) / REPS)),
               "rates": {k: float((labels == k).mean()) for k in ("not supported", "supported", "undecided")},
               "within_lambda_median": float(np.nanmedian(lam_w)), "within_lambda_5_95": [float(x) for x in np.nanpercentile(lam_w, [5, 95])],
               "within_lambda_undefined_share": float(np.mean(~np.isfinite(lam_w))),
               "cross_lambda_median": float(np.nanmedian(lam_c)), "cross_lambda_5_95": [float(x) for x in np.nanpercentile(lam_c, [5, 95])],
               "cross_lambda_undefined_share": float(np.mean(~np.isfinite(lam_c))),
               "logdiff_median": float(np.nanmedian(dpt)),
               "committed_function_check": {"replicates": checked, "label_mismatches": mism}}
        row["mc_se_max"] = float(np.sqrt(max(p * (1 - p) for p in row["rates"].values()) / REPS))
        if src_name == "datadecide_rel_original":
            ref = R1_18[cov_name]
            row["anchor_matches_r1_18"] = bool(all(abs(row["rates"][k] - ref[k]) < 1e-12 for k in ("not supported", "supported", "undecided"))
                                               and abs(round(p1, 3) - ref["r1"]) < 1e-12)
        out["scenarios"][name] = row
        print(f"[{name}] R1 pass {p1:.4f} within med {row['within_lambda_median']:.3f} 5-95 "
              f"{row['within_lambda_5_95'][0]:.3f}-{row['within_lambda_5_95'][1]:.3f} R2 {row['rates']} "
              f"check {checked} mismatches {mism} {time.time() - t0:.0f}s", flush=True)

out["wall_seconds"] = time.time() - t0
(W / "r5_09_pp_noise_power.json").write_text(json.dumps(out, indent=1))
shutil.rmtree(runs_dir, ignore_errors=True)
print("[done]", round(time.time() - t0), "s")
