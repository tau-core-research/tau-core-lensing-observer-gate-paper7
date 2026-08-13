#!/usr/bin/env python3
"""Select the finite cross-terminal route after the scalar clock no-go."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
OUT_DIR = RESULTS / "tau_core_lensing_relational_cone_cross_terminal_route_v1"


def load(name: str) -> dict:
    return json.loads((RESULTS / name / "summary.json").read_text())


def main() -> None:
    clock = load(
        "tau_core_lensing_observer_clock_empirical_branch_consolidation_v1"
    )
    cone = load("tau_core_lensing_desj0408_modeled_cone_morphology_v1")
    los = load("tau_core_lensing_desj0408_strides_los_morphology_v1")
    cubic = load("tau_core_lensing_desj0408_local_cubic_los_transport_v1")
    arc = load("tau_core_lensing_desj0408_local_cubic_f814w_arc_template_v1")
    oiii = load("tau_core_lensing_wgd2038_oiii_distinct_terminal_v1")
    oiii_completion = load(
        "tau_core_lensing_wgd2038_oiii_prior_predictive_compatibility_v1"
    )

    routes = [
        {
            "route": "DES_J0408_local_cubic_to_F814W_arc",
            "source_frozen_relational_predictor": bool(
                arc["source_forward_template_materialized"]
            ),
            "path_resolved_cone_structure": True,
            "complete_causal_support": bool(
                cone["complete_physical_light_cone_morphology_materialized"]
                and los["complete_physical_light_cone_morphology_materialized"]
            ),
            "non_clock_terminal": True,
            "terminal_held_out_before_predictor_selection": not bool(
                arc["endpoint_was_previously_opened"]
            ),
            "standard_completion_first": True,
            "result": arc["verdict"],
            "predictor_status": cubic["verdict"],
            "confirmatory": bool(arc["confirmatory_evidence_allowed"]),
        },
        {
            "route": "WGD2038_relational_cone_to_OIII_amplitude",
            "source_frozen_relational_predictor": False,
            "path_resolved_cone_structure": False,
            "complete_causal_support": False,
            "non_clock_terminal": bool(
                oiii["distinct_from_time_delay_terminal"]
            ),
            "terminal_held_out_before_predictor_selection": True,
            "standard_completion_first": True,
            "result": oiii_completion["verdict"],
            "tau_specific_excess": bool(
                oiii_completion["tau_specific_excess_materialized"]
            ),
            "confirmatory": False,
        },
    ]
    required = [
        "source_frozen_relational_predictor",
        "path_resolved_cone_structure",
        "complete_causal_support",
        "non_clock_terminal",
        "terminal_held_out_before_predictor_selection",
        "standard_completion_first",
    ]
    for route in routes:
        route["passed_requirements"] = [
            key for key in required if route.get(key) is True
        ]
        route["failed_requirements"] = [
            key for key in required if route.get(key) is not True
        ]
        route["route_admissible_for_time_reopening"] = not route[
            "failed_requirements"
        ]

    admissible = [
        route for route in routes if route["route_admissible_for_time_reopening"]
    ]
    result = {
        "schema": "Paper 7 relational-cone cross-terminal route audit v1",
        "upstream_clock_verdict": clock["verdict"],
        "requirements": required,
        "routes": routes,
        "admissible_routes": admissible,
        "verdict": (
            "NO_CURRENT_ROUTE_SATISFIES_COMPLETE_CONE_AND_BLIND_NONCLOCK_TEST"
        ),
        "finite_route_decision": (
            "Do not reopen the clock branch. Freeze one relational cone "
            "predictor on a new lens system using imaging, redshift, "
            "environment, and lens-model information only; reserve a "
            "predeclared non-clock terminal and its covariance until the "
            "predictor and sign are frozen."
        ),
        "selected_terminal_class": (
            "A path-sensitive amplitude or extended-source morphology "
            "observable not used in constructing the lens/cone predictor."
        ),
        "rejection_rules": [
            "no predictor coefficient may be selected from the held-out residual",
            "no incomplete cone may be labeled complete causal support",
            "no standard flux or morphology nuisance may be relabeled as Tau",
            "no clock score may be opened before cross-terminal validation",
        ],
        "claim_boundary": (
            "This audit selects an empirical protocol. It neither constructs "
            "the full parent morphology nor proves a Tau-specific cone law."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("admissible routes:", len(admissible))


if __name__ == "__main__":
    main()
