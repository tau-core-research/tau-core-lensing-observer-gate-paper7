#!/usr/bin/env python3
"""Materialize the public part of the WGD2038 holdout contract.

This is deliberately not a DES-frozen score run.  It builds the model-level
manifest that can be filled from the current public payload and records exactly
which contract fields still require the missing image-wise posterior/joblib
table.
"""

from __future__ import annotations

import csv
import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results"
PAYLOAD_ROOT = ROOT / "data" / "external" / "wgd2038_public_payload"
TDCOSMO = PAYLOAD_ROOT / "tdcosmo2025_wgd2038"
PROCESSED = TDCOSMO / "WGD2038-4008_const_processed.pkl"
DDT_CSV = TDCOSMO / "desj2038_pl_nokext_nokin_dt_weight.csv"
KAPPA_CAT = TDCOSMO / (
    "kappahist_2038_measured_3innermask_nobeta_removehandpicked_"
    "zgap-1.0_-1.0_fiducial_120_gal_120_oneoverr_22.5_med_increments2_2_emptymsk.cat"
)
CONTRACT = RESULTS / "tau_core_lensing_wgd2038_holdout_extraction_contract_v1" / "summary.json"
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_partial_holdout_materialization_v1"
OUT_TABLE = DERIVED / "wgd2038_partial_holdout_materialization_v1.csv"


def load_contract() -> dict[str, Any]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def weighted_quantile(values: np.ndarray, weights: np.ndarray, qs: list[float]) -> list[float]:
    order = np.argsort(values)
    sorted_values = values[order]
    sorted_weights = weights[order]
    cumulative = np.cumsum(sorted_weights)
    if cumulative[-1] <= 0:
        return [float("nan") for _ in qs]
    cumulative = cumulative / cumulative[-1]
    return [float(np.interp(q, cumulative, sorted_values)) for q in qs]


def processed_stats() -> dict[str, Any]:
    with PROCESSED.open("rb") as handle:
        processed = pickle.load(handle)

    ddt = np.asarray(processed["ddt_samples"], dtype=float)
    weights = np.asarray(processed["ddt_weights"], dtype=float)
    weight_sum = float(np.sum(weights))
    normalized = weights / weight_sum
    ddt_q16, ddt_q50, ddt_q84 = weighted_quantile(ddt, normalized, [0.16, 0.5, 0.84])

    kappa_pdf = np.asarray(processed["kappa_pdf"], dtype=float)
    kappa_edges = np.asarray(processed["kappa_bin_edges"], dtype=float)
    kappa_centers = 0.5 * (kappa_edges[:-1] + kappa_edges[1:])
    kappa_mass = float(np.trapz(kappa_pdf, kappa_centers))
    if kappa_mass > 0:
        kappa_weights = kappa_pdf / np.sum(kappa_pdf)
        kappa_mean = float(np.sum(kappa_centers * kappa_weights))
        kappa_q16, kappa_q50, kappa_q84 = weighted_quantile(
            kappa_centers, kappa_weights, [0.16, 0.5, 0.84]
        )
    else:
        kappa_mean = float("nan")
        kappa_q16 = kappa_q50 = kappa_q84 = float("nan")

    return {
        "z_lens": float(processed["z_lens"]),
        "z_source": float(processed["z_source"]),
        "ddt_sample_count": int(ddt.size),
        "ddt_weight_sum": weight_sum,
        "ddt_weighted_mean": float(np.sum(ddt * normalized)),
        "ddt_weighted_q16": ddt_q16,
        "ddt_weighted_q50": ddt_q50,
        "ddt_weighted_q84": ddt_q84,
        "sigma_v_measurement": float(np.asarray(processed["sigma_v_measurement"])[0]),
        "kappa_pdf_bin_count": int(kappa_pdf.size),
        "kappa_pdf_integral_trapezoid": kappa_mass,
        "kappa_weighted_mean": kappa_mean,
        "kappa_weighted_q16": kappa_q16,
        "kappa_weighted_q50": kappa_q50,
        "kappa_weighted_q84": kappa_q84,
        "theta_E_property": float(processed["kwargs_lens_properties"]["theta_E"]),
        "gamma_property": float(processed["kwargs_lens_properties"]["gamma"]),
        "r_eff_property": float(processed["kwargs_lens_properties"]["r_eff"]),
    }


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return max(0, sum(1 for _ in handle) - 1)


