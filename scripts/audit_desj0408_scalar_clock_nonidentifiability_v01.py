#!/usr/bin/env python3
"""Audit whether the stable DES J0408 scalar uniquely defines a body clock."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
HOST = RESULTS / "tau_core_lensing_desj0408_positive_host_moment_v1/summary.json"
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_scalar_clock_nonidentifiability_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def main() -> None:
    host = json.loads(HOST.read_text(encoding="utf-8"))
    q = float(host["mean_moment_trace_arcsec2"])
    scale = q
    candidates = [
        {
            "name": "linear",
            "definition": "Theta(q)=q/q_*",
            "value_at_q": q / scale,
            "derivative_at_q_per_arcsec2": 1.0 / scale,
        },
        {
            "name": "logarithmic",
            "definition": "Theta(q)=log(q/q_*)",
            "value_at_q": math.log(q / scale),
            "derivative_at_q_per_arcsec2": 1.0 / q,
        },
        {
            "name": "square_root",
            "definition": "Theta(q)=sqrt(q/q_*)",
            "value_at_q": math.sqrt(q / scale),
            "derivative_at_q_per_arcsec2": 0.5 / math.sqrt(q * scale),
        },
        {
            "name": "quadratic",
            "definition": "Theta(q)=(q/q_*)^2",
            "value_at_q": (q / scale) ** 2,
            "derivative_at_q_per_arcsec2": 2.0 * q / scale**2,
        },
    ]
    derivatives = {
        round(row["derivative_at_q_per_arcsec2"], 12)
        for row in candidates
    }
    all_monotone = all(
        row["derivative_at_q_per_arcsec2"] > 0.0 for row in candidates
    )
    same_rank_one_null = all_monotone
    nonunique_covectors = len(derivatives) > 1

    result = {
        "schema": "paper7 DES J0408 scalar clock nonidentifiability v1",
        "target": "DES J0408-5354 quasar host at z=2.375",
        "input_scope": (
            "stable image-only source moment trace; no delay data, residual, "
            "time endpoint, or fitted clock normalization"
        ),
        "observed_scalar": {
            "symbol": "q_s=tr(Q_s)",
            "value_arcsec2": q,
            "model_family_coefficient_of_variation": host[
                "trace_coefficient_of_variation"
            ],
            "rotation_and_path_label_invariant": True,
            "compatible_with_rank_one_common_representation": True,
        },
        "reference_scale_used_only_for_counterfamily_arcsec2": scale,
        "candidate_clock_family": candidates,
        "all_candidates_monotone_rank_one": all_monotone,
        "all_candidates_have_same_local_null_as_dq": same_rank_one_null,
        "candidate_clock_covectors_are_nonunique": nonunique_covectors,
        "sfh_01_representation_compatible_scalar_class_materialized": True,
        "theta_M_identified": False,
        "clock_scale_selected_by_source_law": False,
        "clock_function_selected_by_source_law": False,
        "a_O_identified": False,
        "h_tau_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "RANK_ONE_COMMON_SCALAR_CLASS_FOUND__PHYSICAL_BODY_CLOCK_NONIDENTIFIABLE"
            if same_rank_one_null and nonunique_covectors
            else "SCALAR_CLOCK_COUNTERFAMILY_FAILED"
        ),
        "claim_boundary": (
            "The stable scalar can occupy the representation type required by "
            "the common rank-one body coordinate. Symmetry, rank, and null-space "
            "data do not select its calibration or functional form, so it is not "
            "Theta_M, a descended observer covector, h_tau, or time distortion."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 scalar clock nonidentifiability v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        "The stable source trace has the correct invariant rank-one type for a "
        "common body coordinate. Four explicit monotone clock candidates share "
        "its local null but induce different covectors. A parent source law and "
        "absolute calibration are therefore required to identify `Theta_M`.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "candidate_count": len(candidates),
                "same_null": same_rank_one_null,
                "theta_M_identified": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
