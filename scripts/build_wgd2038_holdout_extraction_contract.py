#!/usr/bin/env python3
"""Build the WGD2038 holdout extraction contract for the DES-frozen T2 score.

This artifact specifies the per-sample image/model table required before the
DES J0408 frozen one-amplitude score can be tested on WGD2038. It does not
extract missing private/joblib payloads and does not authorize real-data T2
sampling.
"""

from __future__ import annotations

import ast
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results"
PAYLOAD_ROOT = ROOT / "data" / "external" / "wgd2038_public_payload"
NOTEBOOK = (
    PAYLOAD_ROOT
    / "wgd2038_repo_notebooks"
    / "Fermat potentials and lens model comparisons.ipynb"
)
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_holdout_extraction_contract_v1"
OUT_TABLE = DERIVED / "wgd2038_holdout_extraction_contract_v1.csv"


def load_result(name: str) -> dict[str, Any]:
    return json.loads((RESULTS / name / "summary.json").read_text(encoding="utf-8"))


def notebook_text(path: Path) -> str:
    if not path.exists():
        return ""
    nb = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    chunks: list[str] = []
    for cell in nb.get("cells", []):
        src = cell.get("source", [])
        chunks.append("".join(str(part) for part in src) if isinstance(src, list) else str(src))
    return "\n".join(chunks)


