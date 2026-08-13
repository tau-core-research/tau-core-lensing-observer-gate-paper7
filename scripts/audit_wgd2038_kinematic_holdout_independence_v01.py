#!/usr/bin/env python3
"""Audit whether later WGD2038 kinematics adds an independent fourth output."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
FAMILY_RANK = (
    RESULTS
    / "tau_core_lensing_wgd2038_mass_family_delay_rank_v1"
    / "summary.json"
)
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_kinematic_holdout_independence_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def main() -> None:
    family_rank = json.loads(FAMILY_RANK.read_text(encoding="utf-8"))
    measurements = [
        {
            "id": "GMOS_S_PRIMARY",
            "value_km_s": 296.0,
            "sigma_km_s": 19.0,
            "used_in_frozen_tdcosmo_ix_delay_predictions": True,
        },
        {
            "id": "GMOS_S_SECONDARY",
            "value_km_s": 303.0,
            "sigma_km_s": 24.0,
            "used_in_frozen_tdcosmo_ix_delay_predictions": True,
        },
        {
            "id": "VLT_XSHOOTER_HOLDOUT",
            "value_km_s": 299.0,
            "sigma_km_s": 12.0,
            "used_in_frozen_tdcosmo_ix_delay_predictions": False,
        },
    ]
    values = np.asarray([item["value_km_s"] for item in measurements])
    errors = np.asarray([item["sigma_km_s"] for item in measurements])
    weights = 1.0 / errors**2
    combined = float(np.sum(weights * values) / np.sum(weights))
    combined_error = float(1.0 / np.sqrt(np.sum(weights)))
    chi2 = float(np.sum(((values - combined) / errors) ** 2))
    primary_holdout_difference_sigma = float(
        (values[2] - values[0]) / np.sqrt(errors[2] ** 2 + errors[0] ** 2)
    )

    summary = {
        "schema": "paper7 WGD2038 kinematic-holdout independence audit v1",
        "sources": [
            {
                "id": "TDCOSMO_IX",
                "url": "https://arxiv.org/abs/2202.11101",
                "used_for": (
                    "GMOS-S 296+/-19 km/s aperture dispersion and explicit "
                    "statement that it was used in the frozen lens predictions"
                ),
            },
            {
                "id": "MELO_2021",
                "url": "https://arxiv.org/abs/2110.01575",
                "used_for": (
                    "later X-Shooter 299+/-12 km/s dispersion and the reported "
                    "GMOS-S 303+/-24 km/s crosscheck"
                ),
            },
        ],
        "measurements": measurements,
        "weighted_common_dispersion_km_s": combined,
        "weighted_common_dispersion_sigma_km_s": combined_error,
        "common_value_chi2": chi2,
        "common_value_degrees_of_freedom": 2,
        "xshooter_minus_primary_gmos_sigma": primary_holdout_difference_sigma,
        "measurement_level_independent_observation": True,
        "terminal_type_independent_of_prior_kinematics": False,
        "same_aperture_averaged_velocity_dispersion_terminal": True,
        "published_delay_vectors_already_conditioned_on_gmos_kinematics": True,
        "joint_delay_kinematic_covariance_publicly_materialized": False,
        "can_append_xshooter_as_naive_fourth_coordinate": False,
        "mass_family_delay_rank_before_kinematic_holdout": family_rank[
            "median_mass_family_nuisance_rank"
        ],
        "independent_tau_or_time_coordinate_materialized": False,
        "confirmatory_tau_score_allowed": False,
        "verdict": (
            "XSHOOTER_CONFIRMS_FROZEN_WGD_KINEMATIC_TERMINAL__"
            "DOES_NOT_SUPPLY_AN_INDEPENDENT_FOURTH_READOUT"
        ),
        "claim_boundary": (
            "The later X-Shooter spectrum is an independent observation but "
            "not an independent terminal type: it refines the same integrated "
            "stellar-dispersion functional already used to condition the "
            "published delay predictions. Its 0.13-sigma agreement with the "
            "primary GMOS-S value supplies a standard consistency check, not "
            "an extra delay-orthogonal Tau coordinate. Appending it without an "
            "unconditioned model ensemble and joint covariance would double count."
        ),
        "next_finite_action": (
            "Require spatially resolved kinematic shape, a genuinely distinct "
            "lensing observable, or a shared cross-lens relation. Do not append "
            "another integrated dispersion measurement to conditioned delays."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# WGD2038 kinematic-holdout independence audit v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        f"The X-Shooter value differs from the frozen primary GMOS-S value by "
        f"`{primary_holdout_difference_sigma:.3f} sigma`. It independently "
        "confirms the same integrated kinematic terminal, but it cannot be "
        "appended as a fourth coordinate to delay predictions already "
        "conditioned on GMOS-S kinematics.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
