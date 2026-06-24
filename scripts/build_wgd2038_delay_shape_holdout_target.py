#!/usr/bin/env python3
"""Freeze a WGD2038 delay-shape target from published summary products.

This is deliberately not a T2 fit and not a posterior-level score.  It freezes
the residual direction left after matching the published TDCOSMO IX WGD2038
no-T2 delay prediction to the TDCOSMO XVI observed delay vector by one scalar.
Future posterior-level WGD products can then be compared against this target
without choosing the shape direction after seeing the posterior-level result.
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
SOURCE_RESULT = RESULTS / "tau_core_lensing_wgd2038_published_model_delay_shape_crosscheck_v1"
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_delay_shape_holdout_target_v1"
OUT_TABLE = DERIVED / "wgd2038_delay_shape_holdout_target_v1.csv"


def load_result(name: str) -> dict[str, Any]:
    return json.loads((RESULTS / name / "summary.json").read_text(encoding="utf-8"))


def vector_from_map(values: dict[str, float], order: list[str]) -> np.ndarray:
    return np.array([values[pair] for pair in order], dtype=float)


def main() -> None:
    crosscheck = json.loads((SOURCE_RESULT / "summary.json").read_text(encoding="utf-8"))
    observed_smoke = load_result("tau_core_lensing_wgd2038_observed_delay_no_t2_smoke_v1")

    pair_order = list(crosscheck["pair_order"])
    covariance = np.array(
        observed_smoke["published_time_delay_covariance"]["matrix"], dtype=float
    )
    cov_inv = np.linalg.inv(covariance)

    best = crosscheck["best_scalar_shape_match"]
    observed = vector_from_map(
        observed_smoke["published_time_delay_vector"]["values"], pair_order
    )
    scaled_model = vector_from_map(best["scaled_model_delay_days"], pair_order)
    residual = observed - scaled_model

    covariance_metric_norm = float(np.sqrt(residual.T @ cov_inv @ residual))
    euclidean_norm_days = float(np.linalg.norm(residual))
    euclidean_unit = residual / euclidean_norm_days

    rows: list[dict[str, Any]] = []
    for index, pair in enumerate(pair_order):
        rows.append(
            {
                "target_id": "wgd2038_published_model_delay_shape_target_v1",
                "basis": "publication_A_centered_Delta_t_AX_days",
                "delay_pair": pair,
                "observed_delay_days": float(observed[index]),
                "scaled_published_model_delay_days": float(scaled_model[index]),
                "target_residual_days": float(residual[index]),
                "target_euclidean_unit_component": float(euclidean_unit[index]),
                "covariance_metric_norm_sigma_units": covariance_metric_norm,
                "source_model_id": best["model_id"],
                "source_claim_level": crosscheck["verdict"]["claim_level"],
                "fits_or_samples_t2": False,
                "posterior_level_score": False,
            }
        )

    summary = {
        "schema": "paper7 WGD2038 delay-shape holdout target v1",
        "purpose": (
            "Freeze the published-model WGD2038 residual direction before any "
            "posterior-level WGD score is available.  Future posterior/Fermat "
            "products can be tested against this predeclared delay-shape target."
        ),
        "source_artifacts": {
            "published_model_delay_shape_crosscheck": (
                "data/derived/repro_results/"
                "tau_core_lensing_wgd2038_published_model_delay_shape_crosscheck_v1/"
                "summary.json"
            ),
            "observed_delay_vector_and_covariance": (
                "data/derived/repro_results/"
                "tau_core_lensing_wgd2038_observed_delay_no_t2_smoke_v1/summary.json"
            ),
        },
        "external_literature_sources": crosscheck["external_literature_sources"],
        "target_definition": {
            "target_id": "wgd2038_published_model_delay_shape_target_v1",
            "basis": "publication_A_centered_Delta_t_AX_days",
            "delay_pair_order": pair_order,
            "selected_published_model_id": best["model_id"],
            "selection_rule": (
                "Choose the published TDCOSMO IX model with the lowest chi2 after "
                "one covariance-weighted scalar match to the TDCOSMO XVI observed "
                "delay vector."
            ),
            "scalar_match_formula": (
                "s = (m^T C^{-1} d_obs) / (m^T C^{-1} m), "
                "r_target = d_obs - s m"
            ),
            "future_shape_cosine_formula": (
                "cos_C(r, r_target) = (r^T C^{-1} r_target) / "
                "sqrt((r^T C^{-1} r)(r_target^T C^{-1} r_target))"
            ),
            "future_score_allowed_only_if": [
                "a posterior-level or published WGD Fermat/delay table is available",
                "the table uses or is converted into the same A-centered delay convention",
                "model-prediction uncertainty handling is explicitly declared",
                "the comparison is run without changing this target direction",
            ],
        },
        "target_values": {
            "observed_delay_days": {
                pair: float(observed[index]) for index, pair in enumerate(pair_order)
            },
            "scaled_published_model_delay_days": {
                pair: float(scaled_model[index]) for index, pair in enumerate(pair_order)
            },
            "target_residual_days": {
                pair: float(residual[index]) for index, pair in enumerate(pair_order)
            },
            "target_euclidean_unit_direction": {
                pair: float(euclidean_unit[index]) for index, pair in enumerate(pair_order)
            },
            "covariance_metric_norm_sigma_units": covariance_metric_norm,
            "normalized_shape_rmse_sigma_units": best["normalized_shape_rmse_sigma_units"],
            "best_scalar_scale": best["best_scalar_scale"],
            "implied_h0_if_pure_scale_from_h0_70": best[
                "implied_h0_if_pure_scale_from_h0_70"
            ],
        },
        "verdict": {
            "wgd2038_delay_shape_holdout_target_created": True,
            "target_frozen_before_posterior_level_wgd_score": True,
            "uses_published_model_predictions": True,
            "uses_published_observed_delay_measurement": True,
            "uses_missing_posterior_payload": False,
            "posterior_level_score": False,
            "endpoint_blind": False,
            "can_apply_des_frozen_score_now": False,
            "real_data_T2_sampling_authorized": False,
            "t2_specific_time_shift_evidence": False,
            "claim_level": "predeclared_published_model_shape_target_not_T2_evidence",
        },
        "claim_boundary": [
            "The target is defined from WGD2038 published observed delays and published model predictions, so it is not endpoint-blind.",
            "It is a predeclared future comparison target, not an evidence-grade no-T2 reproduction.",
            "It does not fit or sample a T2 parameter.",
            "A posterior-level WGD Fermat/delay table is still required before a real holdout score can be run.",
        ],
        "next_finite_action": (
            "Obtain or reconstruct a posterior-level WGD delay/Fermat table and "
            "evaluate its no-T2 residual vector against this frozen covariance-metric "
            "shape target."
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
    print(json.dumps(summary["target_values"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
