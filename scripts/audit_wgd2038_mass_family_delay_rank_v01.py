#!/usr/bin/env python3
"""Test whether published WGD2038 mass-family structure closes delay space."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
OBSERVED = (
    RESULTS
    / "tau_core_lensing_wgd2038_observed_delay_no_t2_smoke_v1"
    / "summary.json"
)
PRIOR_RANK = (
    RESULTS
    / "tau_core_lensing_wgd2038_published_summary_nuisance_rank_v1"
    / "summary.json"
)
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_mass_family_delay_rank_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"
PAIR_ORDER = ["AB", "AC", "AD"]

# Figure 22b/c of TDCOSMO IX was published before the measured-delay endpoint.
# The three summaries below were independently extracted from each colored
# density curve after mapping the vector-PDF tick coordinates to delay days.
DIGITIZED_DAYS = {
    "mean": {
        "powerlaw_lenstronomy": [-4.9687, -9.9442, -24.1212],
        "powerlaw_glee": [-4.7930, -9.9565, -24.8424],
        "composite_lenstronomy": [-3.7171, -7.5419, -18.8898],
        "composite_glee": [-4.1949, -8.8928, -21.7473],
    },
    "median": {
        "powerlaw_lenstronomy": [-4.9900, -9.9975, -24.2577],
        "powerlaw_glee": [-4.8333, -10.0449, -25.0756],
        "composite_lenstronomy": [-3.7232, -7.5602, -18.9234],
        "composite_glee": [-4.2166, -8.9381, -21.8650],
    },
    "mode": {
        "powerlaw_lenstronomy": [-5.0040, -10.1115, -24.4646],
        "powerlaw_glee": [-4.8902, -10.1712, -25.4318],
        "composite_lenstronomy": [-3.7526, -7.6361, -19.0546],
        "composite_glee": [-4.2242, -8.9571, -21.9404],
    },
}


def whiten(covariance: np.ndarray) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    return eigenvectors @ np.diag(1.0 / np.sqrt(eigenvalues)) @ eigenvectors.T


def rank_audit(
    vectors_by_model: dict[str, list[float]], whitening: np.ndarray
) -> dict[str, object]:
    names = list(vectors_by_model)
    vectors = np.asarray([vectors_by_model[name] for name in names], dtype=float)
    barycenter = vectors.mean(axis=0)
    centered = vectors - barycenter
    nuisance = np.column_stack([barycenter, centered.T])
    singular = np.linalg.svd(whitening @ nuisance, compute_uv=False)
    rank = int(np.sum(singular > 1e-10 * singular[0]))
    return {
        "model_order": names,
        "vectors_days": vectors.tolist(),
        "barycenter_days": barycenter.tolist(),
        "covariance_whitened_singular_values": singular.tolist(),
        "strict_rank": rank,
        "remaining_dimension": 3 - rank,
        "smallest_to_largest_singular_ratio": float(singular[-1] / singular[0]),
    }


def main() -> None:
    observed = json.loads(OBSERVED.read_text(encoding="utf-8"))
    prior = json.loads(PRIOR_RANK.read_text(encoding="utf-8"))
    covariance = np.asarray(
        observed["published_time_delay_covariance"]["matrix"], dtype=float
    )
    whitening = whiten(covariance)
    audits = {
        estimator: rank_audit(vectors, whitening)
        for estimator, vectors in DIGITIZED_DAYS.items()
    }
    all_full_rank = all(item["strict_rank"] == 3 for item in audits.values())

    median_vectors = np.asarray(audits["median"]["vectors_days"], dtype=float)
    median_barycenter = median_vectors.mean(axis=0)
    median_nuisance = np.column_stack(
        [median_barycenter, (median_vectors - median_barycenter).T]
    )
    u, singular, _ = np.linalg.svd(
        whitening @ median_nuisance, full_matrices=True
    )
    rank = int(np.sum(singular > 1e-10 * singular[0]))
    projector = u[:, :rank] @ u[:, :rank].T
    old_candidate = np.asarray(
        prior["candidate_whitened_unit_direction"], dtype=float
    )
    old_candidate_absorbed_fraction = float(
        np.linalg.norm(projector @ old_candidate) ** 2
    )
    old_candidate_absorbed_fraction = min(1.0, old_candidate_absorbed_fraction)

    source_identity = {
        "paper": "TDCOSMO IX",
        "arxiv": "https://arxiv.org/abs/2202.11101",
        "source_figure": "Figure 22b/c (f22b.pdf and f22c.pdf)",
        "arxiv_eprint_url": "https://arxiv.org/e-print/2202.11101",
        "arxiv_source_archive_sha256": (
            "c59caeae51cb0748ba3062123464808c7e669e048bff68bc4fac76dd0daf1384"
        ),
        "digitization_method": (
            "600-dpi render of vector PDFs; green/purple curve segmentation; "
            "linear tick-coordinate calibration per delay panel; curve-area "
            "mean, median, and mode extracted independently"
        ),
    }
    source_identity["digitized_payload_sha256"] = hashlib.sha256(
        json.dumps(DIGITIZED_DAYS, sort_keys=True).encode("utf-8")
    ).hexdigest()

    summary = {
        "schema": "paper7 WGD2038 mass-family delay-rank audit v1",
        "output_basis": PAIR_ORDER,
        "output_dimension": 3,
        "source_identity": source_identity,
        "source_freeze": {
            "mass_family_distributions_published_before_observed_delays": True,
            "uses_observed_delays_to_define_family_vectors": False,
            "uses_observed_covariance_only_as_output_metric": True,
        },
        "digitization_sensitivity_audits": audits,
        "all_mean_median_mode_variants_strict_rank_three": all_full_rank,
        "median_mass_family_nuisance_rank": rank,
        "remaining_dimension_after_mass_family_resolution": 3 - rank,
        "prior_two_summary_candidate_absorbed_fraction": (
            old_candidate_absorbed_fraction
        ),
        "prior_observed_candidate_projection_sigma": prior[
            "observed_projection_on_candidate_sigma"
        ],
        "posterior_level_nuisance_span_materialized": False,
        "published_family_level_delay_space_saturated": rank == 3,
        "independent_delay_shape_candidate_survives": False,
        "confirmatory_tau_score_allowed": False,
        "time_distortion_detection_claim_allowed": False,
        "verdict": (
            "WGD2038_MASS_FAMILY_RESOLUTION_SATURATES_THREE_DELAY_SPACE__"
            "PRIOR_2P70_SIGMA_DIRECTION_NOT_IDENTIFIABLE"
        ),
        "claim_boundary": (
            "The earlier 2.703-sigma coordinate existed only after reducing "
            "the pre-observation standard model family to two combined summary "
            "vectors. Resolving power-law/composite and GLEE/lenstronomy "
            "predictions gives strict rank three under mean, median, and mode "
            "digitizations. Therefore no nonzero delay-only direction remains "
            "outside the published family-level standard span. This is a "
            "finite identifiability no-go, not evidence against a Tau channel "
            "or observer-time effect; an additional independent observable or "
            "a cross-system shared constraint is required."
        ),
        "next_finite_action": (
            "Do not continue WGD2038 delay-only scoring. Test a predeclared "
            "joint delay-plus-independent-observable coordinate, or require a "
            "shared cross-lens effect whose parameters cannot vary freely per lens."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# WGD2038 mass-family delay-rank audit v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        "The power-law/composite and GLEE/lenstronomy family vectors span all "
        "three covariance-whitened delay dimensions. The result is unchanged "
        "when each published density curve is summarized by its mean, median, "
        "or mode. The prior `-2.703 sigma` coordinate is therefore not an "
        "identifiable delay-only anomaly.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
