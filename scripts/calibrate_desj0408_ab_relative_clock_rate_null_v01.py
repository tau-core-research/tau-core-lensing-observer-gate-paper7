#!/usr/bin/env python3
"""Parametric unit-stretch calibration of the DES J0408 A/B clock audit."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.interpolate import UnivariateSpline


ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = ROOT / "scripts/audit_desj0408_ab_relative_clock_rate_v01.py"
AUDIT_SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_ab_relative_clock_rate_v1/summary.json"
)
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_ab_relative_clock_rate_null_calibration_v1"
)
N_MOCKS = 128
SEED = 2038040801


def load_audit_module():
    spec = importlib.util.spec_from_file_location("clock_audit", AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load clock audit module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    audit = load_audit_module()
    audit.acquire()
    data = audit.load_wfi()
    observed = json.loads(AUDIT_SUMMARY.read_text(encoding="utf-8"))
    central = observed["central_exploratory_fit"]

    t = data["mhjd"]
    pivot = float(np.mean(t))
    delay = float(central["shift_only_delay_days"])
    source = UnivariateSpline(
        t,
        data["mag_A"],
        w=1.0 / data["magerr_A"],
        s=len(t),
    )
    shifted_t = t - delay
    overlap = (shifted_t >= np.min(t)) & (shifted_t <= np.max(t))
    x = (t[overlap] - pivot) / 100.0
    design = np.stack([np.ones_like(x), x], axis=1)
    target = data["mag_B"][overlap] - source(shifted_t[overlap])
    variance = data["magerr_B"][overlap] ** 2 + 0.005**2
    whiten = 1.0 / np.sqrt(variance)
    trend_beta = np.linalg.lstsq(
        design * whiten[:, None], target * whiten, rcond=None
    )[0]

    rng = np.random.default_rng(SEED)
    rates = []
    improvements = []
    delays = []
    for _ in range(N_MOCKS):
        mock = {
            "mhjd": t.copy(),
            "magerr_A": data["magerr_A"].copy(),
            "magerr_B": data["magerr_B"].copy(),
        }
        mock["mag_A"] = source(t) + rng.normal(0.0, data["magerr_A"])
        slow_trend = trend_beta[0] + trend_beta[1] * (t - pivot) / 100.0
        mock["mag_B"] = (
            source(t - delay)
            + slow_trend
            + rng.normal(
                0.0, np.sqrt(data["magerr_B"] ** 2 + 0.005**2)
            )
        )
        fit = audit.fit_spec(mock, smoothing_factor=1.0, trend_degree=1)
        rates.append(fit["relative_clock_rate_B_over_A"])
        improvements.append(fit["delta_chi_square_one_extra_parameter"])
        delays.append(fit["shift_stretch_delay_days"])

    rates_array = np.asarray(rates)
    improvements_array = np.asarray(improvements)
    observed_rate = float(central["relative_clock_rate_B_over_A"])
    observed_improvement = float(
        central["delta_chi_square_one_extra_parameter"]
    )
    rate_p = float(
        (1 + np.count_nonzero(np.abs(rates_array - 1) >= abs(observed_rate - 1)))
        / (N_MOCKS + 1)
    )
    improvement_p = float(
        (1 + np.count_nonzero(improvements_array >= observed_improvement))
        / (N_MOCKS + 1)
    )
    result = {
        "schema": "paper7 DES J0408 A/B unit-stretch null calibration v1",
        "source_audit": str(AUDIT_SUMMARY.relative_to(ROOT)),
        "null_hypothesis": "relative_clock_rate_B_over_A=1",
        "mock_count": N_MOCKS,
        "random_seed": SEED,
        "frozen_estimator": {
            "source_spline_smoothing_factor_times_n": 1.0,
            "microlensing_polynomial_degree": 1,
            "delay_search_days": [100.0, 122.0],
            "stretch_search": [0.9, 1.1],
        },
        "mock_construction": (
            "unit-stretch fitted source spline plus fitted linear extrinsic "
            "trend, observed WFI epochs, observed heteroscedastic errors, and "
            "the audit's fixed 0.005 mag noise floor"
        ),
        "observed": {
            "relative_clock_rate_B_over_A": observed_rate,
            "delta_chi_square": observed_improvement,
        },
        "null_distribution": {
            "relative_clock_rate_quantiles_2p5_50_97p5": np.quantile(
                rates_array, [0.025, 0.5, 0.975]
            ).tolist(),
            "delta_chi_square_quantiles_2p5_50_97p5": np.quantile(
                improvements_array, [0.025, 0.5, 0.975]
            ).tolist(),
            "delay_quantiles_2p5_50_97p5_days": np.quantile(
                np.asarray(delays), [0.025, 0.5, 0.975]
            ).tolist(),
        },
        "empirical_two_sided_rate_p_value": rate_p,
        "empirical_improvement_p_value": improvement_p,
        "unit_stretch_rejected_under_parametric_mock": bool(
            rate_p < 0.05 and improvement_p < 0.05
        ),
        "tau_time_distortion_claim_allowed": False,
        "verdict": (
            "UNIT_STRETCH_REJECTED_CONDITIONALLY_ON_PARAMETRIC_MOCK"
            if rate_p < 0.05 and improvement_p < 0.05
            else "OBSERVED_STRETCH_NOT_UNUSUAL_UNDER_UNIT_STRETCH_PARAMETRIC_MOCK"
        ),
        "claim_boundary": (
            "This calibrates estimator bias and finite sampling only under the "
            "same spline-plus-linear-extrinsic model. It does not cover "
            "correlated microlensing, source-model misspecification, the full "
            "analysis grid, or independent-lens replication."
        ),
        "next_finite_action": (
            "Add correlated extrinsic/source residual mocks before opening an "
            "independent high-cadence lens with the estimator unchanged."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "verdict": result["verdict"],
        "rate_p": rate_p,
        "improvement_p": improvement_p,
    }, indent=2))


if __name__ == "__main__":
    main()
