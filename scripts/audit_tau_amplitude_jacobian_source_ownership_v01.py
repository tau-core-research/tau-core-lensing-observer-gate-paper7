#!/usr/bin/env python3
"""Audit Tau source ownership of real gain and holonomy-Jacobian coupling."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_amplitude_jacobian_source_ownership_v1"
)


def main() -> None:
    # A normalized positive-body amplitude is not a positive optical gain:
    # unitary conjugation preserves its Hilbert-Schmidt norm.
    rho = np.diag([0.7, 0.3])
    amplitude = 2.0 * np.diag(np.sqrt(np.diag(rho)))
    theta = 0.63
    unitary = np.diag([np.exp(1j * theta), np.exp(-1j * theta)])
    transported = unitary @ amplitude @ unitary.conj().T
    body_amplitude_norm_change = float(
        abs(np.linalg.norm(transported) - np.linalg.norm(amplitude))
    )

    # The current support-separated packet has zero mixed source Hessian.
    current_cross_hessian = np.zeros((1, 1))

    # Pure-axis data and positivity admit zero and both signs of a mixed
    # holonomy-Jacobian completion. Thus those data cannot select the coupling.
    epsilon_values = [-0.4, 0.0, 0.4]
    mixed_family = {}
    for epsilon in epsilon_values:
        hessian = np.array([[1.0, epsilon], [epsilon, 1.0]])
        mixed_family[str(epsilon)] = {
            "eigenvalues": np.linalg.eigvalsh(hessian).tolist(),
            "positive_definite": bool(
                np.min(np.linalg.eigvalsh(hessian)) > 0.0
            ),
            "mixed_derivative": epsilon,
            "pure_jacobian_curvature": float(hessian[0, 0]),
            "pure_holonomy_curvature": float(hessian[1, 1]),
        }

    result = {
        "schema": "Paper 7 Tau amplitude/Jacobian source-ownership audit v1",
        "positive_body_amplitude": {
            "object": "A_B=2 sqrt(rho_B)",
            "type": (
                "normalized Hilbert-Schmidt positive-cone representative"
            ),
            "unitary_orbit_norm_change": body_amplitude_norm_change,
            "supplies_optical_real_gain_alpha_i": False,
            "reason": (
                "unitary conjugation preserves its norm; PBAL/RMSR does not "
                "type this object as a path-wise R_+ transfer character"
            ),
            "physical_selection_status": (
                "PBAL/PSFR remains conditional in the current Tau source"
            ),
        },
        "current_holonomy_jacobian_cross_jet": {
            "source_packet": "support-separated PJR-X0",
            "mixed_hessian": current_cross_hessian.tolist(),
            "mixed_hessian_norm": float(
                np.linalg.norm(current_cross_hessian)
            ),
            "neighborhood_wide_structural_zero": True,
            "holonomy_to_jacobian_cross_derivative_nonzero": False,
        },
        "admissible_counterfamily": {
            "local_hessian": "H_epsilon=[[1,epsilon],[epsilon,1]]",
            "members": mixed_family,
            "same_pure_axis_restrictions": True,
            "zero_and_both_signs_positive_definite": True,
            "coupling_selected_by_pure_source_data": False,
        },
        "conditional_minimal_completions": {
            "real_gain": (
                "one source-owned path-wise positive R_+ amplitude character "
                "alpha_i, distinct from normalized body amplitude"
            ),
            "geometric_conversion": (
                "one common primitive Gram row coupling the holonomy/contact "
                "sector to the lens-Jacobian response; its mixed derivative "
                "must pass the existing strict contraction bound"
            ),
        },
        "theorem": (
            "The existing conditional positive-body amplitude is norm-fixed "
            "and unitary-orbit invariant, so it does not supply the real "
            "path gain alpha_i required by flux. In the current PJR-X0 source "
            "neighborhood, primitive-row support separation makes the "
            "holonomy/body-response mixed Hessian and all its source "
            "derivatives identically zero. Positive completions with mixed "
            "coefficient epsilon of either sign and epsilon=0 preserve the "
            "same pure-axis Hessians for |epsilon|<1. Therefore current Tau "
            "source laws neither generate nor select a nonzero real-gain "
            "sector or holonomy-to-Jacobian cross derivative."
        ),
        "terminal_values_used": False,
        "real_gain_source_owned": False,
        "holonomy_jacobian_cross_derivative_source_owned": False,
        "verdict": (
            "CURRENT_TAU_SOURCE_OWNS_NEITHER_OPTICAL_REAL_GAIN_NOR_"
            "HOLONOMY_JACOBIAN_CROSS_JET"
        ),
        "next_finite_action": (
            "Do not add a fitted gain or cross coefficient. Either adopt and "
            "justify one enriched common Gram row as a conditional completion, "
            "or demote scalar flux ratios from the direct holonomy route and "
            "move to a terminal with intrinsic coherent phase sensitivity."
        ),
        "claim_boundary": (
            "This is a current-source ownership no-go, not a universal "
            "impossibility theorem. A physically enriched post-body parent "
            "may contain either missing object, but it must source it before "
            "terminal data are used."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("body amplitude norm change:", body_amplitude_norm_change)


if __name__ == "__main__":
    main()
