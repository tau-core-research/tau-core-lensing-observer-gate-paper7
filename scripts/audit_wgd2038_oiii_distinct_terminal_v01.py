#!/usr/bin/env python3
"""Materialize WGD2038 narrow-line flux ratios as a distinct terminal."""

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
KINEMATIC = (
    RESULTS
    / "tau_core_lensing_wgd2038_kinematic_holdout_independence_v1"
    / "summary.json"
)
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_oiii_distinct_terminal_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"
RATIO_ORDER = ["B_over_A", "C_over_A", "D_over_A"]


def main() -> None:
    family_rank = json.loads(FAMILY_RANK.read_text(encoding="utf-8"))
    kinematic = json.loads(KINEMATIC.read_text(encoding="utf-8"))
    observed = np.asarray([1.16, 0.92, 0.46], dtype=float)
    observed_sigma = np.asarray([0.02, 0.02, 0.01], dtype=float)
    smooth_model = np.asarray([1.21, 0.99, 0.46], dtype=float)
    smooth_model_sigma = np.asarray([0.01, 0.10, 0.07], dtype=float)
    residual = observed - smooth_model
    diagonal_sigma = np.sqrt(observed_sigma**2 + smooth_model_sigma**2)
    standardized = residual / diagonal_sigma
    diagonal_chi2 = float(np.sum(standardized**2))

    rows = []
    for index, ratio in enumerate(RATIO_ORDER):
        rows.append(
            {
                "ratio": ratio,
                "observed_oiii_ratio": float(observed[index]),
                "observed_sigma": float(observed_sigma[index]),
                "position_only_smooth_model_ratio": float(smooth_model[index]),
                "smooth_model_sigma": float(smooth_model_sigma[index]),
                "observed_minus_model": float(residual[index]),
                "diagonal_standardized_residual_sigma": float(
                    standardized[index]
                ),
            }
        )

    summary = {
        "schema": "paper7 WGD2038 OIII distinct-terminal audit v1",
        "source": {
            "title": (
                "Double dark matter vision: twice the number of compact-source "
                "lenses with narrow-line lensing and the WFC3 grism"
            ),
            "journal_url": (
                "https://academic.oup.com/mnras/article/492/4/5314/5686725"
            ),
            "source_table": "Table 2, WGD 2038-4008 rows",
            "source_role": (
                "published OIII ratios and smooth position-only macro-model ratios"
            ),
        },
        "ratio_basis": RATIO_ORDER,
        "rows": rows,
        "diagonal_combined_chi2": diagonal_chi2,
        "diagonal_degrees_of_freedom": 3,
        "largest_absolute_component_sigma": float(
            np.max(np.abs(standardized))
        ),
        "largest_component": RATIO_ORDER[int(np.argmax(np.abs(standardized)))],
        "pre_observed_delay_publication": True,
        "excluded_from_tdcosmo_ix_lens_constraints": True,
        "distinct_from_time_delay_terminal": True,
        "distinct_from_integrated_stellar_kinematic_terminal": True,
        "measurement_covariance_materialized": False,
        "joint_delay_flux_model_ensemble_materialized": False,
        "standard_flux_specific_nuisances_fully_marginalized": False,
        "standard_flux_specific_nuisances": [
            "low-mass subhalos and line-of-sight halos",
            "higher-order main-deflector multipoles",
            "finite narrow-line source size",
            "macro-model and astrometric uncertainty",
        ],
        "delay_output_rank_before_oiii": family_rank[
            "median_mass_family_nuisance_rank"
        ],
        "prior_integrated_kinematic_candidate_was_distinct_terminal": kinematic[
            "terminal_type_independent_of_prior_kinematics"
        ],
        "distinct_fourth_terminal_type_materialized": True,
        "tau_specific_coordinate_materialized": False,
        "confirmatory_tau_score_allowed": False,
        "time_distortion_detection_claim_allowed": False,
        "verdict": (
            "WGD2038_OIII_MATERIALIZES_A_DISTINCT_AMPLITUDE_TERMINAL__"
            "B_OVER_A_HAS_2P24_SIGMA_SMOOTH_MODEL_TENSION__"
            "STANDARD_SUBSTRUCTURE_COMPLETION_REQUIRED"
        ),
        "claim_boundary": (
            "Unlike the later integrated velocity-dispersion measurement, the "
            "OIII ratios are a genuinely distinct terminal and were excluded "
            "from the TDCOSMO IX delay-model constraints. The B/A ratio differs "
            "from the position-only smooth macro-model by about 2.24 diagonal "
            "sigma. This is not Tau or observer-time evidence: the published "
            "table does not supply the full ratio covariance or a joint "
            "delay-flux ensemble, and standard substructure, multipoles, and "
            "finite-source effects have not been marginalized."
        ),
        "next_finite_action": (
            "Import or reconstruct a source-frozen standard flux-ratio ensemble "
            "including substructure and multipoles, then test whether any joint "
            "delay-plus-OIII coordinate survives. Do not fit a Tau template to "
            "the current three ratios."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# WGD2038 OIII distinct-terminal audit v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        "The narrow-line flux ratios provide the first public WGD2038 terminal "
        "that is distinct from both delays and integrated stellar kinematics. "
        f"The largest diagonal smooth-model residual is "
        f"`{summary['largest_absolute_component_sigma']:.3f} sigma` in "
        f"`{summary['largest_component']}`. Standard flux-specific nuisance "
        "completion is mandatory before any Tau interpretation.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
