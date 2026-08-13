#!/usr/bin/env python3
"""Audit conditional logarithmic selection for the DES J0408 scalar clock."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
NONIDENT = (
    RESULTS / "tau_core_lensing_desj0408_scalar_clock_nonidentifiability_v1/summary.json"
)
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_log_clock_composition_selection_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def main() -> None:
    nonident = json.loads(NONIDENT.read_text(encoding="utf-8"))
    points = [(0.5, 0.8), (0.75, 1.4), (1.2, 1.7), (2.0, 3.0)]
    functions = {
        "linear": lambda x: x - 1.0,
        "logarithmic": math.log,
        "square_root": lambda x: math.sqrt(x) - 1.0,
        "quadratic": lambda x: x * x - 1.0,
    }
    rows = []
    for name, function in functions.items():
        errors = [
            abs(function(x * y) - function(x) - function(y))
            for x, y in points
        ]
        rows.append(
            {
                "name": name,
                "maximum_additivity_error_under_multiplication": max(errors),
                "passes_frozen_tolerance": max(errors) < 1e-12,
            }
        )

    passing = [row["name"] for row in rows if row["passes_frozen_tolerance"]]
    unique_log = passing == ["logarithmic"]
    result = {
        "schema": "paper7 DES J0408 log clock composition selection v1",
        "target": "DES J0408-5354 quasar host at z=2.375",
        "input_scope": (
            "the previously materialized rank-one scalar class plus a declared "
            "parent composition axiom; no delay data, residual, or time endpoint"
        ),
        "conditional_axioms": [
            "positive dimensionless load x=q/q_*",
            "independent common loads compose multiplicatively: x12=x1*x2",
            "clock coordinate is continuous and additive: Theta(xy)=Theta(x)+Theta(y)",
            "normalization Theta(1)=0 and dTheta/d(log x) at x=1 equals 1",
        ],
        "functional_equation_result": (
            "Theta(x)=log(x) is the unique continuous normalized solution"
        ),
        "finite_candidate_audit": rows,
        "passing_candidates": passing,
        "logarithmic_shape_conditionally_selected": unique_log,
        "measured_source_trace_proved_to_obey_parent_multiplicative_composition": False,
        "absolute_reference_scale_q_star_selected": False,
        "physical_theta_M_identified": False,
        "a_O_identified": False,
        "h_tau_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "LOG_CLOCK_SHAPE_UNIQUE_CONDITIONAL_ON_MULTIPLICATIVE_BODY_COMPOSITION"
            if unique_log
            else "LOG_CLOCK_COMPOSITION_SELECTION_FAILED"
        ),
        "claim_boundary": (
            "The functional equation selects the logarithmic shape only if the "
            "physical body scalar obeys the declared multiplicative composition "
            "law. The DES J0408 image data do not prove that premise or select "
            "q_*, so Theta_M, a_O, h_tau, and observer-time distortion remain open."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 logarithmic clock composition selection v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        "Continuous additive response to multiplicatively composed positive "
        "loads uniquely selects `Theta=log(q/q_*)` after normalization. The "
        "composition premise and absolute reference scale are not selected by "
        "the image-only target data.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "passing_candidates": passing,
                "composition_premise_proved": False,
                "theta_M_identified": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
