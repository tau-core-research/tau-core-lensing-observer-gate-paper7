#!/usr/bin/env python3
"""Construct the finite witness behind blind cross-terminal identifiability."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_blind_cross_terminal_identifiability_theorem_v1"
)


def projector(matrix: np.ndarray) -> np.ndarray:
    return matrix @ np.linalg.pinv(matrix)


def main() -> None:
    # The four output coordinates and this full-rank candidate menu are an
    # exact counterexample to residual-selected predictor identification.
    design = np.array(
        [
            [1.0, 0.0, 1.0, 0.0],
            [0.0, 1.0, 1.0, 0.0],
            [0.0, 0.0, 1.0, 1.0],
            [1.0, 1.0, 0.0, 1.0],
        ]
    )
    terminal = np.array([0.7, -1.2, 0.4, 1.8])
    adaptive_coefficients = np.linalg.solve(design, terminal)
    adaptive_prediction = design @ adaptive_coefficients

    nuisance = np.column_stack(
        [np.ones(4), np.array([-1.5, -0.5, 0.5, 1.5])]
    )
    frozen_prediction = design @ np.array([0.3, -0.2, 0.5, 0.1])
    q_nuisance = np.eye(4) - projector(nuisance)
    testable_prediction = q_nuisance @ frozen_prediction

    result = {
        "schema": "Paper 7 blind cross-terminal identifiability theorem v1",
        "formal_objects": {
            "X": "source-side observer-cone data",
            "N": "predeclared standard nuisance design",
            "Y": "held-out non-clock terminal",
            "P_theta": "relational predictor f_theta(X)",
            "Q_N": "I minus the orthogonal projector onto col(N)",
        },
        "theorem": (
            "If theta is selected after opening Y and the evaluated predictor "
            "menu has output rank m, any m-dimensional terminal vector can be "
            "interpolated exactly; the in-sample association is therefore not "
            "independent evidence. If theta and the sign are frozen without Y, "
            "only Q_N P_theta is identifiable beyond standard nuisances. A "
            "nonzero held-out association can then falsify the conditional-null "
            "Y independent of P_theta given N."
        ),
        "exact_counterexample": {
            "output_dimension": int(design.shape[0]),
            "design_rank": int(np.linalg.matrix_rank(design)),
            "adaptive_coefficients": adaptive_coefficients.tolist(),
            "maximum_interpolation_error": float(
                np.max(np.abs(adaptive_prediction - terminal))
            ),
        },
        "frozen_predictor_check": {
            "nuisance_rank": int(np.linalg.matrix_rank(nuisance)),
            "testable_prediction": testable_prediction.tolist(),
            "testable_prediction_norm": float(
                np.linalg.norm(testable_prediction)
            ),
            "novel_direction_exists": bool(
                np.linalg.norm(testable_prediction) > 1e-12
            ),
        },
        "necessary_conditions": [
            "theta and predictor sign are measurable from X and training data only",
            "Y and its residual remain unopened until the predictor is frozen",
            "Q_N P_theta is nonzero on the validation sample",
            "the terminal covariance and test statistic are predeclared",
            "standard nuisance completion is included in N before Tau attribution",
        ],
        "not_proved": [
            "that nature realizes a nonzero Tau relational cone law",
            "that any current lens has complete physical causal-support data",
            "that a successful non-clock association originates in observer time",
        ],
        "verdict": "BLIND_CROSS_TERMINAL_PROTOCOL_IS_MATHEMATICALLY_NECESSARY",
        "claim_boundary": (
            "This is an identifiability theorem plus a finite exact "
            "counterexample. It proves the necessity of source freezing and "
            "terminal blindness, not the existence of a physical Tau signal."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print(
        "maximum adaptive interpolation error:",
        result["exact_counterexample"]["maximum_interpolation_error"],
    )


if __name__ == "__main__":
    main()
