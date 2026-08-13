#!/usr/bin/env python3
"""Freeze the admissible collective LOS completion after the arc-template audit."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data/derived/repro_results"
STRIDES = (
    DERIVED
    / "tau_core_lensing_desj0408_strides_los_morphology_v1/summary.json"
)
ARC = (
    DERIVED
    / "tau_core_lensing_desj0408_local_cubic_f814w_arc_template_v1/summary.json"
)
OUT_DIR = (
    DERIVED
    / "tau_core_lensing_desj0408_collective_los_completion_decision_v1"
)
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def main() -> None:
    strides = json.loads(STRIDES.read_text(encoding="utf-8"))
    arc = json.loads(ARC.read_text(encoding="utf-8"))

    # Buckley-Geer et al. (2020), arXiv:2003.12117, Sec. 7 and conclusion.
    kappa_median_interval = [-0.05, -0.04]
    kappa_width = 0.03
    h0_factor_interval = [
        1.0 - kappa_median_interval[1],
        1.0 - kappa_median_interval[0],
    ]

    summary = {
        "schema": "paper7 DES J0408 collective LOS completion decision v1",
        "source": {
            "arxiv": "2003.12117",
            "section": "external convergence inference and conclusion",
            "method": (
                "weighted galaxy counts matched to ray-traced Millennium "
                "Simulation lines of sight"
            ),
        },
        "explicit_multiplane_perturbers": ["G3", "G4", "G5", "G6"],
        "subthreshold_population_role": (
            "collective external convergence distribution, not 178 "
            "independently summed untruncated halos"
        ),
        "reported_kappa_ext_median_interval": kappa_median_interval,
        "reported_kappa_ext_approximate_width": kappa_width,
        "reported_group_removal_median_change_upper_bound": 0.01,
        "h0_relation": "H0=H0_model*(1-kappa_ext)",
        "implied_h0_multiplicative_factor_interval_at_reported_median": (
            h0_factor_interval
        ),
        "mass_sheet_transform": {
            "kappa_lambda": "lambda*kappa+(1-lambda)",
            "beta_lambda": "lambda*beta",
            "relative_image_mapping_invariant_after_source_rescaling": True,
            "time_delays_scale_with_lambda": True,
        },
        "spectroscopic_completeness_fraction": strides[
            "reported_spectroscopic_completeness"
        ]["fraction"],
        "local_point_mass_arc_completion_result": arc["verdict"],
        "local_point_mass_fixed_amplitude_sse_reduction": arc[
            "fixed_amplitude_fractional_unweighted_sse_reduction"
        ],
        "individual_truncated_halo_completion_identified_from_current_payload": False,
        "new_f814w_spatial_template_authorized_from_kappa_ext": False,
        "kappa_ext_time_delay_nuisance_required": True,
        "tau_specific_information_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "COLLECTIVE_LOS_COMPLETION_IS_KAPPA_EXT_NUISANCE__"
            "NO_NEW_F814W_TEMPLATE__TIME_DELAY_SCALE_ONLY"
        ),
        "claim_boundary": (
            "The published collective LOS completion is a standard external-"
            "convergence distribution. Under the mass-sheet degeneracy it "
            "cannot be identified as a new spatial arc template from the same "
            "imaging data after source rescaling. It must enter any later "
            "time-delay analysis as a standard nuisance prior. This supplies "
            "neither a Tau-specific residual nor observer-time distortion."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 collective LOS completion decision v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        "The finite standard completion is explicit G3--G6 multi-plane "
        "structure plus the published collective external-convergence "
        "distribution. The latter is a time-delay/H0 nuisance, not another "
        "independently scoreable F814W residual template.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
