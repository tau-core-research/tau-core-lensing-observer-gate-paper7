#!/usr/bin/env python3
"""Audit the source-frozen WGD2038 published-summary delay nuisance rank."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
CROSSCHECK = (
    RESULTS
    / "tau_core_lensing_wgd2038_published_model_delay_shape_crosscheck_v1"
    / "summary.json"
)
OBSERVED = (
    RESULTS
    / "tau_core_lensing_wgd2038_observed_delay_no_t2_smoke_v1"
    / "summary.json"
)
OUT_DIR = (
    RESULTS
    / "tau_core_lensing_wgd2038_published_summary_nuisance_rank_v1"
)
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def vector(values: dict[str, float], order: list[str]) -> np.ndarray:
    return np.asarray([values[key] for key in order], dtype=float)


def main() -> None:
    crosscheck = json.loads(CROSSCHECK.read_text(encoding="utf-8"))
    observed_payload = json.loads(OBSERVED.read_text(encoding="utf-8"))
    order = list(crosscheck["pair_order"])
    predictions = crosscheck["published_model_predictions"]
    glee = vector(predictions["glee_combined_h0_70_flat_lcdm"], order)
    lenstronomy = vector(
        predictions["lenstronomy_combined_h0_70_flat_lcdm"], order
    )
    observed = vector(
        observed_payload["published_time_delay_vector"]["values"], order
    )
    covariance = np.asarray(
        observed_payload["published_time_delay_covariance"]["matrix"],
        dtype=float,
    )

    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    whitening = (
        eigenvectors
        @ np.diag(1.0 / np.sqrt(eigenvalues))
        @ eigenvectors.T
    )
    common_scale = 0.5 * (glee + lenstronomy)
    software_difference = lenstronomy - glee
    raw_nuisance = np.column_stack([common_scale, software_difference])
    whitened_nuisance = whitening @ raw_nuisance
    u, singular, _ = np.linalg.svd(whitened_nuisance, full_matrices=True)
    rank = int(np.sum(singular > 1e-10 * singular[0]))
    projector = u[:, :rank] @ u[:, :rank].T
    residual_projector = np.eye(3) - projector
    whitened_observed = whitening @ observed
    residualized = residual_projector @ whitened_observed
    residualized_norm = float(np.linalg.norm(residualized))
    candidate_direction = u[:, rank]
    signed_coordinate = float(candidate_direction @ whitened_observed)

    summary = {
        "schema": "paper7 WGD2038 published-summary nuisance-rank audit v1",
        "output_basis": order,
        "output_dimension": 3,
        "source_freeze": {
            "model_predictions_frozen_before_observed_delays": True,
            "common_scale_role": "H0/kappa_ext/internal-MST shared scale",
            "software_difference_role": "GLEE-vs-lenstronomy combined-model shape",
            "uses_observed_delays_to_select_nuisance_basis": False,
        },
        "published_model_vectors_days": {
            "glee": glee.tolist(),
            "lenstronomy": lenstronomy.tolist(),
            "common_scale": common_scale.tolist(),
            "software_difference": software_difference.tolist(),
        },
        "covariance_whitened_nuisance_singular_values": singular.tolist(),
        "published_summary_nuisance_rank": rank,
        "remaining_published_summary_dimension": 3 - rank,
        "candidate_whitened_unit_direction": candidate_direction.tolist(),
        "observed_projection_on_candidate_sigma": signed_coordinate,
        "observed_residualized_norm_sigma": residualized_norm,
        "candidate_direction_materialized_before_endpoint_projection": True,
        "posterior_level_nuisance_span_materialized": False,
        "model_family_resolved_vectors_materialized": False,
        "published_summary_exploratory_score_allowed": True,
        "confirmatory_tau_score_allowed": False,
        "tau_specific_information_materialized": False,
        "time_distortion_detection_claim_allowed": False,
        "verdict": (
            "WGD2038_PUBLISHED_SUMMARY_LEAVES_ONE_DELAY_SHAPE_DIRECTION__"
            "OBSERVED_PROJECTION_EXPLORATORY_ONLY"
        ),
        "claim_boundary": (
            "The two pre-observation combined model summaries span a rank-two "
            "standard subspace in the three-delay output and leave one "
            "covariance-whitened direction. The observed projection is a "
            "published-summary diagnostic only: absent posterior samples and "
            "mass-family-resolved delay vectors, the complete nuisance span is "
            "unknown and no Tau/time attribution is allowed."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# WGD2038 published-summary nuisance-rank audit v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        f"The frozen summary nuisance rank is `{rank}` in dimension three. "
        f"The later observed vector projects by `{signed_coordinate:.3f} sigma` "
        "onto the remaining direction. This is exploratory because the "
        "posterior-level and mass-family-resolved nuisance span is unavailable.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
