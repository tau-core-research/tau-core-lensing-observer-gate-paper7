#!/usr/bin/env python3
"""Audit whether public DES J0408 host light admits physical direct moments."""

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
    "repro_results/tau_core_lensing_desj0408_host_brightness_moment_preflight_v1"
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

root = Path(sys.argv[1])
model_id = sys.argv[2]
path = root / (
    "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography/"
    f"model_posteriors/lens_models/{model_id}_mod_out.txt"
)
with path.open("rb") as handle:
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

model = MultiLinear(
    bands,
    kwargs_model,
    likelihood_mask_list=kwargs_likelihood["image_likelihood_mask_list"],
    linear_solver=True,
)
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
    _, _, _, parameters = model.image_linear_solve(**kwargs)

host = result["kwargs_source"][:2]
center_x = host[0]["center_x"]
center_y = host[0]["center_y"]
axis = np.linspace(-0.8, 0.8, 241)
y, x = np.meshgrid(axis + center_y, axis + center_x, indexing="ij")
light = LightModel(["SERSIC_ELLIPSE", "SHAPELETS"])
brightness = light.surface_brightness(x.ravel(), y.ravel(), host).reshape(x.shape)
positive = float(np.clip(brightness, 0, None).sum())
negative = float(np.clip(-brightness, 0, None).sum())
print(
    json.dumps(
        {
            "linear_parameter_counts": [
                len(values) if values is not None else None
                for values in parameters
            ],
            "grid_side": 241,
            "grid_half_width_arcsec": 0.8,
            "positive_integrated_brightness": positive,
            "negative_integrated_brightness_absolute": negative,
            "negative_to_positive_ratio": negative / positive,
            "minimum_brightness": float(brightness.min()),
            "maximum_brightness": float(brightness.max()),
        }
    )
)
'''


def main() -> None:
    host_audit = json.loads(HOST_AUDIT.read_text(encoding="utf-8"))
    model_id = host_audit["selected_model_candidate"]["model_id"]
    run = subprocess.run(
        [str(VENV), "-c", HELPER, str(ROOT), model_id],
        check=True,
        capture_output=True,
        text=True,
    )
    extracted = json.loads(run.stdout)
    physical = extracted["negative_to_positive_ratio"] < 0.05
    result = {
        "schema": "paper7 DES J0408 host brightness moment preflight v1",
        "target": "DES J0408-5354 quasar host at z=2.375",
        "selected_imaging_model_id": model_id,
        "input_scope": "lens/image posterior only; no delay data",
        **extracted,
        "positivity_rule": "negative-to-positive integrated brightness ratio <0.05",
        "direct_nonparametric_moment_authorized": physical,
        "sfh_02_relative_morphology_materialized": False,
        "theta_M_identified": False,
        "time_score_authorized": False,
        "verdict": (
            "DESJ0408_DIRECT_HOST_BRIGHTNESS_MOMENT_AVAILABLE"
            if physical
            else "DESJ0408_SIGNED_HOST_RECONSTRUCTION_BLOCKS_DIRECT_MOMENT"
        ),
        "claim_boundary": (
            "Image-only reconstruction preflight. Clipping negative brightness is "
            "not authorized as a physical source descriptor."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(result["verdict"])


if __name__ == "__main__":
    main()
