#!/usr/bin/env python3
"""Audit the source-frozen WGD2038 OIII finite-source completion."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
OIII_PATH = RESULTS / "tau_core_lensing_wgd2038_oiii_prior_predictive_n64_v1/summary.json"
WARM_PATH = (
    RESULTS
    / "tau_core_lensing_wgd2038_warm_dust_prior_predictive_n64_v1"
    / "summary.json"
)
OUT = RESULTS / "tau_core_lensing_wgd2038_oiii_source_kernel_completion_v1"

OBSERVED = np.asarray([1.16, 0.92, 0.46])
SIGMA = np.asarray([0.02, 0.02, 0.01])


def main() -> None:
    oiii = json.loads(OIII_PATH.read_text(encoding="utf-8"))
    warm = json.loads(WARM_PATH.read_text(encoding="utf-8"))
    oiii_ratios = np.asarray(oiii["predicted_flux_ratios"], dtype=float)
    warm_ratios = np.asarray(warm["predicted_flux_ratios"], dtype=float)
    if oiii_ratios.shape != warm_ratios.shape:
        raise ValueError("paired source-kernel batches have different shapes")

    delta = oiii_ratios - OBSERVED
    chi_square = np.sum((delta / SIGMA) ** 2, axis=1)
    log_weight = -0.5 * chi_square
    weight = np.exp(log_weight - np.max(log_weight))
    weight /= np.sum(weight)
    square_sum = float(weight @ weight)
    ess = 1.0 / square_sum
    weighted_mean = weight @ oiii_ratios
    centered = oiii_ratios - weighted_mean
    weighted_covariance = (
        (centered * weight[:, None]).T @ centered / (1.0 - square_sum)
    )

    source_difference = oiii_ratios - warm_ratios
    result = {
        "schema": "paper7 WGD2038 OIII source-kernel completion audit v1",
        "oiii_input_artifact": str(OIII_PATH.relative_to(ROOT)),
        "paired_warm_dust_artifact": str(WARM_PATH.relative_to(ROOT)),
        "source_freeze": {
            "profile": "circular Gaussian",
            "fwhm_pc_prior": [20.0, 50.0],
            "selection_source": (
                "Nierenberg et al. 2020 Section 6.1: independently drawn "
                "20-50 pc Gaussian FWHM"
            ),
            "selected_without_using_wgd2038_flux_residual": True,
        },
        "observed_oiii_ratios": OBSERVED.tolist(),
        "observed_diagonal_sigma": SIGMA.tolist(),
        "prior_realizations": int(oiii_ratios.shape[0]),
        "prior_ratio_mean": np.mean(oiii_ratios, axis=0).tolist(),
        "prior_ratio_covariance_rank": int(
            np.linalg.matrix_rank(np.cov(oiii_ratios, rowvar=False))
        ),
        "likelihood_effective_sample_size": float(ess),
        "likelihood_effective_sample_fraction": float(ess / oiii_ratios.shape[0]),
        "maximum_normalized_weight": float(np.max(weight)),
        "weighted_ratio_mean": weighted_mean.tolist(),
        "weighted_ratio_covariance": weighted_covariance.tolist(),
        "weighted_covariance_rank": int(
            np.linalg.matrix_rank(weighted_covariance)
        ),
        "paired_source_kernel_maximum_absolute_ratio_shift": float(
            np.max(np.abs(source_difference))
        ),
        "paired_source_kernel_rms_ratio_shift": np.sqrt(
            np.mean(source_difference**2, axis=0)
        ).tolist(),
        "paired_source_kernel_mean_ratio_shift": np.mean(
            source_difference, axis=0
        ).tolist(),
        "minimum_effective_samples_for_coarse_conditioning": 20.0,
        "coarse_conditioned_diagnostic_materialized": bool(ess >= 20.0),
        "full_oiii_measurement_covariance_materialized": False,
        "joint_delay_oiii_ensemble_materialized": False,
        "tau_or_observer_time_scoring_allowed": False,
        "verdict": (
            "SOURCE_FROZEN_OIII_FORWARD_KERNEL_MATERIALIZED__"
            + (
                "COARSE_DIAGONAL_LIKELIHOOD_DIAGNOSTIC_PASSES_ESS"
                if ess >= 20.0
                else "N64_DIAGONAL_LIKELIHOOD_ESS_INSUFFICIENT"
            )
        ),
        "claim_boundary": (
            "The 20-50 pc Gaussian OIII source kernel is source-frozen and the "
            "standard forward family is executable. Diagonal likelihood "
            "weighting is not a substitute for the unpublished full OIII "
            "ratio covariance or a joint delay-flux ensemble, and it "
            "authorizes no Tau or observer-time inference."
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "ess": ess,
                "maximum_weight": float(np.max(weight)),
                "maximum_source_kernel_shift": result[
                    "paired_source_kernel_maximum_absolute_ratio_shift"
                ],
                "verdict": result["verdict"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
