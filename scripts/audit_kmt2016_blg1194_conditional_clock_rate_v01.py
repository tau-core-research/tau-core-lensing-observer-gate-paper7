#!/usr/bin/env python3
"""Conditional local clock-rate audit for KMT-2016-BLG-1194."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import erf

import audit_kmt2016_blg1194_variability_ownership_v01 as ownership


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_kmt2016_blg1194_conditional_clock_rate_v1"
)
HARMONICS = 8
EPSILON_GRID = np.linspace(-0.002, 0.002, 401)


def load_sites() -> list[tuple[str, np.ndarray, ...]]:
    sites = []
    for name, data in ownership.load_sites():
        time, flux, error, _, _ = ownership.prepare(data)
        sites.append((name, time, flux, error))
    return sites


def magnification(
    time: np.ndarray, t0: float, t_e: float, u0: float
) -> np.ndarray:
    u = np.sqrt(u0**2 + ((time - t0) / t_e) ** 2)
    return (u**2 + 2) / (u * np.sqrt(u**2 + 4))


def phase(
    time: np.ndarray,
    t0: float,
    t_e: float,
    epsilon: float,
    frequency_correction: float,
    quadratic_drift: float,
) -> np.ndarray:
    x = (time - t0) / t_e
    scaled = (time - ownership.EPOCH) / 1000
    cycles = (
        (time - ownership.EPOCH) / ownership.PERIOD
        + frequency_correction * scaled
        + quadratic_drift * scaled**2
        + epsilon
        * t_e
        / ownership.PERIOD
        * np.sqrt(np.pi / 2)
        * erf(x / np.sqrt(2))
    )
    return 2 * np.pi * cycles


def profile(
    nonlinear: np.ndarray,
    sites: list[tuple[str, np.ndarray, ...]],
    epsilon: float,
) -> tuple[float, list[float]]:
    t0, log_t_e, log_u0, frequency_correction, quadratic_drift = nonlinear
    t_e, u0 = np.exp(log_t_e), np.exp(log_u0)
    columns_per_site = 3 + 2 * HARMONICS
    blocks = []
    fluxes = []
    errors = []
    site_slices = []
    start = 0
    for site_index, (_, time, flux, error) in enumerate(sites):
        amplification = magnification(time, t0, t_e, u0)
        phi = phase(
            time,
            t0,
            t_e,
            epsilon,
            frequency_correction,
            quadratic_drift,
        )
        matrix = np.zeros(
            (len(time), len(sites) * columns_per_site), dtype=float
        )
        offset = site_index * columns_per_site
        matrix[:, offset] = amplification
        matrix[:, offset + 1] = 1
        matrix[:, offset + 2] = (time - t0) / 200
        for order in range(1, HARMONICS + 1):
            matrix[:, offset + 1 + 2 * order] = (
                amplification * np.cos(order * phi)
            )
            matrix[:, offset + 2 + 2 * order] = (
                amplification * np.sin(order * phi)
            )
        blocks.append(matrix)
        fluxes.append(flux)
        errors.append(error)
        site_slices.append(slice(start, start + len(time)))
        start += len(time)

    matrix = np.vstack(blocks)
    flux = np.concatenate(fluxes)
    error = np.concatenate(errors)
    coefficients = np.linalg.lstsq(
        matrix / error[:, None], flux / error, rcond=None
    )[0]
    fitted = np.sum(matrix * coefficients[None, :], axis=1)
    residual = (flux - fitted) / error
    site_chi2 = [
        float(np.sum(np.square(residual[site_slice])))
        for site_slice in site_slices
    ]
    return float(np.sum(site_chi2)), site_chi2


def fit_null(
    sites: list[tuple[str, np.ndarray, ...]]
) -> tuple[np.ndarray, float, list[float]]:
    start = np.array(
        [
            ownership.T0,
            np.log(ownership.TE),
            np.log(ownership.U0),
            0.0,
            0.0,
        ]
    )
    objective = lambda values: profile(values, sites, 0.0)[0]
    fit = minimize(
        objective,
        start,
        method="Nelder-Mead",
        options={"maxiter": 3000, "xatol": 1e-8, "fatol": 1e-5},
    )
    chi2, site_chi2 = profile(fit.x, sites, 0.0)
    return np.asarray(fit.x), chi2, site_chi2


def main() -> None:
    sites = load_sites()
    parameters, null_chi2, null_site_chi2 = fit_null(sites)
    profile_rows = []
    for epsilon in EPSILON_GRID:
        chi2, site_chi2 = profile(parameters, sites, float(epsilon))
        profile_rows.append(
            {
                "epsilon": float(epsilon),
                "chi2": chi2,
                "delta_chi2_vs_null": null_chi2 - chi2,
                "site_chi2": site_chi2,
            }
        )
    zero_row = min(profile_rows, key=lambda row: abs(row["epsilon"]))
    best = min([zero_row, *profile_rows], key=lambda row: row["chi2"])
    locally_identified = (
        abs(best["epsilon"]) > 1e-8
        and best["delta_chi2_vs_null"] > 3.84
    )
    point_count = sum(len(site[1]) for site in sites)
    linear_parameters = len(sites) * (3 + 2 * HARMONICS)
    result = {
        "schema": "Paper 7 KMT-2016-BLG-1194 conditional clock rate v1",
        "event": ownership.EVENT,
        "data_points_after_quality_filter": point_count,
        "frozen_rrc_period_days": ownership.PERIOD,
        "harmonics_per_site": HARMONICS,
        "site_specific_linear_model": (
            "source flux, blend flux, slow linear calibration, and amplified "
            "RRc Fourier coefficients"
        ),
        "profiled_no_clock_parameters": {
            "t0_hjd_minus_2450000": float(parameters[0]),
            "tE_days": float(np.exp(parameters[1])),
            "u0": float(np.exp(parameters[2])),
            "frequency_correction_cycles_per_1000d": float(parameters[3]),
            "quadratic_drift_cycles_per_1000d2": float(parameters[4]),
        },
        "null_chi2": null_chi2,
        "null_degrees_of_freedom": (
            point_count - linear_parameters - len(parameters)
        ),
        "null_reduced_chi2": (
            null_chi2 / (point_count - linear_parameters - len(parameters))
        ),
        "null_site_chi2": null_site_chi2,
        "localized_rate_definition": (
            "d(cycle)/dt gains "
            "epsilon*exp(-0.5*((t-t0)/tE)^2)/period"
        ),
        "epsilon_grid": {
            "minimum": float(EPSILON_GRID[0]),
            "maximum": float(EPSILON_GRID[-1]),
            "points": len(EPSILON_GRID),
            "maximum_asymptotic_phase_step_cycles": float(
                EPSILON_GRID[-1]
                * np.exp(parameters[1])
                / ownership.PERIOD
                * np.sqrt(2 * np.pi)
            ),
        },
        "best_epsilon": best["epsilon"],
        "best_delta_chi2": best["delta_chi2_vs_null"],
        "passes_local_clock_identifiability_precheck": locally_identified,
        "verdict": (
            "KMT1194_LOCAL_CLOCK_CANDIDATE"
            if locally_identified
            else "KMT1194_CONDITIONAL_CLOCK_NULL"
        ),
        "claim_boundary": (
            "The scan conditions on the enriched observed no-clock geometry. "
            "Its large reduced chi-square shows remaining source-shape or "
            "photometric misspecification. A nonzero result would require "
            "mock calibration; a zero result closes this local clock direction "
            "without falsifying common-mode observer dependence in general."
        ),
        "next_finite_action": (
            "If the optimum is zero, preserve KMT-2016-BLG-1194 as an "
            "ownership-certified negative control and stop this event. If it "
            "is nonzero, calibrate the unchanged statistic with site-wise "
            "parametric and block-residual unit-clock mocks."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("epsilon:", result["best_epsilon"])
    print("delta_chi2:", result["best_delta_chi2"])
    print("reduced_chi2:", result["null_reduced_chi2"])


if __name__ == "__main__":
    main()
