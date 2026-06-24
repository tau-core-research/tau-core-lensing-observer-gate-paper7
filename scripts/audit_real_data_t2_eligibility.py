#!/usr/bin/env python3
"""Audit public source families for Paper 7 real-data T2 eligibility.

The audit is intentionally conservative.  A source can help Paper 7 only if it
can support the no-T2 image/model reproduction gate before any T2 perturbation
is sampled.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results" / "tau_core_lensing_real_data_t2_eligibility_audit_v1"

OUT_SUMMARY = RESULTS / "summary.json"
OUT_TABLE = DERIVED / "real_data_t2_eligibility_audit_v1.csv"


CRITERIA = [
    "public_version_pin",
    "target_specific_lens_products",
    "image_or_model_level_products",
    "fermat_or_potential_information",
    "image_parity_or_order_information",
    "time_delay_observations_or_distance_likelihood",
    "nuisance_or_model_ensemble",
    "no_t2_reproduction_possible_without_extra_private_products",
]


SOURCES = [
    {
        "source_id": "TDCOSMO2025_public",
        "url": "https://github.com/TDCOSMO/TDCOSMO2025_public",
        "remote_head": "d7f38db341f68be1df0d9ac1fc528c45113f94cf",
        "source_type": "time_delay_cosmography_likelihood_and_processed_lens_posteriors",
        "inspected_evidence": [
            "README: notebooks and scripts reproduce arXiv:2506.03023 analysis",
            "TDCOSMO_sample/README: individual lens posteriors and joint hierarchical analysis",
            "TDCOSMO_sample/TDCOSMO_data contains per-target distance, kext, and some lens-model posterior products",
        ],
        "criteria": {
            "public_version_pin": True,
            "target_specific_lens_products": True,
            "image_or_model_level_products": "partial",
            "fermat_or_potential_information": "partial",
            "image_parity_or_order_information": False,
            "time_delay_observations_or_distance_likelihood": True,
            "nuisance_or_model_ensemble": True,
            "no_t2_reproduction_possible_without_extra_private_products": False,
        },
        "paper7_use": "priority_followup_source_audit",
        "verdict": "PROMISING_PARTIAL_NOT_YET_T2_ELIGIBLE",
        "reason": (
            "The 2025 package is a major public update and contains processed "
            "per-lens products, but Paper 7 still needs a field-level audit for "
            "image ordering/parity, Fermat-difference samples, and no-T2 Ddt/null "
            "reproduction before T2 sampling can be authorized."
        ),
    },
    {
        "source_id": "TDCOSMO_WGD2038_4008",
        "url": "https://github.com/TDCOSMO/WGD2038-4008",
        "remote_head": "da1eda8a0c5c111cc4a59ca9d5e94f31bf3cac02",
        "source_type": "target_specific_time_delay_lens_modeling_repository",
        "inspected_evidence": [
            "README: cosmographic lens modeling of WGD2038-4008",
            "lenstronomy_modeling/notebooks/Fermat potentials and lens model comparisons.ipynb",
            "README: missing data/posterior folders are in a linked Google Drive folder",
        ],
        "criteria": {
            "public_version_pin": True,
            "target_specific_lens_products": True,
            "image_or_model_level_products": "partial_external_payload_needed",
            "fermat_or_potential_information": "notebook_present",
            "image_parity_or_order_information": "undetermined",
            "time_delay_observations_or_distance_likelihood": True,
            "nuisance_or_model_ensemble": "external_payload_needed",
            "no_t2_reproduction_possible_without_extra_private_products": "maybe_after_drive_payload",
        },
        "paper7_use": "best_single_target_acquisition_candidate",
        "verdict": "BEST_REAL_DATA_T2_ACQUISITION_TARGET_BUT_PAYLOAD_INCOMPLETE",
        "reason": (
            "This is the most direct Paper 7 target because it is target-specific "
            "and already names Fermat-potential/model-comparison notebooks.  It "
            "cannot yet authorize T2 sampling until the linked posterior/data "
            "payload is acquired and shown to include enough image/model products."
        ),
    },
    {
        "source_id": "TDCOSMO_TD_data_public",
        "url": "https://github.com/TDCOSMO/TD_data_public",
        "remote_head": "e78933f7af187d548ae4e421bc548f835b1f1330",
        "source_type": "public_tdcosmo_notebooks_and_mock_material",
        "inspected_evidence": [
            "README: public TDCOSMO data, notebooks, MCMC chains",
            "TDCOSMO_VII: mock images and modeling chains for boxy/discy lens tests",
        ],
        "criteria": {
            "public_version_pin": True,
            "target_specific_lens_products": "mixed",
            "image_or_model_level_products": "mock_or_method_level",
            "fermat_or_potential_information": "not_primary_real_data_gate",
            "image_parity_or_order_information": "not_primary_real_data_gate",
            "time_delay_observations_or_distance_likelihood": "partial",
            "nuisance_or_model_ensemble": "method_level",
            "no_t2_reproduction_possible_without_extra_private_products": False,
        },
        "paper7_use": "method_and_control_support",
        "verdict": "METHOD_SUPPORT_NOT_REAL_DATA_T2_ELIGIBLE",
        "reason": (
            "Useful for method checks and mock/control design, but not enough by "
            "itself for a real-data no-T2 image/model reproduction gate."
        ),
    },
    {
        "source_id": "H0LiCOW_public",
        "url": "https://github.com/shsuyu/H0LiCOW-public",
        "remote_head": "57cf97357e16a94ba0065472bd4185cfbc604aa3",
        "source_type": "distance_posterior_and_cosmology_chains",
        "inspected_evidence": [
            "README: posterior distributions of time-delay and angular-diameter distances",
            "h0licow_distance_chains includes compressed Ddt/Dd products",
        ],
        "criteria": {
            "public_version_pin": True,
            "target_specific_lens_products": "distance_level",
            "image_or_model_level_products": False,
            "fermat_or_potential_information": False,
            "image_parity_or_order_information": False,
            "time_delay_observations_or_distance_likelihood": True,
            "nuisance_or_model_ensemble": "compressed",
            "no_t2_reproduction_possible_without_extra_private_products": False,
        },
        "paper7_use": "compressed_distance_baseline_only",
        "verdict": "TOO_COMPRESSED_FOR_T2_REAL_DATA_GATE",
        "reason": (
            "Good for cosmographic distance context, but too compressed to decide "
            "how image-level Fermat/parity perturbations propagate into the Ddt/null "
            "posterior."
        ),
    },
    {
        "source_id": "tdcosmo_ext",
        "url": "https://github.com/nataliehogg/tdcosmo_ext",
        "remote_head": "2a214f08e836cb1aa9bb5e9cfa93868c97df5eac",
        "source_type": "cobaya_external_likelihood_wrapper",
        "inspected_evidence": [
            "README: TDCOSMO likelihood as an external package for Cobaya",
            "README: safe time-delay and IFU-kinematics processed likelihoods are identified",
        ],
        "criteria": {
            "public_version_pin": True,
            "target_specific_lens_products": "processed_likelihood",
            "image_or_model_level_products": False,
            "fermat_or_potential_information": False,
            "image_parity_or_order_information": False,
            "time_delay_observations_or_distance_likelihood": True,
            "nuisance_or_model_ensemble": "processed_hierarchical_likelihood",
            "no_t2_reproduction_possible_without_extra_private_products": False,
        },
        "paper7_use": "downstream_likelihood_context_after_image_gate",
        "verdict": "LIKELIHOOD_CONTEXT_NOT_T2_GATE_INPUT",
        "reason": (
            "Helpful after an image/model-level no-T2 gate exists, but it does not "
            "supply the image-wise Fermat/parity information needed to define the "
            "Paper 7 T2 perturbation."
        ),
    },
]


def sha256_obj(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def criterion_pass(value: object) -> bool:
    return value is True


def build_summary() -> dict[str, object]:
    rows = []
    for source in SOURCES:
        criteria = source["criteria"]
        pass_count = sum(criterion_pass(criteria[key]) for key in CRITERIA)
        rows.append(
            {
                "source_id": source["source_id"],
                "url": source["url"],
                "remote_head": source["remote_head"],
                "source_type": source["source_type"],
                "pass_count": pass_count,
                "criteria_count": len(CRITERIA),
                "paper7_use": source["paper7_use"],
                "verdict": source["verdict"],
                "reason": source["reason"],
                **{key: criteria[key] for key in CRITERIA},
            }
        )

    summary: dict[str, object] = {
        "schema": "paper7 real-data T2 eligibility audit v1",
        "purpose": (
            "Identify whether newly inspected public time-delay lensing products "
            "can unblock the Paper 7 no-T2 image/model reproduction gate."
        ),
        "claim_boundary": {
            "allowed": [
                "Public source families can be ranked for Paper 7 real-data T2 eligibility.",
                "TDCOSMO2025_public and TDCOSMO/WGD2038-4008 are concrete follow-up source candidates.",
                "The current audit does not authorize real-data T2 sampling.",
            ],
            "forbidden": [
                "Claiming a real-data T2 detection.",
                "Treating compressed distance chains as image-level Fermat/parity products.",
                "Promoting a processed cosmology likelihood to a Tau-derived observer-time law.",
            ],
        },
        "criteria": CRITERIA,
        "source_rows": rows,
        "verdict": {
            "real_data_T2_sampling_authorized": False,
            "evidence_grade_target_found": False,
            "best_followup_target": "TDCOSMO_WGD2038_4008",
            "best_followup_source": "TDCOSMO2025_public",
            "new_information_since_original_paper7": (
                "TDCOSMO2025_public provides a fresh public 2025 analysis package "
                "with processed per-lens products; WGD2038-4008 is a target-specific "
                "repository with Fermat-potential notebook hooks but still needs "
                "the linked posterior/data payload audit."
            ),
            "next_finite_action": (
                "Acquire or inspect the WGD2038-4008 linked posterior/data payload "
                "and run a field-level parser for image labels, parity/order, "
                "Fermat-potential samples, time-delay observations, and nuisance "
                "ensemble membership. If any required field is absent, keep Paper 7 "
                "real-data T2 status blocked."
            ),
        },
    }
    summary["content_hash"] = sha256_obj(summary)
    return summary


def write_outputs(summary: dict[str, object]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = summary["source_rows"]
    assert isinstance(rows, list)
    fieldnames = [
        "source_id",
        "url",
        "remote_head",
        "source_type",
        "pass_count",
        "criteria_count",
        *CRITERIA,
        "paper7_use",
        "verdict",
        "reason",
    ]
    with OUT_TABLE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    summary = build_summary()
    write_outputs(summary)
    print(OUT_SUMMARY)
    print(OUT_TABLE)
    print(summary["verdict"]["next_finite_action"])


if __name__ == "__main__":
    main()
