#!/usr/bin/env python3
"""Transfer the finite-source clock criterion to two replacement OGLE events."""

from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, minimize, minimize_scalar

import audit_ogle2004_blg081_finite_source_clock_discriminator_v01 as finite
import audit_ogle2004_blg081_local_clock_rate_v01 as clock


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data/external/ogle_ews_periodic"
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle_replacement_same_source_clock_candidates_v1"
)
EVENTS = {
    "2002-BLG-103": {
        "period_days": 0.82756,
        "phase_zero_hjd": 2452124.72705,
        "t0_hjd": 2452456.915,
        "tE_days": 74.904,
        "u0": 0.051,
        "ews_blend_fraction": 0.891,
    },
    "2004-BLG-390": {
        "period_days": 0.34825,
        "phase_zero_hjd": 2452128.58350,
        "t0_hjd": 2453212.567,
        "tE_days": 28.873,
        "u0": 0.412,
        "ews_blend_fraction": 1.0,
    },
}


def load(event: str) -> np.ndarray:
    path = DATA_DIR / f"{event}.tar.gz"
    with tarfile.open(path, "r:gz") as archive:
        name = next(
            member for member in archive.getnames() if member.endswith("phot.dat")
        )
        handle = archive.extractfile(name)
        if handle is None:
            raise RuntimeError(f"Cannot extract {event} photometry")
        return np.loadtxt(io.BytesIO(handle.read()))


def fit_shape_null(
    t: np.ndarray,
    flux: np.ndarray,
    sigma: np.ndarray,
    event: dict,
) -> tuple[float, np.ndarray]:
    bounds = [
        (event["t0_hjd"] - 0.25 * event["tE_days"],
         event["t0_hjd"] + 0.25 * event["tE_days"]),
        (np.log(0.5 * event["tE_days"]), np.log(2 * event["tE_days"])),
        (np.log(max(0.01, 0.25 * event["u0"])),
         np.log(min(1.5, 4 * event["u0"]))),
        (-1.0, 1.0),
        (-0.5, 0.5),
    ]
    objective = lambda values: finite.profile(
        values, t, flux, sigma, False
    )
    global_fit = differential_evolution(
        objective,
        bounds,
        seed=70408104,
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
        bounds=bounds,
        options={"maxiter": 3000, "ftol": 1e-12, "gtol": 1e-8},
    )
    candidates = [global_fit.x, local.x]
    values = min(candidates, key=objective)
    return float(objective(values)), np.asarray(values)


def conditional_clock(
    t: np.ndarray,
    flux: np.ndarray,
    sigma: np.ndarray,
    null_parameters: np.ndarray,
) -> tuple[float, float]:
    null_chi2 = finite.profile(
        null_parameters, t, flux, sigma, False
    )
    objective = lambda epsilon: finite.profile(
        np.r_[null_parameters, epsilon], t, flux, sigma, True
    )
    candidates = [(0.0, null_chi2)]
    for lower, upper in ((-0.05, -1e-8), (-1e-8, 0.05)):
        result = minimize_scalar(
            objective,
            bounds=(lower, upper),
            method="bounded",
            options={"xatol": 1e-8, "maxiter": 120},
        )
        candidates.append((float(result.x), float(result.fun)))
    epsilon, alt_chi2 = min(candidates, key=lambda item: item[1])
    return epsilon, max(0.0, null_chi2 - alt_chi2)


def main() -> None:
    rows = []
    for name, event in EVENTS.items():
        clock.PERIOD = event["period_days"]
        clock.PHASE_ZERO = event["phase_zero_hjd"]
        phot = load(name)
        t, mag, mag_error = phot.T
        flux = 10 ** (-0.4 * (mag - np.median(mag)))
        sigma = flux * np.log(10) * 0.4 * mag_error
        null_chi2, parameters = fit_shape_null(
            t, flux, sigma, event
        )
        epsilon, delta_chi2 = conditional_clock(
            t, flux, sigma, parameters
        )
        locally_nonzero = abs(epsilon) > 1e-6 and delta_chi2 > 3.84
        rows.append(
            {
                "event": name,
                **event,
                "data_points": int(len(t)),
                "finite_tangent_null_chi2": null_chi2,
                "finite_tangent_null_reduced_chi2": (
                    null_chi2 / (len(t) - (2 + 6 * clock.HARMONICS + 5))
                ),
                "conditional_clock_epsilon": epsilon,
                "conditional_clock_delta_chi2": delta_chi2,
                "passes_local_clock_identifiability_precheck": locally_nonzero,
            }
        )

    survivors = [
        row["event"]
        for row in rows
        if row["passes_local_clock_identifiability_precheck"]
    ]
    result = {
        "schema": "Paper 7 OGLE replacement same-source clock candidates v1",
        "frozen_transfer_rule": (
            "Same 8-harmonic even/odd finite-source tangent and conditional "
            "localized epsilon scan used to close OGLE-2004-BLG-081."
        ),
        "excluded_before_fit": {
            "2004-BLG-101": (
                "Wyrzykowski et al. (2006) Table 3 assigns periodic "
                "variability to the blend, not the lensed source."
            )
        },
        "events": rows,
        "survivors": survivors,
        "verdict": (
            "REPLACEMENT_LOCAL_CLOCK_CANDIDATE_EXISTS"
            if survivors
            else "NO_REPLACEMENT_EVENT_PASSES_LOCAL_CLOCK_PRECHECK"
        ),
        "claim_boundary": (
            "A survivor is only eligible for null calibration. The historical "
            "paper did not uniquely fit source ownership for these events, "
            "and the finite tangent is not an exact binary-source model."
        ),
        "next_finite_action": (
            "Calibrate only surviving events under their own finite-tangent "
            "null; if none survive, close the current public OGLE sample."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    for row in rows:
        print(
            row["event"],
            f"epsilon={row['conditional_clock_epsilon']:.8g}",
            f"delta_chi2={row['conditional_clock_delta_chi2']:.3f}",
            row["passes_local_clock_identifiability_precheck"],
        )


if __name__ == "__main__":
    main()
