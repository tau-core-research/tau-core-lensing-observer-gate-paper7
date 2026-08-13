#!/usr/bin/env python3
"""Solve a positivity-constrained DES J0408 host moment across lens models."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv_wgd2038_repro/bin/python"
DATA = ROOT / "data/derived"
HOST_AUDIT = DATA / (
    "repro_results/tau_core_lensing_desj0408_single_body_host_descriptor_v1/"
    "summary.json"
)
OUT_DIR = DATA / (
    "repro_results/tau_core_lensing_desj0408_positive_host_moment_v1"
)
OUT = OUT_DIR / "summary.json"


HELPER = r'''
import copy
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

from lenstronomy.ImSim.MultiBand.multi_linear import MultiLinear
from lenstronomy.LightModel.light_model import LightModel
from scipy.optimize import LinearConstraint, minimize

root = Path(sys.argv[1])
model_ids = json.loads(sys.argv[2])
lens_dir = root / (
    "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography/"
    "model_posteriors/lens_models"
)
rows = []
for model_id in model_ids:
    with (lens_dir / f"{model_id}_mod_out.txt").open("rb") as handle:
        input_, output_ = pickle.load(handle, encoding="latin1")
    _, _, kwargs_model, _, kwargs_likelihood, _, _ = input_
    result = copy.deepcopy(output_[0])
    bands = copy.deepcopy(output_[1])
    for band in bands:
        psf = band[1]
        if "psf_error_map" in psf:
            psf["psf_variance_map"] = psf.pop("psf_error_map")
    for name, values in zip(kwargs_model["lens_model_list"], result["kwargs_lens"]):
        if name == "SPEMD" and "s_scale" not in values:
            values["s_scale"] = 0.0

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        multi = MultiLinear(
            bands,
            kwargs_model,
            likelihood_mask_list=kwargs_likelihood["image_likelihood_mask_list"],
            compute_bool=[True, False, False],
            linear_solver=True,
        )
    image_model = multi._image_model_list[0]
    kwargs = {
        key: result.get(key)
        for key in (
            "kwargs_lens",
            "kwargs_source",
            "kwargs_lens_light",
            "kwargs_ps",
            "kwargs_extinction",
            "kwargs_special",
        )
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        response = image_model.linear_response_matrix(**kwargs)
        data = image_model.data_response
        variance, _ = image_model.error_response(
            result["kwargs_lens"],
            result["kwargs_ps"],
            kwargs_special=result["kwargs_special"],
        )
    weight = 1.0 / np.maximum(variance, 1e-20)
    quadratic = (response * weight) @ response.T
    linear = -(response * weight) @ data
    scale = max(np.trace(quadratic) / len(quadratic), 1e-30)
    quadratic /= scale
    linear /= scale

    center_x = result["kwargs_source"][0]["center_x"]
    center_y = result["kwargs_source"][0]["center_y"]
    axis = np.linspace(-0.5, 0.5, 41)
    y, x = np.meshgrid(axis + center_y, axis + center_x, indexing="ij")
    light = LightModel(["SERSIC_ELLIPSE", "SHAPELETS"])
    host_response = []
    for index in range(response.shape[0]):
        local = copy.deepcopy(result)
        unit = np.zeros(response.shape[0])
        unit[index] = 1.0
        _, source, _, _ = image_model.update_linear_kwargs(
            unit,
            local["kwargs_lens"],
            local["kwargs_source"],
            local["kwargs_lens_light"],
            local["kwargs_ps"],
        )
        host_response.append(
            light.surface_brightness(
                x.ravel(), y.ravel(), source[:2]
            )
        )
    host_response = np.asarray(host_response).T
    objective = lambda values: (
        0.5 * values @ quadratic @ values + linear @ values
    )
    gradient = lambda values: quadratic @ values + linear
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        solved = minimize(
            objective,
            np.zeros(response.shape[0]),
            jac=gradient,
            method="SLSQP",
            constraints=[LinearConstraint(host_response, 0.0, np.inf)],
            options={"maxiter": 750, "ftol": 1e-9},
        )
    brightness = (host_response @ solved.x).reshape(x.shape)
    flux = float(brightness.sum())
    centroid_x = float((brightness * x).sum() / flux)
    centroid_y = float((brightness * y).sum() / flux)
    dx = x - centroid_x
    dy = y - centroid_y
    moment = np.array(
        [
            [
                (brightness * dx * dx).sum() / flux,
                (brightness * dx * dy).sum() / flux,
            ],
            [
                (brightness * dx * dy).sum() / flux,
                (brightness * dy * dy).sum() / flux,
            ],
        ]
    )
    eigenvalues, eigenvectors = np.linalg.eigh(moment)
    major = eigenvectors[:, 1]
    angle = float(np.arctan2(major[1], major[0]))
    trace = float(np.trace(moment))
    ellipticity = float(
        (eigenvalues[1] - eigenvalues[0]) / np.sum(eigenvalues)
    )
    prediction = response.T @ solved.x
    chi2 = float(np.sum((prediction - data) ** 2 * weight))
    zero_chi2 = float(np.sum(data**2 * weight))
    rows.append(
        {
            "model_id": model_id,
            "solver_success": bool(solved.success),
            "solver_message": solved.message,
            "solver_iterations": int(solved.nit),
            "minimum_source_brightness": float(brightness.min()),
            "fit_chi2_over_zero_model_chi2": chi2 / zero_chi2,
            "host_flux_grid_units": flux,
            "centroid_arcsec": [centroid_x, centroid_y],
            "second_moment_tensor_arcsec2": moment.tolist(),
            "moment_trace_arcsec2": trace,
            "moment_ellipticity": ellipticity,
            "moment_major_axis_angle_rad_mod_pi": angle,
        }
    )

trace = np.asarray([row["moment_trace_arcsec2"] for row in rows])
ellipticity = np.asarray([row["moment_ellipticity"] for row in rows])
angles = np.asarray([row["moment_major_axis_angle_rad_mod_pi"] for row in rows])
mean_angle = np.angle(np.mean(np.exp(2j * angles))) / 2.0
angle_delta = 0.5 * np.angle(np.exp(2j * (angles - mean_angle)))
print(
    json.dumps(
        {
            "models": rows,
            "trace_coefficient_of_variation": float(
                np.std(trace, ddof=1) / np.mean(trace)
            ),
            "ellipticity_coefficient_of_variation": float(
                np.std(ellipticity, ddof=1) / np.mean(ellipticity)
            ),
            "axial_angle_rms_rad": float(np.sqrt(np.mean(angle_delta**2))),
        }
    )
)
'''


def solve_positive_models(model_ids: list[str]) -> dict:
    run = subprocess.run(
        [str(VENV), "-c", HELPER, str(ROOT), json.dumps(model_ids)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(run.stdout)


def main() -> None:
    host = json.loads(HOST_AUDIT.read_text(encoding="utf-8"))
    model_ids = [row["model_id"] for row in host["top_five_models"]]
    extracted = solve_positive_models(model_ids)
    models = extracted["models"]
    stable_trace = (
        all(row["solver_success"] for row in models)
        and all(row["minimum_source_brightness"] >= -1e-8 for row in models)
        and extracted["trace_coefficient_of_variation"] < 0.25
    )
    stable = (
        all(row["solver_success"] for row in models)
        and all(row["minimum_source_brightness"] >= -1e-8 for row in models)
        and extracted["trace_coefficient_of_variation"] < 0.25
        and extracted["ellipticity_coefficient_of_variation"] < 0.25
        and extracted["axial_angle_rms_rad"] < 0.25
    )
    result = {
        "schema": "paper7 DES J0408 positive host moment v1",
        "target": "DES J0408-5354 quasar host at z=2.375",
        "input_scope": "lens/image posterior band 0 only; no delay data",
        "solver": (
            "SLSQP convex quadratic image fit with nonnegative total host "
            "brightness on a frozen 41x41 source grid"
        ),
        "model_count": len(models),
        **extracted,
        "stability_rule": (
            "all solvers succeed; minimum brightness >=-1e-8; trace and "
            "ellipticity CV <0.25; axial-angle RMS <0.25 rad"
        ),
        "positive_common_host_moment_promoted": stable,
        "stable_scalar_trace_materialized": stable_trace,
        "mean_moment_trace_arcsec2": sum(
            row["moment_trace_arcsec2"] for row in models
        ) / len(models),
        "sfh_02_relative_morphology_materialized": stable,
        "theta_M_identified": False,
        "time_score_authorized": False,
        "verdict": (
            "DESJ0408_POSITIVE_COMMON_HOST_MOMENT_STABLE"
            if stable
            else "DESJ0408_POSITIVE_HOST_MOMENT_NOT_MODEL_STABLE"
        ),
        "claim_boundary": (
            "Positivity-constrained image-only source moment; not Theta_M, a body "
            "clock, observer-time covector, time distortion, or Tau detection."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(result["verdict"])


if __name__ == "__main__":
    main()
