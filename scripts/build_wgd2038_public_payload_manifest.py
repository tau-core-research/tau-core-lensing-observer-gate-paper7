#!/usr/bin/env python3
"""Build a manifest for the locally acquired WGD2038 public payload.

This is an acquisition/provenance artifact only.  It records which public
WGD2038/TDCOSMO files are present locally and whether they are sufficient for
the Paper 7 no-T2 image/model reproduction gate.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_ROOT = ROOT / "data" / "external" / "wgd2038_public_payload"
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results" / "tau_core_lensing_wgd2038_public_payload_acquisition_v1"
OUT_SUMMARY = RESULTS / "summary.json"
OUT_TABLE = DERIVED / "wgd2038_public_payload_acquisition_manifest_v1.csv"

GOOGLE_DRIVE_FOLDER = "https://drive.google.com/drive/folders/1CHfFN1O9mbTdnWpOabOcA4Ztu2AWi2Ko"

ACQUISITION_ATTEMPTS = [
    {
        "route": "Google Drive folder declared by TDCOSMO/WGD2038-4008 README",
        "target": GOOGLE_DRIVE_FOLDER,
        "method": "gdown folder download and direct unauthenticated browser/API checks",
        "result": "failed",
        "evidence": "folder contents could not be retrieved; direct folder URL returned 404 from current environment",
    },
    {
        "route": "TDCOSMO/WGD2038-4008 GitHub tree",
        "target": "https://github.com/TDCOSMO/WGD2038-4008",
        "method": "recursive GitHub tree inspection",
        "result": "support_only",
        "evidence": "Git tree contains README/notebook hooks but not the temp/joblib model-posterior outputs",
    },
    {
        "route": "TDCOSMO2025_public GitHub tree",
        "target": "https://github.com/TDCOSMO/TDCOSMO2025_public",
        "method": "recursive GitHub tree inspection",
        "result": "support_only",
        "evidence": "Git tree contains WGD2038 processed Ddt/kappa products but not image-wise Fermat/parity joblib outputs",
    },
    {
        "route": "paper/source supplementary route",
        "target": "arXiv:2202.11101 and arXiv:2406.02683 source/public pages",
        "method": "source-package and public-page inspection for data links",
        "result": "summary_source_tables_found_no_joblib_payload",
        "evidence": (
            "arXiv:2406.02683 source includes Ddt/H0 TeX tables now materialized "
            "locally; it does not include the per-sample joblib/Fermat posterior payload"
        ),
    },
    {
        "route": "Zenodo public record search",
        "target": "Zenodo API",
        "method": "keyword search for WGD2038/TDCOSMO IX/model-posterior payload",
        "result": "no_payload_found",
        "evidence": "no relevant WGD2038 model-posterior record found in the queried public records",
    },
    {
        "route": "GitHub authenticated code search for model IDs",
        "target": "TDCOSMO/WGD2038-4008 notebooks",
        "method": "search concrete model IDs and posterior filenames",
        "result": "notebook_hooks_only",
        "evidence": (
            "model IDs occur in additional notebooks such as radial-profile, velocity-dispersion, "
            "PSF-test, and parameter-comparison notebooks, but no corresponding joblib/temp "
            "payload file is tracked"
        ),
    },
    {
        "route": "generic public data repositories",
        "target": "Dataverse, OSF, Figshare-style searches",
        "method": "keyword search for WGD2038/TDCOSMO/model-posterior payload",
        "result": "no_public_payload_found",
        "evidence": "no alternative public archive containing the target WGD2038 joblib/model-posterior payload was found",
    },
]

EXPECTED_FILES = [
    {
        "relative_path": "tdcosmo2025_wgd2038/WGD2038-4008_const_processed.pkl",
        "source_family": "TDCOSMO2025_public",
        "role": "processed WGD2038 Ddt/kappa/nuisance support",
        "t2_status": "support_only",
    },
    {
        "relative_path": "tdcosmo2025_wgd2038/desj2038_pl_nokext_nokin_dt_weight.csv",
        "source_family": "TDCOSMO2025_public",
        "role": "compressed Ddt posterior with weights",
        "t2_status": "support_only_no_image_wise_fermat_or_parity",
    },
    {
        "relative_path": (
            "tdcosmo2025_wgd2038/"
            "kappahist_2038_measured_3innermask_nobeta_removehandpicked_zgap-1.0_-1.0_"
            "fiducial_120_gal_120_oneoverr_22.5_med_increments2_2_emptymsk.cat"
        ),
        "source_family": "TDCOSMO2025_public",
        "role": "external-convergence/environment support",
        "t2_status": "support_only",
    },
    {
        "relative_path": "wgd2038_repo_metadata/README.md",
        "source_family": "TDCOSMO/WGD2038-4008",
        "role": "target repository metadata and Google Drive pointer",
        "t2_status": "provenance_support",
    },
    {
        "relative_path": "wgd2038_repo_notebooks/Fermat potentials and lens model comparisons.ipynb",
        "source_family": "TDCOSMO/WGD2038-4008",
        "role": "Fermat-potential design-vector notebook hook",
        "t2_status": "requires_missing_model_posterior_joblib_payload",
    },
    {
        "relative_path": "wgd2038_repo_notebooks/Check models and MCMC chain convergence.ipynb",
        "source_family": "TDCOSMO/WGD2038-4008",
        "role": "model-chain/convergence notebook hook",
        "t2_status": "requires_missing_model_posterior_joblib_payload",
    },
    {
        "relative_path": "arxiv_2406_02683_source_tables/tab_2038_ddt.tex",
        "source_family": "arXiv:2406.02683 source bundle",
        "role": "published WGD2038 Ddt constraints by model family",
        "t2_status": "published_summary_only_no_image_wise_fermat_or_parity",
    },
    {
        "relative_path": "arxiv_2406_02683_source_tables/tab_2038_ddtmodel_nokext_nokin.tex",
        "source_family": "arXiv:2406.02683 source bundle",
        "role": "published WGD2038 Ddt constraints without kext or kinematics",
        "t2_status": "published_summary_only_no_image_wise_fermat_or_parity",
    },
    {
        "relative_path": "arxiv_2406_02683_source_tables/tab_2038_lcdm_h0.tex",
        "source_family": "arXiv:2406.02683 source bundle",
        "role": "published WGD2038 flat LCDM H0 and Ddt constraints",
        "t2_status": "published_summary_only_no_image_wise_fermat_or_parity",
    },
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_obj(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def inspect_file(row: dict[str, str]) -> dict[str, Any]:
    path = PAYLOAD_ROOT / row["relative_path"]
    present = path.exists()
    return {
        **row,
        "present": present,
        "path": str(path),
        "size_bytes": path.stat().st_size if present else None,
        "sha256": sha256_file(path) if present else None,
    }


def extract_expected_joblib_targets() -> list[dict[str, str]]:
    notebook_path = PAYLOAD_ROOT / "wgd2038_repo_notebooks" / "Fermat potentials and lens model comparisons.ipynb"
    if not notebook_path.exists():
        return []
    notebook = json.loads(notebook_path.read_text(encoding="utf-8", errors="replace"))
    targets: list[dict[str, str]] = []
    model_lists = {
        "powerlaw_files": "powerlaw",
        "composite_files": "composite",
        "composite_files_prev": "composite_previous",
    }
    for cell in notebook.get("cells", []):
        source = cell.get("source", [])
        text = "".join(str(part) for part in source) if isinstance(source, list) else str(source)
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
                                "expected_joblib_path": f"lenstronomy_modeling/temp/{model_id}_out.txt",
                            }
                        )
    return targets


def build_summary() -> dict[str, Any]:
    files = [inspect_file(row) for row in EXPECTED_FILES]
    all_expected_present = all(item["present"] for item in files)
    acquired_support_files = [item for item in files if item["present"]]
    missing_files = [item for item in files if not item["present"]]
    missing_joblib_targets = extract_expected_joblib_targets()

    criteria = {
        "local_public_partial_payload_acquired": all_expected_present,
        "processed_pickle_present": any(
            item["present"] and item["relative_path"].endswith("WGD2038-4008_const_processed.pkl")
            for item in files
        ),
        "ddt_weight_csv_present": any(
            item["present"] and item["relative_path"].endswith("desj2038_pl_nokext_nokin_dt_weight.csv")
            for item in files
        ),
        "fermat_notebook_present": any(
            item["present"] and "Fermat potentials" in item["relative_path"] for item in files
        ),
        "model_posterior_joblib_payload_acquired": False,
        "image_wise_t2_table_acquired": False,
        "google_drive_payload_acquired": False,
        "arxiv_2406_02683_source_tables_acquired": all(
            item["present"] and item["relative_path"].startswith("arxiv_2406_02683_source_tables/")
            for item in files
            if item["relative_path"].startswith("arxiv_2406_02683_source_tables/")
        ),
        "real_data_T2_sampling_authorized": False,
    }

    summary: dict[str, Any] = {
        "schema": "paper7 WGD2038 public payload acquisition manifest v1",
        "purpose": (
            "Record the locally acquired public WGD2038 support payload and preserve "
            "the remaining model-posterior/joblib blocker without promoting it to a "
            "real-data T2 result."
        ),
        "payload_root": str(PAYLOAD_ROOT),
        "google_drive_folder_declared_by_wgd_repo": GOOGLE_DRIVE_FOLDER,
        "google_drive_acquisition_status": (
            "blocked_inaccessible_or_unretrievable_from_current_environment"
        ),
        "acquisition_attempts": ACQUISITION_ATTEMPTS,
        "files": files,
        "missing_model_posterior_joblib_targets": missing_joblib_targets,
        "criteria": criteria,
        "counts": {
            "expected_files": len(files),
            "present_files": len(acquired_support_files),
            "missing_expected_files": len(missing_files),
            "expected_joblib_targets_from_fermat_notebook": len(missing_joblib_targets),
            "total_present_size_bytes": sum(int(item["size_bytes"] or 0) for item in files),
        },
        "verdict": {
            "WGD2038_public_support_payload_acquired": all_expected_present,
            "real_data_T2_sampling_authorized": False,
            "claim_level": "source_backed_partial_payload_acquisition_not_real_data_detection",
            "remaining_blocker": (
                "The public support files are present locally, but the target-specific "
                "model-posterior/joblib payload that drives the Fermat notebook is not "
                "publicly retrievable from the checked routes. Therefore Paper 7 still "
                "lacks the per-sample image/model table needed for a no-T2 reproduction "
                "and T2 perturbation test."
            ),
            "next_finite_action": (
                "Obtain access to the WGD2038 Google Drive payload or reconstruct the "
                "notebook's joblib/temp outputs from reproducible model products, then "
                "extract image labels, parity/order, dphi_AB/dphi_AC/dphi_AD, Ddt "
                "contributions, and model-sample IDs into a frozen audit table."
            ),
        },
        "claim_boundary": {
            "allowed": [
                "The WGD2038 public support payload has been locally acquired and hashed.",
                "The acquired payload supports a concrete follow-up route.",
                "The route remains blocked for real-data T2 sampling pending image-wise model products.",
            ],
            "forbidden": [
                "Claiming a real-data T2 signal.",
                "Inferring image parity/order from Ddt-weight samples alone.",
                "Treating the notebook hook as a materialized image-wise Fermat posterior.",
            ],
        },
    }
    summary["content_hash"] = sha256_obj(summary)
    return summary


def write_outputs(summary: dict[str, Any]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fieldnames = [
        "relative_path",
        "source_family",
        "role",
        "t2_status",
        "present",
        "size_bytes",
        "sha256",
        "path",
    ]
    with OUT_TABLE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary["files"])


def main() -> None:
    summary = build_summary()
    write_outputs(summary)
    print(OUT_SUMMARY)
    print(OUT_TABLE)
    print(summary["verdict"]["remaining_blocker"])


if __name__ == "__main__":
    main()
