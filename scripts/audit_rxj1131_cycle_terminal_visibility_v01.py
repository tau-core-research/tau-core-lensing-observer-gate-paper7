#!/usr/bin/env python3
"""Audit visibility of non-exact pair cycles in a four-image flux-ratio terminal."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_rxj1131_cycle_terminal_visibility_v1"
)


def main() -> None:
    labels = ["A", "B", "C", "D"]
    pairs = list(itertools.combinations(range(len(labels)), 2))
    incidence = np.zeros((len(pairs), len(labels)))
    pair_labels = []
    for row, (left, right) in enumerate(pairs):
        incidence[row, left] = 1.0
        incidence[row, right] = -1.0
        pair_labels.append(f"{labels[left]}_{labels[right]}")

    cut_projector = incidence @ np.linalg.pinv(incidence)
    cycle_projector = np.eye(len(pairs)) - cut_projector

    # A flux-ratio terminal is exact after taking logarithms:
    # log(F_i/F_j) = log(F_i) - log(F_j).
    synthetic_log_fluxes = np.array([0.2, -0.4, 0.7, 1.1])
    exact_terminal = incidence @ synthetic_log_fluxes
    terminal_cycle_component = cycle_projector @ exact_terminal

    trial_edge_relation = np.array([0.3, -0.2, 0.8, 0.5, -0.7, 0.4])
    nonexact_cycle = cycle_projector @ trial_edge_relation
    cycle_boundary = incidence.T @ nonexact_cycle
    cycle_terminal_pairing = float(nonexact_cycle @ exact_terminal)

    result = {
        "schema": "Paper 7 RXJ1131 cycle-terminal visibility audit v1",
        "target": "RXJ1131-1231",
        "pair_labels": pair_labels,
        "pair_space_dimension": len(pairs),
        "cut_space_rank": int(np.linalg.matrix_rank(incidence)),
        "cycle_space_rank": int(
            np.linalg.matrix_rank(cycle_projector, tol=1e-12)
        ),
        "cut_cycle_projector_overlap_norm": float(
            np.linalg.norm(cut_projector @ cycle_projector)
        ),
        "flux_ratio_factorization": (
            "y_ij=log(F_i/F_j)=ell_i-ell_j=(B ell)_ij"
        ),
        "synthetic_exact_terminal_cycle_norm": float(
            np.linalg.norm(terminal_cycle_component)
        ),
        "nonexact_cycle_boundary_norm": float(np.linalg.norm(cycle_boundary)),
        "nonexact_cycle_exact_terminal_pairing": cycle_terminal_pairing,
        "nonexact_cycle_directly_visible_in_flux_ratios": False,
        "terminal_values_used": False,
        "theorem": (
            "For four image fluxes let B be the six-by-four pair-incidence "
            "matrix. Log flux ratios lie in the exact cut space im(B). The "
            "non-exact pair-cycle space is ker(B^T), and finite-dimensional "
            "Hodge decomposition gives R^6=im(B) direct-sum ker(B^T). Hence "
            "every cycle vector is orthogonal to every flux-ratio terminal. "
            "A path holonomy is testable here only after a separately derived "
            "terminal map converts it into endpoint flux changes; those "
            "changes then appear as an exact cut vector and do not by "
            "themselves identify their non-exact origin."
        ),
        "verdict": (
            "RXJ1131_NONEXACT_CYCLE_SECTOR_IS_DIRECTLY_INVISIBLE_TO_"
            "SCALAR_FLUX_RATIOS"
        ),
        "next_finite_action": (
            "Do not construct a cycle score from the opened RXJ1131 ratios. "
            "Either derive a source-owned holonomy-to-flux terminal map before "
            "using endpoint data, select a terminal intrinsically sensitive "
            "to path phase or loop transport, or move to a multi-lens "
            "shared-coefficient test with physically constrained nuisances."
        ),
        "claim_boundary": (
            "This is a terminal-factorization no-go, not a proof that physical "
            "path holonomy is absent. It shows only that scalar endpoint flux "
            "ratios cannot directly distinguish the cycle sector."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("cycle-terminal pairing:", cycle_terminal_pairing)


if __name__ == "__main__":
    main()
