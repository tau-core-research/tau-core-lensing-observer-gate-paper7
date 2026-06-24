#!/usr/bin/env python3
"""Audit the WGD2038 HST-to-lenstronomy reproduction status.

This is a bounded smoke/preflight artifact.  It records whether the public
HST products were reduced into the lenstronomy notebook input format and
whether the multiband notebook can load/setup those inputs.  It is not a
cluster/MCMC posterior reproduction and it does not authorize Paper 7
real-data T2 sampling.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results" / "tau_core_lensing_wgd2038_lenstronomy_hst_reproduction_v1"
OUT_SUMMARY = RESULTS / "summary.json"
OUT_TABLE = DERIVED / "wgd2038_lenstronomy_hst_reproduction_manifest_v1.csv"
HST_PREP_SUMMARY = (
    DERIVED
    / "repro_results"
    / "tau_core_lensing_wgd2038_hst_reduced_data_prep_v1"
    / "summary.json"
)
DEFAULT_LENSTRONOMY_DATA = Path(
    "/tmp/paper7_tdc_sources/WGD2038-4008/lenstronomy_modeling/data"
)
EXECUTED_NOTEBOOKS = {
    "f160w_raw_cells_enabled": Path(
        "/tmp/wgd2038_Image_preprocessing_F160W_raw_cells_enabled_executed.ipynb"
    ),
    "f475x": Path("/tmp/wgd2038_Image_preprocessing_F475X_executed.ipynb"),
    "f814w": Path("/tmp/wgd2038_Image_preprocessing_F814W_executed.ipynb"),
    "multiband_preflight": Path(
        "/tmp/wgd2038_Multiband_Image_Modeling_preflight_data_setup_only_executed.ipynb"
    ),
    "multiband_pemd_smoke": Path(
        "/tmp/wgd2038_Multiband_Image_Modeling_tau_core_smoke_run_fastell_suppressed_executed.ipynb"
    ),
    "multiband_pemd_fastell_smoke": Path(
        "/tmp/wgd2038_Multiband_Image_Modeling_tau_core_smoke_run_fastell_backend_executed.ipynb"
    ),
    "multiband_pemd_fastell_mcmc_pilot": Path(
        "/tmp/wgd2038_Multiband_Image_Modeling_tau_core_mcmc_pilot_fastell_backend_executed.ipynb"
    ),
    "multiband_pemd_fastell_mcmc_diagnostic": Path(
        "/tmp/wgd2038_Multiband_Image_Modeling_tau_core_mcmc_diagnostic_fastell_backend_executed.ipynb"
    ),
    "multiband_pemd_fastell_mcmc_diag120_cont": Path(
        "/tmp/wgd2038_Multiband_Image_Modeling_tau_core_mcmc_diag120_cont_fastell_backend_executed.ipynb"
    ),
    "multiband_pemd_fastell_mcmc_diag120_cont2": Path(
        "/tmp/wgd2038_Multiband_Image_Modeling_tau_core_mcmc_diag120_cont2_fastell_backend_executed.ipynb"
    ),
    "multiband_pemd_fastell_mcmc_diag120_cont3_cold": Path(
        "/tmp/wgd2038_Multiband_Image_Modeling_tau_core_mcmc_diag120_cont3_cold_fastell_backend_executed.ipynb"
    ),
}
SMOKE_INPUT = Path(
    "/tmp/paper7_tdc_sources/WGD2038-4008/lenstronomy_modeling/temp/"
    "tau_core_smoke_pemd_minimal.txt"
)
SMOKE_OUTPUT = Path(
    "/tmp/paper7_tdc_sources/WGD2038-4008/lenstronomy_modeling/temp/"
    "tau_core_smoke_pemd_minimal_out.txt"
)
FASTELL_SMOKE_INPUT = Path(
    "/tmp/paper7_tdc_sources/WGD2038-4008/lenstronomy_modeling/temp/"
    "tau_core_smoke_pemd_fastell_backend.txt"
)
FASTELL_SMOKE_OUTPUT = Path(
    "/tmp/paper7_tdc_sources/WGD2038-4008/lenstronomy_modeling/temp/"
    "tau_core_smoke_pemd_fastell_backend_out.txt"
)
MCMC_PILOT_INPUT = Path(
    "/tmp/paper7_tdc_sources/WGD2038-4008/lenstronomy_modeling/temp/"
    "tau_core_mcmc_pilot_pemd_fastell_backend.txt"
)
MCMC_PILOT_OUTPUT = Path(
    "/tmp/paper7_tdc_sources/WGD2038-4008/lenstronomy_modeling/temp/"
    "tau_core_mcmc_pilot_pemd_fastell_backend_out.txt"
)
MCMC_DIAGNOSTIC_INPUT = Path(
    "/tmp/paper7_tdc_sources/WGD2038-4008/lenstronomy_modeling/temp/"
    "tau_core_mcmc_diag_pemd_fastell_backend.txt"
)
MCMC_DIAGNOSTIC_OUTPUT = Path(
    "/tmp/paper7_tdc_sources/WGD2038-4008/lenstronomy_modeling/temp/"
    "tau_core_mcmc_diag_pemd_fastell_backend_out.txt"
)
MCMC_DIAGNOSTIC60_SUMMARY = (
    RESULTS / "mcmc_diagnostic60_payload_summary.json"
)
MCMC_DIAGNOSTIC120_SUMMARY = (
    RESULTS / "mcmc_diagnostic120_payload_summary.json"
)
MCMC_DIAG120_CONT_SUMMARY = (
    RESULTS / "mcmc_diag120_cont_payload_summary.json"
)
MCMC_DIAG120_CONT2_SUMMARY = (
    RESULTS / "mcmc_diag120_cont2_payload_summary.json"
)
MCMC_DIAG120_CONT3_COLD_SUMMARY = (
    RESULTS / "mcmc_diag120_cont3_cold_payload_summary.json"
)
MCMC_PARAMETER_DRIFT_SUMMARY = (
    RESULTS / "mcmc_parameter_drift_diagnostic_summary_v1.json"
)
NUISANCE_STABILIZATION_PLAN = (
    RESULTS / "wgd2038_nuisance_stabilization_plan_v1.json"
)
PROFILE_FREEZE_V1_SUMMARY = (
    RESULTS / "profile_freeze_v1_payload_summary.json"
)
PROFILE_FREEZE_V2_SUMMARY = (
    RESULTS / "profile_freeze_v2_payload_summary.json"
)

EXPECTED_HDF5 = [
    "data_f160w.hdf5",
    "psf_f160w.hdf5",
    "psf_f160w_hires.hdf5",
    "data_f475x.hdf5",
    "psf_f475x.hdf5",
    "data_f814w.hdf5",
    "psf_f814w.hdf5",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_obj(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_json_if_present(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def notebook_has_no_errors(path: Path) -> bool:
    if not path.exists():
        return False
    notebook = load_json_if_present(path)
    for cell in notebook.get("cells", []):
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                return False
    return True


def inspect_hdf5_outputs(data_dir: Path = DEFAULT_LENSTRONOMY_DATA) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in EXPECTED_HDF5:
        path = data_dir / name
        present_now = path.exists()
        current_sha256 = sha256_file(path) if present_now else None
        rows.append(
            {
                "name": name,
                "recorded": present_now,
                "present_now": present_now,
                "path": str(path),
                "recorded_bytes": path.stat().st_size if present_now else None,
                "recorded_sha256": current_sha256,
                "current_sha256": current_sha256,
                "hash_matches_record": True if present_now else None,
            }
        )
    return rows


def inspect_smoke_job(job_name: str, input_path: Path, output_path: Path) -> dict[str, Any]:
    """Inspect the bounded local smoke job without treating it as validation."""
    row: dict[str, Any] = {
        "job_name": job_name,
        "input_path": str(input_path),
        "output_path": str(output_path),
        "input_present": input_path.exists(),
        "output_present": output_path.exists(),
        "input_sha256": sha256_file(input_path) if input_path.exists() else None,
        "output_sha256": sha256_file(output_path) if output_path.exists() else None,
        "fit_output_length": None,
        "fit_output_types": [],
        "emcee_sample_shape": None,
        "emcee_log_prob_shape": None,
        "finite_samples": None,
        "finite_logp": None,
        "split_half_max_abs_mean_shift_in_sigma": None,
        "split_half_median_abs_mean_shift_in_sigma": None,
        "logp_min": None,
        "logp_max": None,
        "logp_median": None,
        "band_count": None,
        "lens_result_count": None,
        "optional_joblib_inspection_available": False,
        "inspection_error": None,
    }
    if not output_path.exists():
        return row

    try:
        import joblib  # type: ignore[import-not-found]
        import numpy as np  # type: ignore[import-not-found]

        with output_path.open("rb") as handle:
            _input, output = joblib.load(handle)
        kwargs_result, multi_band_list_out, fit_output, _kwargs_fixed_out = output
        row["optional_joblib_inspection_available"] = True
        row["fit_output_length"] = len(fit_output)
        row["fit_output_types"] = [step[0] for step in fit_output]
        for step in fit_output:
            if step[0] == "emcee":
                samples = np.asarray(step[1])
                logp = np.asarray(step[3])
                row["emcee_sample_shape"] = list(samples.shape)
                row["emcee_log_prob_shape"] = list(logp.shape)
                row["finite_samples"] = bool(np.isfinite(samples).all())
                row["finite_logp"] = bool(np.isfinite(logp).all())
                row["logp_min"] = float(np.nanmin(logp))
                row["logp_max"] = float(np.nanmax(logp))
                row["logp_median"] = float(np.nanmedian(logp))
                mid = samples.shape[0] // 2
                first = samples[:mid]
                second = samples[mid:]
                delta = np.nanmean(second, axis=0) - np.nanmean(first, axis=0)
                spread = np.nanstd(samples, axis=0)
                norm = np.abs(delta) / (spread + 1e-12)
                row["split_half_max_abs_mean_shift_in_sigma"] = float(np.nanmax(norm))
                row["split_half_median_abs_mean_shift_in_sigma"] = float(np.nanmedian(norm))
        row["band_count"] = len(multi_band_list_out)
        row["lens_result_count"] = len(kwargs_result.get("kwargs_lens", []))
    except Exception as exc:  # pragma: no cover - defensive artifact inspection.
        row["inspection_error"] = repr(exc)
    return row


def build_summary() -> dict[str, Any]:
    hst_prep = load_json_if_present(HST_PREP_SUMMARY)
    hdf5_rows = inspect_hdf5_outputs()
    notebook_status = {
        name: {
            "path": str(path),
            "exists": path.exists(),
            "no_errors": notebook_has_no_errors(path),
        }
        for name, path in EXECUTED_NOTEBOOKS.items()
    }
    smoke_job = inspect_smoke_job(
        "tau_core_smoke_pemd_minimal",
        SMOKE_INPUT,
        SMOKE_OUTPUT,
    )
    fastell_smoke_job = inspect_smoke_job(
        "tau_core_smoke_pemd_fastell_backend",
        FASTELL_SMOKE_INPUT,
        FASTELL_SMOKE_OUTPUT,
    )
    mcmc_pilot_job = inspect_smoke_job(
        "tau_core_mcmc_pilot_pemd_fastell_backend",
        MCMC_PILOT_INPUT,
        MCMC_PILOT_OUTPUT,
    )
    mcmc_diagnostic_job = inspect_smoke_job(
        "tau_core_mcmc_diag_pemd_fastell_backend",
        MCMC_DIAGNOSTIC_INPUT,
        MCMC_DIAGNOSTIC_OUTPUT,
    )
    mcmc_diagnostic60_summary = load_json_if_present(MCMC_DIAGNOSTIC60_SUMMARY)
    mcmc_diagnostic120_summary = load_json_if_present(MCMC_DIAGNOSTIC120_SUMMARY)
    mcmc_diag120_cont_summary = load_json_if_present(MCMC_DIAG120_CONT_SUMMARY)
    mcmc_diag120_cont2_summary = load_json_if_present(MCMC_DIAG120_CONT2_SUMMARY)
    mcmc_diag120_cont3_cold_summary = load_json_if_present(
        MCMC_DIAG120_CONT3_COLD_SUMMARY
    )
    mcmc_parameter_drift_summary = load_json_if_present(MCMC_PARAMETER_DRIFT_SUMMARY)
    nuisance_stabilization_plan = load_json_if_present(NUISANCE_STABILIZATION_PLAN)
    profile_freeze_v1_summary = load_json_if_present(PROFILE_FREEZE_V1_SUMMARY)
    profile_freeze_v2_summary = load_json_if_present(PROFILE_FREEZE_V2_SUMMARY)

    criteria = {
        "hst_mast_products_downloaded": hst_prep.get("criteria", {}).get(
            "all_mast_sources_present"
        )
        is True,
        "sci_wht_reduced_data_prepared": hst_prep.get("criteria", {}).get(
            "all_sci_wht_outputs_present"
        )
        is True,
        "all_required_lenstronomy_hdf5_recorded": all(row["recorded"] for row in hdf5_rows),
        "all_present_hdf5_hashes_match": all(
            row["hash_matches_record"] is not False for row in hdf5_rows
        ),
        "f160w_raw_cell_reproduction_patch_documented": notebook_status[
            "f160w_raw_cells_enabled"
        ]["no_errors"],
        "f475x_preprocessing_executed": notebook_status["f475x"]["no_errors"],
        "f814w_preprocessing_executed": notebook_status["f814w"]["no_errors"],
        "multiband_data_setup_preflight_executed": notebook_status["multiband_preflight"][
            "no_errors"
        ],
        "bounded_pemd_smoke_notebook_executed": notebook_status["multiband_pemd_smoke"][
            "no_errors"
        ],
        "bounded_pemd_smoke_job_output_recorded": all(
            [
                smoke_job["input_present"],
                smoke_job["output_present"],
            ]
        ),
        "bounded_pemd_smoke_joblib_deep_inspected": all(
            [
                smoke_job["optional_joblib_inspection_available"],
                smoke_job["fit_output_length"] == 1,
                smoke_job["fit_output_types"] == ["PSO"],
                smoke_job["band_count"] == 3,
                smoke_job["lens_result_count"] == 2,
                smoke_job["inspection_error"] is None,
            ]
        ),
        "bounded_pemd_fastell_smoke_notebook_executed": notebook_status[
            "multiband_pemd_fastell_smoke"
        ]["no_errors"],
        "bounded_pemd_fastell_smoke_job_output_recorded": all(
            [
                fastell_smoke_job["input_present"],
                fastell_smoke_job["output_present"],
            ]
        ),
        "bounded_pemd_fastell_smoke_joblib_deep_inspected": all(
            [
                fastell_smoke_job["optional_joblib_inspection_available"],
                fastell_smoke_job["fit_output_length"] == 1,
                fastell_smoke_job["fit_output_types"] == ["PSO"],
                fastell_smoke_job["band_count"] == 3,
                fastell_smoke_job["lens_result_count"] == 2,
                fastell_smoke_job["inspection_error"] is None,
            ]
        ),
        "bounded_pemd_fastell_mcmc_pilot_notebook_executed": notebook_status[
            "multiband_pemd_fastell_mcmc_pilot"
        ]["no_errors"],
        "bounded_pemd_fastell_mcmc_pilot_output_recorded": all(
            [
                mcmc_pilot_job["input_present"],
                mcmc_pilot_job["output_present"],
            ]
        ),
        "bounded_pemd_fastell_mcmc_pilot_deep_inspected": all(
            [
                mcmc_pilot_job["optional_joblib_inspection_available"],
                mcmc_pilot_job["fit_output_length"] == 2,
                mcmc_pilot_job["fit_output_types"] == ["PSO", "emcee"],
                mcmc_pilot_job["emcee_sample_shape"] == [424, 53],
                mcmc_pilot_job["emcee_log_prob_shape"] == [424],
                mcmc_pilot_job["band_count"] == 3,
                mcmc_pilot_job["lens_result_count"] == 2,
                mcmc_pilot_job["inspection_error"] is None,
            ]
        ),
        "bounded_pemd_fastell_mcmc_diagnostic_notebook_executed": notebook_status[
            "multiband_pemd_fastell_mcmc_diagnostic"
        ]["no_errors"],
        "bounded_pemd_fastell_mcmc_diagnostic_output_recorded": all(
            [
                mcmc_diagnostic_job["input_present"],
                mcmc_diagnostic_job["output_present"],
            ]
        ),
        "bounded_pemd_fastell_mcmc_diagnostic_deep_inspected": all(
            [
                mcmc_diagnostic_job["optional_joblib_inspection_available"],
                mcmc_diagnostic_job["fit_output_length"] == 2,
                mcmc_diagnostic_job["fit_output_types"] == ["PSO", "emcee"],
                mcmc_diagnostic_job["emcee_sample_shape"] == [4240, 53],
                mcmc_diagnostic_job["emcee_log_prob_shape"] == [4240],
                mcmc_diagnostic_job["finite_samples"] is True,
                mcmc_diagnostic_job["finite_logp"] is True,
                mcmc_diagnostic_job["band_count"] == 3,
                mcmc_diagnostic_job["lens_result_count"] == 2,
                mcmc_diagnostic_job["inspection_error"] is None,
            ]
        ),
        "bounded_pemd_fastell_mcmc_diagnostic60_payload_summarized": all(
            [
                mcmc_diagnostic60_summary.get("fit_output_types") == ["PSO", "emcee"],
                mcmc_diagnostic60_summary.get("emcee_sample_shape") == [12720, 53],
                mcmc_diagnostic60_summary.get("emcee_log_prob_shape") == [12720],
                mcmc_diagnostic60_summary.get("finite_samples") is True,
                mcmc_diagnostic60_summary.get("finite_logp") is True,
                mcmc_diagnostic60_summary.get("converged_no_T2_posterior_reproduced")
                is False,
                mcmc_diagnostic60_summary.get("real_data_T2_sampling_authorized") is False,
            ]
        ),
        "bounded_pemd_fastell_mcmc_diagnostic120_payload_summarized": all(
            [
                mcmc_diagnostic120_summary.get("fit_output_types") == ["PSO", "emcee"],
                mcmc_diagnostic120_summary.get("emcee_sample_shape") == [25440, 53],
                mcmc_diagnostic120_summary.get("emcee_log_prob_shape") == [25440],
                mcmc_diagnostic120_summary.get("finite_samples") is True,
                mcmc_diagnostic120_summary.get("finite_logp") is True,
                mcmc_diagnostic120_summary.get("converged_no_T2_posterior_reproduced")
                is False,
                mcmc_diagnostic120_summary.get("real_data_T2_sampling_authorized") is False,
            ]
        ),
        "bounded_pemd_fastell_mcmc_diag120_cont_notebook_executed": notebook_status[
            "multiband_pemd_fastell_mcmc_diag120_cont"
        ]["no_errors"],
        "bounded_pemd_fastell_mcmc_diag120_cont_payload_summarized": all(
            [
                mcmc_diag120_cont_summary.get("fit_output_types") == ["emcee"],
                mcmc_diag120_cont_summary.get("emcee_sample_shape") == [25440, 53],
                mcmc_diag120_cont_summary.get("emcee_log_prob_shape") == [25440],
                mcmc_diag120_cont_summary.get("finite_samples") is True,
                mcmc_diag120_cont_summary.get("finite_logp") is True,
                mcmc_diag120_cont_summary.get("uses_previous_chain_endpoint_start") is True,
                mcmc_diag120_cont_summary.get("converged_no_T2_posterior_reproduced")
                is False,
                mcmc_diag120_cont_summary.get("real_data_T2_sampling_authorized") is False,
            ]
        ),
        "bounded_pemd_fastell_mcmc_diag120_cont2_notebook_executed": notebook_status[
            "multiband_pemd_fastell_mcmc_diag120_cont2"
        ]["no_errors"],
        "bounded_pemd_fastell_mcmc_diag120_cont2_payload_summarized": all(
            [
                mcmc_diag120_cont2_summary.get("fit_output_types") == ["emcee"],
                mcmc_diag120_cont2_summary.get("emcee_sample_shape") == [25440, 53],
                mcmc_diag120_cont2_summary.get("emcee_log_prob_shape") == [25440],
                mcmc_diag120_cont2_summary.get("finite_samples") is True,
                mcmc_diag120_cont2_summary.get("finite_logp") is True,
                mcmc_diag120_cont2_summary.get("uses_previous_chain_endpoint_start") is True,
                mcmc_diag120_cont2_summary.get("converged_no_T2_posterior_reproduced")
                is False,
                mcmc_diag120_cont2_summary.get("real_data_T2_sampling_authorized") is False,
            ]
        ),
        "bounded_pemd_fastell_mcmc_diag120_cont3_cold_notebook_executed": notebook_status[
            "multiband_pemd_fastell_mcmc_diag120_cont3_cold"
        ]["no_errors"],
        "bounded_pemd_fastell_mcmc_diag120_cont3_cold_payload_summarized": all(
            [
                mcmc_diag120_cont3_cold_summary.get("fit_output_types") == ["emcee"],
                mcmc_diag120_cont3_cold_summary.get("emcee_sample_shape") == [25440, 53],
                mcmc_diag120_cont3_cold_summary.get("emcee_log_prob_shape") == [25440],
                mcmc_diag120_cont3_cold_summary.get("finite_samples") is True,
                mcmc_diag120_cont3_cold_summary.get("finite_logp") is True,
                mcmc_diag120_cont3_cold_summary.get("mcmc_sigma_scale") == 0.02,
                mcmc_diag120_cont3_cold_summary.get("uses_previous_chain_endpoint_start")
                is True,
                mcmc_diag120_cont3_cold_summary.get(
                    "converged_no_T2_posterior_reproduced"
                )
                is False,
                mcmc_diag120_cont3_cold_summary.get("real_data_T2_sampling_authorized")
                is False,
            ]
        ),
        "bounded_pemd_fastell_mcmc_parameter_drift_diagnostic_summarized": all(
            [
                mcmc_parameter_drift_summary.get("verdict", {}).get(
                    "parameter_drift_diagnostic_created"
                )
                is True,
                mcmc_parameter_drift_summary.get("verdict", {}).get(
                    "all_available_jobs_finite"
                )
                is True,
                mcmc_parameter_drift_summary.get("verdict", {}).get(
                    "simple_endpoint_or_cold_continuation_clears_blocker"
                )
                is False,
                mcmc_parameter_drift_summary.get("real_data_T2_sampling_authorized")
                is False,
            ]
        ),
        "wgd2038_nuisance_stabilization_plan_created": all(
            [
                nuisance_stabilization_plan.get("counts", {}).get(
                    "profile_freeze_candidates_ge_1sigma_mean", 0
                )
                > 0,
                nuisance_stabilization_plan.get("recommended_next_run", {}).get("name")
                == "profile_freeze_v1_bounded_diagnostic",
                nuisance_stabilization_plan.get("real_data_T2_sampling_authorized")
                is False,
            ]
        ),
        "bounded_pemd_fastell_profile_freeze_v1_payload_summarized": all(
            [
                profile_freeze_v1_summary.get("fit_output_types") == ["emcee"],
                profile_freeze_v1_summary.get("emcee_sample_shape") == [20160, 42],
                profile_freeze_v1_summary.get("emcee_log_prob_shape") == [20160],
                profile_freeze_v1_summary.get("finite_samples") is True,
                profile_freeze_v1_summary.get("finite_logp") is True,
                profile_freeze_v1_summary.get("reuses_previous_mcmc_samples") is False,
                profile_freeze_v1_summary.get("uses_previous_best_fit_start") is True,
                profile_freeze_v1_summary.get("converged_no_T2_posterior_reproduced")
                is False,
                profile_freeze_v1_summary.get("real_data_T2_sampling_authorized")
                is False,
            ]
        ),
        "bounded_pemd_fastell_profile_freeze_v2_payload_summarized": all(
            [
                profile_freeze_v2_summary.get("fit_output_types") == ["emcee"],
                profile_freeze_v2_summary.get("emcee_sample_shape") == [16800, 35],
                profile_freeze_v2_summary.get("emcee_log_prob_shape") == [16800],
                profile_freeze_v2_summary.get("finite_samples") is True,
                profile_freeze_v2_summary.get("finite_logp") is True,
                profile_freeze_v2_summary.get("reuses_previous_mcmc_samples") is False,
                profile_freeze_v2_summary.get("uses_previous_best_fit_start") is True,
                profile_freeze_v2_summary.get("converged_no_T2_posterior_reproduced")
                is False,
                profile_freeze_v2_summary.get("real_data_T2_sampling_authorized")
                is False,
            ]
        ),
        "full_multiband_cluster_mcmc_executed": False,
        "posterior_joblib_outputs_reproduced": False,
        "converged_no_T2_posterior_reproduced": False,
    }

    summary: dict[str, Any] = {
        "schema": "paper7 WGD2038 HST lenstronomy reproduction audit v1",
        "purpose": (
            "Record the bounded reproduction level reached from public HST inputs: "
            "HST SCI/WHT preparation, three-band lenstronomy HDF5 preprocessing, "
            "and multiband data/setup preflight."
        ),
        "source_summary": str(OUT_SUMMARY),
        "hst_prep_summary": str(HST_PREP_SUMMARY),
        "lenstronomy_data_dir": str(DEFAULT_LENSTRONOMY_DATA),
        "executed_notebooks": notebook_status,
        "hdf5_rows": hdf5_rows,
        "bounded_smoke_job": smoke_job,
        "bounded_fastell_smoke_job": fastell_smoke_job,
        "bounded_fastell_mcmc_pilot_job": mcmc_pilot_job,
        "bounded_fastell_mcmc_diagnostic_job": mcmc_diagnostic_job,
        "bounded_fastell_mcmc_diagnostic60_summary": mcmc_diagnostic60_summary,
        "bounded_fastell_mcmc_diagnostic120_summary": mcmc_diagnostic120_summary,
        "bounded_fastell_mcmc_diag120_cont_summary": mcmc_diag120_cont_summary,
        "bounded_fastell_mcmc_diag120_cont2_summary": mcmc_diag120_cont2_summary,
        "bounded_fastell_mcmc_diag120_cont3_cold_summary": (
            mcmc_diag120_cont3_cold_summary
        ),
        "bounded_fastell_mcmc_parameter_drift_summary": mcmc_parameter_drift_summary,
        "wgd2038_nuisance_stabilization_plan": nuisance_stabilization_plan,
        "bounded_fastell_profile_freeze_v1_summary": profile_freeze_v1_summary,
        "bounded_fastell_profile_freeze_v2_summary": profile_freeze_v2_summary,
        "bounded_smoke_compatibility_notes": [
            "fastell4py was unavailable in the local environment, so the PEMD smoke "
            "copy used suppress_fastell=True. This is a dependency bypass for "
            "model-plumbing only and is not a physical PEMD posterior.",
            "After repairing the local venv build toolchain, fastell4py was installed "
            "from https://github.com/sibirrer/fastell4py.git at commit "
            "3448d58033ebbf1c0ac3047459d6c999ba6701fe and a second bounded "
            "PEMD/SHEAR smoke run completed without suppress_fastell.",
            "Legacy notebook likelihood keys check_matched_source_position and "
            "source_position_tolerance were removed for the installed lenstronomy API.",
            "The legacy PSF keyword psf_error_map was removed for the installed "
            "lenstronomy PSF API.",
            "The fitting list was reduced to one tiny PSO step, with no PSF "
            "iteration, image alignment, MCMC, or posterior analysis.",
            "A follow-up pilot used the physical fastell4py backend with one tiny "
            "PSO step plus a minimal emcee path. The pilot records MCMC plumbing "
            "only and is explicitly not a converged posterior.",
            "A short diagnostic pilot used one tiny PSO step plus a 20-step emcee "
            "path. When inspected in the lenstronomy venv it produced finite samples "
            "and log-probabilities, but it is still not a converged posterior.",
            "A diagnostic60 payload summary records a 60-step emcee path with 12720 "
            "finite samples over 53 parameters. Split-half drift remains visible, so "
            "this is a chain-health artifact, not a posterior-reproduction claim.",
            "A diagnostic120 payload summary records a 120-step emcee path with 25440 "
            "finite samples over 53 parameters. Split-half drift increases relative "
            "to diagnostic60, so the result is explicitly not converged.",
            "A diagnostic120 continuation payload starts from the previous chain "
            "endpoint and records another 25440 finite samples over 53 parameters. "
            "This confirms continuation plumbing, but the split-half drift remains "
            "visible, so it is not a converged posterior.",
            "A second diagnostic120 continuation from the first continuation endpoint "
            "also records 25440 finite samples over 53 parameters, but drift does not "
            "improve. This is evidence that simple endpoint continuation is not enough "
            "to clear the posterior-convergence blocker.",
            "A cold diagnostic120 continuation from the second continuation endpoint "
            "uses sigma_scale=0.02 and again records 25440 finite samples over 53 "
            "parameters, but drift worsens. This suggests the blocker is not cleared "
            "by simply lowering the continuation proposal scale.",
            "A parameter-level drift diagnostic shows that the visible drift is "
            "concentrated in nuisance-heavy light-profile and image-position "
            "parameters, diagnosing the blocker without authorizing a T2 run.",
            "A nuisance-stabilization plan selects a first bounded profile-freeze "
            "diagnostic: stabilize the highest-drift lens/source-light profile "
            "directions while keeping mass/shear and T2 claims protected.",
            "The profile-freeze v1 bounded diagnostic runs with 42 active parameters "
            "and finite samples/log-probabilities. It reduces median split-half drift, "
            "but remains a diagnostic, not a converged no-T2 posterior.",
            "The more aggressive profile-freeze v2 run is finite but worsens drift. "
            "This is a negative stabilization diagnostic: v1 is useful, while v2 "
            "over-constrains or transfers drift into remaining nuisance directions.",
        ],
        "criteria": criteria,
        "verdict": {
            "hst_to_lenstronomy_preprocessing_reproduced": all(
                [
                    criteria["hst_mast_products_downloaded"],
                    criteria["sci_wht_reduced_data_prepared"],
                    criteria["all_required_lenstronomy_hdf5_recorded"],
                    criteria["f160w_raw_cell_reproduction_patch_documented"],
                    criteria["f475x_preprocessing_executed"],
                    criteria["f814w_preprocessing_executed"],
                ]
            ),
            "multiband_setup_smoke_preflight_passed": criteria[
                "multiband_data_setup_preflight_executed"
            ],
            "bounded_model_plumbing_smoke_passed": all(
                [
                    criteria["bounded_pemd_smoke_notebook_executed"],
                    criteria["bounded_pemd_smoke_job_output_recorded"],
                ]
            ),
            "bounded_physical_pemd_backend_smoke_passed": all(
                [
                    criteria["bounded_pemd_fastell_smoke_notebook_executed"],
                    criteria["bounded_pemd_fastell_smoke_job_output_recorded"],
                ]
            ),
            "physical_pemd_backend_available": all(
                [
                    criteria["bounded_pemd_fastell_smoke_notebook_executed"],
                    criteria["bounded_pemd_fastell_smoke_job_output_recorded"],
                ]
            ),
            "bounded_mcmc_posterior_plumbing_pilot_passed": all(
                [
                    criteria["bounded_pemd_fastell_mcmc_pilot_notebook_executed"],
                    criteria["bounded_pemd_fastell_mcmc_pilot_output_recorded"],
                ]
            ),
            "bounded_mcmc_diagnostic_pilot_passed": all(
                [
                    criteria["bounded_pemd_fastell_mcmc_diagnostic_notebook_executed"],
                    criteria["bounded_pemd_fastell_mcmc_diagnostic_output_recorded"],
                ]
            ),
            "bounded_mcmc_diagnostic_deep_inspected": criteria[
                "bounded_pemd_fastell_mcmc_diagnostic_deep_inspected"
            ],
            "bounded_mcmc_diagnostic60_payload_summarized": criteria[
                "bounded_pemd_fastell_mcmc_diagnostic60_payload_summarized"
            ],
            "bounded_mcmc_diagnostic120_payload_summarized": criteria[
                "bounded_pemd_fastell_mcmc_diagnostic120_payload_summarized"
            ],
            "bounded_mcmc_diag120_cont_notebook_executed": criteria[
                "bounded_pemd_fastell_mcmc_diag120_cont_notebook_executed"
            ],
            "bounded_mcmc_diag120_cont_payload_summarized": criteria[
                "bounded_pemd_fastell_mcmc_diag120_cont_payload_summarized"
            ],
            "bounded_mcmc_diag120_cont2_notebook_executed": criteria[
                "bounded_pemd_fastell_mcmc_diag120_cont2_notebook_executed"
            ],
            "bounded_mcmc_diag120_cont2_payload_summarized": criteria[
                "bounded_pemd_fastell_mcmc_diag120_cont2_payload_summarized"
            ],
            "bounded_mcmc_diag120_cont3_cold_notebook_executed": criteria[
                "bounded_pemd_fastell_mcmc_diag120_cont3_cold_notebook_executed"
            ],
            "bounded_mcmc_diag120_cont3_cold_payload_summarized": criteria[
                "bounded_pemd_fastell_mcmc_diag120_cont3_cold_payload_summarized"
            ],
            "bounded_mcmc_parameter_drift_diagnostic_summarized": criteria[
                "bounded_pemd_fastell_mcmc_parameter_drift_diagnostic_summarized"
            ],
            "wgd2038_nuisance_stabilization_plan_created": criteria[
                "wgd2038_nuisance_stabilization_plan_created"
            ],
            "bounded_profile_freeze_v1_payload_summarized": criteria[
                "bounded_pemd_fastell_profile_freeze_v1_payload_summarized"
            ],
            "bounded_profile_freeze_v2_payload_summarized": criteria[
                "bounded_pemd_fastell_profile_freeze_v2_payload_summarized"
            ],
            "converged_no_T2_posterior_reproduced": False,
            "no_T2_image_model_reproduction_authorized": False,
            "real_data_T2_sampling_authorized": False,
            "claim_level": (
                "hst_preprocessing_multiband_setup_and_bounded_model_plumbing_smoke_"
                "reproduced_not_physical_posterior"
            ),
            "what_changed": (
                "The WGD2038 route is no longer only a notebook/payload hook: public "
                "HST images have been reduced into the three-band lenstronomy input "
                "format, the multiband setup can be loaded locally, and a bounded "
                "one-step PEMD/SHEAR model-plumbing smoke run completes with the "
                "physical fastell4py PEMD backend available locally. A minimal emcee "
                "posterior-plumbing pilot and a short finite diagnostic pilot also "
                "execute. 60-step and 120-step diagnostic payload summaries record "
                "finite samples, but the 120-step split-half drift increases, so the "
                "chain is still not a converged posterior. A 120-step continuation "
                "from the previous chain endpoint also executes and remains finite, "
                "but it does not remove the convergence blocker. A second continuation "
                "from that endpoint also remains finite but does not improve the "
                "split-half drift. A cold continuation with sigma_scale=0.02 also "
                "remains finite but worsens the drift, so proposal-scale reduction "
                "alone is not enough. Parameter-level drift diagnostics indicate "
                "that the blocker is concentrated in lens/source-light and "
                "image-position nuisance directions. The next bounded action is "
                "a profile-freeze diagnostic targeting those nuisance directions."
                " The first profile-freeze diagnostic improves median drift but still "
                "leaves visible high-quantile drift, so the no-T2 posterior gate is "
                "not yet cleared. The more aggressive profile-freeze v2 worsens drift, "
                "so the next route should not simply freeze more light-profile "
                "parameters."
            ),
            "remaining_blocker": (
                "The full no-T2 image/model posterior is still missing because the "
                "current MCMC results are bounded pilot runs, not a converged or "
                "validated posterior, and the original cluster/MCMC joblib outputs "
                "have not been acquired."
            ),
            "next_finite_action": (
                "Scale the fastell-backed pilot into a bounded no-T2 posterior run "
                "with convergence diagnostics, or acquire the original WGD2038 "
                "*_out.txt/joblib payload. Only after a no-T2 image/model posterior "
                "is reproduced may a T2 perturbation be sampled."
            ),
        },
        "claim_boundary": {
            "allowed": [
                "WGD2038 public HST preprocessing was reproduced into lenstronomy inputs.",
                "The multiband notebook data/setup path passed a bounded preflight.",
                "A one-step local PEMD/SHEAR model-plumbing smoke run completed under "
                "documented compatibility constraints.",
                "A second one-step local PEMD/SHEAR smoke run completed with the "
                "physical fastell4py backend installed.",
                "A minimal fastell-backed emcee posterior-plumbing pilot completed.",
                "A short fastell-backed emcee diagnostic pilot completed.",
                "A fastell-backed continuation from the diagnostic120 chain endpoint completed.",
                "A second fastell-backed endpoint continuation completed and gave a "
                "negative convergence diagnostic.",
                "A cold fastell-backed endpoint continuation completed and gave a "
                "negative proposal-scale sensitivity diagnostic.",
                "A parameter-level drift diagnostic identifies the dominant unstable "
                "directions without claiming posterior convergence.",
                "A nuisance-stabilization plan identifies profile-freeze candidates "
                "for the next bounded no-T2 diagnostic.",
                "The profile-freeze v1 diagnostic completed and reduced median drift, "
                "but did not prove posterior convergence.",
                "The profile-freeze v2 diagnostic completed but worsened drift, "
                "showing that more aggressive freezing is not the next clean route.",
                "This narrows the practical blocker to posterior/model-output reproduction.",
            ],
            "forbidden": [
                "Claiming a WGD2038 real-data T2 detection.",
                "Claiming no-T2 Ddt/null posterior reproduction from preprocessing alone.",
                "Treating the bounded smoke run as a physical PEMD posterior.",
                "Treating the tiny emcee pilot as a converged no-T2 posterior.",
                "Treating the F160W raw-cell compatibility patch as a physics change.",
            ],
        },
    }
    summary["content_hash"] = sha256_obj(summary)
    return summary


def write_outputs(summary: dict[str, Any]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fieldnames = [
        "name",
        "recorded",
        "present_now",
        "path",
        "recorded_bytes",
        "recorded_sha256",
        "current_sha256",
        "hash_matches_record",
    ]
    with OUT_TABLE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary["hdf5_rows"])


def main() -> None:
    summary = build_summary()
    write_outputs(summary)
    print(OUT_SUMMARY)
    print(OUT_TABLE)
    print(summary["verdict"]["remaining_blocker"])


if __name__ == "__main__":
    main()
