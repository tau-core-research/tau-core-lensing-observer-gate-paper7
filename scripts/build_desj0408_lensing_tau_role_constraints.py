#!/usr/bin/env python3
"""Build DES J0408 lensing-feature to Tau-role constraints.

This artifact converts the strict DES J0408 no-T2 feature rows into cautious
Tau-side morphology constraints.  It does not derive a physical Tau lensing
response law.  It records which weak Tau roles are forced by the clean
data-side lensing readout and which claims remain blocked.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results"
FEATURE_SUMMARY = (
    RESULTS
    / "tau_core_lensing_desj0408_powerlaw_57_core_feature_table_v1"
    / "summary.json"
)
FAILURE_SUMMARY = (
    RESULTS
    / "tau_core_lensing_desj0408_powerlaw_57_core_failure_diagnostic_v1"
    / "summary.json"
)
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_tau_role_constraints_v1"
CSV_PATH = DERIVED / "desj0408_tau_role_constraints_v1.csv"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    feature = load_json(FEATURE_SUMMARY)
    failure = load_json(FAILURE_SUMMARY)
    rows = feature["rows"]
    clean_rows = [
        row
        for row in rows
        if row["rowwise_feature_row_usable_for_no_t2_baseline"]
        and row["distributional_feature_row_usable_for_no_t2_baseline"]
    ]
    if len(clean_rows) != 2:
        raise SystemExit(f"Expected exactly two strict DES J0408 clean rows, got {len(clean_rows)}")

    clean_model_ids = [row["model_id"] for row in clean_rows]
    lens_families = sorted({row["lens_model_list"] for row in clean_rows})
    source_families = sorted({row["source_light_model_list"] for row in clean_rows})
    max_clean_rmse = max(row["recomputed_vs_public_prefix_rmse_days"] for row in clean_rows)
    max_clean_abs = max(row["recomputed_vs_public_prefix_max_abs_days"] for row in clean_rows)
    max_clean_warning_count = max(row["runtime_warning_count"] for row in clean_rows)
    best_public_chi2 = min(row["published_mean_chi2_vs_observed"] for row in clean_rows)

    constraint_rows = [
        {
            "constraint_id": "LENS_ROLE_01_PROVENANCE",
            "tau_role": "endpoint_blind_source_provenance",
            "data_side_witness": "|".join(clean_model_ids),
            "constraint_statement": (
                "A usable lensing readout must be sourced from public posterior rows "
                "and public time-delay tables before any T2 perturbation is introduced."
            ),
            "evidence_level": "diagnostic_data_constraint",
            "status": "forced_for_strict_desj0408_core",
        },
        {
            "constraint_id": "LENS_ROLE_02_MID_MASS",
            "tau_role": "rho_mid_mass_geometry",
            "data_side_witness": "|".join(lens_families),
            "constraint_statement": (
                "The clean DES readout requires an internal lens-mass geometry carrier; "
                "in the strict rows this is the SPEMD component."
            ),
            "evidence_level": "diagnostic_data_constraint",
            "status": "forced_for_strict_desj0408_core",
        },
        {
            "constraint_id": "LENS_ROLE_03_ENVIRONMENT",
            "tau_role": "rho_env_line_of_sight",
            "data_side_witness": "|".join(lens_families),
            "constraint_statement": (
                "The clean DES readout includes shear and perturber carriers, so the "
                "Tau morphology candidate cannot be a pure isolated-object role."
            ),
            "evidence_level": "diagnostic_data_constraint",
            "status": "forced_for_strict_desj0408_core",
        },
        {
            "constraint_id": "LENS_ROLE_04_SOURCE_STRUCTURE",
            "tau_role": "rho_source_readout_anchor",
            "data_side_witness": "|".join(source_families),
            "constraint_statement": (
                "The clean DES readout is anchored by structured source-light carriers; "
                "source morphology cannot be dropped from the lensing role cover."
            ),
            "evidence_level": "diagnostic_data_constraint",
            "status": "forced_for_strict_desj0408_core",
        },
        {
            "constraint_id": "LENS_ROLE_05_CLOSURE_STABILITY",
            "tau_role": "rho_closure_rowwise_stability",
            "data_side_witness": f"max_rmse_days={max_clean_rmse:.6g};max_abs_days={max_clean_abs:.6g}",
            "constraint_statement": (
                "The strict rows reproduce the public arrival-time table rowwise and "
                "distributionally; a candidate morphology must preserve this closure."
            ),
            "evidence_level": "diagnostic_data_constraint",
            "status": "forced_for_strict_desj0408_core",
        },
        {
            "constraint_id": "LENS_ROLE_06_OBSERVED_DELAY_SCALE",
            "tau_role": "rho_scale_observed_delay_compatibility",
            "data_side_witness": f"best_public_mean_chi2={best_public_chi2:.6g}",
            "constraint_statement": (
                "The lensing readout must remain compatible with observed DES delays "
                "under the declared observed-delay uncertainties."
            ),
            "evidence_level": "diagnostic_data_constraint",
            "status": "forced_for_strict_desj0408_core",
        },
        {
            "constraint_id": "LENS_ROLE_07_NEGATIVE_ROW_POLICY",
            "tau_role": "rho_null_policy_blocker",
            "data_side_witness": "|".join(failure["aggregate"]["outlier_dominated_model_ids"]),
            "constraint_statement": (
                "Outlier-dominated failed models cannot be promoted without an independent "
                "row-recovery or null-policy proof."
            ),
            "evidence_level": "negative_diagnostic_constraint",
            "status": "blocked_not_promoted",
        },
    ]

    summary = {
        "schema": "paper7 DES J0408 lensing-feature to Tau-role constraints v1",
        "purpose": (
            "Convert strict DES J0408 no-T2 feature rows into weak Tau morphology "
            "role constraints for the common morphology candidate."
        ),
        "source": {
            "feature_summary": str(FEATURE_SUMMARY.relative_to(ROOT)),
            "failure_summary": str(FAILURE_SUMMARY.relative_to(ROOT)),
            "clean_model_ids": clean_model_ids,
        },
        "aggregate": {
            "strict_clean_model_count": len(clean_rows),
            "constraint_count": len(constraint_rows),
            "forced_constraint_count": sum(
                row["status"] == "forced_for_strict_desj0408_core" for row in constraint_rows
            ),
            "blocked_constraint_count": sum(
                row["status"] == "blocked_not_promoted" for row in constraint_rows
            ),
            "max_clean_recomputed_vs_public_prefix_rmse_days": max_clean_rmse,
            "max_clean_recomputed_vs_public_prefix_max_abs_days": max_clean_abs,
            "max_clean_runtime_warning_count": max_clean_warning_count,
        },
        "criteria": {
            "uses_only_strict_clean_desj0408_no_t2_rows": True,
            "introduces_t2_parameter": False,
            "derives_physical_tau_lensing_response_law": False,
            "promotes_failed_models": False,
            "constrains_common_morphology_candidate": True,
            "real_data_T2_sampling_authorized": False,
        },
        "verdict": {
            "desj0408_tau_role_constraints_created": True,
            "common_morphology_lensing_role_cover_narrowed": True,
            "physical_response_tau_lens_derived": False,
            "failed_desj0408_models_remain_blocked": True,
            "real_data_T2_sampling_authorized": False,
        },
        "rows": constraint_rows,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(constraint_rows[0]))
        writer.writeheader()
        writer.writerows(constraint_rows)

    print(json.dumps(summary["verdict"], indent=2, sort_keys=True))
    print(json.dumps(summary["aggregate"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
