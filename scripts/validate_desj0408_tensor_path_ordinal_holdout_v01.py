#!/usr/bin/env python3
"""Validate the frozen DES J0408 tensor/path ordinal signature on holdouts."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from audit_desj0408_joint_tensor_path_interaction_v01 import interaction
from freeze_desj0408_image_path_pullbacks_v01 import extract_paths
from solve_desj0408_positive_host_moment_v01 import solve_positive_models


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
HOST_AUDIT = (
    RESULTS / "tau_core_lensing_desj0408_single_body_host_descriptor_v1/summary.json"
)
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_tensor_path_ordinal_holdout_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def signature(values: list[float]) -> dict[str, bool]:
    return {
        "path_2_negative": values[2] < 0.0,
        "path_3_positive": values[3] > 0.0,
        "path_1_below_path_0": values[1] < values[0],
        "path_2_below_path_0": values[2] < values[0],
        "path_3_above_path_2": values[3] > values[2],
    }


def main() -> None:
    host_audit = json.loads(HOST_AUDIT.read_text(encoding="utf-8"))
    discovery_ids = {
        row["model_id"] for row in host_audit["top_five_models"]
    }
    holdout_ids = [
        row["model_id"]
        for row in host_audit["eligible_models"]
        if row["model_id"] not in discovery_ids
    ]
    solved = solve_positive_models(holdout_ids)

    rows = []
    for model in solved["models"]:
        paths = extract_paths(model["model_id"], {})["paths"]
        moment = np.asarray(model["second_moment_tensor_arcsec2"], dtype=float)
        values = [
            interaction(
                moment,
                np.asarray(path["image_from_source_local_pullback"], dtype=float),
            )
            for path in paths
        ]
        tests = signature(values)
        rows.append(
            {
                "model_id": model["model_id"],
                "solver_success": model["solver_success"],
                "minimum_source_brightness": model["minimum_source_brightness"],
                "second_moment_tensor_arcsec2": model[
                    "second_moment_tensor_arcsec2"
                ],
                "moment_trace_arcsec2": model["moment_trace_arcsec2"],
                "moment_area_character_arcsec2": float(
                    np.sqrt(
                        np.linalg.det(
                            np.asarray(
                                model["second_moment_tensor_arcsec2"],
                                dtype=float,
                            )
                        )
                    )
                ),
                "path_interactions": values,
                "frozen_signature_tests": tests,
                "full_signature_pass": all(tests.values()),
            }
        )

    test_names = list(rows[0]["frozen_signature_tests"]) if rows else []
    pass_counts = {
        name: sum(row["frozen_signature_tests"][name] for row in rows)
        for name in test_names
    }
    all_solvers_valid = all(
        row["solver_success"] and row["minimum_source_brightness"] >= -1e-8
        for row in rows
    )
    full_pass_count = sum(row["full_signature_pass"] for row in rows)
    exact_replication = bool(
        rows and all_solvers_valid and full_pass_count == len(rows)
    )

    result = {
        "schema": "paper7 DES J0408 tensor-path ordinal holdout v1",
        "target": "DES J0408-5354 quasar host at z=2.375",
        "freeze_rule": (
            "The five inequalities were discovered on the top-five "
            "imaging-evidence models and frozen before opening the remaining "
            "eligible SPEMD models."
        ),
        "input_scope": (
            "remaining image-only SPEMD model posteriors; no delay data, "
            "residual, or time endpoint"
        ),
        "discovery_model_ids": sorted(discovery_ids),
        "holdout_model_ids": holdout_ids,
        "holdout_model_count": len(rows),
        "all_holdout_positive_solvers_valid": all_solvers_valid,
        "frozen_signature": list(signature([1.0, 0.0, -1.0, 1.0])),
        "signature_pass_counts": pass_counts,
        "full_signature_pass_count": full_pass_count,
        "exact_ordinal_signature_replication": exact_replication,
        "rows": rows,
        "independent_target_replication": False,
        "sfh_02_relative_morphology_materialized": False,
        "sfh_03_body_conditioned_path_pullback_materialized": False,
        "theta_M_identified": False,
        "h_tau_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "ORDINAL_SIGNATURE_REPLICATED_ON_INTERNAL_MODEL_HOLDOUT"
            if exact_replication
            else "ORDINAL_SIGNATURE_NOT_REPLICATED_ON_INTERNAL_MODEL_HOLDOUT"
        ),
        "claim_boundary": (
            "A lower-ranked within-target model holdout tests model-family "
            "robustness only. Even exact replication is not a second-target "
            "validation, complete morphology handoff, body clock, h_tau, "
            "observer-time distortion, or Tau detection."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 tensor-path ordinal holdout v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        f"Full frozen-signature passes: `{full_pass_count}/{len(rows)}`.\n\n"
        "The holdout is internal to one lens system and cannot establish an "
        "observer-time effect.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "holdout_models": len(rows),
                "full_signature_passes": full_pass_count,
                "time_score_authorized": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
