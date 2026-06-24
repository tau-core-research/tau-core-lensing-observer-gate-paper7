#!/usr/bin/env python3
"""Diagnose DES J0408 57-parameter core alignment failures.

The 57-core feature table showed that a longer 1,024-sample prefix narrows the
usable no-T2 baseline from five candidate core models to two strict models.
This diagnostic answers one bounded question: are the failures caused by a few
catastrophic rows, or by broad ordinary-row incompatibility?

It does not introduce T2, repair by fitting, or promote a failed model.
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
OUT_DIR = DERIVED / "repro_results" / "tau_core_lensing_desj0408_powerlaw_57_core_failure_diagnostic_v1"
CSV_PATH = DERIVED / "desj0408_powerlaw_57_core_failure_diagnostic_v1.csv"


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
    "0408_run1001_0_0_0_0_0_1_1_0",
    "0408_run902_0_0_1_0_0_1_1_0",
    "0408_run905_0_1_0_0_0_1_1_0",
    "0408_run1006_0_1_1_0_0_1_1_0",
    "0408_run909_0_2_0_0_0_1_1_0",
    "0408_run910_0_2_1_0_0_1_1_0",
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
    recomputed, warning_count = recompute_time_delays(
        param_class, lens_model, aligned[:sample_limit]
    )
    delta = recomputed - published
    abs_delta = np.abs(delta)
    row_max = np.max(abs_delta, axis=1)
    sorted_delta = np.sort(recomputed, axis=0) - np.sort(published, axis=0)
    bad_mask_005 = row_max > 0.05
    bad_mask_050 = row_max > 0.50
    good_mask = ~bad_mask_005
    trimmed_rmse = (
        float(np.sqrt(np.mean(delta[good_mask] ** 2))) if np.any(good_mask) else float("nan")
    )
    worst_indices = np.argsort(row_max)[-5:][::-1]
    rows.append({
        "model_id": model_id,
        "sample_limit": int(sample_limit),
        "old_param_count": int(len(old_names)),
        "modern_param_count": int(modern_count),
        "missing_modern_params": "|".join(missing),
        "rowwise_rmse_days": float(np.sqrt(np.mean(delta ** 2))),
        "sorted_distribution_rmse_days": float(np.sqrt(np.mean(sorted_delta ** 2))),
        "mean_abs_delta_dt1_days": float(np.mean(abs_delta[:, 0])),
        "mean_abs_delta_dt2_days": float(np.mean(abs_delta[:, 1])),
        "median_row_max_abs_delta_days": float(np.median(row_max)),
        "p90_row_max_abs_delta_days": float(np.quantile(row_max, 0.90)),
        "p95_row_max_abs_delta_days": float(np.quantile(row_max, 0.95)),
        "p99_row_max_abs_delta_days": float(np.quantile(row_max, 0.99)),
        "max_row_abs_delta_days": float(np.max(row_max)),
        "bad_row_count_gt_0p05_days": int(np.sum(bad_mask_005)),
        "bad_row_fraction_gt_0p05_days": float(np.mean(bad_mask_005)),
        "bad_row_count_gt_0p50_days": int(np.sum(bad_mask_050)),
        "bad_row_fraction_gt_0p50_days": float(np.mean(bad_mask_050)),
        "trimmed_rmse_excluding_gt_0p05_days": trimmed_rmse,
        "worst_row_indices": "|".join(str(int(i)) for i in worst_indices),
        "runtime_warning_count": int(warning_count),
        "strict_rowwise_pass": bool(float(np.sqrt(np.mean(delta ** 2))) < 0.05),
        "outlier_dominated_failure": bool(
            float(np.median(row_max)) < 0.05
            and float(np.quantile(row_max, 0.95)) < 0.05
            and float(np.max(row_max)) > 0.50
        ),
        "untrimmed_distribution_metric_fails": bool(
            float(np.sqrt(np.mean(sorted_delta ** 2))) >= 0.10
        ),
        "broad_ordinary_row_failure": bool(
            float(np.quantile(row_max, 0.95)) >= 0.05
            or float(np.mean(bad_mask_005)) >= 0.05
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
            "DES J0408 57-core failure diagnostic helper failed\n"
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
    failed = [row for row in rows if not bool(row["strict_rowwise_pass"])]
    outlier_dominated = [row for row in failed if bool(row["outlier_dominated_failure"])]
    broad = [row for row in failed if bool(row["broad_ordinary_row_failure"])]
    untrimmed_distribution_failures = [
        row for row in failed if bool(row["untrimmed_distribution_metric_fails"])
    ]
    summary = {
        "schema": "paper7 DES J0408 power-law 57-core failure diagnostic v1",
        "purpose": (
            "Classify 57-parameter core mismatches as strict passes, "
            "outlier-dominated failures, or broad distribution-level failures."
        ),
        "source": {
            "source_id": "DESJ0408_time_delay_cosmography",
            "helper_python": str(VENV),
            "sample_limit": 1024,
        },
        "aggregate": {
            "model_count": len(rows),
            "strict_rowwise_pass_count": sum(bool(row["strict_rowwise_pass"]) for row in rows),
            "failed_model_count": len(failed),
            "outlier_dominated_failure_count": len(outlier_dominated),
            "untrimmed_distribution_metric_failure_count": len(untrimmed_distribution_failures),
            "broad_ordinary_row_failure_count": len(broad),
            "failed_model_ids": [row["model_id"] for row in failed],
            "outlier_dominated_model_ids": [row["model_id"] for row in outlier_dominated],
            "untrimmed_distribution_metric_failure_model_ids": [
                row["model_id"] for row in untrimmed_distribution_failures
            ],
            "broad_ordinary_row_failure_model_ids": [row["model_id"] for row in broad],
        },
        "criteria": {
            "validated_57_param_models_diagnosed": True,
            "failure_mode_classified_without_refitting": True,
            "no_t2_parameters_introduced": True,
            "failed_models_promoted_to_baseline": False,
            "real_data_T2_sampling_authorized": False,
        },
        "verdict": {
            "desj0408_powerlaw_57_core_failure_diagnostic_created": True,
            "failures_are_outlier_dominated_under_current_alignment": (
                len(failed) > 0 and len(outlier_dominated) == len(failed)
            ),
            "broad_ordinary_row_failure_detected": len(broad) > 0,
            "strict_baseline_should_remain_2_model_core_without_outlier_policy": len(failed) > 0,
            "bounded_no_t2_baseline_reproduction_completed": False,
            "real_data_T2_sampling_authorized": False,
        },
        "rows": rows,
        "claim_boundary": [
            "This diagnostic classifies legacy-posterior compatibility failures; it does not repair them.",
            "Failed models are not promoted into the no-T2 baseline.",
            "No T2 posterior, Bayes factor, or operator-necessity claim is introduced.",
        ],
        "next_finite_action": (
            "Freeze the strict two-model DES no-T2 feature core for now.  The "
            "failed 57-parameter models require a row-level provenance/outlier "
            "policy before they can be considered for promotion."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["verdict"], indent=2))
    print(json.dumps(summary["aggregate"], indent=2))


if __name__ == "__main__":
    main()
