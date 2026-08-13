#!/usr/bin/env python3
"""Diagnostic localized clock-rate fit for eclipsing OGLE-2004-BLG-081."""

from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, minimize
from scipy.special import erf


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data/external/ogle_ews_periodic/2004-BLG-081.tar.gz"
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg081_local_clock_rate_v1"
)
PERIOD = 3.96628
PHASE_ZERO = 2452406.8730
HARMONICS = 8


def load_photometry() -> np.ndarray:
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        names = [name for name in archive.getnames() if name.endswith("phot.dat")]
        handle = archive.extractfile(names[0])
        if handle is None:
            raise RuntimeError("Cannot extract OGLE photometry")
        return np.loadtxt(io.BytesIO(handle.read()))


def magnification(t: np.ndarray, t0: float, t_e: float, u0: float) -> np.ndarray:
    u = np.sqrt(u0**2 + ((t - t0) / t_e) ** 2)
    return (u**2 + 2) / (u * np.sqrt(u**2 + 4))


def phase(
    t: np.ndarray,
    t0: float,
    t_e: float,
    epsilon: float,
    alpha: float,
    beta: float,
) -> np.ndarray:
    base_cycles = (t - PHASE_ZERO) / PERIOD
    x = (t - t0) / t_e
    localized_cycles = (
        epsilon * t_e / PERIOD * np.sqrt(np.pi / 2) * erf(x / np.sqrt(2))
    )
    span = 1000.0
    scaled_time = (t - PHASE_ZERO) / span
    drift_cycles = alpha * scaled_time + beta * scaled_time**2
    return 2 * np.pi * (base_cycles + localized_cycles + drift_cycles)


def design(a: np.ndarray, phi: np.ndarray, ownership: str) -> np.ndarray:
    trig = []
    for k in range(1, HARMONICS + 1):
        trig.extend([np.cos(k * phi), np.sin(k * phi)])
    periodic = np.column_stack(trig)
    if ownership == "source":
        return np.column_stack([np.ones_like(a), a, a[:, None] * periodic])
    return np.column_stack([np.ones_like(a), a, periodic])


def profile_chi2(
    nonlinear: np.ndarray,
    t: np.ndarray,
    flux: np.ndarray,
    sigma: np.ndarray,
    ownership: str,
    allow_clock: bool,
) -> float:
    t0, log_t_e, log_u0, alpha, beta = nonlinear[:5]
    epsilon = nonlinear[5] if allow_clock else 0.0
    t_e, u0 = np.exp(log_t_e), np.exp(log_u0)
    a = magnification(t, t0, t_e, u0)
    phi = phase(t, t0, t_e, epsilon, alpha, beta)
    matrix = design(a, phi, ownership)
    weighted = matrix / sigma[:, None]
    coeff, *_ = np.linalg.lstsq(weighted, flux / sigma, rcond=None)
    residual = (flux - matrix @ coeff) / sigma
    return float(residual @ residual)


