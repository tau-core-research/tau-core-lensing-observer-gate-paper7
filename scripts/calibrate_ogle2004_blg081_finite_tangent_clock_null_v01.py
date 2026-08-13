#!/usr/bin/env python3
"""Calibrate the clock statistic after finite-source tangent enrichment."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

import audit_ogle2004_blg081_finite_source_clock_discriminator_v01 as finite
import audit_ogle2004_blg081_local_clock_rate_v01 as clock


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg081_finite_tangent_clock_null_v1"
)
CENTRAL = finite.OUT_DIR / "summary.json"
N_MOCKS = 64
BLOCK_LENGTH = 8
SEED = 70408103


def conditional_clock_fit(
    t: np.ndarray,
    flux: np.ndarray,
    sigma: np.ndarray,
    null_parameters: np.ndarray,
) -> tuple[float, float, float]:
    null_chi2 = finite.profile(
        null_parameters, t, flux, sigma, False
    )
    objective = lambda epsilon: finite.profile(
        np.r_[null_parameters, epsilon], t, flux, sigma, True
    )
    intervals = [(-0.05, -1e-8), (-1e-8, 0.05)]
    candidates = [(0.0, null_chi2)]
    for lower, upper in intervals:
        result = minimize_scalar(
            objective,
            bounds=(lower, upper),
            method="bounded",
            options={"xatol": 1e-7, "maxiter": 100},
        )
        candidates.append((float(result.x), float(result.fun)))
    epsilon, alt_chi2 = min(candidates, key=lambda item: item[1])
    return float(null_chi2), alt_chi2, epsilon


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
    finite.main()
    central = json.loads(CENTRAL.read_text())
    phot = clock.load_photometry()
    t, mag, mag_error = phot.T
    flux = 10 ** (-0.4 * (mag - np.median(mag)))
    sigma = flux * np.log(10) * 0.4 * mag_error
    null_fit = finite.fit(t, flux, sigma, False)
    null_parameters = np.asarray(null_fit["_parameters"])
    observed_null, observed_alt, observed_epsilon = conditional_clock_fit(
        t, flux, sigma, null_parameters
    )
    observed_delta = observed_null - observed_alt
    mean = fitted_mean(t, flux, sigma, null_parameters)
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
            null_chi2, alt_chi2, mock_epsilon = conditional_clock_fit(
                t, mock_flux, sigma, null_parameters
            )
            rows.append(
                {
                    "mock": index,
                    "delta_chi2": max(0.0, null_chi2 - alt_chi2),
                    "epsilon": mock_epsilon,
                }
            )
        families.append(
            {
                "null_family": family,
                "mock_count": N_MOCKS,
                "empirical_improvement_p": (
                    1
                    + sum(row["delta_chi2"] >= observed_delta for row in rows)
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
        "schema": "Paper 7 OGLE-2004-BLG-081 finite-tangent clock null v1",
        "seed": SEED,
        "observed_delta_chi2": observed_delta,
        "observed_epsilon": observed_epsilon,
        "mock_count_per_family": N_MOCKS,
        "total_mock_light_curves": 2 * N_MOCKS,
        "nonlinear_nuisance_profiled_in_each_mock": False,
        "conditional_on_frozen_finite_tangent_null": True,
        "families": families,
        "survives_finite_tangent_statistical_null": survives,
        "exact_binary_source_model_executed": False,
        "verdict": (
            "FINITE_TANGENT_CONDITIONAL_CLOCK_SURVIVAL"
            if survives
            else "CLOCK_CANDIDATE_FAILS_FINITE_TANGENT_IDENTIFIABILITY"
        ),
        "claim_boundary": (
            "This finite conditional calibration freezes the nonlinear lens "
            "and ephemeris nuisance at the observed finite-tangent null. It "
            "profiles the full linear shape and clock coefficient but is not "
            "a fully reprofiled p-value or an exact binary-source calculation."
        ),
        "next_finite_action": (
            "Close OGLE-2004-BLG-081 as a positive clock result. Preserve it "
            "as a same-source method prototype; require a new event whose "
            "clock coefficient is locally nonzero after shape conditioning."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    for row in families:
        print(
            row["null_family"],
            f"p_delta={row['empirical_improvement_p']:.4f}",
            f"p_rate={row['empirical_two_sided_rate_p']:.4f}",
        )


if __name__ == "__main__":
    main()
