#!/usr/bin/env python3
"""Audit alternate public source candidates for the Paper 7 real-data route.

This script does not sample T2 and does not claim a real-data detection.  It
records whether locally cached public source repositories contain enough
image/model material to justify a bounded no-T2 reproduction follow-up.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "data" / "external" / "source_candidate_repos"
DERIVED = ROOT / "data" / "derived"
OUT_DIR = DERIVED / "repro_results" / "tau_core_lensing_alternate_source_candidate_audit_v1"
CSV_PATH = DERIVED / "alternate_real_data_source_candidate_audit_v1.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_files(root: Path, suffix: str) -> int:
    return sum(1 for p in root.rglob(f"*{suffix}") if p.is_file())


def notebook_hits(root: Path) -> dict[str, list[str]]:
    terms = [
        "Fermat",
        "fermat",
        "potential",
        "kwargs_result",
        "D_dt",
        "Ddt",
        "time delay",
        "joblib",
        "pickle",
        "fit_sequence",
        "MCMC",
        "emcee",
        "lenstronomy",
        "image_position",
        "ra_image",
        "dec_image",
        "kappa_ext",
        "blind",
    ]
    hits: dict[str, list[str]] = {}
    for nb in sorted(root.rglob("*.ipynb")):
        text = nb.read_text(encoding="utf-8", errors="ignore")
        found = [term for term in terms if re.search(re.escape(term), text, re.IGNORECASE)]
        hits[str(nb.relative_to(root))] = found
    return hits


def first_text_shape(path: Path) -> tuple[int, int | None]:
    rows = 0
    cols: int | None = None
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            rows += 1
            if cols is None:
                cols = len(stripped.split())
    return rows, cols


def audit_desj0408() -> dict[str, object]:
    root = EXTERNAL / "DESJ0408_time_delay_cosmography"
    data_dir = root / "data"
    lens_dir = root / "model_posteriors" / "lens_models"
    td_dir = root / "model_posteriors" / "time_delays"
    vd_dir = root / "model_posteriors" / "velocity_dispersion"
    known = root / "notebooks" / "known_solution.pickle"
    time_delay_files = sorted(td_dir.glob("*.txt")) if td_dir.exists() else []
    time_delay_rows, time_delay_cols = (0, None)
    if time_delay_files:
        time_delay_rows, time_delay_cols = first_text_shape(time_delay_files[0])
    lens_files = sorted(lens_dir.glob("*.txt")) if lens_dir.exists() else []
    hdf5_files = sorted(data_dir.glob("*.hdf5")) if data_dir.exists() else []
    criteria = {
        "repository_cached": root.exists(),
        "real_lens_not_mock": True,
        "processed_multiband_imaging_available": len(hdf5_files) >= 6,
        "known_solution_pickle_available": known.exists(),
        "lens_model_posterior_files_available": len(lens_files) >= 1,
        "time_delay_posterior_files_available": len(time_delay_files) >= 1,
        "velocity_dispersion_grid_available": vd_dir.exists()
        and len(list(vd_dir.glob("*.txt"))) >= 1,
        "lenstronomy_notebooks_available": count_files(root, ".ipynb") >= 1,
        "fermat_keyword_found": any(
            "fermat" in term.lower()
            for terms in notebook_hits(root).values()
            for term in terms
        ),
        "image_position_keyword_found": any(
            term in {"image_position", "ra_image", "dec_image"}
            for terms in notebook_hits(root).values()
            for term in terms
        ),
        "direct_t2_sampling_authorized": False,
    }
    followup_ready = all(
        [
            criteria["repository_cached"],
            criteria["processed_multiband_imaging_available"],
            criteria["known_solution_pickle_available"],
            criteria["lens_model_posterior_files_available"],
            criteria["time_delay_posterior_files_available"],
            criteria["lenstronomy_notebooks_available"],
        ]
    )
    return {
        "source_id": "DESJ0408_time_delay_cosmography",
        "source_url": "https://github.com/ajshajib/DESJ0408_time_delay_cosmography",
        "classification": "REAL_TARGET_NOTEBOOK_AND_POSTERIOR_CANDIDATE",
        "local_path": str(root.relative_to(ROOT)),
        "criteria": criteria,
        "counts": {
            "notebooks": count_files(root, ".ipynb"),
            "hdf5_data_psf_files": len(hdf5_files),
            "lens_model_posterior_files": len(lens_files),
            "time_delay_posterior_files": len(time_delay_files),
            "velocity_dispersion_files": len(list(vd_dir.glob("*.txt"))) if vd_dir.exists() else 0,
            "representative_time_delay_rows": time_delay_rows,
            "representative_time_delay_columns": time_delay_cols,
        },
        "representative_hashes": {
            "known_solution_pickle_sha256": sha256(known) if known.exists() else None,
            "first_time_delay_file_sha256": sha256(time_delay_files[0]) if time_delay_files else None,
            "first_lens_model_file_sha256": sha256(lens_files[0]) if lens_files else None,
        },
        "notebook_hits": notebook_hits(root),
        "followup_ready_for_bounded_no_t2_reproduction": followup_ready,
        "real_data_T2_sampling_authorized": False,
        "claim_boundary": (
            "DES J0408 is a stronger alternate public follow-up candidate than a "
            "compressed distance-posterior source, but this audit does not clear "
            "the no-T2 posterior gate or authorize T2 sampling."
        ),
        "next_step": (
            "Build a compatibility extractor for the DES J0408 notebooks/posterior "
            "files and run a bounded no-T2 baseline reproduction before any T2 path."
        ),
    }


def audit_td_data_public() -> dict[str, object]:
    root = EXTERNAL / "TD_data_public"
    tdc_vii = root / "TDCOSMO_VII"
    example_files = tdc_vii / "example_files"
    criteria = {
        "repository_cached": root.exists(),
        "contains_tdcosmo_i_pstd_notebook": (root / "TDCOSMO_I" / "PSTD_notebook.ipynb").exists(),
        "contains_tdcosmo_vii_multipole_notebook": (
            root / "TDCOSMO_VII" / "multipole_project_core_code_public.ipynb"
        ).exists(),
        "contains_mock_or_example_fits": len(list(example_files.glob("*.fits")))
        if example_files.exists()
        else 0,
        "contains_mock_or_example_mcmc_npy": len(list(example_files.glob("*mcmc*.npy")))
        if example_files.exists()
        else 0,
        "real_target_image_model_payload_confirmed": False,
        "direct_t2_sampling_authorized": False,
    }
    return {
        "source_id": "TD_data_public",
        "source_url": "https://github.com/TDCOSMO/TD_data_public",
        "classification": "METHOD_CONTROL_OR_MOCK_VALIDATION_CANDIDATE",
        "local_path": str(root.relative_to(ROOT)),
        "criteria": criteria,
        "counts": {
            "notebooks": count_files(root, ".ipynb"),
            "fits": count_files(root, ".fits"),
            "npy": count_files(root, ".npy"),
        },
        "notebook_hits": notebook_hits(root),
        "followup_ready_for_bounded_no_t2_reproduction": False,
        "real_data_T2_sampling_authorized": False,
        "claim_boundary": (
            "TD_data_public is useful for method and mock/control validation; this "
            "audit does not identify it as a real-target no-T2 evidence gate."
        ),
        "next_step": (
            "Use only as a method-control source unless a target-specific real-data "
            "image/model posterior payload is identified."
        ),
    }


def write_csv(rows: list[dict[str, object]]) -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    fields = [
        "source_id",
        "classification",
        "followup_ready_for_bounded_no_t2_reproduction",
        "real_data_T2_sampling_authorized",
        "source_url",
        "local_path",
        "next_step",
    ]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def main() -> None:
    rows = [audit_desj0408(), audit_td_data_public()]
    best = max(
        rows,
        key=lambda row: (
            bool(row["followup_ready_for_bounded_no_t2_reproduction"]),
            row["classification"] == "REAL_TARGET_NOTEBOOK_AND_POSTERIOR_CANDIDATE",
        ),
    )
    summary = {
        "schema": "paper7 alternate real-data source candidate audit v1",
        "purpose": (
            "Search for a better public Paper 7 real-data no-T2 follow-up source "
            "after the WGD2038 nuisance-stability blocker."
        ),
        "sources": rows,
        "verdict": {
            "alternate_source_audit_completed": True,
            "best_current_alternate_target": best["source_id"],
            "best_current_alternate_classification": best["classification"],
            "best_current_alternate_followup_ready": best[
                "followup_ready_for_bounded_no_t2_reproduction"
            ],
            "real_data_T2_sampling_authorized": False,
            "wgd2038_superseded_as_only_route": True,
        },
        "claim_boundary": [
            "No real-data T2 posterior was sampled.",
            "No alternate source clears the Paper 7 proof gate in this audit alone.",
            "DES J0408 is promoted only to bounded no-T2 reproduction follow-up.",
        ],
        "next_finite_action": (
            "Implement a DES J0408 compatibility extractor and smoke-run the "
            "published no-T2 lensing/time-delay baseline."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_csv(rows)
    print(json.dumps(summary["verdict"], indent=2))


if __name__ == "__main__":
    main()
