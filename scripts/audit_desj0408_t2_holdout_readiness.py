#!/usr/bin/env python3
"""Audit independent holdout readiness for the DES-frozen T2 score direction.

The DES one-amplitude pretest is deliberately not counted as real T2 evidence.
This audit asks which independent lens target currently has the fields required
to test the frozen direction outside DES J0408.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results"
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_t2_holdout_readiness_v1"
CSV_PATH = DERIVED / "desj0408_t2_holdout_readiness_v1.csv"


def load(name: str) -> dict[str, object]:
    return json.loads((RESULTS / name / "summary.json").read_text(encoding="utf-8"))


def bool01(value: bool) -> int:
    return 1 if value else 0


def main() -> None:
    wgd_field = load("tau_core_lensing_wgd2038_field_level_payload_audit_v1")
    wgd_acq = load("tau_core_lensing_wgd2038_public_payload_acquisition_v1")
    wgd_hst = load("tau_core_lensing_wgd2038_lenstronomy_hst_reproduction_v1")
    he0435 = load("tau_core_lensing_he0435_public_repro_model_level_psf_correction_fit_v0")
    rxj_wfi = load("tau_core_lensing_rxj1131_wfi2033_public_product_probe_v0")
    des_wgd_probe = load("tau_core_lensing_wgd2038_desj0408_public_product_probe_v0")
    t2_score = load("tau_core_lensing_desj0408_one_amplitude_t2_operator_pretest_v1")

    rows = [
        {
            "target_id": "WGD2038-4008",
            "source_artifacts": (
                "wgd2038_field_level_payload_audit_v1;"
                "wgd2038_public_payload_acquisition_v1;"
                "wgd2038_lenstronomy_hst_reproduction_v1"
            ),
            "independent_from_des": True,
            "time_delay_observations_or_ddt": bool(
                wgd_field["criteria"]["ddt_samples_available"]
            ),
            "image_model_products_present": bool(
                wgd_hst["criteria"]["hst_mast_products_downloaded"]
                and wgd_hst["criteria"]["sci_wht_reduced_data_prepared"]
                and wgd_hst["criteria"]["multiband_data_setup_preflight_executed"]
            ),
            "image_parity_order_available": bool(
                wgd_field["criteria"]["image_parity_available"]
            ),
            "image_wise_fermat_or_arrival_samples": bool(
                wgd_field["criteria"]["image_wise_fermat_samples_available"]
            ),
            "converged_no_t2_posterior": bool(
                wgd_hst["criteria"]["converged_no_T2_posterior_reproduced"]
            ),
            "posterior_joblib_payload_available": bool(
                wgd_acq["criteria"]["model_posterior_joblib_payload_acquired"]
            ),
            "can_apply_des_frozen_score_now": False,
            "blocking_reason": (
                "WGD2038 has public support payload and local HST/model-plumbing "
                "progress, but lacks the extracted image-wise Fermat/arrival table, "
                "image parity/order, original joblib posterior payload, and a "
                "converged no-T2 posterior."
            ),
            "recommended_next_action": (
                "Extract or reconstruct the WGD2038 per-sample image/model table "
                "with image labels, parity/order, dphi_AB/dphi_AC/dphi_AD, model "
                "sample IDs, and observed-delay/Ddt linkage."
            ),
        },
        {
            "target_id": "HE0435-1223",
            "source_artifacts": "he0435_public_repro_model_level_psf_correction_fit_v0",
            "independent_from_des": True,
            "time_delay_observations_or_ddt": True,
            "image_model_products_present": True,
            "image_parity_order_available": False,
            "image_wise_fermat_or_arrival_samples": False,
            "converged_no_t2_posterior": False,
            "posterior_joblib_payload_available": False,
            "can_apply_des_frozen_score_now": False,
            "blocking_reason": (
                "HE0435 remains useful as a public fallback, but the current "
                "artifact is a model-level PSF/reproduction edge diagnostic, not "
                "the image-wise time-delay residual table needed for the DES-frozen "
                "operator."
            ),
            "recommended_next_action": (
                "Only use after extracting image-wise Fermat/parity/arrival-time "
                "fields and a no-T2 residual vector comparable to the DES basis."
            ),
        },
        {
            "target_id": "RXJ1131-1231_or_WFI2033-4723",
            "source_artifacts": "rxj1131_wfi2033_public_product_probe_v0",
            "independent_from_des": True,
            "time_delay_observations_or_ddt": True,
            "image_model_products_present": False,
            "image_parity_order_available": False,
            "image_wise_fermat_or_arrival_samples": False,
            "converged_no_t2_posterior": False,
            "posterior_joblib_payload_available": False,
            "can_apply_des_frozen_score_now": False,
            "blocking_reason": (
                "The public probe found useful products, but they are too "
                "compressed for an image-level T2 holdout test."
            ),
            "recommended_next_action": (
                "Use only if target-specific image/model posterior products become "
                "available."
            ),
        },
    ]

    required_fields = [
        "independent_from_des",
        "time_delay_observations_or_ddt",
        "image_model_products_present",
        "image_parity_order_available",
        "image_wise_fermat_or_arrival_samples",
        "converged_no_t2_posterior",
    ]
    for row in rows:
        row["readiness_score_0_to_6"] = sum(bool01(bool(row[field])) for field in required_fields)

    best = max(rows, key=lambda row: int(row["readiness_score_0_to_6"]))
    summary = {
        "schema": "paper7 DES-frozen T2 independent holdout readiness v1",
        "purpose": (
            "Determine whether the DES-frozen one-amplitude T2 score can be tested "
            "on an independent lens target using existing public/reconstructed "
            "artifacts."
        ),
        "source": {
            "des_score_summary": (
                "data/derived/repro_results/"
                "tau_core_lensing_desj0408_one_amplitude_t2_operator_pretest_v1/"
                "summary.json"
            ),
            "des_score_verdict": t2_score["verdict"],
            "wgd2038_probe_verdict": des_wgd_probe.get("verdict"),
            "he0435_verdict": he0435.get("verdict"),
            "rxj_wfi_verdict": rxj_wfi.get("verdict"),
        },
        "required_holdout_fields": required_fields,
        "best_current_holdout_target": {
            "target_id": best["target_id"],
            "readiness_score_0_to_6": best["readiness_score_0_to_6"],
            "can_apply_des_frozen_score_now": best["can_apply_des_frozen_score_now"],
            "blocking_reason": best["blocking_reason"],
            "recommended_next_action": best["recommended_next_action"],
        },
        "verdict": {
            "desj0408_t2_holdout_readiness_audit_created": True,
            "independent_holdout_score_ready_now": False,
            "best_current_holdout_target": best["target_id"],
            "best_current_holdout_readiness_score_0_to_6": best[
                "readiness_score_0_to_6"
            ],
            "wgd2038_is_best_next_holdout_route": best["target_id"] == "WGD2038-4008",
            "des_one_amplitude_score_remains_design_only": True,
            "real_data_T2_sampling_authorized": False,
        },
        "rows": rows,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps(summary["verdict"], indent=2, sort_keys=True))
    print(json.dumps(summary["best_current_holdout_target"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
