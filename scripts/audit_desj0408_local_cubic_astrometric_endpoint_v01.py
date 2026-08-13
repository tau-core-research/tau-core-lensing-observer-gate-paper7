#!/usr/bin/env python3
"""Audit whether public DES J0408 astrometry can test the frozen LOS signal."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
MODELED = RESULTS / "tau_core_lensing_desj0408_modeled_cone_morphology_v1/summary.json"
PREDICTION = RESULTS / "tau_core_lensing_desj0408_local_cubic_los_transport_v1/summary.json"
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_local_cubic_astrometric_endpoint_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def main() -> None:
    modeled = json.loads(MODELED.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    positions = np.asarray(
        [model["image_positions_arcsec"] for model in modeled["models"]]
    )
    posterior_coordinate_rms = float(
        np.sqrt(np.mean((positions - np.mean(positions, axis=0)) ** 2))
    )
    predicted_path = float(
        prediction["median_maximum_path_residual_arcsec"]
    )
    pixel_scales = {"F814W": 0.04, "F160W": 0.08}
    summary = {
        "schema": "paper7 DES J0408 local cubic astrometric endpoint v1",
        "predicted_median_maximum_path_residual_arcsec": predicted_path,
        "predicted_median_maximum_path_residual_mas": predicted_path * 1000.0,
        "published_model_coordinate_rms_arcsec": posterior_coordinate_rms,
        "published_model_coordinate_rms_mas": posterior_coordinate_rms * 1000.0,
        "prediction_to_model_coordinate_rms_ratio": predicted_path
        / posterior_coordinate_rms,
        "hst_pixel_scales_arcsec": pixel_scales,
        "prediction_to_f814w_pixel_ratio": predicted_path
        / pixel_scales["F814W"],
        "prediction_to_f160w_pixel_ratio": predicted_path
        / pixel_scales["F160W"],
        "public_positions_are_model_fitted_not_independent_holdout": True,
        "independent_sub_mas_astrometric_covariance_materialized": False,
        "direct_astrometric_endpoint_authorized": False,
        "extended_arc_endpoint_preferred": True,
        "tau_specific_information_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "DIRECT_POINT_ASTROMETRY_UNDERPOWERED_AND_NOT_INDEPENDENT__"
            "REDIRECT_TO_EXTENDED_ARC_ENDPOINT"
        ),
        "claim_boundary": (
            "The predicted 0.17 mas scale is compared only with public model "
            "position dispersion and detector pixel scales. Subpixel centroiding "
            "can outperform a pixel, so this is not an impossibility theorem. "
            "However, the public image positions are fit inputs/outputs and no "
            "independent sub-mas covariance is materialized; direct scoring would "
            "be circular. No Tau or time inference is authorized."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 local cubic astrometric endpoint v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        "The frozen signal is smaller than the public posterior position spread "
        "and lacks an independent sub-mas astrometric covariance. Extended arcs "
        "are the next non-circular endpoint.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