def main() -> None:
    contract = load_contract()
    targets = contract["notebook_hooks"]["expected_joblib_target_preview"][:]
    # The preview intentionally contains only the first five rows; use rows from
    # the contract summary by re-reading the expected target list stored there.
    targets = contract["notebook_hooks"].get("expected_joblib_target_preview", [])

    # Recover the full 36 target list from the contract script output if present
    # in the generated rows is not possible; parse it again through the contract
    # artifact by importing its helper-free JSON preview would lose rows.  Keep
    # this script independent by reading the generated contract table's model
    # targets from the notebook hook cache when available in source.
    from build_wgd2038_holdout_extraction_contract import (  # noqa: PLC0415
        NOTEBOOK,
        extract_expected_joblib_targets,
    )

    targets = extract_expected_joblib_targets(NOTEBOOK)
    stats = processed_stats()
    ddt_csv_rows = count_csv_rows(DDT_CSV)

    rows: list[dict[str, Any]] = []
    for idx, target in enumerate(targets, start=1):
        rows.append(
            {
                "row_id": f"WGD_PARTIAL_MODEL_{idx:02d}",
                "target_id": "WGD2038-4008",
                "model_family": target["model_family"],
                "model_id": target["model_id"],
                "expected_joblib_path": target["expected_joblib_path"],
                "expected_joblib_present": False,
                "z_lens": stats["z_lens"],
                "z_source": stats["z_source"],
                "ddt_sample_count": stats["ddt_sample_count"],
                "ddt_csv_row_count": ddt_csv_rows,
                "ddt_weighted_mean": stats["ddt_weighted_mean"],
                "ddt_weighted_q16": stats["ddt_weighted_q16"],
                "ddt_weighted_q50": stats["ddt_weighted_q50"],
                "ddt_weighted_q84": stats["ddt_weighted_q84"],
                "kappa_weighted_mean": stats["kappa_weighted_mean"],
                "kappa_weighted_q16": stats["kappa_weighted_q16"],
                "kappa_weighted_q50": stats["kappa_weighted_q50"],
                "kappa_weighted_q84": stats["kappa_weighted_q84"],
                "theta_E_property": stats["theta_E_property"],
                "gamma_property": stats["gamma_property"],
                "r_eff_property": stats["r_eff_property"],
                "per_sample_image_table_present": False,
                "can_compute_dphi_AB_AC_AD": False,
                "can_compute_no_t2_residual_vector": False,
            }
        )

    summary = {
        "schema": "paper7 WGD2038 partial holdout materialization v1",
        "purpose": (
            "Materialize the public, model-level part of the WGD2038 holdout "
            "contract without pretending to have the missing image-wise posterior table."
        ),
        "sources": {
            "contract": str(CONTRACT.relative_to(ROOT)),
            "processed_pickle": str(PROCESSED.relative_to(ROOT)),
            "ddt_weight_csv": str(DDT_CSV.relative_to(ROOT)),
            "kappa_catalog": str(KAPPA_CAT.relative_to(ROOT)),
        },
        "public_payload_stats": stats | {"ddt_csv_row_count": ddt_csv_rows},
        "materialization_counts": {
            "expected_model_target_count": len(targets),
            "materialized_model_manifest_rows": len(rows),
            "expected_joblib_present_count": sum(1 for row in rows if row["expected_joblib_present"]),
            "per_sample_image_table_present_count": sum(
                1 for row in rows if row["per_sample_image_table_present"]
            ),
            "score_ready_model_rows": sum(
                1
                for row in rows
                if row["can_compute_dphi_AB_AC_AD"]
                and row["can_compute_no_t2_residual_vector"]
            ),
        },
        "contract_field_status": {
            "source_backed_now": [
                "target_id",
                "model_family",
                "model_id",
                "ddt_or_time_delay_observable_distribution",
                "ddt_weight_distribution",
                "kappa_environment_distribution",
                "lens_property_summary",
            ],
            "still_missing_for_score": [
                "sample_id",
                "image_label",
                "image_order_index",
                "parity_or_morse_type",
                "ra_image",
                "dec_image",
                "dphi_AB",
                "dphi_AC",
                "dphi_AD",
                "no_t2_model_residual_vector",
            ],
        },
        "verdict": {
            "wgd2038_partial_holdout_materialized": True,
            "public_model_level_manifest_created": True,
            "public_ddt_kappa_support_materialized": True,
            "per_sample_score_table_materialized": False,
            "can_apply_des_frozen_score_now": False,
            "real_data_T2_sampling_authorized": False,
            "claim_level": "source_backed_partial_materialization_not_time_shift_evidence",
        },
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
    print(json.dumps(summary["materialization_counts"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
