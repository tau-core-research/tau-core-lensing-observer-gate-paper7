#!/usr/bin/env python3
"""Calibrate the surviving OGLE-2004-BLG-390 conditional clock candidate."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import audit_ogle2004_blg081_finite_source_clock_discriminator_v01 as finite
import audit_ogle2004_blg081_local_clock_rate_v01 as clock
import audit_ogle_replacement_same_source_clock_candidates_v01 as replacement


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg390_finite_tangent_clock_null_v1"
)
EVENT_NAME = "2004-BLG-390"
N_MOCKS = 64
BLOCK_LENGTH = 8
SEED = 70408390


def fitted_mean(
    t: np.ndarray,
    flux: np.ndarray,
    sigma: np.ndarray,
    parameters: np.ndarray,
) -> np.ndarray:
    t0, log_t_e, log_u0, alpha, beta = parameters
    t_e, u0 = np.exp(log_t_e), np.exp(log_u0)
    phi = clock.phase(t, t0, t_e, 0.0, alpha, beta)
    matrix = finite.finite_tangent_design(t, t0, t_e, u0, phi)
    coeff, *_ = np.linalg.lstsq(
        matrix / sigma[:, None], flux / sigma, rcond=None
    )
    return matrix @ coeff


def circular_blocks(
    residual: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    values = []
    while len(values) < len(residual):
        start = int(rng.integers(0, len(residual)))
        values.extend(
            residual[(start + offset) % len(residual)]
            for offset in range(BLOCK_LENGTH)
        )
    return np.asarray(values[: len(residual)])


def main() -> None:
    event = replacement.EVENTS[EVENT_NAME]
    clock.PERIOD = event["period_days"]
    clock.PHASE_ZERO = event["phase_zero_hjd"]
    phot = replacement.load(EVENT_NAME)
    t, mag, mag_error = phot.T
    flux = 10 ** (-0.4 * (mag - np.median(mag)))
    sigma = flux * np.log(10) * 0.4 * mag_error
    null_chi2, parameters = replacement.fit_shape_null(
        t, flux, sigma, event
    )
    observed_epsilon, observed_delta = replacement.conditional_clock(
        t, flux, sigma, parameters
    )
    mean = fitted_mean(t, flux, sigma, parameters)
    residual = (flux - mean) / sigma
    residual -= np.mean(residual)
    rng = np.random.default_rng(SEED)
    families = []

    for family in ("parametric", "block_residual"):
        rows = []
        for index in range(N_MOCKS):
            if family == "parametric":
                mock_flux = mean + sigma * rng.normal(size=len(t))
            else:
                mock_flux = mean + sigma * circular_blocks(residual, rng)
            epsilon, delta = replacement.conditional_clock(
                t, mock_flux, sigma, parameters
            )
            rows.append(
                {"mock": index, "epsilon": epsilon, "delta_chi2": delta}
            )
        families.append(
            {
                "null_family": family,
                "mock_count": N_MOCKS,
                "empirical_improvement_p": (
                    1 + sum(row["delta_chi2"] >= observed_delta for row in rows)
                )
                / (N_MOCKS + 1),
                "empirical_two_sided_rate_p": (
                    1
                    + sum(
                        abs(row["epsilon"]) >= abs(observed_epsilon)
                        for row in rows
                    )
                )
                / (N_MOCKS + 1),
                "median_mock_delta_chi2": float(
                    np.median([row["delta_chi2"] for row in rows])
                ),
                "median_abs_mock_epsilon": float(
                    np.median([abs(row["epsilon"]) for row in rows])
                ),
            }
        )

    survives = all(
        row["empirical_improvement_p"] <= 0.05
        and row["empirical_two_sided_rate_p"] <= 0.05
        for row in families
    )
    result = {
        "schema": "Paper 7 OGLE-2004-BLG-390 finite-tangent clock null v1",
        "event": EVENT_NAME,
        "observed_finite_tangent_null_chi2": null_chi2,
        "observed_epsilon": observed_epsilon,
        "observed_delta_chi2": observed_delta,
        "mock_count_per_family": N_MOCKS,
        "total_mock_light_curves": 2 * N_MOCKS,
        "conditional_on_frozen_finite_tangent_geometry": True,
        "families": families,
        "survives_conditional_statistical_null": survives,
        "source_variability_ownership_proved": False,
        "verdict": (
            "BLG390_CONDITIONAL_CLOCK_CANDIDATE_SURVIVES"
            if survives
            else "BLG390_CLOCK_CANDIDATE_FAILS_CONDITIONAL_NULL"
        ),
        "claim_boundary": (
            "Survival authorizes an ownership and robustness audit only. The "
            "2006 paper did not uniquely fit whether the periodic variability "
            "belongs to the lensed source, and the finite tangent remains a "
            "surrogate rather than an exact finite-source model."
        ),
        "next_finite_action": (
            "Test source-versus-blend ownership from magnification-dependent "
            "periodic amplitude, then perturb harmonic order, block length, "
            "and event window without changing the clock law."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("epsilon:", f"{observed_epsilon:.8g}")
    print("delta_chi2:", f"{observed_delta:.3f}")
    for row in families:
        print(
            row["null_family"],
            f"p_delta={row['empirical_improvement_p']:.4f}",
            f"p_rate={row['empirical_two_sided_rate_p']:.4f}",
        )


if __name__ == "__main__":
    main()
