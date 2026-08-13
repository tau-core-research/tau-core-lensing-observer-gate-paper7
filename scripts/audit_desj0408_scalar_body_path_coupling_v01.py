#!/usr/bin/env python3
"""Audit the scalar DES J0408 host moment against local lens transports."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
HOST = RESULTS / "tau_core_lensing_desj0408_positive_host_moment_v1/summary.json"
PATHS = RESULTS / "tau_core_lensing_desj0408_image_path_pullbacks_v1/summary.json"
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_scalar_body_path_coupling_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def main() -> None:
    host = json.loads(HOST.read_text(encoding="utf-8"))
    paths = json.loads(PATHS.read_text(encoding="utf-8"))

    source_trace = float(host["mean_moment_trace_arcsec2"])
    source_covariance = 0.5 * source_trace * np.eye(2)
    rows = []
    for path in paths["paths"]:
        pullback = np.asarray(
            path["image_from_source_local_pullback"], dtype=float
        )
        image_covariance = pullback @ source_covariance @ pullback.T
        scalar_stretch = 0.5 * float(np.trace(pullback @ pullback.T))
        image_trace = float(np.trace(image_covariance))
        rows.append(
            {
                "path_index": path["path_index"],
                "parity": path["parity"],
                "signed_magnification": path["signed_magnification"],
                "scalar_shape_stretch": scalar_stretch,
                "predicted_isotropic_image_trace_arcsec2": image_trace,
                "source_normalized_image_trace": image_trace / source_trace,
                "factorization_error": abs(
                    image_trace - source_trace * scalar_stretch
                ),
            }
        )

    max_error = max(row["factorization_error"] for row in rows)
    normalized = np.asarray(
        [row["source_normalized_image_trace"] for row in rows]
    )
    stretch = np.asarray([row["scalar_shape_stretch"] for row in rows])
    exact_factorization = bool(
        max_error < 1e-12 and np.allclose(normalized, stretch, atol=1e-12)
    )

    result = {
        "schema": "paper7 DES J0408 scalar body-path coupling audit v1",
        "target": "DES J0408-5354 quasar host at z=2.375",
        "input_scope": (
            "image-only stable scalar host moment and frozen local lens "
            "Jacobians; no delay data, residual, or time endpoint"
        ),
        "source_scalar": {
            "definition": "q_s = tr(Q_s)",
            "mean_moment_trace_arcsec2": source_trace,
            "model_family_coefficient_of_variation": host[
                "trace_coefficient_of_variation"
            ],
            "materialized": host["stable_scalar_trace_materialized"],
        },
        "transport_law": (
            "Q_s^iso=(q_s/2)I; Q_i=R_i Q_s^iso R_i^T; "
            "tr(Q_i)=q_s tr(R_i R_i^T)/2"
        ),
        "rows": rows,
        "maximum_factorization_error": max_error,
        "exact_scalar_body_path_factorization": exact_factorization,
        "source_information_survives_normalized_path_contrast": False,
        "independent_body_path_interaction_materialized": False,
        "partial_single_body_scalar_descriptor_materialized": bool(
            host["stable_scalar_trace_materialized"]
        ),
        "sfh_02_relative_morphology_materialized": False,
        "sfh_03_body_conditioned_path_pullback_materialized": False,
        "theta_M_identified": False,
        "h_tau_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "SCALAR_TRANSPORT_EXACTLY_FACTORIZES__NO_NEW_BODY_PATH_INFORMATION"
            if exact_factorization
            else "SCALAR_TRANSPORT_FACTORIZATION_FAILED"
        ),
        "claim_boundary": (
            "The stable host-size scalar produces finite path-conditioned image "
            "sizes, but after source normalization the result is exactly the "
            "standard local lens-Jacobian stretch. This is a useful scalar "
            "control and partial body descriptor, not a complete SFH_02/SFH_03 "
            "handoff, body clock, h_tau, observer-time distortion, or Tau signal."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 scalar body-path coupling audit v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        "The stable source trace is transported through all four local lens "
        "Jacobians. The resulting image-size scalar factorizes exactly into "
        "source size times standard Jacobian stretch. Source normalization "
        "therefore removes all body information; no independent body-path "
        "interaction or observer-time covector is materialized.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "source_trace_arcsec2": source_trace,
                "maximum_factorization_error": max_error,
                "time_score_authorized": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