def fit(
    t: np.ndarray,
    flux: np.ndarray,
    sigma: np.ndarray,
    ownership: str,
    allow_clock: bool,
    initial: np.ndarray | None = None,
) -> dict:
    bounds = [
        (2453100.0, 2453112.0),
        (np.log(60.0), np.log(150.0)),
        (np.log(0.05), np.log(0.5)),
        (-1.0, 1.0),
        (-0.5, 0.5),
    ]
    if allow_clock:
        bounds.append((-0.05, 0.05))
    objective = lambda x: profile_chi2(
        x, t, flux, sigma, ownership, allow_clock
    )
    global_fit = differential_evolution(
        objective,
        bounds,
        seed=704081,
        polish=True,
        workers=1,
        maxiter=400,
        popsize=20,
        tol=1e-9,
    )
    starts = [global_fit.x]
    if initial is not None:
        starts.append(initial)
    local_fits = [
        minimize(
            objective,
            start,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 5000, "ftol": 1e-12, "gtol": 1e-8},
        )
        for start in starts
    ]
    candidate_values = [global_fit.x, *starts, *(fit.x for fit in local_fits)]
    values = min(candidate_values, key=objective)
    nonlinear_count = 6 if allow_clock else 5
    linear_count = 2 + 2 * HARMONICS
    chi2 = float(objective(values))
    return {
        "ownership": ownership,
        "allow_localized_clock_rate": allow_clock,
        "chi2": chi2,
        "bic": chi2 + (nonlinear_count + linear_count) * np.log(len(t)),
        "t0_hjd": float(values[0]),
        "tE_days": float(np.exp(values[1])),
        "u0": float(np.exp(values[2])),
        "linear_ephemeris_correction_cycles_per_1000d": float(values[3]),
        "quadratic_phase_drift_cycles_per_1000d2": float(values[4]),
        "localized_fractional_clock_rate": (
            float(values[5]) if allow_clock else 0.0
        ),
        "optimizer_success": bool(
            global_fit.success or any(fit.success for fit in local_fits)
        ),
        "_profile_parameters": [float(value) for value in values],
    }


def main() -> None:
    phot = load_photometry()
    t, mag, mag_error = phot.T
    flux = 10 ** (-0.4 * (mag - np.median(mag)))
    sigma = flux * np.log(10) * 0.4 * mag_error
    fits = []
    for ownership in ("source", "blend"):
        null = fit(t, flux, sigma, ownership, False)
        alternative_start = np.asarray(null["_profile_parameters"] + [0.0])
        alternative = fit(
            t, flux, sigma, ownership, True, initial=alternative_start
        )
        alternative["delta_chi2_vs_null"] = null["chi2"] - alternative["chi2"]
        alternative["delta_bic_vs_null"] = null["bic"] - alternative["bic"]
        null.pop("_profile_parameters")
        alternative.pop("_profile_parameters")
        fits.extend([null, alternative])

    source_null, source_alt, blend_null, blend_alt = fits
    result = {
        "schema": "Paper 7 OGLE-2004-BLG-081 localized clock-rate diagnostic v1",
        "event": "OGLE-2004-BLG-081 / OGLE180540.47-273427.5",
        "data_points": int(len(t)),
        "frozen_period_days": PERIOD,
        "frozen_phase_zero_hjd": PHASE_ZERO,
        "periodic_waveform": f"weighted Fourier profile with {HARMONICS} harmonics",
        "localized_rate_gate": (
            "d(cycle)/dt gains epsilon*exp(-0.5*((t-t0)/tE)^2)/P"
        ),
        "slow_clock_control": (
            "linear ephemeris correction and quadratic phase drift fitted "
            "in every model"
        ),
        "fits": fits,
        "source_ownership_preferred_by_null_bic": (
            bool(source_null["bic"] < blend_null["bic"])
        ),
        "clock_rate_sign_consistent_across_ownership": (
            bool(
                np.sign(source_alt["localized_fractional_clock_rate"])
                == np.sign(blend_alt["localized_fractional_clock_rate"])
            )
        ),
        "clock_rate_test_executed": True,
        "null_calibration_executed": False,
        "verdict": "CENTRAL_DIAGNOSTIC_ONLY__NULL_CALIBRATION_REQUIRED",
        "claim_boundary": (
            "The fitted epsilon is not evidence for a clock effect. Its null "
            "distribution must be calibrated with cadence-preserving, "
            "heteroscedastic mocks including eclipse-shape mismatch, "
            "microlensing-parameter uncertainty and source/blend ownership."
        ),
        "next_finite_action": (
            "Generate source-frozen unit-clock mocks at the observed epochs "
            "from both ownership models and score the same profiled statistic."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    for row in (source_alt, blend_alt):
        print(
            row["ownership"],
            "epsilon=",
            f"{row['localized_fractional_clock_rate']:.6g}",
            "delta_bic=",
            f"{row['delta_bic_vs_null']:.3f}",
        )


if __name__ == "__main__":
    main()
