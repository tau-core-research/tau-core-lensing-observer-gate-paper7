#!/usr/bin/env python3
"""Freeze a delay-blind DES J0408 source-morphology triangle."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv_wgd2038_repro/bin/python"
DATA = ROOT / "data/derived"
OUT_DIR = DATA / (
    "repro_results/tau_core_lensing_desj0408_source_morphology_triangle_v1"
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
    source = output_[0]["kwargs_source"]
    lens_models = list(input_[2]["lens_model_list"])
    if not lens_models or lens_models[0] != "SPEMD":
        continue
    if len(source) <= 8:
        continue
    indices = (0, 6, 8)
    if any(
        input_[2]["source_light_model_list"][index] != "SERSIC_ELLIPSE"
        for index in indices
    ):
        continue
    points = [
        (float(source[index]["center_x"]), float(source[index]["center_y"]))
        for index in indices
    ]
    distances = [
        math.dist(points[0], points[1]),
        math.dist(points[0], points[2]),
        math.dist(points[1], points[2]),
    ]
    rows.append(
        {
            "model_id": path.name.removesuffix("_mod_out.txt"),
            "imaging_log_evidence": float(output_[2][-1][4]),
            "source_component_indices": list(indices),
            "source_component_centers_arcsec": points,
            "source_component_redshifts": [
                float(input_[2]["source_redshift_list"][index])
                for index in indices
            ],
            "triangle_edges_arcsec": distances,
        }
    )

rows.sort(key=lambda row: row["imaging_log_evidence"], reverse=True)
top = rows[:5]
array = np.asarray([row["triangle_edges_arcsec"] for row in top])
payload = {
    "eligible_model_count": len(rows),
    "selected": rows[0],
    "top_five_models": top,
    "top_five_edge_mean_arcsec": np.mean(array, axis=0).tolist(),
    "top_five_edge_std_arcsec": np.std(array, axis=0, ddof=1).tolist(),
    "top_five_edge_coefficient_of_variation": (
        np.std(array, axis=0, ddof=1) / np.mean(array, axis=0)
    ).tolist(),
}
print(json.dumps(payload))
'''


def main() -> None:
    run = subprocess.run(
        [str(VENV), "-c", HELPER, str(ROOT)],
        check=True,
        capture_output=True,
        text=True,
    )
    extracted = json.loads(run.stdout)
    cv = extracted["top_five_edge_coefficient_of_variation"]
    stable = max(cv) < 0.10
    selected = extracted["selected"]
    redshifts = selected["source_component_redshifts"]
    single_source_plane = len(set(redshifts)) == 1
    centers = selected["source_component_centers_arcsec"]
    edge_vectors = {
        "host_to_inner_arc": [
            centers[1][axis] - centers[0][axis] for axis in range(2)
        ],
        "host_to_outer_arc": [
            centers[2][axis] - centers[0][axis] for axis in range(2)
        ],
        "inner_to_outer_arc": [
            centers[2][axis] - centers[1][axis] for axis in range(2)
        ],
    }
    result = {
        "schema": "paper7 DES J0408 source morphology triangle v1",
        "target": "DES J0408-5354",
        "input_scope": (
            "public lens/image posterior files only; no time-delay files, "
            "observed delays, delay residuals, or T2 score"
        ),
        "selection_rule": (
            "maximum imaging log evidence among exactly runtime-reconstructible "
            "SPEMD models carrying the declared three-component Sersic source topology"
        ),
        "component_roles": [
            "lensed quasar-host source",
            "additional inner-arc source",
            "additional outer-arc source",
        ],
        "source_component_redshifts": redshifts,
        "single_source_plane": single_source_plane,
        "relative_morphology_coordinates": {
            "host_to_inner_arc_arcsec": selected["triangle_edges_arcsec"][0],
            "host_to_outer_arc_arcsec": selected["triangle_edges_arcsec"][1],
            "inner_to_outer_arc_arcsec": selected["triangle_edges_arcsec"][2],
        },
        "oriented_edge_vectors_arcsec_in_source_frame": edge_vectors,
        "edge_closure_rule": (
            "host_to_inner_arc + inner_to_outer_arc = host_to_outer_arc"
        ),
        "selected_model_id": selected["model_id"],
        "selected_model_imaging_log_evidence": selected["imaging_log_evidence"],
        "eligible_model_count": extracted["eligible_model_count"],
        "top_five_edge_coefficient_of_variation": cv,
        "top_five_maximum_coefficient_of_variation": max(cv),
        "stability_rule": "all three top-five edge coefficients of variation < 0.10",
        "observer_field_geometry_calibrator_materialized": stable,
        "source_frozen_relative_morphology_materialized": (
            stable and single_source_plane
        ),
        "sfh_02_relative_morphology_materialized": (
            stable and single_source_plane
        ),
        "theta_M_identified": False,
        "path_pullback_identified": False,
        "a_O_identified": False,
        "time_score_authorized": False,
        "verdict": (
            "DESJ0408_SOURCE_MORPHOLOGY_TRIANGLE_FROZEN"
            if stable and single_source_plane
            else "DESJ0408_MULTISOURCE_TRIANGLE_NOT_SINGLE_BODY"
            if stable
            else "DESJ0408_SOURCE_MORPHOLOGY_TRIANGLE_UNSTABLE"
        ),
        "claim_boundary": (
            "Delay-blind multisource observer-field geometry. It is not a single "
            "morphological-body descriptor, body clock, path pullback, observer-time "
            "covector, time distortion, or Tau detection."
        ),
        "sensitivity": extracted["top_five_models"],
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    coordinates = result["relative_morphology_coordinates"]
    REPORT.write_text(
        "# DES J0408 source-morphology triangle v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        "The frozen relative coordinates are "
        f"`{coordinates['host_to_inner_arc_arcsec']:.5f}`, "
        f"`{coordinates['host_to_outer_arc_arcsec']:.5f}`, and "
        f"`{coordinates['inner_to_outer_arc_arcsec']:.5f}` arcsec. "
        f"The largest top-five imaging-model coefficient of variation is "
        f"`{max(cv):.4f}`.\n\n"
        "Only lens/image posterior files enter this freeze. No delay file or "
        "delay-derived score is opened.\n"
    )
    print(result["verdict"])


if __name__ == "__main__":
    main()
