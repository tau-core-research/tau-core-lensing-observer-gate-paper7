#!/usr/bin/env python3
"""Trace the four DES J0408 rays through the observed LOS morphology."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv_wgd2038_repro/bin/python"
RESULTS = ROOT / "data/derived/repro_results"
MODELED = RESULTS / "tau_core_lensing_desj0408_modeled_cone_morphology_v1/summary.json"
LOS_DIR = RESULTS / "tau_core_lensing_desj0408_strides_los_morphology_v1"
GALAXIES = LOS_DIR / "desj0408_spectroscopic_galaxies.csv"
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_los_path_transport_geometry_v1"
OUT = OUT_DIR / "summary.json"
CSV_OUT = OUT_DIR / "los_path_transport_geometry.csv"
REPORT = OUT_DIR / "report.md"


HELPER = r'''
import json
import pickle
import sys
import warnings
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

from lenstronomy.LensModel.lens_model import LensModel

root = Path(sys.argv[1])
model_ids = json.loads(sys.argv[2])
redshifts = np.asarray(json.loads(sys.argv[3]), dtype=float)
lens_dir = root / (
    "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography/"
    "model_posteriors/lens_models"
)

models = []
for model_id in model_ids:
    with (lens_dir / f"{model_id}_mod_out.txt").open("rb") as handle:
        input_, output_ = pickle.load(handle, encoding="latin1")
    kwargs_model = input_[2]
    result = output_[0]
    names = list(kwargs_model["lens_model_list"])
    lens_redshifts = list(kwargs_model["lens_redshift_list"])
    kwargs_lens = [dict(values) for values in result["kwargs_lens"]]
    for name, values in zip(names, kwargs_lens):
        if name == "SPEMD" and "s_scale" not in values:
            values["s_scale"] = 0.0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        lens = LensModel(
            lens_model_list=names,
            z_lens=None,
            z_source=kwargs_model["z_source"],
            lens_redshift_list=lens_redshifts,
            multi_plane=kwargs_model["multi_plane"],
            observed_convention_index=kwargs_model.get("observed_convention_index"),
            cosmo=kwargs_model.get("cosmo"),
        )
    ra = np.asarray(result["kwargs_ps"][0]["ra_image"], dtype=float)
    dec = np.asarray(result["kwargs_ps"][0]["dec_image"], dtype=float)
    center_x = float(kwargs_lens[0].get("center_x", 0.0))
    center_y = float(kwargs_lens[0].get("center_y", 0.0))
    path_positions = []
    for redshift in redshifts:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            beta_x, beta_y, _, _ = lens.lens_model.ray_shooting_partial(
                np.zeros_like(ra),
                np.zeros_like(dec),
                ra,
                dec,
                0,
                float(redshift),
                kwargs_lens,
                include_z_start=False,
            )
        path_positions.append(np.stack([beta_x, beta_y], axis=-1).tolist())
    models.append(
        {
            "model_id": model_id,
            "main_lens_center_model_arcsec": [center_x, center_y],
            "image_positions_model_arcsec": np.stack([ra, dec], axis=-1).tolist(),
            "ray_positions_by_redshift_model_arcsec": path_positions,
        }
    )
print(json.dumps({"models": models}))
'''


def main() -> None:
    modeled = json.loads(MODELED.read_text(encoding="utf-8"))
    model_ids = [row["model_id"] for row in modeled["models"]]
    with GALAXIES.open(encoding="utf-8") as handle:
        galaxies = list(csv.DictReader(handle))
    redshifts = [float(row["redshift"]) for row in galaxies]
    run = subprocess.run(
        [
            str(VENV),
            "-c",
            HELPER,
            str(ROOT),
            json.dumps(model_ids),
            json.dumps(redshifts),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    traced = json.loads(run.stdout)["models"]

    lens_ra = 62.090417
    lens_dec = -53.899889
    cos_dec = np.cos(np.deg2rad(lens_dec))
    rows = []
    for model in traced:
        center = np.asarray(model["main_lens_center_model_arcsec"], dtype=float)
        ray_positions = np.asarray(
            model["ray_positions_by_redshift_model_arcsec"], dtype=float
        )
        for index, galaxy in enumerate(galaxies):
            sky_offset = np.asarray(
                [
                    (float(galaxy["ra_deg"]) - lens_ra) * cos_dec * 3600.0,
                    (float(galaxy["dec_deg"]) - lens_dec) * 3600.0,
                ]
            )
            object_position = center + sky_offset
            separation = np.linalg.norm(
                ray_positions[index] - object_position[None, :], axis=1
            )
            lens_center_separation = float(
                galaxy["separation_arcsec"]
            )
            flexion = galaxy["log10_flexion_auger"]
            for path_index in range(4):
                path_flexion_proxy = None
                if flexion and lens_center_separation > 0 and separation[path_index] > 0:
                    path_flexion_proxy = (
                        float(flexion)
                        + 3.0
                        * np.log10(
                            lens_center_separation / separation[path_index]
                        )
                    )
                rows.append(
                    {
                        "model_id": model["model_id"],
                        "object_id": galaxy["object_id"],
                        "object_redshift": galaxy["redshift"],
                        "path_index": path_index,
                        "ray_x_model_arcsec": ray_positions[index, path_index, 0],
                        "ray_y_model_arcsec": ray_positions[index, path_index, 1],
                        "object_x_model_arcsec": object_position[0],
                        "object_y_model_arcsec": object_position[1],
                        "ray_object_separation_arcsec": separation[path_index],
                        "published_lens_center_log10_flexion_auger": flexion,
                        "published_flexion_path_rescaling": path_flexion_proxy,
                    }
                )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    separations = np.asarray(
        [float(row["ray_object_separation_arcsec"]) for row in rows]
    ).reshape(len(model_ids), len(galaxies), 4)
    path_spread = np.ptp(separations, axis=2)
    proxies = [
        float(row["published_flexion_path_rescaling"])
        for row in rows
        if row["published_flexion_path_rescaling"] not in (None, "")
    ]
    threshold_rows = [
        row
        for row in rows
        if row["published_flexion_path_rescaling"] is not None
        and float(row["published_flexion_path_rescaling"]) > -4.0
    ]
    threshold_objects = sorted({row["object_id"] for row in threshold_rows})
    per_model_path_counts = {}
    for row in threshold_rows:
        key = f"{row['model_id']}::path_{row['path_index']}"
        per_model_path_counts[key] = per_model_path_counts.get(key, 0) + 1
    count_values = list(per_model_path_counts.values())
    summary = {
        "schema": "paper7 DES J0408 LOS path transport geometry v1",
        "target": "DES J0408-5354",
        "model_count": len(model_ids),
        "observed_los_object_count": len(galaxies),
        "path_count": 4,
        "transport_row_count": len(rows),
        "lens_center_icrs_deg": [lens_ra, lens_dec],
        "median_path_separation_spread_arcsec": float(np.median(path_spread)),
        "maximum_path_separation_spread_arcsec": float(np.max(path_spread)),
        "minimum_ray_object_separation_arcsec": float(np.min(separations)),
        "published_flexion_path_rescaling_count": len(proxies),
        "objects_above_explicit_modeling_threshold_on_any_path": threshold_objects,
        "above_threshold_object_count": len(threshold_objects),
        "above_threshold_count_range_per_model_path": [
            min(count_values),
            max(count_values),
        ],
        "all_above_threshold_objects_already_explicitly_modeled": (
            set(threshold_objects)
            == {"488068102", "488065185", "488066144", "488066768"}
        ),
        "path_dependent_threshold_membership_present": (
            len(set(count_values)) > 1
        ),
        "redshift_dependent_four_path_geometry_materialized": True,
        "path_discrimination_nonzero": bool(np.any(path_spread > 1e-10)),
        "published_leading_order_flexion_transport_materialized": True,
        "complete_physical_environment_transport_materialized": False,
        "complete_physical_light_cone_morphology_materialized": False,
        "tau_specific_information_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "REDSHIFT_DEPENDENT_FOUR_PATH_LOS_GEOMETRY_MATERIALIZED__"
            "LEADING_FLEXION_TRANSPORT_MATERIALIZED__COMPLETENESS_OPEN"
        ),
        "claim_boundary": (
            "The exact standard multi-plane rays are intersected with the "
            "published spectroscopic sky/redshift morphology. Within the "
            "published flexion-shift approximation, rescaling by the exact "
            "path separation cubed gives the leading non-tidal transport. All "
            "objects crossing the explicit-model threshold are the four "
            "perturbers already included in the lens posterior. This is not a "
            "complete environmental mass transport, Tau covector, h_tau, or "
            "time distortion."
        ),
    }
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 LOS four-path transport geometry v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        "All released spectroscopic objects are intersected with all four rays "
        "at their own redshifts for twelve posterior models. The result is a "
        "path-resolved geometric cone, not yet a complete mass transport.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
