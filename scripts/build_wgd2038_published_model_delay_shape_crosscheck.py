#!/usr/bin/env python3
"""Cross-check WGD2038 observed delays against published model predictions.

This uses the TDCOSMO IX published GLEE and lenstronomy delay predictions, not
the missing posterior payload.  It asks a narrower question: after allowing one
global time-delay scale factor, is the observed WGD2038 delay-vector shape
already compatible with the published no-T2 lens-model delay shape?
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results"
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_published_model_delay_shape_crosscheck_v1"
OUT_TABLE = DERIVED / "wgd2038_published_model_delay_shape_crosscheck_v1.csv"
PAIR_ORDER = ["AB", "AC", "AD"]

PUBLISHED_MODEL_DELAYS_DAYS = {
    "glee_combined_h0_70_flat_lcdm": {
        "AB": -4.4,
        "AC": -9.4,
        "AD": -23.0,
    },
    "lenstronomy_combined_h0_70_flat_lcdm": {
        "AB": -5.0,
        "AC": -10.0,
        "AD": -24.2,
    },
}


def load_result(name: str) -> dict[str, Any]:
    return json.loads((RESULTS / name / "summary.json").read_text(encoding="utf-8"))


def vector_from_map(values: dict[str, float]) -> np.ndarray:
    return np.array([values[pair] for pair in PAIR_ORDER], dtype=float)


def main() -> None:
    observed_smoke = load_result("tau_core_lensing_wgd2038_observed_delay_no_t2_smoke_v1")
    observed = vector_from_map(observed_smoke["published_time_delay_vector"]["values"])
    covariance = np.array(
        observed_smoke["published_time_delay_covariance"]["matrix"], dtype=float
    )
    cov_inv = np.linalg.inv(covariance)

    rows: list[dict[str, Any]] = []
    model_summaries: list[dict[str, Any]] = []
    for model_id, delay_map in PUBLISHED_MODEL_DELAYS_DAYS.items():
        model = vector_from_map(delay_map)
        scale = float((model.T @ cov_inv @ observed) / (model.T @ cov_inv @ model))
        scaled_model = scale * model
        residual = observed - scaled_model
        chi2_scaled = float(residual.T @ cov_inv @ residual)
        chi2_unscaled = float((observed - model).T @ cov_inv @ (observed - model))
        dof_scaled = len(PAIR_ORDER) - 1
        normalized_rmse = float(np.sqrt(chi2_scaled / dof_scaled))
        implied_h0_if_prediction_h0_70 = float(70.0 / scale) if scale != 0 else float("nan")

        for index, pair in enumerate(PAIR_ORDER):
            rows.append(
                {
                    "model_id": model_id,
                    "delay_pair": pair,
                    "published_model_prediction_days_at_h0_70": delay_map[pair],
                    "observed_delay_days": float(observed[index]),
                    "best_scalar_scale": scale,
                    "scaled_model_delay_days": float(scaled_model[index]),
                    "shape_residual_observed_minus_scaled_model_days": float(residual[index]),
                    "implied_h0_if_pure_scale_from_h0_70": implied_h0_if_prediction_h0_70,
                    "uses_missing_posterior_payload": False,
                    "fits_or_samples_t2": False,
                }
            )

        model_summaries.append(
            {
                "model_id": model_id,
                "published_model_prediction_days_at_h0_70": delay_map,
                "best_scalar_scale": scale,
                "implied_h0_if_pure_scale_from_h0_70": implied_h0_if_prediction_h0_70,
                "scaled_model_delay_days": {
                    pair: float(scaled_model[index]) for index, pair in enumerate(PAIR_ORDER)
                },
                "shape_residual_observed_minus_scaled_model_days": {
                    pair: float(residual[index]) for index, pair in enumerate(PAIR_ORDER)
                },
                "chi2_unscaled_against_observed_covariance": chi2_unscaled,
                "chi2_after_best_scalar_against_observed_covariance": chi2_scaled,
                "degrees_of_freedom_after_scalar": dof_scaled,
                "normalized_shape_rmse_sigma_units": normalized_rmse,
            }
        )

    best = min(
        model_summaries,
        key=lambda item: item["chi2_after_best_scalar_against_observed_covariance"],
    )
    summary = {
        "schema": "paper7 WGD2038 published-model delay-shape crosscheck v1",
        "purpose": (
            "Use published TDCOSMO IX GLEE/lenstronomy delay predictions to test "
            "whether the measured WGD2038 delay vector is compatible with the "
            "published no-T2 lens-model delay shape after one global scale."
        ),
        "external_literature_sources": [
            {
                "id": "TDCOSMO_IX_WGD2038",
                "title": (
                    "TDCOSMO. IX. Systematic comparison between lens modelling "
                    "software programs: Time-delay prediction for WGD 2038-4008"
                ),
                "journal_url": "https://www.aanda.org/articles/aa/full_html/2022/11/aa43401-22/aa43401-22.html",
                "arxiv_url": "https://arxiv.org/abs/2202.11101",
                "used_for": [
                    "published combined GLEE delay prediction at H0=70",
                    "published combined lenstronomy delay prediction at H0=70",
                    "delay-pair convention and model-prediction claim boundary",
                ],
            },
            {
                "id": "TDCOSMO_XVI_WGD2038_FIG2",
                "title": (
                    "TDCOSMO. XVI. Measurement of the Hubble Constant from the "
                    "Lensed Quasar WGD 2038-4008"
                ),
                "arxiv_url": "https://arxiv.org/abs/2406.02683",
                "used_for": [
                    "published observed delay vector",
                    "published observed delay covariance",
                ],
            },
        ],
        "observed_delay_source_artifact": (
            "data/derived/repro_results/"
            "tau_core_lensing_wgd2038_observed_delay_no_t2_smoke_v1/summary.json"
        ),
        "pair_order": PAIR_ORDER,
        "published_model_predictions": PUBLISHED_MODEL_DELAYS_DAYS,
        "model_summaries": model_summaries,
        "best_scalar_shape_match": best,
        "verdict": {
            "published_model_delay_shape_crosscheck_created": True,
            "uses_published_model_predictions": True,
            "uses_published_observed_delay_measurement": True,
            "uses_missing_posterior_payload": False,
            "single_scale_shape_residual_present": (
                best["normalized_shape_rmse_sigma_units"] > 1.0
            ),
            "can_apply_des_frozen_score_now": False,
            "real_data_T2_sampling_authorized": False,
            "t2_specific_time_shift_evidence": False,
            "claim_level": "published_model_level_delay_shape_crosscheck_not_T2_evidence",
        },
        "claim_boundary": [
            "This is not a posterior-level WGD score; it uses published summary delay predictions.",
            "The scalar fit tests shape compatibility after a global time-delay scale only.",
            "Model-prediction uncertainties are not fully propagated because the posterior payload is still missing.",
            "No T2 parameter is fitted or sampled.",
        ],
        "next_finite_action": (
            "Use the shape residual to define a WGD holdout score target once a "
            "posterior-level Fermat/delay table is available; until then keep WGD "
            "at published-model-level crosscheck status."
        ),
        "rows": rows,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    with OUT_TABLE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps(summary["verdict"], indent=2, sort_keys=True))
    print(json.dumps(best, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
