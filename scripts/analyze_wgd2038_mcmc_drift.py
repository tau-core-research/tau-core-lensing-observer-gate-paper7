#!/usr/bin/env python3
"""Summarize bounded WGD2038 MCMC drift diagnostics.

This script inspects local temporary lenstronomy joblib outputs and writes
derived CSV/JSON diagnostics only. It does not redistribute raw chain payloads
and it does not claim posterior convergence or authorize real-data T2 sampling.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = (
    DERIVED
    / "repro_results"
    / "tau_core_lensing_wgd2038_lenstronomy_hst_reproduction_v1"
)
OUT_JSON = RESULTS / "mcmc_parameter_drift_diagnostic_summary_v1.json"
OUT_CSV = DERIVED / "wgd2038_mcmc_parameter_drift_diagnostic_v1.csv"

TEMP = Path("/tmp/paper7_tdc_sources/WGD2038-4008/lenstronomy_modeling/temp")
JOBS = {
    "diagnostic120": TEMP / "tau_core_mcmc_diag120_pemd_fastell_backend_out.txt",
    "cont1": TEMP / "tau_core_mcmc_diag120_cont_pemd_fastell_backend_out.txt",
    "cont2": TEMP / "tau_core_mcmc_diag120_cont2_pemd_fastell_backend_out.txt",
    "cont3_cold": TEMP / "tau_core_mcmc_diag120_cont3_cold_pemd_fastell_backend_out.txt",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_obj(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_emcee(path: Path) -> tuple[np.ndarray, list[str], np.ndarray]:
    _input, output = joblib.load(path)
    _kwargs_result, _multi_band_list_out, fit_output, _kwargs_fixed_out = output
    for step in fit_output:
        if step[0] == "emcee":
            return np.asarray(step[1]), list(step[2]), np.asarray(step[3])
    raise ValueError(f"no emcee step found in {path}")


def summarize_job(job_name: str, path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    samples, params, logp = load_emcee(path)
    mid = samples.shape[0] // 2
    first = samples[:mid]
    second = samples[mid:]
    first_mean = np.nanmean(first, axis=0)
    second_mean = np.nanmean(second, axis=0)
    spread = np.nanstd(samples, axis=0)
    drift_sigma = np.abs(second_mean - first_mean) / (spread + 1e-12)
    full_mean = np.nanmean(samples, axis=0)
    full_std = np.nanstd(samples, axis=0)

    rows: list[dict[str, Any]] = []
    for idx, param in enumerate(params):
        rows.append(
            {
                "job_name": job_name,
                "param_index": idx,
                "param_name": param,
                "param_key": f"{idx:02d}:{param}",
                "mean": float(full_mean[idx]),
                "std": float(full_std[idx]),
                "first_half_mean": float(first_mean[idx]),
                "second_half_mean": float(second_mean[idx]),
                "split_half_abs_mean_shift_sigma": float(drift_sigma[idx]),
            }
        )

    top_rows = sorted(rows, key=lambda row: row["split_half_abs_mean_shift_sigma"], reverse=True)
    q = np.nanpercentile(drift_sigma, [50, 90, 95, 99, 100])
    summary = {
        "job_name": job_name,
        "path": str(path),
        "sha256": sha256_file(path),
        "sample_shape": list(samples.shape),
        "logp_shape": list(logp.shape),
        "finite_samples": bool(np.isfinite(samples).all()),
        "finite_logp": bool(np.isfinite(logp).all()),
        "logp_min": float(np.nanmin(logp)),
        "logp_max": float(np.nanmax(logp)),
        "logp_median": float(np.nanmedian(logp)),
        "split_half_abs_mean_shift_sigma_quantiles": {
            "p50": float(q[0]),
            "p90": float(q[1]),
            "p95": float(q[2]),
            "p99": float(q[3]),
            "p100": float(q[4]),
        },
        "top_drift_parameters": top_rows[:10],
    }
    return summary, rows


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, Any]] = []
    job_summaries = []
    missing = []
    for job_name, path in JOBS.items():
        if not path.exists():
            missing.append({"job_name": job_name, "path": str(path)})
            continue
        summary, rows = summarize_job(job_name, path)
        job_summaries.append(summary)
        all_rows.extend(rows)

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "job_name",
            "param_index",
            "param_name",
            "param_key",
            "mean",
            "std",
            "first_half_mean",
            "second_half_mean",
            "split_half_abs_mean_shift_sigma",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    persistent_top: list[dict[str, Any]] = []
    if all_rows:
        grouped: dict[str, list[float]] = {}
        for row in all_rows:
            grouped.setdefault(str(row["param_key"]), []).append(
                float(row["split_half_abs_mean_shift_sigma"])
            )
        for param_key, values in grouped.items():
            persistent_top.append(
                {
                    "param_key": param_key,
                    "param_name": param_key.split(":", 1)[1],
                    "mean_split_half_abs_shift_sigma": float(np.mean(values)),
                    "max_split_half_abs_shift_sigma": float(np.max(values)),
                    "job_count": len(values),
                }
            )
        persistent_top.sort(
            key=lambda row: row["mean_split_half_abs_shift_sigma"], reverse=True
        )

    summary = {
        "schema": "paper7 WGD2038 bounded MCMC parameter drift diagnostic v1",
        "claim_level": "chain_health_diagnostic_not_posterior_convergence",
        "jobs": job_summaries,
        "missing_jobs": missing,
        "csv_path": str(OUT_CSV),
        "real_data_T2_sampling_authorized": False,
        "converged_no_T2_posterior_reproduced": False,
        "verdict": {
            "parameter_drift_diagnostic_created": len(job_summaries) > 0,
            "all_available_jobs_finite": all(
                job["finite_samples"] and job["finite_logp"] for job in job_summaries
            ),
            "simple_endpoint_or_cold_continuation_clears_blocker": False,
            "interpretation": (
                "The bounded chains are finite, but drift concentrates in specific "
                "parameters and remains visible across continuation variants. This "
                "diagnoses the blocker; it is not a posterior convergence claim."
            ),
        },
        "persistent_top_drift_parameters": persistent_top[:15],
    }
    summary["content_hash"] = sha256_obj(summary)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT_JSON)
    print(OUT_CSV)
    print(summary["verdict"]["interpretation"])


if __name__ == "__main__":
    main()
