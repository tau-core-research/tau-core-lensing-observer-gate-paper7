#!/usr/bin/env python3
"""Compare independent WGD2038 OIII and JWST warm-dust amplitude terminals."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import chi2


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
OIII = RESULTS / "tau_core_lensing_wgd2038_oiii_distinct_terminal_v1/summary.json"
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_cross_amplitude_stability_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"
RATIO_ORDER = ["B_over_A", "C_over_A", "D_over_A"]


def main() -> None:
    oiii = json.loads(OIII.read_text(encoding="utf-8"))
    old = np.asarray([1.16, 0.92, 0.46], dtype=float)
    old_cov = np.diag(np.asarray([0.02, 0.02, 0.01], dtype=float) ** 2)

    warm_dust = np.asarray([1.209, 0.939, 0.430], dtype=float)
    warm_dust_cov = np.asarray(
        [
            [0.0013163769158846795, 0.00012240530553126578, 0.000091145427724005],
            [0.00012240530553126578, 0.0008747728497371431, 0.00005562121299135247],
            [0.000091145427724005, 0.00005562121299135247, 0.00020187066122068058],
        ],
        dtype=float,
    )

    difference = warm_dust - old
    difference_cov = old_cov + warm_dust_cov
    mahalanobis_sq = float(difference @ np.linalg.solve(difference_cov, difference))
    mahalanobis = float(np.sqrt(mahalanobis_sq))
    p_value = float(chi2.sf(mahalanobis_sq, df=3))
    component_sigma = difference / np.sqrt(np.diag(difference_cov))

    summary = {
        "schema": "paper7 WGD2038 cross-amplitude terminal stability audit v1",
        "sources": {
            "oiii": {
                "title": "Nierenberg et al. 2020 narrow-line lensing",
                "url": "https://arxiv.org/abs/1908.06344",
                "source_scale_pc": "narrow-line region; not identified with warm dust",
            },
            "warm_dust": {
                "title": "JWST Lensed Quasar Dark Matter Survey III",
                "url": "https://arxiv.org/abs/2511.07765",
                "source_scale_prior_pc": [1.0, 10.0],
                "public_payload": (
                    "dangilman/samana launch_scripts.zip at commit "
                    "fc0f595730197a8869f5d12f37acbd0788f2659a"
                ),
            },
        },
        "ratio_basis": RATIO_ORDER,
        "oiii_ratios": old.tolist(),
        "warm_dust_ratios": warm_dust.tolist(),
        "warm_dust_covariance": warm_dust_cov.tolist(),
        "warm_dust_minus_oiii": difference.tolist(),
        "component_standardized_differences": component_sigma.tolist(),
        "mahalanobis_squared": mahalanobis_sq,
        "mahalanobis_distance": mahalanobis,
        "gaussian_chi_square_degrees_of_freedom": 3,
        "gaussian_chi_square_survival_probability": p_value,
        "covariance_assumption": (
            "The published OIII diagonal errors and public JWST covariance are "
            "combined as independent measurement covariances. Unknown OIII "
            "off-diagonal covariance is not represented."
        ),
        "same_lens_geometry": True,
        "same_terminal_family": "relative path-amplitude ratios",
        "same_physical_source_region": False,
        "source_size_dependent_transfer_expected": True,
        "strong_cross_terminal_incompatibility_detected": p_value < 0.01,
        "shared_tau_or_time_coordinate_identified": False,
        "confirmatory_tau_score_allowed": False,
        "time_distortion_detection_claim_allowed": False,
        "verdict": (
            "WGD2038_OIII_AND_WARM_DUST_AMPLITUDE_TERMINALS_ARE_"
            "STATISTICALLY_COMPATIBLE_AT_CURRENT_PRECISION__"
            "SOURCE_SCALE_DEPENDENT_SHIFT_REMAINS__NO_TAU_ATTRIBUTION"
        ),
        "claim_boundary": (
            "The two source regions provide distinct measurements through the "
            "same lens geometry. Their three-ratio difference has chi-square "
            "5.324 for three dimensions (p about 0.150) under the available "
            "measurement covariance, so no strong incompatibility is detected. "
            "The comparison does not isolate lens morphology, dark "
            "substructure, source-size transfer, variability, or a Tau channel."
        ),
        "next_finite_action": (
            "Use the source-frozen samana configuration to materialize the "
            "warm-dust accepted-simulation distribution, then compare both "
            "amplitude terminals only through a model that explicitly carries "
            "their different source-size kernels."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# WGD2038 cross-amplitude terminal stability audit v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        f"The OIII and JWST warm-dust vectors differ by Mahalanobis distance "
        f"`{mahalanobis:.3f}` (`chi2={mahalanobis_sq:.3f}`, `df=3`, "
        f"`p={p_value:.3f}`). They are compatible at current precision, but "
        "they are emitted by physically different source regions and cannot "
        "be treated as duplicate samples of one terminal kernel.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
