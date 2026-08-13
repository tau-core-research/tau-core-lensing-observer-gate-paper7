#!/usr/bin/env python3
"""Audit whether the RXJ1131 path descriptor exceeds its standard nuisance span."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DESCRIPTOR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_rxj1131_dimensionless_path_descriptor_v1/summary.json"
)
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_rxj1131_standard_nuisance_span_v1"
)


def main() -> None:
    payload = json.loads(DESCRIPTOR.read_text())
    components = payload["component_names"]
    pair_labels = list(payload["pairwise_path_contrasts"])
    path_matrix = np.array(
        [
            [
                payload["pairwise_path_contrasts"][pair][component]
                for component in components
            ]
            for pair in pair_labels
        ],
        dtype=float,
    )

    # Each column was constructed from a standard lens-model coordinate.
    # The conservative standard nuisance design must therefore contain their
    # complete span before any extra-physics interpretation is attempted.
    nuisance = path_matrix.copy()
    projector = nuisance @ np.linalg.pinv(nuisance)
    orthogonal_projector = np.eye(len(pair_labels)) - projector
    projected_descriptor = orthogonal_projector @ path_matrix
    maximum_residual = float(np.max(np.abs(projected_descriptor)))
    descriptor_rank = int(np.linalg.matrix_rank(path_matrix))
    projected_rank = int(np.linalg.matrix_rank(projected_descriptor, tol=1e-12))

    witness_weights = np.array([0.7, -0.4, 0.2, 1.1])
    witness = path_matrix @ witness_weights
    projected_witness = orthogonal_projector @ witness
    witness_norm = float(np.linalg.norm(projected_witness))

    result = {
        "schema": "Paper 7 RXJ1131 standard nuisance-span audit v1",
        "target": payload["target"],
        "source_descriptor": str(DESCRIPTOR.relative_to(ROOT)),
        "pair_labels": pair_labels,
        "component_names": components,
        "standard_nuisance_ownership": {
            "rho_main": "main-lens Einstein-scale radial coordinate",
            "shear_radial_contraction": "standard external shear",
            "gradient_radial_contraction": "standard convergence gradient",
            "satellite_relative_load": "standard satellite lens contribution",
        },
        "descriptor_matrix_shape": list(path_matrix.shape),
        "descriptor_rank": descriptor_rank,
        "standard_nuisance_rank": int(np.linalg.matrix_rank(nuisance)),
        "nuisance_orthogonal_descriptor_rank": projected_rank,
        "maximum_nuisance_orthogonal_entry": maximum_residual,
        "arbitrary_linear_weight_witness": {
            "weights": witness_weights.tolist(),
            "nuisance_orthogonal_norm": witness_norm,
        },
        "linear_tau_direction_survives": bool(
            maximum_residual > 1e-12 or witness_norm > 1e-12
        ),
        "terminal_values_used": False,
        "nonlinear_extension_tested": False,
        "complete_object_level_cone_used": False,
        "theorem": (
            "Let P be the six-by-four matrix of frozen pair contrasts. Since "
            "every column of P is constructed from a declared standard "
            "lens-model coordinate, a complete conservative nuisance design N "
            "contains col(P). Therefore (I-Pi_col(N))P=0, and every linear "
            "scalar P w is also annihilated. No linear weighting of this "
            "descriptor is identifiable as extra Tau content."
        ),
        "verdict": (
            "RXJ1131_CURRENT_LINEAR_PATH_DESCRIPTOR_IS_STANDARD_NUISANCE__"
            "NO_TAU_DIRECTION_SURVIVES"
        ),
        "next_finite_action": (
            "Seek one independently source-derived relational coordinate not "
            "factorizing through these four standard columns. The finite "
            "candidates are an object-level path-resolved cone invariant or a "
            "predeclared nonlinear cross-relation forced by the body law; do "
            "not select it using the opened 2026 terminal."
        ),
        "claim_boundary": (
            "This exact linear-span no-go does not exclude nonlinear Tau "
            "content, a richer full-cone descriptor, or observer-dependent "
            "readout physics. It excludes only extra-content claims for linear "
            "combinations of the current four standard coordinates."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("maximum orthogonal entry:", maximum_residual)


if __name__ == "__main__":
    main()
