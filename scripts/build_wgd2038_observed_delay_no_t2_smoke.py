#!/usr/bin/env python3
"""Build a WGD2038 observed-delay vector and no-T2 residual smoke.

This script transcribes the published TDCOSMO XVI WGD2038 delay vector and
covariance from Fig. 2, then combines it with the local bounded Fermat
preflight.  It is not a T2 fit and not a converged WGD posterior score.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results"
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_observed_delay_no_t2_smoke_v1"
OUT_TABLE = DERIVED / "wgd2038_observed_delay_no_t2_smoke_v1.csv"

# lenstronomy LensCosmo.time_delay_units uses:
# D_dt[Mpc] * Mpc / c / day_s * arcsec**2 * fermat_pot[arcsec^2].
MPC_M = 3.08567758e22
C_M_PER_S = 299792458.0
DAY_S = 86400.0
ARCSEC_RAD = 4.84813681109536e-06
DAYS_PER_MPC_ARCSEC2 = MPC_M / C_M_PER_S / DAY_S * ARCSEC_RAD**2

OBSERVED_DELAY_DAYS = {
    "AB": -12.4,
    "AC": -5.3,
    "AD": -33.3,
}

OBSERVED_COV_DAYS2 = np.array(
    [
        [14.2, 6.1, 7.5],
        [6.1, 14.8, 7.1],
        [7.5, 7.1, 39.9],
    ],
    dtype=float,
)

PAIR_ORDER = ["AB", "AC", "AD"]


def load_result(name: str) -> dict[str, Any]:
    return json.loads((RESULTS / name / "summary.json").read_text(encoding="utf-8"))


def vector_from_map(values: dict[str, float]) -> np.ndarray:
    return np.array([values[pair] for pair in PAIR_ORDER], dtype=float)


def main() -> None:
    partial = load_result("tau_core_lensing_wgd2038_partial_holdout_materialization_v1")
    fermat = load_result("tau_core_lensing_wgd2038_bounded_local_fermat_preflight_v1")

    ddt_mean = float(partial["public_payload_stats"]["ddt_weighted_mean"])
    ddt_q50 = float(partial["public_payload_stats"]["ddt_weighted_q50"])
    ddt_q16 = float(partial["public_payload_stats"]["ddt_weighted_q16"])
    ddt_q84 = float(partial["public_payload_stats"]["ddt_weighted_q84"])
    ddt_to_days = ddt_mean * DAYS_PER_MPC_ARCSEC2
    observed_vec = vector_from_map(OBSERVED_DELAY_DAYS)
    cov_inv = np.linalg.inv(OBSERVED_COV_DAYS2)

    rows: list[dict[str, Any]] = []
    job_summaries: list[dict[str, Any]] = []
    for job in fermat["job_summaries"]:
        if not job.get("extraction_success"):
            continue

        # The WGD notebook hook stores dphi_AB = phi_B - phi_A, while the
        # publication reports AX delays as t_A - t_X.  Convert to the
        # publication's A-centered convention by flipping the notebook sign.
        notebook_dphi = {
            "AB": float(job["dphi_AB"]),
            "AC": float(job["dphi_AC"]),
            "AD": float(job["dphi_AD"]),
        }
        ax_dphi = {pair: -value for pair, value in notebook_dphi.items()}
        model_delay = {pair: ddt_to_days * ax_dphi[pair] for pair in PAIR_ORDER}
        model_vec = vector_from_map(model_delay)
        residual_vec = observed_vec - model_vec
        chi2 = float(residual_vec.T @ cov_inv @ residual_vec)
        normalized_rmse = float(np.sqrt(chi2 / len(PAIR_ORDER)))

        for pair in PAIR_ORDER:
            rows.append(
                {
                    "target_id": "WGD2038-4008",
                    "job_name": job["job_name"],
                    "claim_level": job["claim_level"],
                    "delay_pair": pair,
                    "published_delay_convention": "Delta_t_AX=t_A-t_X",
                    "observed_delay_days": OBSERVED_DELAY_DAYS[pair],
                    "notebook_basis_dphi_phi_X_minus_phi_A": notebook_dphi[pair],
                    "publication_basis_dphi_phi_A_minus_phi_X": ax_dphi[pair],
                    "ddt_weighted_mean_mpc": ddt_mean,
                    "days_per_mpc_arcsec2": DAYS_PER_MPC_ARCSEC2,
                    "model_no_t2_delay_days": model_delay[pair],
                    "observed_minus_model_no_t2_residual_days": residual_vec[
                        PAIR_ORDER.index(pair)
                    ],
                    "uses_converged_or_published_wgd_posterior": False,
                    "t2_parameter_fit_or_sampled": False,
                    "usable_for_des_frozen_score": False,
                }
            )

        job_summaries.append(
            {
                "job_name": job["job_name"],
                "claim_level": job["claim_level"],
                "notebook_basis_dphi_phi_X_minus_phi_A": notebook_dphi,
                "publication_basis_dphi_phi_A_minus_phi_X": ax_dphi,
                "model_no_t2_delay_days": model_delay,
                "observed_minus_model_no_t2_residual_days": {
                    pair: float(residual_vec[i]) for i, pair in enumerate(PAIR_ORDER)
                },
                "chi2_against_published_delay_covariance": chi2,
                "normalized_rmse_sigma_units": normalized_rmse,
                "score_interpretation": (
                    "diagnostic residual smoke only; the local Fermat table is bounded "
                    "and non-converged, so this is not a holdout score."
                ),
            }
        )

    primary = next(
        (
            item
            for item in job_summaries
            if item["job_name"] == "tau_core_profile_freeze_v2_pemd_fastell_backend"
        ),
        job_summaries[0] if job_summaries else None,
    )

    summary = {
        "schema": "paper7 WGD2038 observed-delay no-T2 smoke v1",
        "purpose": (
            "Materialize the published WGD2038 observed-delay vector/covariance and "
            "compute a bounded no-T2 residual smoke in the same A-centered delay convention."
        ),
        "external_literature_sources": [
            {
                "id": "TDCOSMO_XVI_WGD2038_FIG2",
                "title": (
                    "TDCOSMO. XVI. Measurement of the Hubble Constant from the "
                    "Lensed Quasar WGD 2038-4008"
                ),
                "journal_url": "https://www.aanda.org/articles/aa/full_html/2024/09/aa50979-24/aa50979-24.html",
                "arxiv_url": "https://arxiv.org/abs/2406.02683",
                "source_location": "Fig. 2 upper-left delay and covariance panel",
                "transcription_basis": "manual transcription from rendered arXiv/A&A figure and source PDF",
            }
        ],
        "published_time_delay_vector": {
            "convention": "Delta_t_AX=t_A-t_X",
            "units": "days",
            "values": OBSERVED_DELAY_DAYS,
            "selected_solution": "negative_AC_solution",
        },
        "published_time_delay_covariance": {
            "units": "days^2",
            "pair_order": PAIR_ORDER,
            "matrix": OBSERVED_COV_DAYS2.tolist(),
        },
        "dimension_check": {
            "formula": "Delta_t_AX_days = Ddt_Mpc * days_per_mpc_arcsec2 * Delta_phi_AX_arcsec2",
            "days_per_mpc_arcsec2": DAYS_PER_MPC_ARCSEC2,
            "ddt_weighted_mean_mpc": ddt_mean,
            "ddt_weighted_q16_mpc": ddt_q16,
            "ddt_weighted_q50_mpc": ddt_q50,
            "ddt_weighted_q84_mpc": ddt_q84,
            "weighted_mean_days_per_arcsec2": ddt_to_days,
        },
        "input_artifacts": {
            "partial_materialization": (
                "data/derived/repro_results/"
                "tau_core_lensing_wgd2038_partial_holdout_materialization_v1/summary.json"
            ),
            "fermat_preflight": (
                "data/derived/repro_results/"
                "tau_core_lensing_wgd2038_bounded_local_fermat_preflight_v1/summary.json"
            ),
        },
        "counts": {
            "successful_local_fermat_job_count": len(job_summaries),
            "delay_pair_row_count": len(rows),
            "score_ready_row_count": sum(
                1 for row in rows if row["usable_for_des_frozen_score"]
            ),
        },
        "primary_job_summary": primary,
        "verdict": {
            "wgd2038_observed_delay_vector_materialized": True,
            "wgd2038_observed_delay_covariance_materialized": True,
            "wgd2038_no_t2_residual_smoke_computed": len(rows) > 0,
            "uses_published_observed_delay_measurement": True,
            "uses_converged_or_published_wgd_posterior": False,
            "can_apply_des_frozen_score_now": False,
            "real_data_T2_sampling_authorized": False,
            "t2_specific_time_shift_evidence": False,
            "claim_level": "published_delay_vector_plus_local_nonconverged_no_t2_smoke_not_T2_evidence",
        },
        "claim_boundary": [
            "The observed-delay vector and covariance are source-backed from TDCOSMO XVI Fig. 2.",
            "The Fermat inputs are local bounded diagnostics, not the converged/published WGD posterior.",
            "The residual vector is therefore a convention-checked smoke test, not a DES-frozen holdout score.",
            "No T2 parameter is fitted or sampled.",
        ],
        "next_finite_action": (
            "Replace the local bounded Fermat table with a converged or published WGD "
            "Fermat/posterior table in the same A-centered convention, then re-run this "
            "smoke as the first score-ready holdout residual."
        ),
        "job_summaries": job_summaries,
        "rows": rows,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    if rows:
        with OUT_TABLE.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    else:
        OUT_TABLE.write_text("", encoding="utf-8")

    print(json.dumps(summary["verdict"], indent=2, sort_keys=True))
    if primary is not None:
        print(json.dumps(primary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
