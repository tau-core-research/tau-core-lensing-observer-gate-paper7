#!/usr/bin/env python3
"""Transfer an independently frozen OGLE RRc template to KMT-2016-BLG-1194."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

import audit_kmt2016_blg1194_conditional_clock_rate_v01 as clock
import audit_kmt2016_blg1194_variability_ownership_v01 as ownership


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data/external/kmt2016_ogle_periodic_crossmatch"
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_kmt2016_blg1194_ogle_template_clock_transfer_v1"
)
OGLE_URL = (
    "https://www.astrouw.edu.pl/ogle/ogle4/OCVS/blg/rrlyr/phot/I/"
    "OGLE-BLG-RRLYR-29501.dat"
)
OGLE_SHA256 = "e52acfa7392b4719ac6f5f6479ec0ca6bdef634c4a0344bb02e8d212547d110a"
HARMONICS = 8
EPSILON_GRID = np.linspace(-0.002, 0.002, 401)


def acquire_ogle() -> Path:
    path = DATA_DIR / "OGLE-BLG-RRLYR-29501_I.dat"
    if not path.exists():
        urllib.request.urlretrieve(OGLE_URL, path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != OGLE_SHA256:
        raise RuntimeError(f"Unexpected OGLE template SHA-256: {digest}")
    return path


def freeze_template() -> tuple[np.ndarray, float]:
    data = np.loadtxt(acquire_ogle())
    time, magnitude, error = data.T
    flux = 10 ** (-0.4 * (magnitude - np.median(magnitude)))
    flux_error = flux * np.log(10) * 0.4 * error
    phi = 2 * np.pi * (time - ownership.EPOCH) / ownership.PERIOD
    columns = [np.ones_like(phi)]
    for order in range(1, HARMONICS + 1):
        columns.extend([np.cos(order * phi), np.sin(order * phi)])
    matrix = np.column_stack(columns)
    coefficients = np.linalg.lstsq(
        matrix / flux_error[:, None], flux / flux_error, rcond=None
    )[0]
    fitted = np.sum(matrix * coefficients[None, :], axis=1)
    residual = (flux - fitted) / flux_error
    return coefficients, float(np.sum(np.square(residual)))


def evaluate_template(phi: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    value = np.full_like(phi, coefficients[0])
    for order in range(1, HARMONICS + 1):
        value += coefficients[2 * order - 1] * np.cos(order * phi)
        value += coefficients[2 * order] * np.sin(order * phi)
    return value - coefficients[0]


def profile(
    nonlinear: np.ndarray,
    sites: list[tuple[str, np.ndarray, ...]],
    template_coefficients: np.ndarray,
    epsilon: float,
) -> tuple[float, list[float], list[int]]:
    t0, log_t_e, log_u0, frequency_correction, quadratic_drift = nonlinear
    t_e, u0 = np.exp(log_t_e), np.exp(log_u0)
    blocks = []
    fluxes = []
    errors = []
    lengths = []
    for site_index, (_, time, flux, error) in enumerate(sites):
        amplification = clock.magnification(time, t0, t_e, u0)
        phi = clock.phase(
            time,
            t0,
            t_e,
            epsilon,
            frequency_correction,
            quadratic_drift,
        )
        template = evaluate_template(phi, template_coefficients)
        matrix = np.zeros((len(time), 4 * len(sites)))
        offset = 4 * site_index
        matrix[:, offset] = amplification
        matrix[:, offset + 1] = 1
        matrix[:, offset + 2] = (time - t0) / 200
        matrix[:, offset + 3] = amplification * template
        blocks.append(matrix)
        fluxes.append(flux)
        errors.append(error)
        lengths.append(len(time))
    matrix = np.vstack(blocks)
    flux = np.concatenate(fluxes)
    error = np.concatenate(errors)
    coefficients = np.linalg.lstsq(
        matrix / error[:, None], flux / error, rcond=None
    )[0]
    fitted = np.sum(matrix * coefficients[None, :], axis=1)
    residual = (flux - fitted) / error
    site_chi2 = []
    start = 0
    for length in lengths:
        site_chi2.append(
            float(np.sum(np.square(residual[start : start + length])))
        )
        start += length
    return float(np.sum(site_chi2)), site_chi2, lengths


def main() -> None:
    template_coefficients, template_chi2 = freeze_template()
    sites = clock.load_sites()
    start = np.array(
        [
            ownership.T0,
            np.log(ownership.TE),
            np.log(ownership.U0),
            0.0,
            0.0,
        ]
    )
    objective = lambda values: profile(
        values, sites, template_coefficients, 0.0
    )[0]
    fit = minimize(
        objective,
        start,
        method="Nelder-Mead",
        options={"maxiter": 3000, "xatol": 1e-8, "fatol": 1e-5},
    )
    parameters = np.asarray(fit.x)
    null_chi2, null_site_chi2, site_lengths = profile(
        parameters, sites, template_coefficients, 0.0
    )
    rows = []
    for epsilon in EPSILON_GRID:
        chi2, site_chi2, _ = profile(
            parameters, sites, template_coefficients, float(epsilon)
        )
        raw_delta = null_chi2 - chi2
        rescaled_delta = sum(
            (null_value - alt_value)
            / (null_value / max(1, length - 4))
            for null_value, alt_value, length in zip(
                null_site_chi2, site_chi2, site_lengths
            )
        )
        rows.append(
            {
                "epsilon": float(epsilon),
                "raw_delta_chi2": raw_delta,
                "site_error_rescaled_delta_chi2": rescaled_delta,
            }
        )
    zero = min(rows, key=lambda row: abs(row["epsilon"]))
    best = max([zero, *rows], key=lambda row: row["site_error_rescaled_delta_chi2"])
    locally_identified = (
        abs(best["epsilon"]) > 1e-8
        and best["site_error_rescaled_delta_chi2"] > 3.84
    )
    points = sum(site_lengths)
    degrees_of_freedom = points - 4 * len(sites) - len(parameters)
    result = {
        "schema": "Paper 7 KMT-2016-BLG-1194 OGLE-template clock transfer v1",
        "event": ownership.EVENT,
        "template_source": "OGLE-BLG-RRLYR-29501 long-baseline I-band photometry",
        "template_sha256": OGLE_SHA256,
        "template_points": 867,
        "template_harmonics": HARMONICS,
        "template_chi2": template_chi2,
        "kmt_points": points,
        "site_specific_kmt_parameters": (
            "source flux, blend flux, slow linear calibration, and one "
            "amplitude for the fixed OGLE waveform"
        ),
        "profiled_no_clock_parameters": {
            "t0_hjd_minus_2450000": float(parameters[0]),
            "tE_days": float(np.exp(parameters[1])),
            "u0": float(np.exp(parameters[2])),
            "frequency_correction_cycles_per_1000d": float(parameters[3]),
            "quadratic_drift_cycles_per_1000d2": float(parameters[4]),
        },
        "null_chi2": null_chi2,
        "null_reduced_chi2": null_chi2 / degrees_of_freedom,
        "best_epsilon": best["epsilon"],
        "best_raw_delta_chi2": best["raw_delta_chi2"],
        "best_site_error_rescaled_delta_chi2": best[
            "site_error_rescaled_delta_chi2"
        ],
        "passes_local_clock_identifiability_precheck": locally_identified,
        "verdict": (
            "INDEPENDENT_OGLE_TEMPLATE_CLOCK_CANDIDATE"
            if locally_identified
            else "INDEPENDENT_OGLE_TEMPLATE_CLOCK_NULL"
        ),
        "claim_boundary": (
            "The source waveform was frozen independently of KMT lensing. "
            "Site-wise error rescaling prevents underestimated pySIS errors "
            "from creating formal significance. The result remains conditional "
            "on a point-lens transfer and is not a Tau-specific test by itself."
        ),
        "next_finite_action": (
            "If null, close KMT-2016-BLG-1194 without further waveform "
            "enrichment. If nonzero, require sign stability against harmonic "
            "order and site leave-one-out before mocks."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("epsilon:", result["best_epsilon"])
    print(
        "rescaled_delta_chi2:",
        result["best_site_error_rescaled_delta_chi2"],
    )
    print("reduced_chi2:", result["null_reduced_chi2"])


if __name__ == "__main__":
    main()
