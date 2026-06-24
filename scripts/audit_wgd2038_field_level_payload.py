#!/usr/bin/env python3
"""Field-level audit for the WGD2038 Paper 7 real-data T2 route.

This script inspects locally available public TDCOSMO/WGD2038 products when
they have been cloned outside the reproducibility package.  The generated
summary is a source-audit artifact, not a T2 measurement.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import pickle
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results" / "tau_core_lensing_wgd2038_field_level_payload_audit_v1"
OUT_SUMMARY = RESULTS / "summary.json"
OUT_TABLE = DERIVED / "wgd2038_field_level_payload_audit_v1.csv"

DEFAULT_TDCOSMO2025 = Path(
    "/tmp/paper7_tdc_sources/TDCOSMO2025_public/TDCOSMO_sample"
)
DEFAULT_WGD_REPO = Path("/tmp/paper7_tdc_sources/WGD2038-4008")
LOCAL_PUBLIC_PAYLOAD = ROOT / "data" / "external" / "wgd2038_public_payload"
LOCAL_TDCOSMO2025 = LOCAL_PUBLIC_PAYLOAD / "tdcosmo2025_wgd2038"
LOCAL_WGD_NOTEBOOKS = LOCAL_PUBLIC_PAYLOAD / "wgd2038_repo_notebooks"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_obj(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def safe_shape(value: object) -> str | None:
    shape = getattr(value, "shape", None)
    if shape is None:
        return None
    return "x".join(str(part) for part in shape)


def inspect_processed_pickle(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"available": False, "path": str(path)}
    with path.open("rb") as handle:
        payload = pickle.load(handle)
    if not isinstance(payload, dict):
        return {"available": True, "path": str(path), "type": type(payload).__name__}
    keys = sorted(payload.keys())
    fields = {
        key: {
            "type": type(payload[key]).__name__,
            "shape": safe_shape(payload[key]),
            "present": payload[key] is not None,
        }
        for key in keys
    }
    return {
        "available": True,
        "path": str(path),
        "sha256": sha256_file(path),
        "keys": keys,
        "fields": fields,
        "has_ddt_samples": bool(fields.get("ddt_samples", {}).get("present")),
        "ddt_samples_shape": fields.get("ddt_samples", {}).get("shape"),
        "has_ddt_weights": bool(fields.get("ddt_weights", {}).get("present")),
        "has_kappa_pdf": bool(fields.get("kappa_pdf", {}).get("present")),
        "has_lens_properties": bool(fields.get("kwargs_lens_properties", {}).get("present")),
        "has_image_parity": any("parity" in key.lower() for key in keys),
        "has_image_order": any("order" in key.lower() or "image" in key.lower() for key in keys),
        "has_fermat_field": any("fermat" in key.lower() or "phi" in key.lower() for key in keys),
    }


def inspect_csv(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"available": False, "path": str(path)}
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        rows = [row for _, row in zip(range(5), reader)]
    return {
        "available": True,
        "path": str(path),
        "sha256": sha256_file(path),
        "header": header,
        "sample_rows": rows,
        "has_ddt_column": any(col.lower() == "ddt" for col in header),
        "has_weight_column": any(col.lower() == "weight" for col in header),
        "has_image_parity_column": any("parity" in col.lower() for col in header),
        "has_fermat_column": any("fermat" in col.lower() or "phi" in col.lower() for col in header),
    }


def inspect_notebook(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"available": False, "path": str(path)}
    nb = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    text_chunks: list[str] = []
    for cell in nb.get("cells", []):
        src = cell.get("source", [])
        if isinstance(src, list):
            text_chunks.append("".join(str(part) for part in src))
        else:
            text_chunks.append(str(src))
    text = "\n".join(text_chunks).lower()
    return {
        "available": True,
        "path": str(path),
        "sha256": sha256_file(path),
        "mentions_fermat": "fermat" in text,
        "mentions_parity": "parity" in text,
        "mentions_dphi_ab_ac_ad": all(token in text for token in ["dphi_ab", "dphi_ac", "dphi_ad"]),
        "mentions_model_image_positions": "model_image_positions" in text,
        "mentions_joblib_load": "joblib.load" in text,
        "mentions_temp_outputs": "temp" in text and "_out.txt" in text,
        "mentions_saved_lenstronomy_posteriors": "../model_posteriors" in text,
        "mentions_arrival_time": "arrival" in text and "time" in text,
        "mentions_image_labels": "image" in text,
        "mentions_lenstronomy": "lenstronomy" in text,
    }


def inspect_missing_payload_hooks(wgd_repo: Path) -> dict[str, Any]:
    model_posteriors = wgd_repo / "lenstronomy_modeling" / "model_posteriors"
    data_dir = wgd_repo / "lenstronomy_modeling" / "data"
    temp_dir = wgd_repo / "lenstronomy_modeling" / "temp"
    hooks = {
        "model_posteriors_dir": model_posteriors,
        "data_dir": data_dir,
        "temp_joblib_dir": temp_dir,
    }
    return {
        name: {
            "path": str(path),
            "exists": path.exists(),
            "file_count": sum(1 for child in path.rglob("*") if child.is_file())
            if path.exists()
            else 0,
            "has_only_readme_or_lfs_pointer": (
                path.exists()
                and all(
                    child.name in {"README.md", ".gitattributes"}
                    for child in path.iterdir()
                    if child.is_file()
                )
            ),
        }
        for name, path in hooks.items()
    }


def build_summary() -> dict[str, Any]:
    tdcosmo_root = Path(os.environ.get("PAPER7_TDCOSMO2025_SAMPLE", DEFAULT_TDCOSMO2025))
    wgd_repo = Path(os.environ.get("PAPER7_WGD2038_REPO", DEFAULT_WGD_REPO))
    wgd_data = tdcosmo_root / "TDCOSMO_data" / "WGD2038-4008"

    processed_path = LOCAL_TDCOSMO2025 / "WGD2038-4008_const_processed.pkl"
    if not processed_path.exists():
        processed_path = tdcosmo_root / "WGD2038-4008_const_processed.pkl"

    dt_weight_path = LOCAL_TDCOSMO2025 / "desj2038_pl_nokext_nokin_dt_weight.csv"
    if not dt_weight_path.exists():
        dt_weight_path = wgd_data / "desj2038_pl_nokext_nokin_dt_weight.csv"

    fermat_notebook_path = LOCAL_WGD_NOTEBOOKS / "Fermat potentials and lens model comparisons.ipynb"
    if not fermat_notebook_path.exists():
        fermat_notebook_path = (
            wgd_repo
            / "lenstronomy_modeling"
            / "notebooks"
            / "Fermat potentials and lens model comparisons.ipynb"
        )

    convergence_notebook_path = LOCAL_WGD_NOTEBOOKS / "Check models and MCMC chain convergence.ipynb"
    if not convergence_notebook_path.exists():
        convergence_notebook_path = (
            wgd_repo
            / "lenstronomy_modeling"
            / "notebooks"
            / "Check models and MCMC chain convergence.ipynb"
        )

    processed = inspect_processed_pickle(processed_path)
    dt_weight = inspect_csv(dt_weight_path)
    fermat_notebook = inspect_notebook(fermat_notebook_path)
    convergence_notebook = inspect_notebook(convergence_notebook_path)
    payload_hooks = inspect_missing_payload_hooks(wgd_repo)

    criteria = {
        "processed_pickle_available": processed.get("available") is True,
        "ddt_samples_available": processed.get("has_ddt_samples") is True,
        "ddt_weight_csv_available": dt_weight.get("available") is True
        and dt_weight.get("has_ddt_column") is True
        and dt_weight.get("has_weight_column") is True,
        "kappa_environment_available": processed.get("has_kappa_pdf") is True,
        "fermat_notebook_available": fermat_notebook.get("available") is True
        and fermat_notebook.get("mentions_fermat") is True,
        "notebook_defines_t2_design_vector_fields": fermat_notebook.get(
            "mentions_dphi_ab_ac_ad"
        )
        is True
        and fermat_notebook.get("mentions_model_image_positions") is True,
        "notebook_requires_external_model_payload": fermat_notebook.get(
            "mentions_joblib_load"
        )
        is True
        and fermat_notebook.get("mentions_temp_outputs") is True,
        "image_parity_available": processed.get("has_image_parity") is True
        or dt_weight.get("has_image_parity_column") is True
        or fermat_notebook.get("mentions_parity") is True,
        "image_wise_fermat_samples_available": processed.get("has_fermat_field") is True
        or dt_weight.get("has_fermat_column") is True,
        "no_t2_image_model_reproduction_authorized": False,
    }

    rows = [
        {
            "artifact": "TDCOSMO2025 WGD2038 processed pickle",
            "available": processed.get("available"),
            "t2_relevance": "Ddt/kappa/nuisance context",
            "blocking_gap": "No explicit image parity/order or image-wise Fermat samples found in pickle keys.",
            "path": processed.get("path"),
        },
        {
            "artifact": "TDCOSMO2025 WGD2038 Ddt-weight CSV",
            "available": dt_weight.get("available"),
            "t2_relevance": "compressed Ddt posterior support",
            "blocking_gap": "Columns are Ddt and weight only; no image-wise Fermat/parity columns.",
            "path": dt_weight.get("path"),
        },
        {
            "artifact": "WGD2038 Fermat notebook",
            "available": fermat_notebook.get("available"),
            "t2_relevance": "potential route to image/model Fermat reconstruction",
            "blocking_gap": (
                "Notebook defines dphi_AB/dphi_AC/dphi_AD and model image-position "
                "paths, but the joblib/model-posterior payload is not present as an "
                "extracted audit table."
            ),
            "path": fermat_notebook.get("path"),
        },
        {
            "artifact": "WGD2038 convergence/model-chain notebook",
            "available": convergence_notebook.get("available"),
            "t2_relevance": "model-chain/nuisance context",
            "blocking_gap": "Useful for model audit, not sufficient alone for T2 image-wise perturbation.",
            "path": convergence_notebook.get("path"),
        },
    ]

    summary: dict[str, Any] = {
        "schema": "paper7 WGD2038 field-level payload audit v1",
        "purpose": (
            "Decide whether currently inspected WGD2038/TDCOSMO2025 public products "
            "can authorize the Paper 7 no-T2 image/model reproduction gate."
        ),
        "source_roots": {
            "local_public_payload": str(LOCAL_PUBLIC_PAYLOAD),
            "tdcosmo2025_sample": str(tdcosmo_root),
            "wgd2038_repo": str(wgd_repo),
        },
        "artifact_rows": rows,
        "inspections": {
            "processed_pickle": processed,
            "dt_weight_csv": dt_weight,
            "fermat_notebook": fermat_notebook,
            "convergence_notebook": convergence_notebook,
            "missing_payload_hooks": payload_hooks,
        },
        "criteria": criteria,
        "verdict": {
            "WGD2038_field_level_payload_audited": True,
            "real_data_T2_sampling_authorized": False,
            "no_T2_image_model_reproduction_authorized": False,
            "best_current_real_data_route": "WGD2038-4008 via TDCOSMO2025 + target-specific WGD repo",
            "useful_fields_found": [
                "Ddt posterior samples",
                "Ddt weights",
                "kappa/environment distribution",
                "Fermat-potential notebook hook",
                "notebook-level dphi_AB/dphi_AC/dphi_AD design-vector variables",
                "notebook-level model image-position variables",
                "model-chain/convergence notebook hook",
            ],
            "blocking_fields_missing_or_unproven": [
                "image parity/order table",
                "extracted image-wise Fermat-potential difference samples",
                "per-sample mapping from lens-model posterior to T2 design vector",
                "local model posterior/joblib payload needed by the Fermat notebook",
                "validated no-T2 Ddt/null reproduction from those image/model fields",
            ],
            "field_level_interpretation": (
                "The obstacle is no longer that the WGD route lacks a Fermat design "
                "concept. The public notebook contains the relevant dphi_AB/dphi_AC/"
                "dphi_AD construction hooks. The remaining blocker is payload-level: "
                "the model posterior/joblib products must be acquired or extracted "
                "before a reproducible no-T2 image/model table can be built."
            ),
            "claim_level": "source_backed_partial_payload_audit_not_real_data_detection",
            "next_finite_action": (
                "Acquire the WGD2038 Google Drive/LFS model-posterior payload named "
                "by the repository, or otherwise reconstruct the joblib temp outputs, "
                "then run an extractor that materializes per-sample dphi_AB/dphi_AC/"
                "dphi_AD, image positions, image labels, parity/order, Ddt "
                "contribution, and model-sample ID. Without that table Paper 7 "
                "remains real-data blocked."
            ),
        },
        "claim_boundary": {
            "allowed": [
                "WGD2038 is now a concrete best single-target route for Paper 7 real-data follow-up.",
                "Current public products provide Ddt/kappa/model-notebook support.",
                "Current public products still do not authorize T2 sampling.",
            ],
            "forbidden": [
                "Claiming real-data T2 evidence from Ddt-weight samples alone.",
                "Treating a Fermat notebook name as an extracted image-wise Fermat/parity posterior.",
                "Claiming the observer-time distortion is detected.",
            ],
        },
    }
    summary["content_hash"] = sha256_obj(summary)
    return summary


def write_outputs(summary: dict[str, Any]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fieldnames = ["artifact", "available", "t2_relevance", "blocking_gap", "path"]
    with OUT_TABLE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary["artifact_rows"])


def main() -> None:
    summary = build_summary()
    write_outputs(summary)
    print(OUT_SUMMARY)
    print(OUT_TABLE)
    print(summary["verdict"]["next_finite_action"])


if __name__ == "__main__":
    main()
