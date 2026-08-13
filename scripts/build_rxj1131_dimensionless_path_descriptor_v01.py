#!/usr/bin/env python3
"""Build a terminal-blind dimensionless RXJ1131 path descriptor."""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_rxj1131_pre2026_predictor_source_packet_v1/summary.json"
)
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_rxj1131_dimensionless_path_descriptor_v1"
)


def pa_to_cartesian_angle(position_angle_deg: float) -> float:
    """Convert astronomical PA (north through east) to atan2(y, x)."""
    return math.radians(90.0 - position_angle_deg)


def matrix_rank(rows: list[list[float]], tolerance: float = 1e-12) -> int:
    matrix = [row[:] for row in rows]
    rank = 0
    column_count = len(matrix[0]) if matrix else 0
    for column in range(column_count):
        pivot = max(
            range(rank, len(matrix)),
            key=lambda row: abs(matrix[row][column]),
            default=rank,
        )
        if pivot >= len(matrix) or abs(matrix[pivot][column]) <= tolerance:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][column]
        matrix[rank] = [value / scale for value in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[rank])
            ]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def main() -> None:
    packet = json.loads(PACKET.read_text())
    geometry = packet["lens_centered_image_geometry"]
    model = packet["body_and_environment_inputs"]["lens_model"]
    satellite = packet["satellite_relation"]

    theta_e = model["main_einstein_radius_arcsec"]["value"]
    gamma = model["external_shear"]["value"]
    phi_gamma = pa_to_cartesian_angle(
        model["external_shear"]["position_angle_deg"]
    )
    gradient = model["convergence_gradient_per_arcsec"]["value"]
    phi_gradient = pa_to_cartesian_angle(
        model["convergence_gradient_per_arcsec"]["position_angle_deg"]
    )
    satellite_b = satellite["einstein_radius_arcsec"]["value"]
    satellite_x = satellite["dx_from_lens_arcsec"]
    satellite_y = satellite["dy_from_lens_arcsec"]

    labels = packet["image_labels"]
    descriptors = {}
    for label in labels:
        point = geometry[label]
        radius = point["radius_arcsec"]
        phi = point["polar_angle_rad"]
        distance_to_satellite = math.hypot(
            point["dx_arcsec"] - satellite_x,
            point["dy_arcsec"] - satellite_y,
        )
        descriptors[label] = {
            "rho_main": radius / theta_e,
            "shear_radial_contraction": gamma
            * math.cos(2.0 * (phi - phi_gamma)),
            "gradient_radial_contraction": theta_e
            * gradient
            * math.cos(phi - phi_gradient),
            "satellite_relative_load": satellite_b / distance_to_satellite,
        }

    component_names = list(descriptors[labels[0]])
    pairwise = {}
    for left, right in itertools.combinations(labels, 2):
        pairwise[f"{left}_{right}"] = {
            component: descriptors[left][component]
            - descriptors[right][component]
            for component in component_names
        }

    means = {
        component: sum(descriptors[label][component] for label in labels)
        / len(labels)
        for component in component_names
    }
    centered_rows = [
        [
            descriptors[label][component] - means[component]
            for component in component_names
        ]
        for label in labels
    ]
    finite = all(
        math.isfinite(value)
        for descriptor in descriptors.values()
        for value in descriptor.values()
    )

    result = {
        "schema": "Paper 7 RXJ1131 dimensionless path descriptor v1",
        "target": packet["target"],
        "source_packet": str(PACKET.relative_to(ROOT)),
        "construction": {
            "path_descriptor": (
                "d_i=(r_i/theta_E, gamma*cos(2(phi_i-phi_gamma)), "
                "theta_E*grad(kappa)*cos(phi_i-phi_grad), "
                "b_sat/|r_i-r_sat|)"
            ),
            "pair_descriptor": "Delta_ij=d_i-d_j",
            "angle_convention": (
                "Published astronomical position angles are converted from "
                "north-through-east to atan2(dDec,dRA*cosDec)."
            ),
        },
        "component_names": component_names,
        "path_descriptors": descriptors,
        "pairwise_path_contrasts": pairwise,
        "centered_path_matrix_rank": matrix_rank(centered_rows),
        "all_components_dimensionless": True,
        "all_values_finite": finite,
        "terminal_values_used": False,
        "fitted_weights_used": False,
        "scalar_predictor_selected": False,
        "predictor_sign_selected": False,
        "complete_object_level_cone_used": False,
        "vector_descriptor_materialized": finite and len(pairwise) == 6,
        "verdict": (
            "RXJ1131_DIMENSIONLESS_VECTOR_PATH_DESCRIPTOR_MATERIALIZED__"
            "SCALAR_LAW_AND_COMPLETE_CONE_OPEN"
        ),
        "next_finite_action": (
            "Place the six frozen pair contrasts against a declared standard "
            "lens-model nuisance design and test whether any source-fixed "
            "component survives nuisance projection. Do not open or fit the "
            "2026 terminal values during that construction."
        ),
        "claim_boundary": (
            "This is a terminal-blind coordinate construction from pre-2026 "
            "inputs. It is not a Tau scalar law, a complete light cone, "
            "a flux prediction, or evidence for observer-time distortion."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("centered path-matrix rank:", result["centered_path_matrix_rank"])


if __name__ == "__main__":
    main()
