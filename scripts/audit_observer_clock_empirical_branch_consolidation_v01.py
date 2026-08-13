#!/usr/bin/env python3
"""Consolidate the finite Paper 7 observer-clock empirical branch."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
OUT_DIR = RESULTS / (
    "tau_core_lensing_observer_clock_empirical_branch_consolidation_v1"
)


def load(name: str) -> dict:
    return json.loads((RESULTS / name / "summary.json").read_text())


def main() -> None:
    des = load("tau_core_lensing_desj0408_ab_correlated_clock_null_v1")
    he = load("tau_core_lensing_he0435_bc_relative_clock_rate_v1")
    blg081 = load(
        "tau_core_lensing_ogle2004_blg081_finite_tangent_clock_null_v1"
    )
    replacement = load(
        "tau_core_lensing_ogle_replacement_same_source_clock_candidates_v1"
    )
    blg390 = load(
        "tau_core_lensing_ogle2004_blg390_clock_robustness_grid_v1"
    )
    kmt1194 = load(
        "tau_core_lensing_kmt2016_blg1194_ogle_template_clock_transfer_v1"
    )

    blg103 = next(
        row for row in replacement["events"] if row["event"] == "2002-BLG-103"
    )
    tests = [
        {
            "geometry": "differential_multiple_image",
            "target": "DES J0408 A/B",
            "result": "calibrated_null",
            "rate_p_value": des["pooled_rate_p_value"],
            "improvement_p_value": des["pooled_improvement_p_value"],
        },
        {
            "geometry": "differential_multiple_image",
            "target": "HE 0435 B/C",
            "result": "independent_calibrated_null",
            "rate_p_value": he["official_mock_null"][
                "empirical_two_sided_rate_p_value"
            ],
            "improvement_p_value": he["official_mock_null"][
                "empirical_improvement_p_value"
            ],
        },
        {
            "geometry": "same_source_local_microlensing",
            "target": "OGLE-2004-BLG-081",
            "result": "shape_conditioned_null",
            "epsilon": blg081["observed_epsilon"],
            "delta_chi2": blg081["observed_delta_chi2"],
        },
        {
            "geometry": "same_source_local_microlensing",
            "target": "OGLE-2002-BLG-103",
            "result": "shape_conditioned_null",
            "epsilon": blg103["conditional_clock_epsilon"],
            "delta_chi2": blg103["conditional_clock_delta_chi2"],
        },
        {
            "geometry": "same_source_local_microlensing",
            "target": "OGLE-2004-BLG-390",
            "result": "sign_unstable_candidate_rejected",
            "epsilon_range": blg390["epsilon_range_among_passing"],
            "sign_stable": blg390["passing_sign_stable"],
        },
        {
            "geometry": "same_source_local_microlensing",
            "target": "KMT-2016-BLG-1194",
            "result": "independent_source_template_null",
            "epsilon": kmt1194["best_epsilon"],
            "site_error_rescaled_delta_chi2": kmt1194[
                "best_site_error_rescaled_delta_chi2"
            ],
        },
    ]
    positive = [
        row
        for row in tests
        if row["result"] not in {
            "calibrated_null",
            "independent_calibrated_null",
            "shape_conditioned_null",
            "sign_unstable_candidate_rejected",
            "independent_source_template_null",
        }
    ]
    result = {
        "schema": "Paper 7 observer-clock empirical branch consolidation v1",
        "tested_hypothesis_class": (
            "A directly identifiable scalar clock-rate deformation that is "
            "either constant between resolved image paths or localized by the "
            "standard scalar microlensing strength of one periodic source."
        ),
        "tests": tests,
        "independent_measurement_geometries": 2,
        "test_targets": len(tests),
        "positive_robust_targets": positive,
        "verdict": "SIMPLE_SCALAR_OBSERVER_CLOCK_BRANCH_NOT_SUPPORTED",
        "conditional_no_go": (
            "Within the frozen estimators, public data, nuisance families, "
            "and tested amplitudes, no robust directly identifiable scalar "
            "observer-clock deformation survives."
        ),
        "not_excluded": [
            "a common-mode factor that cancels from every tested comparison",
            "a non-scalar or tensorial observer-source response",
            "a response controlled by complete causal-support morphology rather than magnification alone",
            "a terminal effect below the sensitivity of these data",
            "a different physical readout not reducible to clock rate",
        ],
        "forbidden_next_moves": [
            "refit a closed event with another event-specific waveform",
            "relax source ownership after seeing a residual",
            "identify any remaining lensing residual directly with Tau time",
        ],
        "next_finite_action": (
            "Replace the scalar magnification-localized clock ansatz by one "
            "source-frozen relational predictor derived from complete "
            "observer-source causal-support morphology, then test it on a "
            "held-out non-clock terminal before reopening time."
        ),
        "claim_boundary": (
            "This is a conditional empirical no-go for a narrow model class, "
            "not a falsification of Tau Core, observer dependence, channel "
            "complexity, or the existence of time as a terminal readout."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("targets:", result["test_targets"])
    print("positive robust targets:", len(positive))


if __name__ == "__main__":
    main()
