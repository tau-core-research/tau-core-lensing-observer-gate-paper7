#!/usr/bin/env python3
"""Freeze the modeled DES J0408 cone-interior morphology descriptor."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv_wgd2038_repro/bin/python"
RESULTS = ROOT / "data/derived/repro_results"
HOST_AUDIT = (
    RESULTS / "tau_core_lensing_desj0408_single_body_host_descriptor_v1/summary.json"
)
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_modeled_cone_morphology_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


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

from lenstronomy.LensModel.lens_model import LensModel

root = Path(sys.argv[1])
model_ids = json.loads(sys.argv[2])
lens_dir = root / (
    "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography/"
    "model_posteriors/lens_models"
)

def jacobians(lens, ra, dec, kwargs_lens):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f_xx, f_xy, f_yx, f_yy = lens.hessian(ra, dec, kwargs_lens)
    return np.stack(
        [
            np.stack([1.0-f_xx, -f_xy], axis=-1),
            np.stack([-f_yx, 1.0-f_yy], axis=-1),
        ],
        axis=-2,
    )

models = []
for model_id in model_ids:
    with (lens_dir / f"{model_id}_mod_out.txt").open("rb") as handle:
        input_, output_ = pickle.load(handle, encoding="latin1")
    kwargs_model = input_[2]
    result = output_[0]
    names = list(kwargs_model["lens_model_list"])
    redshifts = list(kwargs_model["lens_redshift_list"])
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
            lens_redshift_list=redshifts,
            multi_plane=kwargs_model["multi_plane"],
            observed_convention_index=kwargs_model.get("observed_convention_index"),
            cosmo=kwargs_model.get("cosmo"),
        )
    ra = np.asarray(result["kwargs_ps"][0]["ra_image"], dtype=float)
    dec = np.asarray(result["kwargs_ps"][0]["dec_image"], dtype=float)
    full = jacobians(lens, ra, dec, kwargs_lens)
    components = []
    for index, (name, redshift, values) in enumerate(
        zip(names, redshifts, kwargs_lens)
    ):
        removed = copy.deepcopy(kwargs_lens)
        strength_keys = [
            key for key in ("theta_E", "gamma_ext", "alpha_Rs", "sigma0")
            if key in removed[index]
        ]
        for key in strength_keys:
            removed[index][key] = 0.0
        without = jacobians(lens, ra, dec, removed)
        delta = full - without
        components.append(
            {
                "component_index": index,
                "model_type": name,
                "redshift": float(redshift),
                "center_arcsec": [
                    float(values.get("center_x", values.get("ra_0", 0.0))),
                    float(values.get("center_y", values.get("dec_0", 0.0))),
                ],
                "strength_keys_zeroed": strength_keys,
                "effective_jacobian_delta_by_path": delta.tolist(),
                "frobenius_norm_by_path": np.linalg.norm(
                    delta, axis=(1, 2)
                ).tolist(),
            }
        )
    summed = np.sum(
        [np.asarray(row["effective_jacobian_delta_by_path"]) for row in components],
        axis=0,
    )
    additive_reconstruction = np.eye(2)[None, :, :] + summed
    nonadditivity = full - additive_reconstruction
    denominator = np.maximum(
        np.linalg.norm(full - np.eye(2)[None, :, :], axis=(1, 2)), 1e-15
    )
    models.append(
        {
            "model_id": model_id,
            "source_redshift": float(kwargs_model["z_source"]),
            "multi_plane": bool(kwargs_model["multi_plane"]),
            "image_positions_arcsec": np.stack([ra, dec], axis=-1).tolist(),
            "full_source_from_image_jacobian_by_path": full.tolist(),
            "components": components,
            "unique_lens_redshifts": sorted(set(float(z) for z in redshifts)),
            "loco_nonadditivity_matrix_by_path": nonadditivity.tolist(),
            "loco_nonadditivity_fraction_by_path": (
                np.linalg.norm(nonadditivity, axis=(1, 2)) / denominator
            ).tolist(),
        }
    )
print(json.dumps({"models": models}))
'''


def main() -> None:
    host = json.loads(HOST_AUDIT.read_text(encoding="utf-8"))
    model_ids = [row["model_id"] for row in host["eligible_models"]]
    run = subprocess.run(
        [str(VENV), "-c", HELPER, str(ROOT), json.dumps(model_ids)],
        check=True,
        capture_output=True,
        text=True,
    )
    models = json.loads(run.stdout)["models"]
    fractions = np.asarray(
        [
            model["loco_nonadditivity_fraction_by_path"]
            for model in models
        ],
        dtype=float,
    )
    component_counts = {len(model["components"]) for model in models}
    plane_counts = {len(model["unique_lens_redshifts"]) for model in models}
    finite = all(
        np.all(np.isfinite(model["loco_nonadditivity_fraction_by_path"]))
        for model in models
    )
    nonzero = bool(np.any(fractions > 1e-10))

    result = {
        "schema": "paper7 DES J0408 modeled cone morphology v1",
        "target": "DES J0408-5354",
        "input_scope": (
            "twelve image-only multi-plane lens posteriors; no delay data, "
            "residual, time endpoint, or unmodeled line-of-sight catalog"
        ),
        "descriptor_type": (
            "path x modeled-cone-component x 2x2 leave-one-component-out "
            "effective Jacobian response"
        ),
        "model_count": len(models),
        "component_counts": sorted(component_counts),
        "lens_plane_counts": sorted(plane_counts),
        "all_values_finite": finite,
        "multi_plane_loco_nonadditivity_nonzero": nonzero,
        "median_nonadditivity_fraction_by_path": np.median(
            fractions, axis=0
        ).tolist(),
        "maximum_nonadditivity_fraction": float(np.max(fractions)),
        "models": models,
        "modeled_cone_descriptor_materialized": (
            finite and component_counts == {8} and plane_counts == {3}
        ),
        "complete_physical_light_cone_morphology_materialized": False,
        "standard_multiplane_lensing_information_only": True,
        "tau_specific_cone_information_materialized": False,
        "theta_M_identified": False,
        "a_O_identified": False,
        "h_tau_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "MODELED_THREE_PLANE_CONE_DESCRIPTOR_MATERIALIZED__PHYSICAL_CONE_INCOMPLETE"
            if finite and component_counts == {8} and plane_counts == {3}
            else "MODELED_CONE_DESCRIPTOR_FAILED"
        ),
        "claim_boundary": (
            "The descriptor resolves the cone interior represented by the "
            "published standard multi-plane lens model. It omits unmodeled "
            "line-of-sight morphology and therefore is not the complete physical "
            "causal support, a Tau-specific covector, h_tau, or time distortion."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 modeled cone morphology v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        "Each of twelve models contains eight deflecting components on three "
        "redshift planes. Leave-one-component-out effective Jacobian tensors are "
        "frozen for all four paths. Nonadditivity records ordinary multi-plane "
        "coupling; the physical cone remains incomplete.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "models": len(models),
                "components": sorted(component_counts),
                "planes": sorted(plane_counts),
                "maximum_nonadditivity_fraction": result[
                    "maximum_nonadditivity_fraction"
                ],
                "time_score_authorized": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
