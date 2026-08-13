#!/usr/bin/env python3
"""Audit likelihood reweighting of the bounded WGD2038 warm-dust ensemble."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]

OBSERVED = np.asarray([1.209, 0.939, 0.430])
COVARIANCE = np.asarray(
    [
        [0.0013163769158846795, 0.00012240530553126578, 0.000091145427724005],
        [0.00012240530553126578, 0.0008747728497371431, 0.00005562121299135247],
        [0.000091145427724005, 0.00005562121299135247, 0.00020187066122068058],
    ]
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-name",
        default="tau_core_lensing_wgd2038_warm_dust_prior_predictive_n64_v1",
    )
    parser.add_argument(
        "--output-name",
        default="tau_core_lensing_wgd2038_warm_dust_likelihood_reweighting_v1",
    )
    parser.add_argument("--minimum-effective-samples", type=float, default=20.0)
    args = parser.parse_args()
    if any(
        "/" in value or value in {"", ".", ".."}
        for value in (args.input_name, args.output_name)
    ):
        parser.error("input and output names must each be one directory name")

    input_path = (
        ROOT / "data/derived/repro_results" / args.input_name / "summary.json"
    )
    out_path = ROOT / "data/derived/repro_results" / args.output_name
    source = json.loads(input_path.read_text(encoding="utf-8"))
    ratios = np.asarray(source["predicted_flux_ratios"], dtype=float)
    delta = ratios - OBSERVED
    chi_square = np.einsum(
        "ni,ij,nj->n", delta, np.linalg.inv(COVARIANCE), delta
    )
    log_weight = -0.5 * chi_square
    weight = np.exp(log_weight - np.max(log_weight))
    weight /= np.sum(weight)
    weight_square_sum = float(weight @ weight)
    effective_sample_size = 1.0 / weight_square_sum

    mean = weight @ ratios
    centered = ratios - mean
    covariance = (
        (centered * weight[:, None]).T @ centered / (1.0 - weight_square_sum)
    )
    result = {
        "schema": "paper7 WGD2038 warm-dust likelihood reweighting audit v1",
        "input_artifact": str(input_path.relative_to(ROOT)),
        "input_realizations": int(ratios.shape[0]),
        "observed_ratio_vector": OBSERVED.tolist(),
        "measurement_covariance": COVARIANCE.tolist(),
        "chi_square_min_median_max": [
            float(np.min(chi_square)),
            float(np.median(chi_square)),
            float(np.max(chi_square)),
        ],
        "effective_sample_size": float(effective_sample_size),
        "effective_sample_fraction": float(effective_sample_size / ratios.shape[0]),
        "maximum_normalized_weight": float(np.max(weight)),
        "samples_above_one_percent_weight": int(np.sum(weight > 0.01)),
        "weighted_ratio_mean": mean.tolist(),
        "weighted_ratio_covariance": covariance.tolist(),
        "weighted_covariance_rank": int(np.linalg.matrix_rank(covariance)),
        "predeclared_minimum_effective_samples": args.minimum_effective_samples,
        "stable_conditioned_inference_allowed": bool(
            effective_sample_size >= args.minimum_effective_samples
        ),
        "tau_or_observer_time_scoring_allowed": False,
        "verdict": (
            "LIKELIHOOD_REWEIGHTED_COARSE_DIAGNOSTIC_MATERIALIZED"
            if effective_sample_size >= args.minimum_effective_samples
            else "LIKELIHOOD_CONDITIONED_REGION_NONEMPTY__"
            "EFFECTIVE_SAMPLE_SIZE_TOO_LOW_FOR_STABLE_INFERENCE"
        ),
        "claim_boundary": (
            "The published Gaussian flux likelihood can be evaluated on the "
            f"bounded prior batch with ESS={effective_sample_size:.2f}. "
            "Passing the coarse ESS threshold materializes only a weighted "
            "warm-dust diagnostic, not a posterior-predictive distribution or "
            "an OIII completion, and authorizes no Tau/time score."
        ),
        "next_finite_action": (
            "Use the weighted warm-dust covariance only as a standard "
            "amplitude-terminal nuisance diagnostic; do not enlarge this "
            "ensemble again without a new endpoint requirement."
        ),
    }
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "effective_sample_size": effective_sample_size,
                "maximum_normalized_weight": float(np.max(weight)),
                "verdict": result["verdict"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
