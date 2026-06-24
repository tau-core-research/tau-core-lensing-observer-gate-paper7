#!/usr/bin/env python3
"""Build a bounded nuisance-stabilization plan from WGD2038 drift diagnostics."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = (
    DERIVED
    / "repro_results"
    / "tau_core_lensing_wgd2038_lenstronomy_hst_reproduction_v1"
)
DRIFT_CSV = DERIVED / "wgd2038_mcmc_parameter_drift_diagnostic_v1.csv"
OUT_JSON = RESULTS / "wgd2038_nuisance_stabilization_plan_v1.json"
OUT_CSV = DERIVED / "wgd2038_nuisance_stabilization_plan_v1.csv"


def sha256_obj(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def classify_param(param_name: str) -> tuple[str, str]:
    if param_name in {"ra_image", "dec_image"}:
        return "image_position", "prior_tighten_or_holdout_audit"
    if "_lens_light" in param_name:
        return "lens_light_profile", "profile_freeze_candidate"
    if "_source_light" in param_name:
        return "source_light_profile", "profile_freeze_candidate"
    if param_name.startswith("gamma") or param_name.startswith("theta_E"):
        return "lens_mass_or_shear", "do_not_freeze_first_pass"
    return "other", "manual_review"


def main() -> None:
    rows = list(csv.DictReader(DRIFT_CSV.open(encoding="utf-8")))
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["param_key"]].append(row)

    plan_rows: list[dict[str, Any]] = []
    for param_key, param_rows in grouped.items():
        values = [float(row["split_half_abs_mean_shift_sigma"]) for row in param_rows]
        param_name = param_rows[0]["param_name"]
        role, action = classify_param(param_name)
        plan_rows.append(
            {
                "param_key": param_key,
                "param_name": param_name,
                "role": role,
                "recommended_action": action,
                "mean_split_half_abs_shift_sigma": mean(values),
                "max_split_half_abs_shift_sigma": max(values),
                "job_count": len(values),
            }
        )

    plan_rows.sort(key=lambda row: row["mean_split_half_abs_shift_sigma"], reverse=True)

    profile_candidates = [
        row
        for row in plan_rows
        if row["recommended_action"] == "profile_freeze_candidate"
        and row["mean_split_half_abs_shift_sigma"] >= 1.0
    ]
    image_candidates = [
        row
        for row in plan_rows
        if row["role"] == "image_position" and row["mean_split_half_abs_shift_sigma"] >= 1.0
    ]
    protected_candidates = [
        row for row in plan_rows if row["recommended_action"] == "do_not_freeze_first_pass"
    ]

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "param_key",
            "param_name",
            "role",
            "recommended_action",
            "mean_split_half_abs_shift_sigma",
            "max_split_half_abs_shift_sigma",
            "job_count",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(plan_rows)

    summary = {
        "schema": "paper7 WGD2038 nuisance stabilization plan v1",
        "claim_level": "diagnostic_plan_not_posterior_convergence",
        "input_csv": str(DRIFT_CSV),
        "output_csv": str(OUT_CSV),
        "real_data_T2_sampling_authorized": False,
        "converged_no_T2_posterior_reproduced": False,
        "counts": {
            "total_parameters": len(plan_rows),
            "profile_freeze_candidates_ge_1sigma_mean": len(profile_candidates),
            "image_position_candidates_ge_1sigma_mean": len(image_candidates),
            "protected_mass_or_shear_parameters": len(protected_candidates),
        },
        "top_profile_freeze_candidates": profile_candidates[:12],
        "top_image_position_candidates": image_candidates[:8],
        "protected_mass_or_shear_candidates": protected_candidates[:8],
        "recommended_next_run": {
            "name": "profile_freeze_v1_bounded_diagnostic",
            "purpose": (
                "Freeze or strongly tighten the highest-drift lens/source-light "
                "profile nuisance directions while leaving mass/shear response "
                "parameters unpromoted and not claiming physical posterior recovery."
            ),
            "do_first": [
                "Use previous best-fit/light-profile values as fixed or tight-prior anchors for the top profile candidates.",
                "Keep image-position parameters under audit rather than interpreting them as Tau/T2 signal.",
                "Rerun the same bounded 120-step diagnostic and compare split-half drift to diagnostic120/cont1/cont2/cont3_cold.",
            ],
            "do_not_claim": [
                "Do not claim no-T2 posterior convergence from a single profile-freeze pass.",
                "Do not sample real-data T2 until a no-T2 image/model posterior is stable.",
                "Do not treat image-position drift as a physical T2 detection.",
            ],
            "success_metric": (
                "Median and p90 split-half drift must fall materially below the "
                "continuation series while finite samples/log-probabilities remain true."
            ),
        },
    }
    summary["content_hash"] = sha256_obj(summary)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT_JSON)
    print(OUT_CSV)
    print(summary["recommended_next_run"]["name"])


if __name__ == "__main__":
    main()
