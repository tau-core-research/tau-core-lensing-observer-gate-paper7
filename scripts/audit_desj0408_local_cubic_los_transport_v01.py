#!/usr/bin/env python3
"""Build the admissible local non-tidal LOS transport after affine projection."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
MODELED = RESULTS / "tau_core_lensing_desj0408_modeled_cone_morphology_v1/summary.json"
GALAXIES = (
    RESULTS
    / "tau_core_lensing_desj0408_strides_los_morphology_v1"
    / "desj0408_spectroscopic_galaxies.csv"
)
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_local_cubic_los_transport_v1"
OUT = OUT_DIR / "summary.json"
CSV_OUT = OUT_DIR / "post_affine_path_residuals.csv"
REPORT = OUT_DIR / "report.md"
EXPLICIT = {"488068102", "488065185", "488066144", "488066768"}


def point_mass_deflection(x: np.ndarray, p: np.ndarray, strength: float) -> np.ndarray:
    displacement = x - p
    radius2 = np.sum(displacement * displacement, axis=-1, keepdims=True)
    return strength * displacement / radius2


def main() -> None:
    modeled = json.loads(MODELED.read_text(encoding="utf-8"))
    lens_ra = 62.090417
    lens_dec = -53.899889
    cos_dec = np.cos(np.deg2rad(lens_dec))
    theta_e_main = 1.80
    galaxies = []
    with GALAXIES.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["object_id"] in EXPLICIT or not row["log10_flexion_auger"]:
                continue
            separation = float(row["separation_arcsec"])
            delta3 = 10.0 ** float(row["log10_flexion_auger"])
            galaxies.append(
                {
                    "object_id": row["object_id"],
                    "position": np.asarray(
                        [
                            (float(row["ra_deg"]) - lens_ra)
                            * cos_dec
                            * 3600.0,
                            (float(row["dec_deg"]) - lens_dec) * 3600.0,
                        ]
                    ),
                    "effective_point_mass_strength": (
                        delta3 * separation**3 / theta_e_main**2
                    ),
                }
            )
    if len(galaxies) != 178:
        raise RuntimeError(f"Expected 178 subthreshold galaxies, got {len(galaxies)}")

    residual_rows = []
    model_summaries = []
    for model in modeled["models"]:
        center = np.asarray(model["components"][0]["center_arcsec"], dtype=float)
        image = np.asarray(model["image_positions_arcsec"], dtype=float) - center
        total_deflection = np.zeros_like(image)
        for galaxy in galaxies:
            total_deflection += point_mass_deflection(
                image,
                galaxy["position"],
                galaxy["effective_point_mass_strength"],
            )

        design = np.column_stack([np.ones(4), image[:, 0], image[:, 1]])
        coefficients, _, rank, _ = np.linalg.lstsq(
            design, total_deflection, rcond=None
        )
        affine = design @ coefficients
        residual = total_deflection - affine
        full_norm = float(np.linalg.norm(total_deflection))
        residual_norm = float(np.linalg.norm(residual))
        model_summaries.append(
            {
                "model_id": model["model_id"],
                "affine_design_rank": int(rank),
                "total_effective_deflection_norm_arcsec": full_norm,
                "post_affine_residual_norm_arcsec": residual_norm,
                "post_affine_residual_fraction": residual_norm
                / max(full_norm, 1e-30),
                "maximum_path_residual_arcsec": float(
                    np.max(np.linalg.norm(residual, axis=1))
                ),
            }
        )
        for path_index, vector in enumerate(residual):
            residual_rows.append(
                {
                    "model_id": model["model_id"],
                    "path_index": path_index,
                    "residual_x_arcsec": vector[0],
                    "residual_y_arcsec": vector[1],
                    "residual_norm_arcsec": np.linalg.norm(vector),
                }
            )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(residual_rows[0]))
        writer.writeheader()
        writer.writerows(residual_rows)

    residual_norms = np.asarray(
        [row["post_affine_residual_norm_arcsec"] for row in model_summaries]
    )
    residual_fractions = np.asarray(
        [row["post_affine_residual_fraction"] for row in model_summaries]
    )
    max_paths = np.asarray(
        [row["maximum_path_residual_arcsec"] for row in model_summaries]
    )
    threshold = 1e-4
    summary = {
        "schema": "paper7 DES J0408 local cubic LOS transport v1",
        "model_count": len(model_summaries),
        "subthreshold_object_count": len(galaxies),
        "excluded_explicit_perturbers": sorted(EXPLICIT),
        "local_completion": (
            "published point-mass flexion strength, exact angular field, "
            "best common affine vector field removed"
        ),
        "affine_nuisance_dimension": 6,
        "median_post_affine_residual_norm_arcsec": float(
            np.median(residual_norms)
        ),
        "post_affine_residual_norm_range_arcsec": [
            float(np.min(residual_norms)),
            float(np.max(residual_norms)),
        ],
        "median_post_affine_residual_fraction": float(
            np.median(residual_fractions)
        ),
        "median_maximum_path_residual_arcsec": float(np.median(max_paths)),
        "conservative_flexion_threshold_arcsec": threshold,
        "models_with_maximum_path_residual_above_threshold": int(
            np.sum(max_paths > threshold)
        ),
        "local_non_tidal_transport_nonzero_after_affine_projection": bool(
            np.all(residual_norms > 1e-12)
        ),
        "standard_affine_compression_sufficient_for_frozen_catalog": bool(
            np.all(max_paths <= threshold)
        ),
        "profile_scope": (
            "effective point-mass far-perturber completion calibrated from "
            "published Auger flexion magnitudes"
        ),
        "complete_physical_light_cone_materialized": False,
        "tau_specific_information_materialized": False,
        "time_score_authorized": False,
        "models": model_summaries,
        "verdict": (
            "LOCAL_CUBIC_SUBTHRESHOLD_RESPONSE_SURVIVES_AFFINE_PROJECTION__"
            "STANDARD_FLEXION_COMPLETION_ONLY"
        ),
        "claim_boundary": (
            "The construction uses the point-mass far-perturber approximation "
            "underlying the published flexion diagnostic and removes a full "
            "six-parameter affine vector field. A surviving residual is a "
            "standard conditional higher-order LOS prediction. Missing objects, "
            "extended halos, diffuse matter, endpoint data, Tau h_tau and "
            "observer-time distortion are not supplied."
        ),
    }
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 local cubic LOS transport v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        "The admissible local point-mass completion leaves a nonzero four-path "
        "residual after a full common affine vector field is removed.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                key: summary[key]
                for key in (
                    "verdict",
                    "median_post_affine_residual_norm_arcsec",
                    "post_affine_residual_norm_range_arcsec",
                    "median_post_affine_residual_fraction",
                    "median_maximum_path_residual_arcsec",
                    "models_with_maximum_path_residual_above_threshold",
                    "tau_specific_information_materialized",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
