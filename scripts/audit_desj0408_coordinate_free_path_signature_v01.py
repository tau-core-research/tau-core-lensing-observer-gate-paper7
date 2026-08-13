#!/usr/bin/env python3
"""Canonicalize the DES J0408 tensor/path signature without image labels."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
DISCOVERY = (
    RESULTS / "tau_core_lensing_desj0408_joint_tensor_path_interaction_v1/summary.json"
)
HOLDOUT = (
    RESULTS / "tau_core_lensing_desj0408_tensor_path_ordinal_holdout_v1/summary.json"
)
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_coordinate_free_path_signature_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def canonical_row(model_id: str, values: list[float]) -> dict:
    # The archived quad has two positive-parity paths followed by two
    # negative-parity paths in every eligible model.
    positive = sorted(values[:2])
    negative = sorted(values[2:])
    return {
        "model_id": model_id,
        "positive_parity_interaction_multiset": positive,
        "negative_parity_interaction_multiset": negative,
        "negative_parity_sign_split": negative[0] < 0.0 < negative[1],
    }


def main() -> None:
    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    holdout = json.loads(HOLDOUT.read_text(encoding="utf-8"))
    rows = [
        canonical_row(model["model_id"], model["path_interactions"])
        for model in discovery["models"]
    ]
    rows.extend(
        canonical_row(model["model_id"], model["path_interactions"])
        for model in holdout["rows"]
    )
    split_count = sum(row["negative_parity_sign_split"] for row in rows)
    exact_split = bool(rows and split_count == len(rows))

    result = {
        "schema": "paper7 DES J0408 coordinate-free path signature audit v1",
        "target": "DES J0408-5354 quasar host at z=2.375",
        "input_scope": (
            "combined discovery and internal-holdout image-only models; no "
            "delay data, residual, or time endpoint"
        ),
        "canonicalization": (
            "replace arbitrary image indices by sorted interaction multisets "
            "within parity classes"
        ),
        "model_count": len(rows),
        "negative_parity_sign_split_count": split_count,
        "negative_parity_sign_split_all_models": exact_split,
        "rows": rows,
        "label_permutation_invariant_signature_materialized": exact_split,
        "standard_lensing_identity": (
            "c=e_Q e_R cos(2 Delta_phi), derived exactly from the source "
            "second-moment tensor and local lens Jacobian"
        ),
        "tau_specific_information_beyond_standard_lensing_materialized": False,
        "coordinate_free_morphology_path_control_materialized": exact_split,
        "independent_target_replication": False,
        "sfh_02_relative_morphology_materialized": False,
        "sfh_03_body_conditioned_path_pullback_materialized": False,
        "theta_M_identified": False,
        "h_tau_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "COORDINATE_FREE_NEGATIVE_PARITY_SPLIT_STABLE__STANDARD_CONTROL_ONLY"
            if exact_split
            else "NO_COORDINATE_FREE_ORDINAL_SIGNATURE"
        ),
        "claim_boundary": (
            "The invariant sign split establishes robust source/path geometry "
            "within DES J0408. Because it is an exact standard-lensing tensor "
            "identity, it is not by itself Tau-specific information, an "
            "observer clock, h_tau, time distortion, or a detection."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 coordinate-free path signature v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        f"The negative-parity sign split is present in "
        f"`{split_count}/{len(rows)}` models. It is invariant under image-label "
        "permutations within a parity class, but follows from standard lensing "
        "tensor transport and is retained as a morphology/path control only.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "models": len(rows),
                "negative_parity_sign_split": split_count,
                "tau_specific_novelty": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