def extract_expected_joblib_targets(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    nb = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    targets: list[dict[str, str]] = []
    model_lists = {
        "powerlaw_files": "powerlaw",
        "composite_files": "composite",
        "composite_files_prev": "composite_previous",
    }
    for cell in nb.get("cells", []):
        src = cell.get("source", [])
        text = "".join(str(part) for part in src) if isinstance(src, list) else str(src)
        try:
            module = ast.parse(text)
        except SyntaxError:
            continue
        for node in module.body:
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if not isinstance(target, ast.Name) or target.id not in model_lists:
                    continue
                try:
                    model_ids = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    continue
                for model_id in model_ids:
                    if isinstance(model_id, str):
                        targets.append(
                            {
                                "model_family": model_lists[target.id],
                                "model_id": model_id,
                                "expected_joblib_path": (
                                    f"lenstronomy_modeling/temp/{model_id}_out.txt"
                                ),
                            }
                        )
    return targets


def contract_rows() -> list[dict[str, object]]:
    rows = [
        {
            "field_name": "target_id",
            "dtype": "string",
            "required": True,
            "source_hook": "constant WGD2038-4008",
            "current_status": "derivable",
            "pass_condition": "all rows equal WGD2038-4008",
            "blocker_if_missing": "cannot identify independent holdout target",
        },
        {
            "field_name": "model_family",
            "dtype": "string enum",
            "required": True,
            "source_hook": "powerlaw_files/composite_files/composite_files_prev",
            "current_status": "notebook_hook_available",
            "pass_condition": "one of powerlaw, composite, composite_previous",
            "blocker_if_missing": "cannot stratify holdout by model family",
        },
        {
            "field_name": "model_id",
            "dtype": "string",
            "required": True,
            "source_hook": "notebook model file lists",
            "current_status": "notebook_hook_available",
            "pass_condition": "matches expected *_out.txt model target",
            "blocker_if_missing": "cannot link rows to source model posterior",
        },
        {
            "field_name": "sample_id",
            "dtype": "integer",
            "required": True,
            "source_hook": "joblib fit_output sample index",
            "current_status": "blocked_missing_joblib_payload",
            "pass_condition": "unique within model_id",
            "blocker_if_missing": "cannot form per-sample holdout residuals",
        },
        {
            "field_name": "image_label",
            "dtype": "string enum",
            "required": True,
            "source_hook": "model_image_positions/image ordering",
            "current_status": "blocked_missing_extracted_image_order",
            "pass_condition": "labels A,B,C,D are present or mapped",
            "blocker_if_missing": "cannot define comparable branch/readout channels",
        },
        {
            "field_name": "image_order_index",
            "dtype": "integer",
            "required": True,
            "source_hook": "model_image_positions order",
            "current_status": "blocked_missing_extracted_image_order",
            "pass_condition": "four-image order is stable per sample",
            "blocker_if_missing": "cannot map dphi_AB/dphi_AC/dphi_AD to image branches",
        },
        {
            "field_name": "parity_or_morse_type",
            "dtype": "string or integer",
            "required": True,
            "source_hook": "lens-model Hessian/Morse classification",
            "current_status": "blocked_not_materialized",
            "pass_condition": "parity/Morse role available for each image",
            "blocker_if_missing": "cannot evaluate parity-weighted T2 controls",
        },
        {
            "field_name": "ra_image",
            "dtype": "float array or scalar",
            "required": True,
            "source_hook": "model_image_positions",
            "current_status": "notebook_hook_available_but_not_extracted",
            "pass_condition": "finite image RA coordinate",
            "blocker_if_missing": "cannot audit image ordering or geometry",
        },
        {
            "field_name": "dec_image",
            "dtype": "float array or scalar",
            "required": True,
            "source_hook": "model_image_positions",
            "current_status": "notebook_hook_available_but_not_extracted",
            "pass_condition": "finite image Dec coordinate",
            "blocker_if_missing": "cannot audit image ordering or geometry",
        },
        {
            "field_name": "dphi_AB",
            "dtype": "float",
            "required": True,
            "source_hook": "notebook dphi_AB = fermat_potential[1] - fermat_potential[3]",
            "current_status": "notebook_formula_available_but_samples_blocked",
            "pass_condition": "finite per-sample AB Fermat difference",
            "blocker_if_missing": "cannot project WGD into DES-like time-residual basis",
        },
        {
            "field_name": "dphi_AC",
            "dtype": "float",
            "required": True,
            "source_hook": "notebook dphi_AC = fermat_potential[1] - fermat_potential[2]",
            "current_status": "notebook_formula_available_but_samples_blocked",
            "pass_condition": "finite per-sample AC Fermat difference",
            "blocker_if_missing": "cannot project WGD into DES-like time-residual basis",
        },
        {
            "field_name": "dphi_AD",
            "dtype": "float",
            "required": True,
            "source_hook": "notebook dphi_AD = fermat_potential[1] - fermat_potential[0]",
            "current_status": "notebook_formula_available_but_samples_blocked",
            "pass_condition": "finite per-sample AD Fermat difference",
            "blocker_if_missing": "cannot project WGD into DES-like time-residual basis",
        },
        {
            "field_name": "ddt_or_time_delay_observable",
            "dtype": "float",
            "required": True,
            "source_hook": "TDCOSMO2025 WGD2038 Ddt/weight support",
            "current_status": "compressed_support_available_not_image_wise",
            "pass_condition": "linked to model/sample or declared as external likelihood",
            "blocker_if_missing": "cannot score observed-vs-model time residual",
        },
        {
            "field_name": "ddt_weight_or_sample_weight",
            "dtype": "float",
            "required": True,
            "source_hook": "desj2038_pl_nokext_nokin_dt_weight.csv or posterior weights",
            "current_status": "compressed_support_available_not_image_wise",
            "pass_condition": "nonnegative finite weight with documented normalization",
            "blocker_if_missing": "cannot aggregate holdout score reproducibly",
        },
        {
            "field_name": "no_t2_model_residual_vector",
            "dtype": "float array",
            "required": True,
            "source_hook": "derived from model dphi/time predictions and observed delay linkage",
            "current_status": "blocked_until_image_model_table_exists",
            "pass_condition": "finite vector comparable to frozen DES score basis",
            "blocker_if_missing": "cannot apply DES-frozen one-amplitude score",
        },
    ]
    for idx, row in enumerate(rows, start=1):
        row["row_id"] = f"WGD_HOLDOUT_FIELD_{idx:02d}"
    return rows


def main() -> None:
    field = load_result("tau_core_lensing_wgd2038_field_level_payload_audit_v1")
    acquisition = load_result("tau_core_lensing_wgd2038_public_payload_acquisition_v1")
    hst = load_result("tau_core_lensing_wgd2038_lenstronomy_hst_reproduction_v1")
    holdout = load_result("tau_core_lensing_desj0408_t2_holdout_readiness_v1")

    text = notebook_text(NOTEBOOK).lower()
    targets = extract_expected_joblib_targets(NOTEBOOK)
    rows = contract_rows()
    required_count = sum(1 for row in rows if row["required"])
    currently_derivable = sum(
        1
        for row in rows
        if str(row["current_status"]) in {"derivable", "notebook_hook_available"}
    )
    blocked_count = sum(1 for row in rows if "blocked" in str(row["current_status"]))

    summary = {
        "schema": "paper7 WGD2038 holdout extraction contract v1",
        "purpose": (
            "Specify the exact per-sample WGD2038 image/model table required to "
            "test the DES-frozen one-amplitude score on an independent lens."
        ),
        "source": {
            "fermat_notebook": str(NOTEBOOK.relative_to(ROOT)),
            "field_payload_audit": (
                "data/derived/repro_results/"
                "tau_core_lensing_wgd2038_field_level_payload_audit_v1/summary.json"
            ),
            "public_payload_acquisition": (
                "data/derived/repro_results/"
                "tau_core_lensing_wgd2038_public_payload_acquisition_v1/summary.json"
            ),
            "hst_reproduction": (
                "data/derived/repro_results/"
                "tau_core_lensing_wgd2038_lenstronomy_hst_reproduction_v1/summary.json"
            ),
            "holdout_readiness": (
                "data/derived/repro_results/"
                "tau_core_lensing_desj0408_t2_holdout_readiness_v1/summary.json"
            ),
        },
        "notebook_hooks": {
            "fermat_notebook_present": NOTEBOOK.exists(),
            "mentions_joblib_load": "joblib.load" in text,
            "mentions_model_image_positions": "model_image_positions" in text,
            "mentions_dphi_ab_ac_ad": all(t in text for t in ["dphi_ab", "dphi_ac", "dphi_ad"]),
            "expected_joblib_target_count": len(targets),
            "expected_joblib_target_preview": targets[:5],
        },
        "contract_counts": {
            "required_field_count": required_count,
            "currently_derivable_or_hook_available_count": currently_derivable,
            "blocked_field_count": blocked_count,
            "expected_joblib_target_count": len(targets),
        },
        "readiness_inputs": {
            "wgd2038_field_criteria": field["criteria"],
            "wgd2038_public_payload_criteria": acquisition["criteria"],
            "wgd2038_hst_criteria_subset": {
                "multiband_data_setup_preflight_executed": hst["criteria"][
                    "multiband_data_setup_preflight_executed"
                ],
                "converged_no_T2_posterior_reproduced": hst["criteria"][
                    "converged_no_T2_posterior_reproduced"
                ],
                "posterior_joblib_outputs_reproduced": hst["criteria"][
                    "posterior_joblib_outputs_reproduced"
                ],
            },
            "holdout_verdict": holdout["verdict"],
        },
        "verdict": {
            "wgd2038_holdout_extraction_contract_created": True,
            "per_sample_contract_defined": True,
            "expected_joblib_targets_identified": len(targets) > 0,
            "can_extract_holdout_table_now": False,
            "can_apply_des_frozen_score_now": False,
            "remaining_primary_blocker": (
                "missing joblib/posterior payload and non-materialized image-wise "
                "Fermat/parity/arrival table"
            ),
            "real_data_T2_sampling_authorized": False,
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
    print(json.dumps(summary["contract_counts"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
