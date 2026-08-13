#!/usr/bin/env python3
"""Audit whether the log-area clock gives nonstandard path information."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from freeze_desj0408_image_path_pullbacks_v01 import extract_paths


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
DISCOVERY = RESULTS / "tau_core_lensing_desj0408_positive_host_moment_v1/summary.json"
HOLDOUT = RESULTS / "tau_core_lensing_desj0408_tensor_path_ordinal_holdout_v1/summary.json"
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_log_area_path_contrast_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def area(moment: np.ndarray) -> float:
    return float(np.sqrt(np.linalg.det(moment)))


def main() -> None:
    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    holdout = json.loads(HOLDOUT.read_text(encoding="utf-8"))
    models = [
        {
            "model_id": row["model_id"],
            "moment": row["second_moment_tensor_arcsec2"],
        }
        for row in discovery["models"]
    ]
    models.extend(
        {
            "model_id": row["model_id"],
            "moment": row["second_moment_tensor_arcsec2"],
        }
        for row in holdout["rows"]
    )

    rows = []
    errors = []
    contrast_errors = []
    for model in models:
        moment = np.asarray(model["moment"], dtype=float)
        source_area = area(moment)
        paths = extract_paths(model["model_id"], {})["paths"]
        path_rows = []
        for path in paths:
            pullback = np.asarray(
                path["image_from_source_local_pullback"], dtype=float
            )
            image_area = area(pullback @ moment @ pullback.T)
            measured_log_gain = math.log(image_area / source_area)
            standard_log_gain = math.log(abs(np.linalg.det(pullback)))
            error = abs(measured_log_gain - standard_log_gain)
            errors.append(error)
            path_rows.append(
                {
                    "path_index": path["path_index"],
                    "measured_log_area_gain": measured_log_gain,
                    "standard_log_abs_det_pullback": standard_log_gain,
                    "identity_error": error,
                }
            )
        reference_measured = path_rows[0]["measured_log_area_gain"]
        reference_standard = path_rows[0][
            "standard_log_abs_det_pullback"
        ]
        contrasts = []
        for path in path_rows[1:]:
            measured = path["measured_log_area_gain"] - reference_measured
            standard = (
                path["standard_log_abs_det_pullback"] - reference_standard
            )
            error = abs(measured - standard)
            contrast_errors.append(error)
            contrasts.append(
                {
                    "path_index": path["path_index"],
                    "reference_path_index": 0,
                    "log_area_clock_contrast": measured,
                    "standard_log_magnification_ratio": standard,
                    "contrast_identity_error": error,
                }
            )
        rows.append(
            {
                "model_id": model["model_id"],
                "source_area_character_arcsec2": source_area,
                "paths": path_rows,
                "contrasts": contrasts,
            }
        )

    max_error = max(errors)
    max_contrast_error = max(contrast_errors)
    exact = max(max_error, max_contrast_error) < 1e-12
    result = {
        "schema": "paper7 DES J0408 log-area path contrast audit v1",
        "target": "DES J0408-5354 quasar host at z=2.375",
        "input_scope": (
            "twelve image-only source moments and matched local lens Jacobians; "
            "no delay data, residual, or time endpoint"
        ),
        "identity": (
            "Theta_i=log(m(R_i Q R_i^T)/m_*)="
            "Theta_source+log(abs(det R_i)); therefore "
            "Theta_i-Theta_j=log(abs(det R_i)/abs(det R_j))"
        ),
        "model_count": len(rows),
        "rows": rows,
        "maximum_single_path_identity_error": max_error,
        "maximum_path_contrast_identity_error": max_contrast_error,
        "exact_reduction_to_standard_log_magnification_ratio": exact,
        "source_area_and_reference_scale_cancel_from_path_contrast": exact,
        "tau_specific_path_information_materialized": False,
        "local_endpoint_log_area_clock_branch_closed": exact,
        "full_causal_support_clock_still_open": True,
        "theta_M_identified": False,
        "a_O_identified": False,
        "h_tau_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "LOG_AREA_PATH_CONTRAST_EQUALS_STANDARD_MAGNIFICATION__BRANCH_CLOSED"
            if exact
            else "LOG_AREA_PATH_CONTRAST_IDENTITY_FAILED"
        ),
        "claim_boundary": (
            "The natural local endpoint log-area character contains no path "
            "information beyond the standard lens Jacobian. This closes that "
            "specific clock realization, not the full causal-support morphology "
            "clock, observer-time theory, or every possible Tau path covector."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 log-area path contrast audit v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        f"The maximum path-contrast identity error is "
        f"`{max_contrast_error:.3e}` across `{len(rows)}` models. The source "
        "area and reference calibration cancel, leaving the standard logarithmic "
        "magnification ratio. The local endpoint clock branch is closed.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "models": len(rows),
                "maximum_contrast_error": max_contrast_error,
                "tau_specific_path_information": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
