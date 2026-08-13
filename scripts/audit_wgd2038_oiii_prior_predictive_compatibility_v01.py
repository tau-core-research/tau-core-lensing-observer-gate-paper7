#!/usr/bin/env python3
"""Place the WGD2038 OIII vector in its source-frozen standard prediction."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import chi2


ROOT = Path(__file__).resolve().parents[1]
INPUT = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_wgd2038_oiii_prior_predictive_n64_v1"
    / "summary.json"
)
OUT = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_wgd2038_oiii_prior_predictive_compatibility_v1"
)
OBSERVED = np.asarray([1.16, 0.92, 0.46])
MEASUREMENT_COVARIANCE = np.diag(np.asarray([0.02, 0.02, 0.01]) ** 2)
BOOTSTRAP_SEED = 20384202
BOOTSTRAP_DRAWS = 10_000


def main() -> None:
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    ratios = np.asarray(source["predicted_flux_ratios"], dtype=float)
    mean = np.mean(ratios, axis=0)
    predictive_covariance = (
        np.cov(ratios, rowvar=False, ddof=1) + MEASUREMENT_COVARIANCE
    )
    delta = OBSERVED - mean
    mahalanobis_square = float(
        delta @ np.linalg.inv(predictive_covariance) @ delta
    )
    gaussian_p = float(chi2.sf(mahalanobis_square, df=3))

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    bootstrap_q = np.empty(BOOTSTRAP_DRAWS)
    for index in range(BOOTSTRAP_DRAWS):
        sample = ratios[rng.integers(0, ratios.shape[0], ratios.shape[0])]
        sample_mean = np.mean(sample, axis=0)
        sample_covariance = (
            np.cov(sample, rowvar=False, ddof=1) + MEASUREMENT_COVARIANCE
        )
        sample_delta = OBSERVED - sample_mean
        bootstrap_q[index] = (
            sample_delta @ np.linalg.inv(sample_covariance) @ sample_delta
        )
    bootstrap_p = chi2.sf(bootstrap_q, df=3)
    levels = np.asarray([0.025, 0.16, 0.5, 0.84, 0.975])

    result = {
        "schema": "paper7 WGD2038 OIII prior-predictive compatibility audit v1",
        "input_artifact": str(INPUT.relative_to(ROOT)),
        "prediction_realizations": int(ratios.shape[0]),
        "source_kernel": "circular Gaussian FWHM uniformly 20-50 pc",
        "observed_ratio_vector": OBSERVED.tolist(),
        "measurement_covariance_assumption": (
            "published diagonal errors; full ratio covariance unavailable"
        ),
        "predictive_mean": mean.tolist(),
        "predictive_covariance_including_measurement": predictive_covariance.tolist(),
        "predictive_covariance_rank": int(
            np.linalg.matrix_rank(predictive_covariance)
        ),
        "gaussian_moment_mahalanobis_square": mahalanobis_square,
        "gaussian_moment_degrees_of_freedom": 3,
        "gaussian_moment_survival_probability": gaussian_p,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "bootstrap_quantile_levels": levels.tolist(),
        "bootstrap_mahalanobis_square_quantiles": np.quantile(
            bootstrap_q, levels
        ).tolist(),
        "bootstrap_gaussian_survival_probability_quantiles": np.quantile(
            bootstrap_p, levels
        ).tolist(),
        "strong_standard_prior_predictive_incompatibility_detected": bool(
            np.quantile(bootstrap_p, 0.025) < 0.01
        ),
        "tau_specific_excess_materialized": False,
        "observer_time_scoring_allowed": False,
        "verdict": (
            "OIII_VECTOR_COMPATIBLE_WITH_COARSE_SOURCE_FROZEN_STANDARD_"
            "PRIOR_PREDICTIVE_MOMENTS__NO_TAU_EXCESS"
        ),
        "claim_boundary": (
            "The source-frozen 20-50 pc standard ensemble removes the earlier "
            "diagonal smooth-macromodel tension at coarse Gaussian-moment "
            "level. N=64, the Gaussian approximation, missing full OIII ratio "
            "covariance, and absence of a joint delay-flux ensemble prevent a "
            "posterior or definitive model-selection claim. No Tau or "
            "observer-time excess is materialized."
        ),
        "stop_decision": (
            "Do not enlarge this branch by blind prior sampling. A future "
            "advance requires the full OIII covariance or a source-frozen "
            "joint delay-flux ensemble."
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
