#!/usr/bin/env python3
"""Correlated unit-stretch null for the DES J0408 A/B clock-rate audit."""

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
    "tau_core_lensing_desj0408_ab_correlated_clock_null_v1"
)
SEED = 2038040802
MOCKS_PER_SCENARIO = 64
SOURCE_TIMESCALES_DAYS = (10.0, 20.0)
EXTRINSIC_TIMESCALES_DAYS = (30.0, 60.0)


def load_audit_module():
    spec = importlib.util.spec_from_file_location("clock_audit", AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load clock audit module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gp_factor(times: np.ndarray, amplitude: float, scale: float) -> np.ndarray:
    separation = np.abs(times[:, None] - times[None, :])
    covariance = amplitude**2 * np.exp(-separation / scale)
    covariance.flat[:: len(times) + 1] += 1e-12
    return np.linalg.cholesky(covariance)


def empirical_p(values: np.ndarray, threshold: float) -> float:
    return float((1 + np.count_nonzero(values >= threshold)) / (len(values) + 1))


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
    residual_a = data["mag_A"] - source(t)
    source_amplitude = float(
        np.sqrt(
            max(
                0.0,
                np.var(residual_a, ddof=1)
                - np.mean(data["magerr_A"] ** 2),
            )
        )
    )

    source_t_b = t - delay
    overlap = (source_t_b >= np.min(t)) & (source_t_b <= np.max(t))
    x = (t[overlap] - pivot) / 100.0
    design = np.stack([np.ones_like(x), x], axis=1)
    target = data["mag_B"][overlap] - source(source_t_b[overlap])
    variance_b = data["magerr_B"][overlap] ** 2 + 0.005**2
    whiten = 1.0 / np.sqrt(variance_b)
    trend_beta = np.linalg.lstsq(
        design * whiten[:, None], target * whiten, rcond=None
    )[0]
    residual_b = target - design @ trend_beta
    extrinsic_amplitude = float(
        np.sqrt(
            max(
                0.0,
                np.var(residual_b, ddof=1) - np.mean(variance_b),
            )
        )
    )

    combined_source_times = np.concatenate([t, t - delay])
    rng = np.random.default_rng(SEED)
    scenario_rows = []
    pooled_rates = []
    pooled_improvements = []
    observed_rate_deviation = abs(
        float(central["relative_clock_rate_B_over_A"]) - 1.0
    )
    observed_improvement = float(
        central["delta_chi_square_one_extra_parameter"]
    )

    for source_scale in SOURCE_TIMESCALES_DAYS:
        source_factor = gp_factor(
            combined_source_times, source_amplitude, source_scale
        )
        for extrinsic_scale in EXTRINSIC_TIMESCALES_DAYS:
            extrinsic_factor = gp_factor(
                t, extrinsic_amplitude, extrinsic_scale
            )
            rates = []
            improvements = []
            for _ in range(MOCKS_PER_SCENARIO):
                common = source_factor @ rng.normal(
                    size=len(combined_source_times)
                )
                common_a = common[: len(t)]
                common_b = common[len(t) :]
                extrinsic = extrinsic_factor @ rng.normal(size=len(t))
                slow_trend = (
                    trend_beta[0] + trend_beta[1] * (t - pivot) / 100.0
                )
                mock = {
                    "mhjd": t.copy(),
                    "magerr_A": data["magerr_A"].copy(),
                    "magerr_B": data["magerr_B"].copy(),
                    "mag_A": (
                        source(t)
                        + common_a
                        + rng.normal(0.0, data["magerr_A"])
                    ),
                    "mag_B": (
                        source(t - delay)
                        + common_b
                        + slow_trend
                        + extrinsic
                        + rng.normal(
                            0.0,
                            np.sqrt(data["magerr_B"] ** 2 + 0.005**2),
                        )
                    ),
                }
                fit = audit.fit_spec(
                    mock, smoothing_factor=1.0, trend_degree=1
                )
                rates.append(fit["relative_clock_rate_B_over_A"])
                improvements.append(
                    fit["delta_chi_square_one_extra_parameter"]
                )
            rate_array = np.asarray(rates)
            improvement_array = np.asarray(improvements)
            pooled_rates.extend(rates)
            pooled_improvements.extend(improvements)
            scenario_rows.append(
                {
                    "source_residual_timescale_days": source_scale,
                    "extrinsic_timescale_days": extrinsic_scale,
                    "mock_count": MOCKS_PER_SCENARIO,
                    "rate_p_value": empirical_p(
                        np.abs(rate_array - 1.0), observed_rate_deviation
                    ),
                    "improvement_p_value": empirical_p(
                        improvement_array, observed_improvement
                    ),
                    "rate_quantiles_2p5_50_97p5": np.quantile(
                        rate_array, [0.025, 0.5, 0.975]
                    ).tolist(),
                }
            )

    pooled_rates_array = np.asarray(pooled_rates)
    pooled_improvements_array = np.asarray(pooled_improvements)
    pooled_rate_p = empirical_p(
        np.abs(pooled_rates_array - 1.0), observed_rate_deviation
    )
    pooled_improvement_p = empirical_p(
        pooled_improvements_array, observed_improvement
    )
    every_scenario_rejects = all(
        row["rate_p_value"] < 0.05
        and row["improvement_p_value"] < 0.05
        for row in scenario_rows
    )
    result = {
        "schema": "paper7 DES J0408 A/B correlated unit-stretch null v1",
        "source_audit": str(AUDIT_SUMMARY.relative_to(ROOT)),
        "null_hypothesis": "relative_clock_rate_B_over_A=1",
        "random_seed": SEED,
        "mock_count_per_scenario": MOCKS_PER_SCENARIO,
        "scenario_count": len(scenario_rows),
        "total_mock_count": len(pooled_rates),
        "estimated_residual_amplitudes_mag": {
            "common_source": source_amplitude,
            "image_B_extrinsic": extrinsic_amplitude,
        },
        "correlation_grid_days": {
            "common_source": list(SOURCE_TIMESCALES_DAYS),
            "image_B_extrinsic": list(EXTRINSIC_TIMESCALES_DAYS),
        },
        "frozen_estimator": {
            "source_spline_smoothing_factor_times_n": 1.0,
            "microlensing_polynomial_degree": 1,
            "delay_search_days": [100.0, 122.0],
            "stretch_search": [0.9, 1.1],
        },
        "observed": {
            "relative_clock_rate_B_over_A": central[
                "relative_clock_rate_B_over_A"
            ],
            "delta_chi_square": observed_improvement,
        },
        "scenario_results": scenario_rows,
        "pooled_rate_p_value": pooled_rate_p,
        "pooled_improvement_p_value": pooled_improvement_p,
        "every_declared_scenario_rejects_unit_stretch": every_scenario_rejects,
        "path_dependent_clock_rate_supported": every_scenario_rejects,
        "tau_time_distortion_claim_allowed": False,
        "verdict": (
            "UNIT_STRETCH_REJECTED_ACROSS_CORRELATED_NULL_GRID"
            if every_scenario_rejects
            else "OBSERVED_STRETCH_NOT_ROBUST_AGAINST_CORRELATED_NULL_GRID"
        ),
        "claim_boundary": (
            "The correlated Gaussian residual grid is a finite conservative "
            "calibration, not a unique physical microlensing model. A positive "
            "result would still require independent-lens replication and "
            "source-frozen path prediction."
        ),
        "next_finite_action": (
            "Freeze the estimator as a null result and transfer it unchanged "
            "to one independent public high-cadence COSMOGRAIL lens."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "verdict": result["verdict"],
        "pooled_rate_p": pooled_rate_p,
        "pooled_improvement_p": pooled_improvement_p,
    }, indent=2))


if __name__ == "__main__":
    main()
