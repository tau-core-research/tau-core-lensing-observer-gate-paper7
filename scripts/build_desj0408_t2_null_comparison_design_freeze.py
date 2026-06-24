#!/usr/bin/env python3
"""Freeze a DES J0408 null-vs-T2 comparison design from the no-T2 residual audit.

The frozen design vector is a pre-registration artifact, not a T2 fit. It
records which residual direction a later bounded T2 model would have to explain
and which null explanations must remain in competition.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results"
RESIDUAL_SUMMARY = (
    RESULTS / "tau_core_lensing_desj0408_no_t2_time_residual_candidate_v1" / "summary.json"
)
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_t2_null_comparison_design_freeze_v1"
CSV_PATH = DERIVED / "desj0408_t2_null_comparison_design_freeze_v1.csv"


def normalize(v: tuple[float, float]) -> tuple[float, float]:
    norm = math.sqrt(v[0] ** 2 + v[1] ** 2)
    if norm == 0:
        raise ValueError("Cannot normalize a zero residual vector")
    return (v[0] / norm, v[1] / norm)


def main() -> None:
    residual = json.loads(RESIDUAL_SUMMARY.read_text(encoding="utf-8"))
    aggregate = residual["aggregate"]
    controls = residual["negative_controls"]
    verdict = residual["verdict"]

    model_minus_observed = (
        float(aggregate["unweighted_model_minus_observed_dt1_days"]),
        float(aggregate["unweighted_model_minus_observed_dt2_days"]),
    )
    observed_minus_model = (-model_minus_observed[0], -model_minus_observed[1])
    design_unit = normalize(observed_minus_model)

    logz_model_minus_observed = (
        float(aggregate["logz_weighted_model_minus_observed_dt1_days"]),
        float(aggregate["logz_weighted_model_minus_observed_dt2_days"]),
    )
    logz_observed_minus_model = (
        -logz_model_minus_observed[0],
        -logz_model_minus_observed[1],
    )

    rows = [
        {
            "row_id": "H0_NULL_NO_T2_BASELINE",
            "role": "primary_null",
            "frozen_before_t2_fit": True,
            "description": (
                "A sufficiently flexible no-T2 lens/source/nuisance model explains "
                "the DES residual without a T2 correction."
            ),
            "success_condition": (
                "Residual projection along the frozen design vector is consistent "
                "with zero after the no-T2 baseline and nuisance policy are fixed."
            ),
            "current_status": "open",
        },
        {
            "row_id": "H1_BOUNDED_T2_DIRECTIONAL",
            "role": "candidate_t2",
            "frozen_before_t2_fit": True,
            "description": (
                "A one-amplitude T2 correction is tested only along the frozen "
                "observed-minus-model residual direction."
            ),
            "success_condition": (
                "A shared-amplitude correction improves the held-out likelihood or "
                "predefined residual score against all listed null controls."
            ),
            "current_status": "design_only_not_fitted",
        },
        {
            "row_id": "N1_LENS_FAMILY_MISMATCH",
            "role": "competing_null",
            "frozen_before_t2_fit": True,
            "description": (
                "The residual direction is an ordinary lens-family or source-model "
                "mismatch, not a time-distortion operator."
            ),
            "success_condition": (
                "Alternative no-T2 lens/source families reduce the frozen residual "
                "as well as or better than the T2 candidate."
            ),
            "current_status": "open",
        },
        {
            "row_id": "N2_DES_ROW_OR_RUNTIME_SYSTEMATIC",
            "role": "competing_null",
            "frozen_before_t2_fit": True,
            "description": (
                "The residual direction is induced by public-row linkage, legacy "
                "runtime semantics, or DES-specific posterior handling."
            ),
            "success_condition": (
                "The effect disappears or materially changes after independent row "
                "recovery, legacy-runtime reconstruction, or a second target."
            ),
            "current_status": "open",
        },
        {
            "row_id": "N3_CLEAN_CORE_NONUNIQUE_CONTROL",
            "role": "negative_control",
            "frozen_before_t2_fit": True,
            "description": (
                "The non-clean DES feature rows show a similar residual direction, "
                "so coherence alone is not a T2-specific discriminator."
            ),
            "success_condition": (
                "A future T2 claim must pass a stronger holdout or independent "
                "lens test; coherence alone cannot be counted as evidence."
            ),
            "current_status": "active_control_blocks_coherence_only_claim",
        },
    ]

    summary = {
        "schema": "paper7 DES J0408 null-vs-T2 comparison design freeze v1",
        "purpose": (
            "Pre-register the residual direction and null competitors for a later "
            "bounded DES J0408 T2 comparison without fitting or sampling T2."
        ),
        "source": {
            "residual_summary": str(RESIDUAL_SUMMARY.relative_to(ROOT)),
            "clean_model_ids": residual["source"]["clean_model_ids"],
            "observed_delays_days": residual["source"]["observed_delays_days"],
        },
        "frozen_design_vector": {
            "interpretation": "correction_to_add_to_no_t2_model_before_any_t2_fit",
            "basis": ["dt1_days", "dt2_days"],
            "unweighted_observed_minus_model_days": list(observed_minus_model),
            "unweighted_unit_direction": list(design_unit),
            "logz_weighted_observed_minus_model_days": list(logz_observed_minus_model),
            "clean_pairwise_residual_cosine": aggregate["min_pairwise_residual_cosine"],
            "nonclean_control_pairwise_residual_cosine": controls["nonclean_feature_rows"][
                "min_pairwise_residual_cosine"
            ],
        },
        "controls": {
            "negative_control_rows_checked": True,
            "coherent_residual_is_clean_core_unique": verdict[
                "coherent_residual_is_clean_core_unique"
            ],
            "coherence_alone_supports_t2_claim": verdict[
                "coherence_alone_supports_t2_claim"
            ],
            "nonclean_feature_rows": controls["nonclean_feature_rows"],
        },
        "decision_policy": {
            "t2_fit_allowed_by_this_artifact": False,
            "real_data_T2_sampling_authorized": False,
            "minimum_before_fit": [
                "freeze no-T2 nuisance policy",
                "freeze score/likelihood comparison",
                "define one-amplitude T2 operator on image-level features",
                "run null-family and scramble controls",
                "preferably confirm the design vector on an independent lens target",
            ],
            "claim_boundary": (
                "This artifact freezes a candidate direction and null competitors. "
                "It does not provide a Tau-specific time-shift detection."
            ),
        },
        "verdict": {
            "desj0408_t2_null_comparison_design_freeze_created": True,
            "residual_direction_frozen_before_t2_fit": True,
            "null_competitors_frozen_before_t2_fit": True,
            "coherence_only_claim_blocked": True,
            "bounded_t2_fit_ready": False,
            "tau_specific_time_shift_evidence": False,
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
    print(json.dumps(summary["frozen_design_vector"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
