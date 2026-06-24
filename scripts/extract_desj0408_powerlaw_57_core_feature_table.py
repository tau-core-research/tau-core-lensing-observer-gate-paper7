#!/usr/bin/env python3
"""Build a DES J0408 no-T2 feature table for the validated power-law core.

The preceding family alignment smoke identified a conservative DES J0408
power-law core whose legacy posterior samples can be occurrence-aligned to the
modern lenstronomy parameter order and then reproduce the public time-delay
tables.  This script turns that compatibility result into a compact feature
artifact for the validated core only.

No T2 parameter is introduced.  The output is a bounded no-T2 data-side
baseline artifact, not an evidence-grade T2 or Tau-response result.
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
OUT_DIR = DERIVED / "repro_results" / "tau_core_lensing_desj0408_powerlaw_57_core_feature_table_v1"
CSV_PATH = DERIVED / "desj0408_powerlaw_57_core_feature_table_v1.csv"


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
observed_delays = np.array([-112.1, -155.5], dtype=float)
observed_sigma = np.array([2.1, 12.8], dtype=float)
model_ids = [
    "0408_run1001_0_0_0_0_0_1_1_0",
    "0408_run905_0_1_0_0_0_1_1_0",
    "0408_run1006_0_1_1_0_0_1_1_0",
    "0408_run909_0_2_0_0_0_1_1_0",
    "0408_run910_0_2_1_0_0_1_1_0",
]
excluded_near_core_model_ids = [
    "0408_run902_0_0_1_0_0_1_1_0",
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


def stable_weight(logz, all_logz):
    arr = np.asarray(all_logz, dtype=float)
    raw = np.exp(arr - np.max(arr))
    weights = raw / np.sum(raw)
    return float(weights[list(all_logz).index(logz)])


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
    warning_count = 0
    for sample in sample_matrix:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            kw = param_class.args2kwargs(sample)
            ra = kw["kwargs_ps"][0]["ra_image"]
            dec = kw["kwargs_ps"][0]["dec_image"]
            arrival = np.asarray(
                lens_model.arrival_time(ra, dec, kw["kwargs_lens"]), dtype=float
            )
        warning_count += len(caught)
        rows.append([arrival[0] - arrival[1], arrival[0] - arrival[3]])
    return np.asarray(rows, dtype=float), warning_count


preloaded = {}
logz_values = []
for model_id in model_ids:
    lens_path = des / "model_posteriors" / "lens_models" / f"{model_id}_mod_out.txt"
    with lens_path.open("rb") as handle:
        input_, output_ = pickle.load(handle, encoding="latin1")
    logz = float(output_[2][-1][4])
    preloaded[model_id] = (input_, output_, logz)
    logz_values.append(logz)

rows = []
for model_id in model_ids:
    input_, output_, logz = preloaded[model_id]
    td_path = des / "model_posteriors" / "time_delays" / f"td_{model_id}_mod_out.txt"
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
    published = np.loadtxt(td_path)
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
    recomputed, warning_count = recompute_time_delays(
        param_class, lens_model, aligned[:sample_limit]
    )
    published_head = published[:sample_limit]
    delta = recomputed - published_head
    sorted_delta = np.sort(recomputed, axis=0) - np.sort(published_head, axis=0)
    recomputed_std = np.std(recomputed, axis=0, ddof=1)
    published_head_std = np.std(published_head, axis=0, ddof=1)
    distributional_match = (
        float(np.max(np.abs(np.mean(delta, axis=0)))) < 0.1
        and float(np.max(np.abs(recomputed_std - published_head_std))) < 0.1
        and float(np.sqrt(np.mean(sorted_delta ** 2))) < 0.1
    )
    public_residual = published - observed_delays
    public_pull = public_residual / observed_sigma
    public_chi2 = np.sum(public_pull ** 2, axis=1)
    recomputed_pull = (recomputed - observed_delays) / observed_sigma
    recomputed_chi2 = np.sum(recomputed_pull ** 2, axis=1)
    rows.append({
        "model_id": model_id,
        "model_family": "powerlaw_57_core",
        "sample_count_public_time_delay": int(len(published)),
        "sample_count_recomputed_prefix": int(len(recomputed)),
        "old_param_count": int(len(old_names)),
        "modern_param_count": int(modern_count),
        "missing_modern_params": "|".join(missing),
        "lens_model_list": "|".join(kwargs_model["lens_model_list"]),
        "source_light_model_list": "|".join(kwargs_model.get("source_light_model_list", [])),
        "logZ": logz,
        "relative_core_logZ_weight": stable_weight(logz, logz_values),
        "published_dt1_mean_days": float(np.mean(published[:, 0])),
        "published_dt2_mean_days": float(np.mean(published[:, 1])),
        "published_dt1_std_days": float(np.std(published[:, 0], ddof=1)),
        "published_dt2_std_days": float(np.std(published[:, 1], ddof=1)),
        "published_dt1_residual_days": float(np.mean(published[:, 0]) - observed_delays[0]),
        "published_dt2_residual_days": float(np.mean(published[:, 1]) - observed_delays[1]),
        "published_mean_chi2_vs_observed": float(np.mean(public_chi2)),
        "published_fraction_within_2sigma_box": float(
            np.mean(np.all(np.abs(published - observed_delays) <= 2 * observed_sigma, axis=1))
        ),
        "recomputed_prefix_dt1_mean_days": float(np.mean(recomputed[:, 0])),
        "recomputed_prefix_dt2_mean_days": float(np.mean(recomputed[:, 1])),
        "recomputed_prefix_dt1_std_days": float(recomputed_std[0]),
        "recomputed_prefix_dt2_std_days": float(recomputed_std[1]),
        "recomputed_prefix_mean_chi2_vs_observed": float(np.mean(recomputed_chi2)),
        "recomputed_vs_public_prefix_mean_delta_dt1_days": float(np.mean(delta[:, 0])),
        "recomputed_vs_public_prefix_mean_delta_dt2_days": float(np.mean(delta[:, 1])),
        "recomputed_vs_public_prefix_std_delta_dt1_days": float(recomputed_std[0] - published_head_std[0]),
        "recomputed_vs_public_prefix_std_delta_dt2_days": float(recomputed_std[1] - published_head_std[1]),
        "recomputed_vs_public_prefix_sorted_rmse_days": float(np.sqrt(np.mean(sorted_delta ** 2))),
        "recomputed_vs_public_prefix_rmse_days": float(np.sqrt(np.mean(delta ** 2))),
        "recomputed_vs_public_prefix_max_abs_days": float(np.max(np.abs(delta))),
        "runtime_warning_count": int(warning_count),
        "rowwise_feature_row_usable_for_no_t2_baseline": bool(
            np.sqrt(np.mean(delta ** 2)) < 0.05 and warning_count == 0
        ),
        "distributional_feature_row_usable_for_no_t2_baseline": bool(
            distributional_match and warning_count == 0
        ),
    })

print(json.dumps({
    "rows": rows,
    "sample_limit": sample_limit,
    "excluded_near_core_model_ids": excluded_near_core_model_ids,
    "observed_delays_days": observed_delays.tolist(),
    "observed_sigma_days": observed_sigma.tolist(),
}))
'''


def run_helper() -> dict[str, object]:
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
            "DES J0408 57-core feature helper failed\n"
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
    result = run_helper()
    rows = result["rows"]
    write_csv(rows)
    rmse = [float(row["recomputed_vs_public_prefix_rmse_days"]) for row in rows]
    sorted_rmse = [
        float(row["recomputed_vs_public_prefix_sorted_rmse_days"]) for row in rows
    ]
    weights = [float(row["relative_core_logZ_weight"]) for row in rows]
    best_chi2_row = min(rows, key=lambda row: float(row["published_mean_chi2_vs_observed"]))
    best_weight_row = max(rows, key=lambda row: float(row["relative_core_logZ_weight"]))
    summary = {
        "schema": "paper7 DES J0408 power-law 57-core no-T2 feature table v1",
        "purpose": (
            "Promote the validated DES J0408 57-parameter power-law core into a "
            "compact no-T2 feature table with reproduced arrival-time differences, "
            "public observed-delay residuals, and core-relative logZ weights."
        ),
        "source": {
            "source_id": "DESJ0408_time_delay_cosmography",
            "helper_python": str(VENV),
            "observed_delays_days": result["observed_delays_days"],
            "observed_sigma_days": result["observed_sigma_days"],
            "recomputed_prefix_sample_limit": result["sample_limit"],
        },
        "aggregate": {
            "core_model_count": len(rows),
            "rowwise_usable_feature_row_count": sum(
                bool(row["rowwise_feature_row_usable_for_no_t2_baseline"]) for row in rows
            ),
            "distributional_usable_feature_row_count": sum(
                bool(row["distributional_feature_row_usable_for_no_t2_baseline"])
                for row in rows
            ),
            "excluded_near_core_model_ids": result["excluded_near_core_model_ids"],
            "recomputed_vs_public_prefix_rmse_days_max": max(rmse),
            "recomputed_vs_public_prefix_rmse_days_median": sorted(rmse)[len(rmse) // 2],
            "recomputed_vs_public_prefix_sorted_rmse_days_max": max(sorted_rmse),
            "recomputed_vs_public_prefix_sorted_rmse_days_median": sorted(sorted_rmse)[
                len(sorted_rmse) // 2
            ],
            "core_relative_weight_max": max(weights),
            "best_core_model_id_by_public_mean_chi2": best_chi2_row["model_id"],
            "best_core_public_mean_chi2_vs_observed": best_chi2_row[
                "published_mean_chi2_vs_observed"
            ],
            "best_core_model_id_by_relative_logZ_weight": best_weight_row["model_id"],
        },
        "criteria": {
            "validated_57_param_core_only": True,
            "arrival_time_features_recomputed_from_lens_posterior": True,
            "all_core_rows_reproduce_public_time_delay_prefix_rowwise": all(
                float(row["recomputed_vs_public_prefix_rmse_days"]) < 0.05 for row in rows
            ),
            "all_core_rows_reproduce_public_time_delay_prefix_distributionally": all(
                bool(row["distributional_feature_row_usable_for_no_t2_baseline"])
                for row in rows
            ),
            "all_core_rows_warning_free": all(int(row["runtime_warning_count"]) == 0 for row in rows),
            "all_core_rows_have_10000_public_delay_samples": all(
                int(row["sample_count_public_time_delay"]) == 10000 for row in rows
            ),
            "no_t2_parameters_introduced": True,
            "model_ensemble_limited_to_validated_core": True,
            "composite_models_included": False,
            "legacy_60_param_models_included": False,
            "evidence_grade_t2_claim": False,
            "real_data_T2_sampling_authorized": False,
        },
        "verdict": {
            "desj0408_powerlaw_57_core_feature_table_created": True,
            "desj0408_powerlaw_57_core_rowwise_baseline_ready": all(
                bool(row["rowwise_feature_row_usable_for_no_t2_baseline"]) for row in rows
            ),
            "desj0408_powerlaw_57_core_distributional_baseline_ready": all(
                bool(row["distributional_feature_row_usable_for_no_t2_baseline"])
                for row in rows
            ),
            "bounded_no_t2_baseline_reproduction_completed": False,
            "real_data_T2_sampling_authorized": False,
        },
        "rows": rows,
        "claim_boundary": [
            "This is a no-T2 feature table for a validated DES J0408 power-law core, not a T2 sampling run.",
            "Row-wise equality is kept separate from distributional feature recovery because posterior row order can be a legacy serialization artifact.",
            "The near-core run902, 60-parameter power-law models, and composite models remain outside this artifact.",
            "The feature table supports a bounded no-T2 baseline path but does not establish a T2 Bayes factor or Tau operator necessity.",
        ],
        "next_finite_action": (
            "Use this feature table as the frozen DES J0408 no-T2 baseline input "
            "for any later observer-term or Tau-readout diagnostic, while keeping "
            "T2 sampling locked behind a separate eligibility decision."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["verdict"], indent=2))
    print(json.dumps(summary["aggregate"], indent=2))


if __name__ == "__main__":
    main()
