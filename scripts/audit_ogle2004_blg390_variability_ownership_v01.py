#!/usr/bin/env python3
"""Test whether BLG-390 periodic variability follows source magnification."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, minimize

import audit_ogle2004_blg081_finite_source_clock_discriminator_v01 as finite
import audit_ogle2004_blg081_local_clock_rate_v01 as clock
import audit_ogle_replacement_same_source_clock_candidates_v01 as replacement


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg390_variability_ownership_v1"
)
EVENT_NAME = "2004-BLG-390"


def bounds(event: dict) -> list[tuple[float, float]]:
    return [
        (event["t0_hjd"] - 0.25 * event["tE_days"],
         event["t0_hjd"] + 0.25 * event["tE_days"]),
        (np.log(0.5 * event["tE_days"]), np.log(2 * event["tE_days"])),
        (np.log(max(0.01, 0.25 * event["u0"])),
         np.log(min(1.5, 4 * event["u0"]))),
        (-1.0, 1.0),
        (-0.5, 0.5),
    ]


def profile(
    values: np.ndarray,
    t: np.ndarray,
    flux: np.ndarray,
    sigma: np.ndarray,
    ownership: str,
) -> float:
    t0, log_t_e, log_u0, alpha, beta = values
    t_e, u0 = np.exp(log_t_e), np.exp(log_u0)
    a = clock.magnification(t, t0, t_e, u0)
    phi = clock.phase(t, t0, t_e, 0.0, alpha, beta)
    matrix = clock.design(a, phi, ownership)
    coeff, *_ = np.linalg.lstsq(
        matrix / sigma[:, None], flux / sigma, rcond=None
    )
    residual = (flux - matrix @ coeff) / sigma
    return float(residual @ residual)


def fit(
    t: np.ndarray,
    flux: np.ndarray,
    sigma: np.ndarray,
    event: dict,
    ownership: str,
) -> dict:
    objective = lambda values: profile(
        values, t, flux, sigma, ownership
    )
    limit = bounds(event)
    global_fit = differential_evolution(
        objective,
        limit,
        seed=70408391,
        maxiter=300,
        popsize=16,
        tol=1e-8,
        workers=1,
        polish=True,
    )
    local = minimize(
        objective,
        global_fit.x,
        method="L-BFGS-B",
        bounds=limit,
        options={"maxiter": 3000, "ftol": 1e-12, "gtol": 1e-8},
    )
    values = min([global_fit.x, local.x], key=objective)
    chi2 = float(objective(values))
    parameter_count = 5 + 2 + 2 * clock.HARMONICS
    return {
        "ownership": ownership,
        "chi2": chi2,
        "bic": chi2 + parameter_count * np.log(len(t)),
        "parameter_count": parameter_count,
        "t0_hjd": float(values[0]),
        "tE_days": float(np.exp(values[1])),
        "u0": float(np.exp(values[2])),
    }


def main() -> None:
    event = replacement.EVENTS[EVENT_NAME]
    clock.PERIOD = event["period_days"]
    clock.PHASE_ZERO = event["phase_zero_hjd"]
    phot = replacement.load(EVENT_NAME)
    t, mag, mag_error = phot.T
    flux = 10 ** (-0.4 * (mag - np.median(mag)))
    sigma = flux * np.log(10) * 0.4 * mag_error
    source = fit(t, flux, sigma, event, "source")
    blend = fit(t, flux, sigma, event, "blend")
    finite_chi2, _ = replacement.fit_shape_null(t, flux, sigma, event)
    finite_parameter_count = 5 + 2 + 6 * clock.HARMONICS
    finite_bic = finite_chi2 + finite_parameter_count * np.log(len(t))
    delta_bic_source_over_blend = blend["bic"] - source["bic"]
    source_preferred = bool(delta_bic_source_over_blend >= 10)
    result = {
        "schema": "Paper 7 OGLE-2004-BLG-390 variability ownership v1",
        "event": EVENT_NAME,
        "ews_blend_fraction": event["ews_blend_fraction"],
        "equal_complexity_models": {
            "variable_lensed_source": source,
            "variable_unlensed_blend": blend,
        },
        "delta_bic_source_over_blend": delta_bic_source_over_blend,
        "source_ownership_strongly_preferred": source_preferred,
        "finite_tangent_source_model": {
            "chi2": finite_chi2,
            "bic": finite_bic,
            "parameter_count": finite_parameter_count,
        },
        "source_ownership_proved": False,
        "verdict": (
            "SOURCE_VARIABILITY_STRONGLY_PREFERRED__NOT_UNIQUE"
            if source_preferred
            else "SOURCE_VARIABILITY_OWNERSHIP_UNRESOLVED"
        ),
        "claim_boundary": (
            "BIC preference and EWS f_bl=1 support source ownership but do not "
            "prove it. A mixed variable-source plus variable-blend model and "
            "independent color/astrometric information are unavailable."
        ),
        "next_finite_action": (
            "Run frozen robustness checks over harmonic order, event window "
            "and block length. Promote only if the local epsilon remains "
            "nonzero with stable sign and source ownership remains preferred."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("delta_bic_source_over_blend:", f"{delta_bic_source_over_blend:.3f}")
    print("source_chi2:", f"{source['chi2']:.3f}")
    print("blend_chi2:", f"{blend['chi2']:.3f}")
    print("finite_source_chi2:", f"{finite_chi2:.3f}")


if __name__ == "__main__":
    main()
