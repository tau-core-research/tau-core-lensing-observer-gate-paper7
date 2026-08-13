#!/usr/bin/env python3
"""Audit DES J0408 source-tensor/path interaction across joint lens models."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from freeze_desj0408_image_path_pullbacks_v01 import extract_paths


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
HOST = RESULTS / "tau_core_lensing_desj0408_positive_host_moment_v1/summary.json"
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_joint_tensor_path_interaction_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def interaction(moment: np.ndarray, pullback: np.ndarray) -> float:
    isotropic_stretch = 0.5 * np.trace(pullback @ pullback.T)
    transported_trace = np.trace(pullback @ moment @ pullback.T)
    return float(transported_trace / (np.trace(moment) * isotropic_stretch) - 1.0)


def anisotropy_vector(tensor: np.ndarray) -> np.ndarray:
    trace = np.trace(tensor)
    return np.asarray(
        [
            (tensor[0, 0] - tensor[1, 1]) / trace,
            (tensor[0, 1] + tensor[1, 0]) / trace,
        ]
    )


def main() -> None:
    host = json.loads(HOST.read_text(encoding="utf-8"))
    model_rows = []
    for model in host["models"]:
        extracted = extract_paths(model["model_id"], {})
        moment = np.asarray(model["second_moment_tensor_arcsec2"], dtype=float)
        source_vector = anisotropy_vector(moment)
        source_amplitude = float(np.linalg.norm(source_vector))
        path_values = []
        for path in extracted["paths"]:
            pullback = np.asarray(
                path["image_from_source_local_pullback"], dtype=float
            )
            path_metric = pullback.T @ pullback
            path_vector = anisotropy_vector(path_metric)
            path_amplitude = float(np.linalg.norm(path_vector))
            value = interaction(moment, pullback)
            denominator = source_amplitude * path_amplitude
            alignment = float(value / denominator) if denominator > 0 else 0.0
            path_values.append(
                {
                    "path_index": path["path_index"],
                    "parity": path["parity"],
                    "morse_index": path[
                        "morse_index_from_symmetric_jacobian"
                    ],
                    "interaction": value,
                    "path_anisotropy_amplitude": path_amplitude,
                    "relative_axis_alignment_cosine": alignment,
                    "decomposition_error": abs(
                        value - denominator * alignment
                    ),
                }
            )
        model_rows.append(
            {
                "model_id": model["model_id"],
                "source_anisotropy_vector": source_vector.tolist(),
                "source_anisotropy_amplitude": source_amplitude,
                "path_interactions": [
                    row["interaction"] for row in path_values
                ],
                "path_decomposition": path_values,
                "all_path_transports_finite": all(
                    np.isfinite(row["interaction"]) for row in path_values
                ),
            }
        )

    matrix = np.asarray(
        [row["path_interactions"] for row in model_rows], dtype=float
    )
    path_rows = []
    for path_index in range(matrix.shape[1]):
        values = matrix[:, path_index]
        signs = np.sign(values).astype(int)
        path_rows.append(
            {
                "path_index": path_index,
                "values": values.tolist(),
                "mean": float(np.mean(values)),
                "sample_standard_deviation": float(np.std(values, ddof=1)),
                "range": float(np.ptp(values)),
                "signs": signs.tolist(),
                "sign_stable": bool(np.all(signs == signs[0]) and signs[0] != 0),
            }
        )

    pair_rows = []
    for first in range(matrix.shape[1]):
        for second in range(first + 1, matrix.shape[1]):
            differences = matrix[:, second] - matrix[:, first]
            signs = np.sign(differences).astype(int)
            pair_rows.append(
                {
                    "first_path": first,
                    "second_path": second,
                    "differences": differences.tolist(),
                    "mean_difference": float(np.mean(differences)),
                    "sign_stable": bool(
                        np.all(signs == signs[0]) and signs[0] != 0
                    ),
                }
            )

    sign_stable_paths = [
        row["path_index"] for row in path_rows if row["sign_stable"]
    ]
    sign_stable_pairs = [
        [row["first_path"], row["second_path"]]
        for row in pair_rows
        if row["sign_stable"]
    ]
    finite = bool(np.all(np.isfinite(matrix)))
    ordinal_interaction = bool(sign_stable_paths or sign_stable_pairs)
    decomposition_error = max(
        path["decomposition_error"]
        for model in model_rows
        for path in model["path_decomposition"]
    )
    path_classes = [
        (
            model_rows[0]["path_decomposition"][index]["parity"],
            model_rows[0]["path_decomposition"][index]["morse_index"],
        )
        for index in range(matrix.shape[1])
    ]
    same_class_opposite_sign_paths = []
    for first in sign_stable_paths:
        for second in sign_stable_paths:
            if first >= second:
                continue
            first_sign = np.sign(matrix[:, first])
            second_sign = np.sign(matrix[:, second])
            if (
                path_classes[first] == path_classes[second]
                and np.all(first_sign == -second_sign)
            ):
                same_class_opposite_sign_paths.append([first, second])
    parity_morse_only_explanation_excluded = bool(
        same_class_opposite_sign_paths
    )

    result = {
        "schema": "paper7 DES J0408 joint tensor-path interaction audit v1",
        "target": "DES J0408-5354 quasar host at z=2.375",
        "input_scope": (
            "five matched image-only positive host tensors and lens models; "
            "no delay data, residual, or time endpoint"
        ),
        "interaction_definition": (
            "c_mi=tr(R_mi Q_m R_mi^T)/"
            "(tr(Q_m) tr(R_mi R_mi^T)/2)-1"
        ),
        "interpretation": (
            "c_mi is zero for an isotropic source and removes the stable scalar "
            "source size; nonzero values require source anisotropy aligned with "
            "the local path operator"
        ),
        "exact_decomposition": (
            "c_mi=e_Q_m e_R_mi cos(2 Delta_phi_mi), where e_Q is source "
            "anisotropy, e_R is anisotropy of R_mi^T R_mi, and the final factor "
            "is their normalized traceless-tensor inner product"
        ),
        "maximum_decomposition_error": decomposition_error,
        "model_count": len(model_rows),
        "path_count": matrix.shape[1],
        "all_joint_transports_finite": finite,
        "models": model_rows,
        "paths": path_rows,
        "path_pairs": pair_rows,
        "sign_stable_paths": sign_stable_paths,
        "sign_stable_path_pairs": sign_stable_pairs,
        "same_parity_morse_class_opposite_sign_paths": (
            same_class_opposite_sign_paths
        ),
        "parity_morse_only_explanation_excluded_on_target": (
            parity_morse_only_explanation_excluded
        ),
        "ordinal_tensor_path_interaction_materialized": ordinal_interaction,
        "amplitude_stable_tensor_path_interaction_materialized": False,
        "sfh_02_relative_morphology_materialized": False,
        "sfh_03_body_conditioned_path_pullback_materialized": False,
        "theta_M_identified": False,
        "h_tau_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "JOINT_TENSOR_PATH_ORDINAL_STRUCTURE_FOUND__AMPLITUDE_UNSTABLE"
            if finite and ordinal_interaction
            else "JOINT_TENSOR_PATH_INTERACTION_NOT_MODEL_STABLE"
        ),
        "claim_boundary": (
            "A sign-stable or ordered image-only tensor/path interaction is a "
            "source-forward morphology control. It does not promote the "
            "model-unstable tensor, identify Theta_M, construct h_tau, use time "
            "delays, or establish observer-time distortion."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 joint tensor-path interaction audit v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        f"Sign-stable paths: `{sign_stable_paths}`. Sign-stable path pairs: "
        f"`{sign_stable_pairs}`.\n\n"
        "The audit pairs every positive source tensor with its own lens model. "
        "Any surviving ordinal structure is endpoint-blind morphology evidence, "
        "not an observer-time detection.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "sign_stable_paths": sign_stable_paths,
                "sign_stable_path_pairs": sign_stable_pairs,
                "parity_morse_only_explanation_excluded_on_target": (
                    parity_morse_only_explanation_excluded
                ),
                "time_score_authorized": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
