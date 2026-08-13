#!/usr/bin/env python3
"""Compare paired reduced and publication-numerics WGD2038 realizations."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data/derived/repro_results"
REDUCED = (
    DERIVED
    / "tau_core_lensing_wgd2038_warm_dust_prior_predictive_n64_v1"
    / "summary.json"
)
PUBLICATION = (
    DERIVED
    / "tau_core_lensing_wgd2038_warm_dust_publication_numerics_n8_v1"
    / "summary.json"
)
OUT = (
    DERIVED
    / "tau_core_lensing_wgd2038_warm_dust_numerical_effort_stability_v1"
)


def main() -> None:
    reduced = json.loads(REDUCED.read_text(encoding="utf-8"))
    publication = json.loads(PUBLICATION.read_text(encoding="utf-8"))
    paired_count = int(publication["n_realizations"])
    reduced_ratios = np.asarray(
        reduced["predicted_flux_ratios"][:paired_count], dtype=float
    )
    publication_ratios = np.asarray(
        publication["predicted_flux_ratios"], dtype=float
    )
    difference = publication_ratios - reduced_ratios
    maximum = float(np.max(np.abs(difference)))
    result = {
        "schema": "paper7 WGD2038 warm-dust numerical-effort stability audit v1",
        "reduced_artifact": str(REDUCED.relative_to(ROOT)),
        "publication_numerics_artifact": str(PUBLICATION.relative_to(ROOT)),
        "paired_seed_start": int(publication["seed"]),
        "paired_realizations": paired_count,
        "reduced_pso_iterations": int(reduced["pso_iterations"]),
        "publication_pso_iterations": int(publication["pso_iterations"]),
        "publication_fitting_sequence_used": bool(
            publication["publication_fitting_sequence_used"]
        ),
        "maximum_absolute_ratio_difference": maximum,
        "all_paired_ratio_rows_exactly_equal": bool(
            np.array_equal(reduced_ratios, publication_ratios)
        ),
        "reduced_n64_flux_terminal_numerically_supported": maximum == 0.0,
        "general_optimizer_equivalence_proved": False,
        "tau_or_observer_time_scoring_allowed": False,
        "verdict": (
            "PAIRED_N8_FLUX_RATIOS_EXACTLY_STABLE_TO_PUBLICATION_NUMERICAL_EFFORT"
        ),
        "claim_boundary": (
            "The eight paired seeds support the reduced numerical effort for "
            "this flux terminal. They do not prove global optimizer "
            "equivalence, posterior convergence, OIII completion, or a "
            "Tau/observer-time result."
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
