#!/usr/bin/env python3
"""Calibrate the OGLE-2004-BLG-081 localized clock statistic under epsilon=0."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

import audit_ogle2004_blg081_local_clock_rate_v01 as clock


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg081_local_clock_null_v1"
)
CENTRAL = clock.OUT_DIR / "summary.json"
N_MOCKS = 64
BLOCK_LENGTH = 8
SEED = 70408101


def bounds(allow_clock: bool) -> list[tuple[float, float]]:
    result = [
        (2453100.0, 2453112.0),
        (np.log(60.0), np.log(150.0)),
        (np.log(0.05), np.log(0.5)),
        (-1.0, 1.0),
        (-0.5, 0.5),
    ]
    if allow_clock:
        result.append((-0.05, 0.05))
    return result


def local_profile(
    t: np.ndarray,
    flux: np.ndarray,
    sigma: np.ndarray,
    ownership: str,
    initial: np.ndarray,
    allow_clock: bool,
) -> tuple[float, np.ndarray]:
    objective = lambda x: clock.profile_chi2(
        x, t, flux, sigma, ownership, allow_clock
    )
    starts = [initial]
    if allow_clock:
        starts = [
            np.r_[initial[:5], epsilon]
            for epsilon in (-0.02, -0.005, 0.0, 0.005, 0.02)
        ]
    candidates = list(starts)
    for start in starts:
        result = minimize(
            objective,
            start,
            method="L-BFGS-B",
            bounds=bounds(allow_clock),
            options={"maxiter": 1500, "ftol": 1e-10, "gtol": 1e-7},
        )
        candidates.append(result.x)
    best = min(candidates, key=objective)
    return float(objective(best)), np.asarray(best)


def fitted_null_mean(
    t: np.ndarray,
    flux: np.ndarray,
    sigma: np.ndarray,
    ownership: str,
    parameters: np.ndarray,
) -> np.ndarray:
    t0, log_t_e, log_u0, alpha, beta = parameters
    t_e, u0 = np.exp(log_t_e), np.exp(log_u0)
    a = clock.magnification(t, t0, t_e, u0)
    phi = clock.phase(t, t0, t_e, 0.0, alpha, beta)
    matrix = clock.design(a, phi, ownership)
    coeff, *_ = np.linalg.lstsq(
        matrix / sigma[:, None], flux / sigma, rcond=None
    )
    return matrix @ coeff


def circular_block_sample(
    residual: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    output = []
    while len(output) < len(residual):
        start = int(rng.integers(0, len(residual)))
        output.extend(
            residual[(start + offset) % len(residual)]
            for offset in range(BLOCK_LENGTH)
        )
    return np.asarray(output[: len(residual)])


def main() -> None:
    clock.main()
    central = json.loads(CENTRAL.read_text())
    phot = clock.load_photometry()
    t, mag, mag_error = phot.T
    flux = 10 ** (-0.4 * (mag - np.median(mag)))
    sigma = flux * np.log(10) * 0.4 * mag_error
    rng = np.random.default_rng(SEED)
    results = []

    for ownership in ("source", "blend"):
        null_fit = clock.fit(t, flux, sigma, ownership, False)
        null_parameters = np.asarray(null_fit["_profile_parameters"])
        mean = fitted_null_mean(
            t, flux, sigma, ownership, null_parameters
        )
        standardized_residual = (flux - mean) / sigma
        standardized_residual -= np.mean(standardized_residual)
        observed_alt = next(
            row
            for row in central["fits"]
            if row["ownership"] == ownership
            and row["allow_localized_clock_rate"]
        )
        observed_delta = observed_alt["delta_chi2_vs_null"]
        observed_epsilon = observed_alt["localized_fractional_clock_rate"]

        for null_family in ("parametric", "block_residual"):
            mock_rows = []
            for index in range(N_MOCKS):
                if null_family == "parametric":
                    mock_flux = mean + sigma * rng.normal(size=len(t))
                else:
                    mock_flux = mean + sigma * circular_block_sample(
                        standardized_residual, rng
                    )
                null_chi2, fitted_null = local_profile(
                    t,
                    mock_flux,
                    sigma,
                    ownership,
                    null_parameters,
                    False,
                )
                alt_chi2, fitted_alt = local_profile(
                    t,
                    mock_flux,
                    sigma,
                    ownership,
                    np.r_[fitted_null, 0.0],
                    True,
                )
                mock_rows.append(
                    {
                        "mock": index,
                        "delta_chi2": max(0.0, null_chi2 - alt_chi2),
                        "epsilon": float(fitted_alt[5]),
                    }
                )
            improvement_p = (
                1
                + sum(row["delta_chi2"] >= observed_delta for row in mock_rows)
            ) / (N_MOCKS + 1)
            rate_p = (
                1
                + sum(
                    abs(row["epsilon"]) >= abs(observed_epsilon)
                    for row in mock_rows
                )
            ) / (N_MOCKS + 1)
            results.append(
                {
                    "ownership": ownership,
                    "null_family": null_family,
                    "mock_count": N_MOCKS,
                    "observed_delta_chi2": observed_delta,
                    "observed_epsilon": observed_epsilon,
                    "empirical_improvement_p": improvement_p,
                    "empirical_two_sided_rate_p": rate_p,
                    "median_mock_delta_chi2": float(
                        np.median([row["delta_chi2"] for row in mock_rows])
                    ),
                    "median_abs_mock_epsilon": float(
                        np.median([abs(row["epsilon"]) for row in mock_rows])
                    ),
                }
            )

    robust_against_calibrated_nulls = all(
        row["empirical_improvement_p"] <= 0.05
        and row["empirical_two_sided_rate_p"] <= 0.05
        for row in results
    )
    result = {
        "schema": "Paper 7 OGLE-2004-BLG-081 localized clock null calibration v1",
        "seed": SEED,
        "mock_count_per_ownership_and_family": N_MOCKS,
        "total_mock_light_curves": 4 * N_MOCKS,
        "block_residual_length_observations": BLOCK_LENGTH,
        "results": results,
        "robust_against_calibrated_statistical_nulls": robust_against_calibrated_nulls,
        "standard_finite_source_binary_nuisance_closed": False,
        "verdict": (
            "STATISTICAL_NULL_SURVIVAL__PHYSICAL_NUISANCE_OPEN"
            if robust_against_calibrated_nulls
            else "LOCALIZED_CLOCK_CANDIDATE_FAILS_CALIBRATED_NULL"
        ),
        "claim_boundary": (
            "Statistical null survival would not identify time distortion. "
            "A microlensed eclipsing binary can change eclipse shape through "
            "finite-source and differential component magnification. That "
            "standard physical nuisance is not represented by either mock "
            "family and must be modeled before any clock interpretation."
        ),
        "next_finite_action": (
            "Fit a binary-source finite-source microlensing model with a fixed "
            "orbital ephemeris, then test whether the localized clock "
            "coefficient retains identifiable improvement."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    for row in results:
        print(
            row["ownership"],
            row["null_family"],
            f"p_delta={row['empirical_improvement_p']:.4f}",
            f"p_rate={row['empirical_two_sided_rate_p']:.4f}",
        )


if __name__ == "__main__":
    main()
