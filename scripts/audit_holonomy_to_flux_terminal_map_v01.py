#!/usr/bin/env python3
"""Derive the minimal holonomy-to-flux terminal map and its no-go boundary."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_holonomy_to_flux_terminal_map_v1"
)


def main() -> None:
    phase = np.linspace(-np.pi, np.pi, 257)
    source_amplitude = 1.3 - 0.4j
    magnification = 2.7

    isolated_amplitude = (
        np.sqrt(magnification) * np.exp(1j * phase) * source_amplitude
    )
    isolated_intensity = np.abs(isolated_amplitude) ** 2
    isolated_variation = float(np.ptp(isolated_intensity))

    second_amplitude = 0.8 + 0.2j
    coherent_amplitude = isolated_amplitude + second_amplitude
    coherent_intensity = np.abs(coherent_amplitude) ** 2
    coherent_variation = float(np.ptp(coherent_intensity))

    real_gain = 0.15 * np.cos(phase)
    nonunitary_amplitude = (
        np.sqrt(magnification)
        * np.exp(real_gain + 1j * phase)
        * source_amplitude
    )
    nonunitary_intensity = np.abs(nonunitary_amplitude) ** 2
    nonunitary_variation = float(np.ptp(nonunitary_intensity))

    result = {
        "schema": "Paper 7 minimal holonomy-to-flux terminal map v1",
        "minimal_transport": {
            "amplitude": "A_i=sqrt(mu_i)*exp(alpha_i+i*phi_i)*A_source",
            "isolated_intensity": (
                "F_i=|A_i|^2=mu_i*exp(2*alpha_i)*|A_source|^2"
            ),
            "pure_u1_case": "alpha_i=0 implies dF_i/dphi_i=0",
        },
        "pure_u1_isolated_path": {
            "intensity_variation_over_phase": isolated_variation,
            "phase_visible": bool(isolated_variation > 1e-12),
        },
        "coherent_two_path_control": {
            "terminal": "F=|A_1 exp(i phi_1)+A_2 exp(i phi_2)|^2",
            "intensity_variation_over_relative_phase": coherent_variation,
            "relative_phase_visible": bool(coherent_variation > 1e-6),
        },
        "nonunitary_control": {
            "terminal": "F=mu*exp(2 alpha(phi))*|A_source|^2",
            "intensity_variation": nonunitary_variation,
            "amplitude_sector_visible": bool(nonunitary_variation > 1e-6),
        },
        "geometric_conversion_route": {
            "formula": (
                "phi_hol -> delta J_lens(phi_hol) -> "
                "delta mu(phi_hol) -> delta F"
            ),
            "status": (
                "requires a separately source-derived holonomy-to-Jacobian "
                "connector; scalar flux does not identify that origin"
            ),
        },
        "theorem": (
            "For one resolved path with scalar U(1) transport U_i=exp(i phi_i) "
            "and an intensity terminal F_i=|sqrt(mu_i) U_i A_s|^2, unitarity "
            "gives U_i^*U_i=1 and F_i=mu_i|A_s|^2. Pure phase holonomy is "
            "therefore exactly flux-blind. Phase becomes intensity-visible "
            "only through coherent superposition of at least two amplitudes. "
            "Without coherence, flux modification requires a nonunitary real "
            "gain alpha_i or a separately derived conversion of holonomy into "
            "the geometric magnification Jacobian."
        ),
        "rxj1131_consequence": (
            "Resolved scalar narrow-line image flux ratios cannot directly "
            "measure a pure U(1) path holonomy. Promoting a phase holonomy to "
            "their explanation requires evidence for coherent branch "
            "interference, a sourced nonunitary amplitude law, or a sourced "
            "holonomy-to-magnification connector."
        ),
        "terminal_values_used": False,
        "pure_u1_holonomy_to_isolated_flux_map_nontrivial": False,
        "verdict": (
            "PURE_U1_HOLONOMY_IS_FLUX_BLIND__AMPLITUDE_INTERFERENCE_OR_"
            "GEOMETRIC_CONVERSION_REQUIRED"
        ),
        "next_finite_action": (
            "Audit the enriched Tau body for a source-owned real amplitude "
            "sector or holonomy-to-lens-Jacobian cross derivative. If neither "
            "exists, remove RXJ1131 scalar flux ratios as a direct holonomy "
            "endpoint and retain them only for cross-system amplitude tests."
        ),
        "claim_boundary": (
            "The theorem excludes direct pure-phase effects on isolated "
            "intensity. It does not exclude wave-optics interference, "
            "nonunitary transport, absorption, geometric magnification "
            "changes, or other amplitude-sector physics."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("isolated phase variation:", isolated_variation)


if __name__ == "__main__":
    main()
