#!/usr/bin/env python3
"""Frozen harmonic-order and time-window robustness grid for BLG-390."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import audit_ogle2004_blg081_local_clock_rate_v01 as clock
import audit_ogle_replacement_same_source_clock_candidates_v01 as replacement


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg390_clock_robustness_grid_v1"
)
EVENT_NAME = "2004-BLG-390"
HARMONIC_ORDERS = (4, 6, 8)
WINDOWS_TE = (4, 8, 16)


def main() -> None:
    event = replacement.EVENTS[EVENT_NAME]
    clock.PERIOD = event["period_days"]
    clock.PHASE_ZERO = event["phase_zero_hjd"]
    phot = replacement.load(EVENT_NAME)
    rows = []

    for harmonics in HARMONIC_ORDERS:
        clock.HARMONICS = harmonics
        for window_t_e in WINDOWS_TE:
            mask = (
                np.abs(phot[:, 0] - event["t0_hjd"])
                <= window_t_e * event["tE_days"]
            )
            selected = phot[mask]
            t, mag, mag_error = selected.T
            flux = 10 ** (-0.4 * (mag - np.median(mag)))
            sigma = flux * np.log(10) * 0.4 * mag_error
            null_chi2, parameters = replacement.fit_shape_null(
                t, flux, sigma, event
            )
            epsilon, delta_chi2 = replacement.conditional_clock(
                t, flux, sigma, parameters
            )
            linear_count = 2 + 6 * harmonics
            dof = len(t) - linear_count - 5
            rows.append(
                {
                    "harmonic_order": harmonics,
                    "window_half_width_tE": window_t_e,
                    "data_points": int(len(t)),
                    "degrees_of_freedom": int(dof),
                    "finite_tangent_null_chi2": null_chi2,
                    "finite_tangent_null_reduced_chi2": (
                        null_chi2 / dof if dof > 0 else None
                    ),
                    "conditional_epsilon": epsilon,
                    "conditional_delta_chi2": delta_chi2,
                    "passes_local_precheck": (
                        bool(abs(epsilon) > 1e-6 and delta_chi2 > 3.84)
                    ),
                }
            )

    passing = [row for row in rows if row["passes_local_precheck"]]
    nonzero = [row["conditional_epsilon"] for row in passing]
    sign_stable = bool(
        nonzero
        and all(np.sign(value) == np.sign(nonzero[0]) for value in nonzero)
    )
    pass_fraction = len(passing) / len(rows)
    result = {
        "schema": "Paper 7 OGLE-2004-BLG-390 clock robustness grid v1",
        "event": EVENT_NAME,
        "frozen_grid": {
            "harmonic_orders": list(HARMONIC_ORDERS),
            "window_half_widths_tE": list(WINDOWS_TE),
            "cell_count": len(rows),
        },
        "cells": rows,
        "local_precheck_pass_fraction": pass_fraction,
        "passing_sign_stable": sign_stable,
        "epsilon_median_among_passing": (
            float(np.median(nonzero)) if nonzero else None
        ),
        "epsilon_range_among_passing": (
            [float(np.min(nonzero)), float(np.max(nonzero))]
            if nonzero
            else None
        ),
        "robustness_gate_passed": bool(pass_fraction >= 0.8 and sign_stable),
        "verdict": (
            "BLG390_CLOCK_CANDIDATE_ROBUST_ACROSS_FROZEN_GRID"
            if pass_fraction >= 0.8 and sign_stable
            else "BLG390_CLOCK_CANDIDATE_NOT_ROBUST_ACROSS_FROZEN_GRID"
        ),
        "claim_boundary": (
            "Grid robustness cannot solve source/blend ownership and does not "
            "turn the finite tangent into an exact physical source model."
        ),
        "next_finite_action": (
            "Only if this grid passes, vary residual block length under the "
            "central finite-tangent null. Otherwise close BLG-390 without "
            "further calibration."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("pass_fraction:", f"{pass_fraction:.3f}")
    print("sign_stable:", sign_stable)
    for row in rows:
        print(
            row["harmonic_order"],
            row["window_half_width_tE"],
            f"epsilon={row['conditional_epsilon']:.7g}",
            f"delta={row['conditional_delta_chi2']:.3f}",
            row["passes_local_precheck"],
        )


if __name__ == "__main__":
    main()
