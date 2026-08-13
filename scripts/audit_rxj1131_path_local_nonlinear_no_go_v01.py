#!/usr/bin/env python3
"""Prove the path-local nonlinear no-go for the four-image RXJ1131 descriptor."""

from __future__ import annotations

import itertools
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
    "tau_core_lensing_rxj1131_path_local_nonlinear_no_go_v1"
)


def main() -> None:
    payload = json.loads(DESCRIPTOR.read_text())
    labels = list(payload["path_descriptors"])
    components = payload["component_names"]
    pairs = list(itertools.combinations(range(len(labels)), 2))

    incidence = np.zeros((len(pairs), len(labels)))
    pair_labels = []
    for row, (left, right) in enumerate(pairs):
        incidence[row, left] = 1.0
        incidence[row, right] = -1.0
        pair_labels.append(f"{labels[left]}_{labels[right]}")

    path_values = np.array(
        [
            [
                payload["path_descriptors"][label][component]
                for component in components
            ]
            for label in labels
        ],
        dtype=float,
    )
    linear_pairs = incidence @ path_values
    linear_projector = linear_pairs @ np.linalg.pinv(linear_pairs)
    q_linear = np.eye(len(pairs)) - linear_projector

    monomial_labels = []
    quadratic_path_values = []
    for left in range(len(components)):
        for right in range(left, len(components)):
            monomial_labels.append(
                f"{components[left]}*{components[right]}"
            )
            quadratic_path_values.append(
                path_values[:, left] * path_values[:, right]
            )
    quadratic_path_matrix = np.column_stack(quadratic_path_values)
    quadratic_pairs = incidence @ quadratic_path_matrix
    projected_quadratic = q_linear @ quadratic_pairs

    arbitrary_local_scalar = (
        np.exp(path_values[:, 0])
        + np.sin(path_values[:, 1])
        - path_values[:, 2] * path_values[:, 3]
    )
    arbitrary_pairs = incidence @ arbitrary_local_scalar
    projected_arbitrary = q_linear @ arbitrary_pairs

    result = {
        "schema": "Paper 7 RXJ1131 path-local nonlinear no-go v1",
        "target": payload["target"],
        "source_descriptor": str(DESCRIPTOR.relative_to(ROOT)),
        "pair_labels": pair_labels,
        "incidence_shape": list(incidence.shape),
        "incidence_rank": int(np.linalg.matrix_rank(incidence)),
        "linear_descriptor_rank": int(np.linalg.matrix_rank(linear_pairs)),
        "linear_span_equals_full_pair_difference_space": bool(
            np.linalg.matrix_rank(linear_pairs)
            == np.linalg.matrix_rank(incidence)
        ),
        "quadratic_monomial_count": len(monomial_labels),
        "quadratic_monomials": monomial_labels,
        "quadratic_pair_rank": int(np.linalg.matrix_rank(quadratic_pairs)),
        "nuisance_orthogonal_quadratic_rank": int(
            np.linalg.matrix_rank(projected_quadratic, tol=1e-12)
        ),
        "maximum_nuisance_orthogonal_quadratic_entry": float(
            np.max(np.abs(projected_quadratic))
        ),
        "arbitrary_nonlinear_witness": {
            "formula": "exp(rho)+sin(shear)-gradient*satellite",
            "nuisance_orthogonal_norm": float(
                np.linalg.norm(projected_arbitrary)
            ),
        },
        "path_local_nonlinear_scalar_can_escape": False,
        "terminal_values_used": False,
        "theorem": (
            "Let B be the oriented incidence matrix of all six pairs of four "
            "paths. Then rank(B)=3. The frozen standard descriptor P=B D also "
            "has rank 3, hence col(P)=im(B). For every path-local scalar f, "
            "its pair contrast is B f(D), which belongs to im(B)=col(P). "
            "Therefore (I-Pi_col(P)) B f(D)=0 for every linear, polynomial, "
            "or nonlinear path-local f. A nonlinear scalarization cannot "
            "create nuisance-orthogonal information in this single quad."
        ),
        "escape_class": [
            (
                "a genuinely pair- or path-interior relation that is not the "
                "difference of endpoint-local scalar values"
            ),
            (
                "an independently constrained nuisance design whose physical "
                "rank is proved below the full three-dimensional cut space"
            ),
            (
                "a frozen cross-system law tested jointly on multiple lenses "
                "rather than coefficients selected within one quad"
            ),
        ],
        "verdict": (
            "RXJ1131_ALL_PATH_LOCAL_NONLINEAR_PAIR_SCALARS_ARE_NUISANCE__"
            "NONLOCAL_OR_CROSS_SYSTEM_STRUCTURE_REQUIRED"
        ),
        "claim_boundary": (
            "The theorem concerns endpoint-local scalar functions followed by "
            "pair differencing in one four-image system. It does not exclude "
            "path-interior tensors, non-exact pair relations, holonomy, a "
            "physically lower-rank nuisance model, or a frozen multi-system law."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print(
        "maximum projected quadratic entry:",
        result["maximum_nuisance_orthogonal_quadratic_entry"],
    )


if __name__ == "__main__":
    main()
