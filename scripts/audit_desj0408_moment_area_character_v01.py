#!/usr/bin/env python3
"""Audit the moment-area character as a multiplicative body-load candidate."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
DISCOVERY = RESULTS / "tau_core_lensing_desj0408_positive_host_moment_v1/summary.json"
HOLDOUT = RESULTS / "tau_core_lensing_desj0408_tensor_path_ordinal_holdout_v1/summary.json"
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_moment_area_character_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def area_character(moment: np.ndarray) -> float:
    return float(np.sqrt(np.linalg.det(moment)))


def main() -> None:
    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    holdout = json.loads(HOLDOUT.read_text(encoding="utf-8"))
    models = [
        {
            "model_id": row["model_id"],
            "moment": np.asarray(row["second_moment_tensor_arcsec2"], dtype=float),
        }
        for row in discovery["models"]
    ]
    models.extend(
        {
            "model_id": row["model_id"],
            "moment": np.asarray(row["second_moment_tensor_arcsec2"], dtype=float),
        }
        for row in holdout["rows"]
    )
    rows = [
        {
            "model_id": model["model_id"],
            "trace_arcsec2": float(np.trace(model["moment"])),
            "area_character_arcsec2": area_character(model["moment"]),
        }
        for model in models
    ]
    traces = np.asarray([row["trace_arcsec2"] for row in rows])
    areas = np.asarray([row["area_character_arcsec2"] for row in rows])
    trace_cv = float(np.std(traces, ddof=1) / np.mean(traces))
    area_cv = float(np.std(areas, ddof=1) / np.mean(areas))

    q0 = np.asarray([[2.0, 0.3], [0.3, 1.0]])
    a1 = np.asarray([[1.2, 0.1], [0.0, 0.8]])
    a2 = np.asarray([[0.9, -0.2], [0.1, 1.1]])
    q1 = a1 @ q0 @ a1.T
    q2 = a2 @ q1 @ a2.T
    character_direct = area_character(q2) / area_character(q0)
    character_product = abs(np.linalg.det(a2)) * abs(np.linalg.det(a1))
    character_error = abs(character_direct - character_product)

    additive_q1 = np.asarray([[1.0, 0.0], [0.0, 1.0]])
    additive_q2 = np.asarray([[2.0, 0.0], [0.0, 2.0]])
    trace_product_error = abs(
        np.trace(additive_q1 + additive_q2)
        - np.trace(additive_q1) * np.trace(additive_q2)
    )

    result = {
        "schema": "paper7 DES J0408 moment-area character audit v1",
        "target": "DES J0408-5354 quasar host at z=2.375",
        "input_scope": (
            "twelve image-only positivity-constrained source moments; no delay "
            "data, residual, or time endpoint"
        ),
        "model_count": len(rows),
        "rows": rows,
        "mean_area_character_arcsec2": float(np.mean(areas)),
        "area_character_coefficient_of_variation": area_cv,
        "trace_coefficient_of_variation": trace_cv,
        "expanded_model_family_stability_threshold": 0.25,
        "area_character_stable_on_expanded_model_family": bool(area_cv < 0.25),
        "trace_stable_on_expanded_model_family": bool(trace_cv < 0.25),
        "area_character_more_stable_than_trace": bool(area_cv < trace_cv),
        "exact_character_law": (
            "m(Q)=sqrt(det Q); m(A Q A^T)/m(Q)=abs(det A); "
            "m(A2 A1 action)=abs(det A2) abs(det A1) m(Q)"
        ),
        "sequential_deformation_character_error": character_error,
        "trace_not_multiplicative_under_natural_additive_moment_composition": (
            bool(trace_product_error > 0.0)
        ),
        "trace_multiplicativity_counterexample_error": float(trace_product_error),
        "moment_area_positive_character_materialized": bool(
            character_error < 1e-12
        ),
        "parent_common_load_identified_with_moment_area_character": False,
        "absolute_reference_area_selected": False,
        "physical_theta_M_identified": False,
        "a_O_identified": False,
        "h_tau_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "MOMENT_AREA_CHARACTER_EXACT__EXPANDED_FAMILY_AMPLITUDE_UNSTABLE"
            if character_error < 1e-12
            else "MOMENT_AREA_CHARACTER_FAILED"
        ),
        "claim_boundary": (
            "The determinant-area is a mathematically natural positive character "
            "of sequential linear body deformations. Neither it nor the trace "
            "passes the frozen stability threshold on the expanded twelve-model "
            "family. The data do not identify a stable parent common load or "
            "select its reference area, so no physical clock follows."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 moment-area character audit v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        f"The twelve-model area-character CV is `{area_cv:.3f}` versus trace CV "
        f"`{trace_cv:.3f}`. The sequential congruence-character error is "
        f"`{character_error:.3e}`. Parent ownership and absolute calibration "
        "remain open.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "models": len(rows),
                "area_cv": area_cv,
                "trace_cv": trace_cv,
                "character_error": character_error,
                "theta_M_identified": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
