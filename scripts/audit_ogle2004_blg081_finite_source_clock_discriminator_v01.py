#!/usr/bin/env python3
"""Test the OGLE clock candidate against finite-source shape modulation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, minimize

import audit_ogle2004_blg081_local_clock_rate_v01 as clock


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg081_finite_source_clock_discriminator_v1"
)


def finite_tangent_design(
    t: np.ndarray,
    t0: float,
    t_e: float,
    u0: float,
    phi: np.ndarray,
) -> np.ndarray:
    a = clock.magnification(t, t0, t_e, u0)
    x = (t - t0) / t_e
    q_even = (a - 1) / np.max(a - 1)
    q_odd = x * q_even
    trig = []
    for k in range(1, clock.HARMONICS + 1):
        trig.extend([np.cos(k * phi), np.sin(k * phi)])
    periodic = np.column_stack(trig)
    base = np.column_stack([np.ones_like(a), a, a[:, None] * periodic])
    # First finite-source tangent: lens-strength and lens-direction dependent
    # modulation of every periodic source-shape coefficient.
    return np.column_stack(
        [
            base,
            (a * q_even)[:, None] * periodic,
            (a * q_odd)[:, None] * periodic,
        ]
    )


def profile(
    nonlinear: np.ndarray,
    t: np.ndarray,
    flux: np.ndarray,
    sigma: np.ndarray,
    allow_clock: bool,
) -> float:
    t0, log_t_e, log_u0, alpha, beta = nonlinear[:5]
    epsilon = nonlinear[5] if allow_clock else 0.0
    t_e, u0 = np.exp(log_t_e), np.exp(log_u0)
    phi = clock.phase(t, t0, t_e, epsilon, alpha, beta)
    matrix = finite_tangent_design(t, t0, t_e, u0, phi)
    coeff, *_ = np.linalg.lstsq(
        matrix / sigma[:, None], flux / sigma, rcond=None
    )
    residual = (flux - matrix @ coeff) / sigma
    return float(residual @ residual)


def fit(
    t: np.ndarray,
    flux: np.ndarray,
    sigma: np.ndarray,
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
    objective = lambda values: profile(
        values, t, flux, sigma, allow_clock
    )
    global_fit = differential_evolution(
        objective,
        bounds,
        seed=70408102,
        maxiter=400,
        popsize=20,
        tol=1e-9,
        workers=1,
        polish=True,
    )
    starts = [global_fit.x]
    if initial is not None:
        starts.append(initial)
    local = [
        minimize(
            objective,
            start,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 5000, "ftol": 1e-12, "gtol": 1e-8},
        )
        for start in starts
    ]
    candidates = [global_fit.x, *starts, *(result.x for result in local)]
    values = min(candidates, key=objective)
    chi2 = float(objective(values))
    linear_count = 2 + 6 * clock.HARMONICS
    nonlinear_count = 6 if allow_clock else 5
    return {
        "allow_localized_clock_rate": allow_clock,
        "chi2": chi2,
        "bic": chi2 + (linear_count + nonlinear_count) * np.log(len(t)),
        "linear_parameter_count": linear_count,
        "nonlinear_parameter_count": nonlinear_count,
        "t0_hjd": float(values[0]),
        "tE_days": float(np.exp(values[1])),
        "u0": float(np.exp(values[2])),
        "linear_ephemeris_correction_cycles_per_1000d": float(values[3]),
        "quadratic_phase_drift_cycles_per_1000d2": float(values[4]),
        "localized_fractional_clock_rate": (
            float(values[5]) if allow_clock else 0.0
        ),
        "_parameters": [float(value) for value in values],
    }


def main() -> None:
    clock.main()
    central = json.loads((clock.OUT_DIR / "summary.json").read_text())
    point_null = next(
        row
        for row in central["fits"]
        if row["ownership"] == "source"
        and not row["allow_localized_clock_rate"]
    )
    point_clock = next(
        row
        for row in central["fits"]
        if row["ownership"] == "source"
        and row["allow_localized_clock_rate"]
    )
    phot = clock.load_photometry()
    t, mag, mag_error = phot.T
    flux = 10 ** (-0.4 * (mag - np.median(mag)))
    sigma = flux * np.log(10) * 0.4 * mag_error

    shape_null = fit(t, flux, sigma, False)
    shape_clock = fit(
        t,
        flux,
        sigma,
        True,
        initial=np.asarray(shape_null["_parameters"] + [0.0]),
    )
    shape_null.pop("_parameters")
    shape_clock.pop("_parameters")
    delta_chi2 = shape_null["chi2"] - shape_clock["chi2"]
    delta_bic = shape_null["bic"] - shape_clock["bic"]
    absorbed = bool(delta_bic <= 0)
    result = {
        "schema": "Paper 7 OGLE-2004-BLG-081 finite-source clock discriminator v1",
        "models": {
            "point_source_no_clock": point_null,
            "point_source_with_clock": point_clock,
            "finite_tangent_no_clock": shape_null,
            "finite_tangent_with_clock": shape_clock,
        },
        "finite_tangent_definition": (
            "Each Fourier source-shape coefficient receives even and odd "
            "first-order modulation by normalized lens strength and signed "
            "lens position."
        ),
        "delta_chi2_clock_after_finite_tangent": delta_chi2,
        "delta_bic_clock_after_finite_tangent": delta_bic,
        "clock_rate_after_finite_tangent": shape_clock[
            "localized_fractional_clock_rate"
        ],
        "finite_tangent_absorbs_clock_candidate": absorbed,
        "exact_binary_source_finite_source_model_executed": False,
        "verdict": (
            "CLOCK_CANDIDATE_ABSORBED_BY_STANDARD_SHAPE_TANGENT"
            if absorbed
            else "CLOCK_COMPONENT_SURVIVES_FIRST_STANDARD_SHAPE_TANGENT"
        ),
        "claim_boundary": (
            "This is a flexible first-order finite-source discriminator, not "
            "an exact eclipsing-binary surface-brightness and lens-trajectory "
            "model. Survival cannot establish time distortion; absorption "
            "would close the current clock candidate."
        ),
        "next_finite_action": (
            "If the clock component survives, calibrate the nested statistic "
            "under the finite-tangent null before deciding whether an exact "
            "binary-source model is warranted."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("delta_chi2:", f"{delta_chi2:.3f}")
    print("delta_bic:", f"{delta_bic:.3f}")
    print(
        "epsilon:",
        f"{shape_clock['localized_fractional_clock_rate']:.8f}",
    )


if __name__ == "__main__":
    main()
