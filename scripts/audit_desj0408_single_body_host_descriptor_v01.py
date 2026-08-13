#!/usr/bin/env python3
"""Audit a delay-blind single-body DES J0408 host descriptor."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv_wgd2038_repro/bin/python"
DATA = ROOT / "data/derived"
OUT_DIR = DATA / (
    "repro_results/tau_core_lensing_desj0408_single_body_host_descriptor_v1"
)
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


HELPER = r'''
import json
import math
import pickle
import sys
from pathlib import Path

import dill._dill as dd
import numpy as np
import astropy.cosmology as cosmo
import astropy.cosmology.core as core
import astropy.cosmology.flrw.scalar_inv_efuncs as scalar

if not hasattr(core, "FlatLambdaCDM"):
    core.FlatLambdaCDM = cosmo.FlatLambdaCDM
sys.modules.setdefault("astropy.cosmology.scalar_inv_efuncs", scalar)
dd._reverse_typemap.setdefault("ObjectType", object)

root = Path(sys.argv[1])
lens_dir = root / (
    "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography/"
    "model_posteriors/lens_models"
)
rows = []
for path in sorted(lens_dir.glob("*_mod_out.txt")):
    with path.open("rb") as handle:
        input_, output_ = pickle.load(handle, encoding="latin1")
    if input_[2]["lens_model_list"][0] != "SPEMD":
        continue
    source = output_[0]["kwargs_source"][0]
    e1 = float(source["e1"])
    e2 = float(source["e2"])
    rows.append(
        {
            "model_id": path.name.removesuffix("_mod_out.txt"),
            "imaging_log_evidence": float(output_[2][-1][4]),
            "R_sersic_arcsec": float(source["R_sersic"]),
            "n_sersic": float(source["n_sersic"]),
            "ellipticity_magnitude": math.hypot(e1, e2),
            "ellipticity_position_angle_rad_mod_pi": (
                0.5 * math.atan2(e2, e1)
            ),
            "e1": e1,
            "e2": e2,
        }
    )
rows.sort(key=lambda row: row["imaging_log_evidence"], reverse=True)
top = rows[:5]
matrix = np.asarray(
    [
        [
            row["R_sersic_arcsec"],
            row["n_sersic"],
            row["ellipticity_magnitude"],
        ]
        for row in top
    ]
)
angles = np.asarray(
    [row["ellipticity_position_angle_rad_mod_pi"] for row in top]
)
mean_phase = np.angle(np.mean(np.exp(2j * angles))) / 2.0
angle_delta = 0.5 * np.angle(np.exp(2j * (angles - mean_phase)))
print(
    json.dumps(
        {
            "eligible_model_count": len(rows),
            "eligible_models": rows,
            "selected": rows[0],
            "top_five_models": top,
            "top_five_scalar_coefficients_of_variation": (
                np.std(matrix, axis=0, ddof=1) / np.mean(matrix, axis=0)
            ).tolist(),
            "top_five_position_angle_rms_rad": float(
                np.sqrt(np.mean(angle_delta**2))
            ),
        }
    )
)
'''


def main() -> None:
    run = subprocess.run(
        [str(VENV), "-c", HELPER, str(ROOT)],
        check=True,
        capture_output=True,
        text=True,
    )
    extracted = json.loads(run.stdout)
    cv = extracted["top_five_scalar_coefficients_of_variation"]
    angle_rms = extracted["top_five_position_angle_rms_rad"]
    stable = max(cv) < 0.25 and angle_rms < 0.25
    result = {
        "schema": "paper7 DES J0408 single-body host descriptor v1",
        "target": "DES J0408-5354 quasar host at z=2.375",
        "input_scope": (
            "public lens/image posterior only; no time-delay file, observed "
            "delay, delay residual, or T2 score"
        ),
        "candidate_coordinates": [
            "R_sersic_arcsec",
            "n_sersic",
            "ellipticity_magnitude",
            "ellipticity_position_angle_rad_mod_pi",
        ],
        "eligible_model_count": extracted["eligible_model_count"],
        "eligible_models": extracted["eligible_models"],
        "selected_model_candidate": extracted["selected"],
        "top_five_scalar_coefficients_of_variation": cv,
        "top_five_position_angle_rms_rad": angle_rms,
        "stability_rule": (
            "top-five CV <0.25 for R_sersic, n_sersic and ellipticity magnitude, "
            "and axial position-angle RMS <0.25 rad"
        ),
        "single_body_host_descriptor_promoted": stable,
        "sfh_02_relative_morphology_materialized": stable,
        "theta_M_identified": False,
        "time_score_authorized": False,
        "top_five_models": extracted["top_five_models"],
        "verdict": (
            "DESJ0408_SINGLE_BODY_HOST_DESCRIPTOR_STABLE"
            if stable
            else "DESJ0408_SINGLE_BODY_HOST_DESCRIPTOR_MODEL_FAMILY_UNSTABLE"
        ),
        "claim_boundary": (
            "Delay-blind single-source morphology robustness audit. A failure "
            "forbids selecting a body clock from one preferred image model."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    REPORT.write_text(
        "# DES J0408 single-body host descriptor audit v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        f"Top-five scalar coefficients of variation are `{cv}`; axial position-"
        f"angle RMS is `{angle_rms:.3f}` rad.\n\n"
        "No time-delay quantity enters this audit.\n"
    )
    print(result["verdict"])


if __name__ == "__main__":
    main()
