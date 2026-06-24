#!/usr/bin/env python3
"""Audit whether WGD2038 observed-delay linkage is score-ready.

The local WGD2038 payload contains Ddt samples and weights, and the bounded
local preflight can compute image Fermat/parity fields.  The missing bridge for
a no-T2 residual vector is a machine-readable observed delay vector/covariance
linked to the same A/B/C/D image convention.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results"
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_observed_delay_linkage_audit_v1"
OUT_TABLE = DERIVED / "wgd2038_observed_delay_linkage_audit_v1.csv"


def load_result(name: str) -> dict[str, Any]:
    return json.loads((RESULTS / name / "summary.json").read_text(encoding="utf-8"))


def main() -> None:
    contract = load_result("tau_core_lensing_wgd2038_holdout_extraction_contract_v1")
    partial = load_result("tau_core_lensing_wgd2038_partial_holdout_materialization_v1")
    fermat = load_result("tau_core_lensing_wgd2038_bounded_local_fermat_preflight_v1")
    observed_smoke = load_result("tau_core_lensing_wgd2038_observed_delay_no_t2_smoke_v1")
    shape_target = load_result("tau_core_lensing_wgd2038_delay_shape_holdout_target_v1")
    observed_present = bool(
        observed_smoke["verdict"]["wgd2038_observed_delay_vector_materialized"]
        and observed_smoke["verdict"]["wgd2038_observed_delay_covariance_materialized"]
    )
    shape_target_present = bool(
        shape_target["verdict"]["wgd2038_delay_shape_holdout_target_created"]
    )

    rows = [
        {
            "row_id": "WGD_DELAY_LINKAGE_001",
            "component": "published_time_delay_measurement_statement",
            "source": "TDCOSMO XVI arXiv:2406.02683v2 / A&A 2024",
            "status": "literature_support_present",
            "detail": (
                "The paper states that WGD2038 has new time-delay measurements, "
                "uses delays relative to image A, and uses the corresponding "
                "covariance matrix in the cosmographic inference."
            ),
            "score_blocker": False,
        },
        {
            "row_id": "WGD_DELAY_LINKAGE_002",
            "component": "machine_readable_observed_delay_vector",
            "source": "TDCOSMO XVI Fig. 2 transcription artifact",
            "status": "present_transcribed_from_publication" if observed_present else "missing",
            "detail": (
                "The published AB/AC/AD delay vector and covariance are now "
                "materialized in a local artifact with the publication convention "
                "Delta_t_AX=t_A-t_X. This removes the observed-delay-vector blocker, "
                "but does not supply a converged/published WGD Fermat posterior."
            ),
            "score_blocker": not observed_present,
        },
        {
            "row_id": "WGD_DELAY_LINKAGE_003",
            "component": "Ddt_weight_support",
            "source": "TDCOSMO2025 WGD2038 processed pickle and Ddt CSV",
            "status": "present",
            "detail": (
                f"{partial['public_payload_stats']['ddt_sample_count']} Ddt samples "
                "and weights are materialized, but these are compressed cosmographic "
                "support rather than the observed image-delay vector itself."
            ),
            "score_blocker": False,
        },
        {
            "row_id": "WGD_DELAY_LINKAGE_004",
            "component": "local_bounded_fermat_parity_table",
            "source": "local bounded WGD diagnostic outputs",
            "status": "diagnostic_only_present",
            "detail": (
                f"{fermat['counts']['image_row_count']} image rows across "
                f"{fermat['counts']['successful_job_count']} bounded local jobs "
                "contain image coordinates, Fermat potentials, and Morse/parity labels."
            ),
            "score_blocker": False,
        },
        {
            "row_id": "WGD_DELAY_LINKAGE_005",
            "component": "no_T2_residual_vector",
            "source": "derived from observed delays minus model delays",
            "status": "diagnostic_smoke_only_not_score_ready",
            "detail": (
                "A bounded no-T2 residual smoke is now derivable after sign-convention "
                "alignment. It is not score-ready because the Fermat basis is a local "
                "non-converged preflight rather than a converged or published WGD posterior."
            ),
            "score_blocker": True,
        },
        {
            "row_id": "WGD_DELAY_LINKAGE_006",
            "component": "predeclared_delay_shape_holdout_target",
            "source": "TDCOSMO IX published model predictions plus TDCOSMO XVI observed delays",
            "status": "present_not_endpoint_blind" if shape_target_present else "missing",
            "detail": (
                "A published-model delay-shape target is frozen before any "
                "posterior-level WGD score. It can constrain a future comparison, "
                "but it is not endpoint-blind and is not itself a posterior-level score."
            ),
            "score_blocker": False,
        },
    ]

    summary = {
        "schema": "paper7 WGD2038 observed-delay linkage audit v1",
        "purpose": (
            "Identify the exact remaining bridge between local WGD Fermat/parity "
            "extraction and a DES-frozen no-T2 residual score."
        ),
        "external_literature_sources": [
            {
                "id": "TDCOSMO_XVI_WGD2038",
                "title": (
                    "TDCOSMO. XVI. Measurement of the Hubble Constant from the "
                    "Lensed Quasar WGD 2038-4008"
                ),
                "arxiv": "2406.02683v2",
                "url": "https://arxiv.org/abs/2406.02683",
                "used_for": [
                    "WGD2038 has new time-delay measurements",
                    "delays are used relative to image A",
                    "full covariance of the three independent delay degrees is required",
                    "negative A-C solution is selected using model-predicted ordering",
                ],
            }
        ],
        "inputs": {
            "contract_counts": contract["contract_counts"],
            "partial_materialization_counts": partial["materialization_counts"],
            "fermat_preflight_counts": fermat["counts"],
            "observed_delay_smoke_counts": observed_smoke["counts"],
            "shape_target_values": shape_target["target_values"],
        },
        "verdict": {
            "wgd2038_observed_delay_linkage_audit_created": True,
            "published_observed_delay_measurement_exists": True,
            "local_machine_readable_observed_delay_vector_present": observed_present,
            "bounded_no_t2_residual_smoke_present": bool(
                observed_smoke["verdict"]["wgd2038_no_t2_residual_smoke_computed"]
            ),
            "predeclared_delay_shape_holdout_target_present": shape_target_present,
            "predeclared_delay_shape_holdout_target_endpoint_blind": bool(
                shape_target["verdict"]["endpoint_blind"]
            ),
            "predeclared_delay_shape_holdout_target_posterior_level_score": bool(
                shape_target["verdict"]["posterior_level_score"]
            ),
            "missing_score_ready_component": (
                "converged_or_published_wgd_fermat_posterior_table"
            ),
            "local_bounded_fermat_parity_preflight_present": True,
            "can_compute_wgd_no_t2_residual_vector_now": observed_present,
            "can_apply_des_frozen_score_now": False,
            "real_data_T2_sampling_authorized": False,
            "claim_level": "source_backed_delay_vector_plus_local_smoke_not_time_shift_evidence",
        },
        "next_finite_action": (
            "Replace the local bounded Fermat preflight with a converged or published "
            "WGD Fermat/posterior table in the same image convention; then evaluate "
            "its no-T2 residual against the frozen delay-shape target and only then "
            "decide whether a DES-frozen comparison is meaningful."
        ),
        "rows": rows,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    with OUT_TABLE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps(summary["verdict"], indent=2, sort_keys=True))
    print(summary["next_finite_action"])


if __name__ == "__main__":
    main()
