#!/usr/bin/env python3
"""Audit provenance of DES J0408 57-core catastrophic rows.

This script inspects the worst alignment-error rows from the 57-parameter
power-law core.  It asks whether those rows look physically/numerically
pathological in their own posterior coordinates, or whether they look like
ordinary posterior rows whose public/recomputed table pairing breaks.

No T2 parameter is introduced and no failed row is removed or repaired.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv_wgd2038_repro" / "bin" / "python"
DERIVED = ROOT / "data" / "derived"
OUT_DIR = DERIVED / "repro_results" / "tau_core_lensing_desj0408_powerlaw_57_core_outlier_provenance_v1"
CSV_PATH = DERIVED / "desj0408_powerlaw_57_core_outlier_provenance_v1.csv"


HELPER = r'''
import csv
import json
import pickle
import sys
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1])
sample_limit = 1024
model_ids = [
    "0408_run902_0_0_1_0_0_1_1_0",
    "0408_run905_0_1_0_0_0_1_1_0",
    "0408_run1006_0_1_1_0_0_1_1_0",
    "0408_run909_0_2_0_0_0_1_1_0",
]

import dill._dill as dd
import astropy.cosmology as cosmo
import astropy.cosmology.core as core
import astropy.cosmology.flrw.scalar_inv_efuncs as scalar
from lenstronomy.Sampling.parameters import Param
from lenstronomy.LensModel.lens_model import LensModel

if not hasattr(core, "FlatLambdaCDM"):
    core.FlatLambdaCDM = cosmo.FlatLambdaCDM
sys.modules.setdefault("astropy.cosmology.scalar_inv_efuncs", scalar)
dd._reverse_typemap.setdefault("ObjectType", object)

des = ROOT / "data" / "external" / "source_candidate_repos" / "DESJ0408_time_delay_cosmography"


def build_occurrence_mapping(old_names, modern_names):
    old_occurrences = defaultdict(list)
    for old_index, name in enumerate(old_names):
        old_occurrences[name].append(old_index)
    used = Counter()
    mapping = []
    missing = []
    for name in modern_names:
        alias = "tau0" if name == "tau0_list" else name
        occurrence = used[alias]
        used[alias] += 1
        if occurrence < len(old_occurrences[alias]):
            mapping.append(old_occurrences[alias][occurrence])
        else:
            mapping.append(None)
            missing.append(name)
    return mapping, missing


def aligned_samples(samples, old_names, modern_names):
    mapping, missing = build_occurrence_mapping(old_names, modern_names)
    aligned = np.zeros((len(samples), len(modern_names)), dtype=float)
    for modern_index, old_index in enumerate(mapping):
        name = modern_names[modern_index]
        if old_index is not None:
            aligned[:, modern_index] = samples[:, old_index]
        elif name == "s_scale_lens0":
            aligned[:, modern_index] = 0.0
        elif name == "tau0_list":
            aligned[:, modern_index] = 1.0
        else:
            aligned[:, modern_index] = 0.0
    return aligned, missing


def recompute_time_delays(param_class, lens_model, sample_matrix):
    rows = []
    warning_counts = []
    for sample in sample_matrix:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            kw = param_class.args2kwargs(sample)
            ra = kw["kwargs_ps"][0]["ra_image"]
            dec = kw["kwargs_ps"][0]["dec_image"]
            arrival = np.asarray(
                lens_model.arrival_time(ra, dec, kw["kwargs_lens"]), dtype=float
            )
        warning_counts.append(len(caught))
        rows.append([arrival[0] - arrival[1], arrival[0] - arrival[3]])
    return np.asarray(rows, dtype=float), np.asarray(warning_counts, dtype=int)


def robust_z(row, matrix):
    med = np.median(matrix, axis=0)
    mad = np.median(np.abs(matrix - med), axis=0)
    scale = 1.4826 * np.where(mad > 0, mad, np.nan)
    z = np.abs((row - med) / scale)
    return float(np.nanmax(z))


def empirical_quantile(value, values):
    values = np.asarray(values, dtype=float)
    return float(np.mean(values <= value))


rows = []
for model_id in model_ids:
    lens_path = des / "model_posteriors" / "lens_models" / f"{model_id}_mod_out.txt"
    td_path = des / "model_posteriors" / "time_delays" / f"td_{model_id}_mod_out.txt"
    with lens_path.open("rb") as handle:
        input_, output_ = pickle.load(handle, encoding="latin1")
    (
        fitting_kwargs_list,
        kwargs_joint,
        kwargs_model,
        kwargs_constraints,
        kwargs_likelihood,
        kwargs_params,
        init_samples,
    ) = input_
    kwargs_result, multi_band_list_out, fit_output, _tail = output_
    sampler_record = fit_output[-1]
    old_samples = np.asarray(sampler_record[1])
    old_names = list(sampler_record[2])
    log_likelihood = np.asarray(sampler_record[3], dtype=float)
    published = np.loadtxt(td_path)[:sample_limit]
    param_class = Param(
        kwargs_model,
        kwargs_params["lens_model"][2],
        kwargs_params["source_model"][2],
        kwargs_params["lens_light_model"][2],
        kwargs_params["point_source_model"][2],
        kwargs_params["special"][2],
        kwargs_params["extinction_model"][2],
        kwargs_lens_init=kwargs_params["lens_model"][0],
        **kwargs_constraints,
    )
    modern_count, modern_names = param_class.num_param()
    lens_model = LensModel(
        lens_model_list=kwargs_model["lens_model_list"],
        z_lens=None,
        z_source=kwargs_model["z_source"],
        lens_redshift_list=kwargs_model["lens_redshift_list"],
        multi_plane=kwargs_model["multi_plane"],
        observed_convention_index=kwargs_model.get("observed_convention_index"),
        z_source_convention=None,
        cosmo=kwargs_model.get("cosmo"),
    )
    aligned, missing = aligned_samples(old_samples, old_names, modern_names)
    recomputed, warning_counts = recompute_time_delays(
        param_class, lens_model, aligned[:sample_limit]
    )
    delta = recomputed - published
    row_max = np.max(np.abs(delta), axis=1)
    worst_indices = np.argsort(row_max)[-3:][::-1]
    recomputed_median = np.median(recomputed, axis=0)
    published_median = np.median(published, axis=0)
    for rank, row_index in enumerate(worst_indices, start=1):
        row_index = int(row_index)
        ll_value = float(log_likelihood[row_index])
        rows.append({
            "model_id": model_id,
            "worst_rank": int(rank),
            "row_index": row_index,
            "row_max_abs_delta_days": float(row_max[row_index]),
            "delta_dt1_days": float(delta[row_index, 0]),
            "delta_dt2_days": float(delta[row_index, 1]),
            "recomputed_dt1_days": float(recomputed[row_index, 0]),
            "recomputed_dt2_days": float(recomputed[row_index, 1]),
            "published_dt1_days": float(published[row_index, 0]),
            "published_dt2_days": float(published[row_index, 1]),
            "recomputed_distance_from_median_days": float(
                np.max(np.abs(recomputed[row_index] - recomputed_median))
            ),
            "published_distance_from_median_days": float(
                np.max(np.abs(published[row_index] - published_median))
            ),
            "recomputed_delay_robust_z": robust_z(recomputed[row_index], recomputed),
            "published_delay_robust_z": robust_z(published[row_index], published),
            "aligned_parameter_robust_z_max": robust_z(aligned[row_index], aligned[:sample_limit]),
            "log_likelihood": ll_value,
            "log_likelihood_quantile_within_prefix": empirical_quantile(
                ll_value, log_likelihood[:sample_limit]
            ),
            "runtime_warning_count": int(warning_counts[row_index]),
            "row_is_parameter_outlier_candidate": bool(
                robust_z(aligned[row_index], aligned[:sample_limit]) > 8.0
            ),
            "row_is_low_loglike_candidate": bool(
                empirical_quantile(ll_value, log_likelihood[:sample_limit]) < 0.01
            ),
            "row_has_runtime_warning": bool(warning_counts[row_index] > 0),
            "row_pairing_defect_candidate": bool(
                robust_z(aligned[row_index], aligned[:sample_limit]) <= 8.0
                and empirical_quantile(ll_value, log_likelihood[:sample_limit]) >= 0.01
                and warning_counts[row_index] == 0
                and row_max[row_index] > 0.5
            ),
        })

print(json.dumps(rows))
'''


def run_helper() -> list[dict[str, object]]:
    if not VENV.exists():
        raise SystemExit(f"lenstronomy helper venv not found: {VENV}")
    proc = subprocess.run(
        [str(VENV), "-c", HELPER, str(ROOT)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(
            "DES J0408 57-core outlier provenance helper failed\n"
            + proc.stderr[-4000:]
            + "\n"
            + proc.stdout[-4000:]
        )
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return json.loads(lines[-1])


def write_csv(rows: list[dict[str, object]]) -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = run_helper()
    write_csv(rows)
    top_rows = [row for row in rows if int(row["worst_rank"]) == 1]
    pairing_candidates = [row for row in top_rows if bool(row["row_pairing_defect_candidate"])]
    parameter_candidates = [
        row for row in top_rows if bool(row["row_is_parameter_outlier_candidate"])
    ]
    low_loglike_candidates = [row for row in top_rows if bool(row["row_is_low_loglike_candidate"])]
    warning_rows = [row for row in top_rows if bool(row["row_has_runtime_warning"])]
    summary = {
        "schema": "paper7 DES J0408 power-law 57-core outlier provenance v1",
        "purpose": (
            "Inspect whether catastrophic 57-core rows look like posterior-coordinate "
            "outliers, low-likelihood samples, runtime-warning rows, or ordinary "
            "rows with a public/recomputed pairing defect."
        ),
        "source": {
            "source_id": "DESJ0408_time_delay_cosmography",
            "helper_python": str(VENV),
            "sample_limit": 1024,
            "worst_rows_per_model": 3,
        },
        "aggregate": {
            "failed_model_count": len(top_rows),
            "top_worst_row_pairing_defect_candidate_count": len(pairing_candidates),
            "top_worst_row_parameter_outlier_candidate_count": len(parameter_candidates),
            "top_worst_row_low_loglike_candidate_count": len(low_loglike_candidates),
            "top_worst_row_runtime_warning_count": len(warning_rows),
            "pairing_defect_candidate_model_ids": [row["model_id"] for row in pairing_candidates],
            "parameter_outlier_candidate_model_ids": [
                row["model_id"] for row in parameter_candidates
            ],
            "low_loglike_candidate_model_ids": [row["model_id"] for row in low_loglike_candidates],
        },
        "criteria": {
            "catastrophic_rows_inspected": True,
            "posterior_coordinate_outlier_test_applied": True,
            "log_likelihood_quantile_test_applied": True,
            "runtime_warning_test_applied": True,
            "no_t2_parameters_introduced": True,
            "failed_rows_removed_or_repaired": False,
            "real_data_T2_sampling_authorized": False,
        },
        "verdict": {
            "desj0408_powerlaw_57_core_outlier_provenance_created": True,
            "top_worst_rows_look_like_pairing_defects": len(pairing_candidates)
            == len(top_rows),
            "top_worst_rows_look_like_parameter_outliers": len(parameter_candidates) > 0,
            "top_worst_rows_look_like_low_loglike_samples": len(low_loglike_candidates) > 0,
            "strict_baseline_should_remain_2_model_core": True,
            "real_data_T2_sampling_authorized": False,
        },
        "rows": rows,
        "claim_boundary": [
            "This is a provenance diagnostic, not an outlier-removal policy.",
            "Pairing-defect candidates are not promoted without an independent row-linkage rule.",
            "No T2 posterior, Bayes factor, or operator-necessity claim is introduced.",
        ],
        "next_finite_action": (
            "Search for an independent DES row-linkage/provenance rule in the public "
            "notebooks or serialized sampler records; without it, keep only the two "
            "strictly clean models in the no-T2 baseline."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["verdict"], indent=2))
    print(json.dumps(summary["aggregate"], indent=2))


if __name__ == "__main__":
    main()
