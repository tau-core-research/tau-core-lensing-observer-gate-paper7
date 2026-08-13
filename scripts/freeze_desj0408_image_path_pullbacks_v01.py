#!/usr/bin/env python3
"""Freeze four delay-blind DES J0408 local image-path pullbacks."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv_wgd2038_repro/bin/python"
DATA = ROOT / "data/derived"
MORPHOLOGY = DATA / (
    "repro_results/tau_core_lensing_desj0408_source_morphology_triangle_v1/"
    "summary.json"
)
OUT_DIR = DATA / (
    "repro_results/tau_core_lensing_desj0408_image_path_pullbacks_v1"
)
OUT = OUT_DIR / "summary.json"
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
model_id = sys.argv[2]
edge_vectors = json.loads(sys.argv[3])
path = root / (
    "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography/"
    f"model_posteriors/lens_models/{model_id}_mod_out.txt"
)
with path.open("rb") as handle:
    input_, output_ = pickle.load(handle, encoding="latin1")

kwargs_model = input_[2]
legacy_names = list(kwargs_model["lens_model_list"])
alias = {
}
runtime_names = [alias.get(name, name) for name in legacy_names]
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    lens = LensModel(
        lens_model_list=runtime_names,
        z_lens=None,
        z_source=kwargs_model["z_source"],
        lens_redshift_list=kwargs_model["lens_redshift_list"],
        multi_plane=kwargs_model["multi_plane"],
        observed_convention_index=kwargs_model.get("observed_convention_index"),
        cosmo=kwargs_model.get("cosmo"),
    )

kwargs_lens = [dict(values) for values in output_[0]["kwargs_lens"]]
for name, values in zip(runtime_names, kwargs_lens):
    if name == "SPEMD" and "s_scale" not in values:
        values["s_scale"] = 0.0
ra = np.asarray(output_[0]["kwargs_ps"][0]["ra_image"], dtype=float)
dec = np.asarray(output_[0]["kwargs_ps"][0]["dec_image"], dtype=float)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    f_xx, f_xy, f_yx, f_yy = lens.hessian(ra, dec, kwargs_lens)
    beta_x, beta_y = lens.ray_shooting(ra, dec, kwargs_lens)

paths = []
for index in range(len(ra)):
    jacobian = np.array(
        [
            [1.0 - f_xx[index], -f_xy[index]],
            [-f_yx[index], 1.0 - f_yy[index]],
        ]
    )
    inverse = np.linalg.inv(jacobian)
    symmetric = 0.5 * (jacobian + jacobian.T)
    eigenvalues = np.linalg.eigvalsh(symmetric)
    determinant = float(np.linalg.det(jacobian))
    mapped_edges = {
        name: (inverse @ np.asarray(vector, dtype=float)).tolist()
        for name, vector in edge_vectors.items()
    }
    paths.append(
        {
            "path_index": index,
            "image_position_arcsec": [float(ra[index]), float(dec[index])],
            "ray_shot_source_position_arcsec": [
                float(beta_x[index]),
                float(beta_y[index]),
            ],
            "source_from_image_jacobian": jacobian.tolist(),
            "image_from_source_local_pullback": inverse.tolist(),
            "jacobian_determinant": determinant,
            "signed_magnification": float(1.0 / determinant),
            "condition_number": float(np.linalg.cond(jacobian)),
            "morse_index_from_symmetric_jacobian": int(np.sum(eigenvalues < 0)),
            "parity": "positive" if determinant > 0 else "negative",
            "mapped_oriented_edges_arcsec": mapped_edges,
        }
    )

print(
    json.dumps(
        {
            "legacy_lens_model_list": legacy_names,
            "runtime_lens_model_list": runtime_names,
            "legacy_aliases": alias,
            "paths": paths,
        }
    )
)
'''


def extract_paths(
    model_id: str, edge_vectors: dict[str, list[float]]
) -> dict[str, Any]:
    run = subprocess.run(
        [
            str(VENV),
            "-c",
            HELPER,
            str(ROOT),
            model_id,
            json.dumps(edge_vectors),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(run.stdout)


def main() -> None:
    morphology = json.loads(MORPHOLOGY.read_text(encoding="utf-8"))
    edge_vectors = morphology["oriented_edge_vectors_arcsec_in_source_frame"]
    extracted = extract_paths(morphology["selected_model_id"], edge_vectors)
    paths = extracted["paths"]
    finite = all(
        path["condition_number"] < 100.0
        and path["jacobian_determinant"] != 0.0
        for path in paths
    )
    body_descriptor_ready = bool(
        morphology["sfh_02_relative_morphology_materialized"]
    )
    parity_counts = {
        parity: sum(path["parity"] == parity for path in paths)
        for parity in ("positive", "negative")
    }
    result = {
        "schema": "paper7 DES J0408 image path pullbacks v1",
        "target": morphology["target"],
        "source_morphology_artifact": str(MORPHOLOGY.relative_to(ROOT)),
        "selected_imaging_model_id": morphology["selected_model_id"],
        "input_scope": (
            "public lens/image posterior only; no time-delay file, observed "
            "delay, delay residual, or T2 score"
        ),
        "operator_definition": (
            "R_gamma_i = inverse[D_theta beta(theta_i)] acting on each frozen "
            "oriented source-morphology edge"
        ),
        "path_count": len(paths),
        "parity_counts": parity_counts,
        "all_pullbacks_finite_and_conditioned": finite,
        "local_lens_transport_materialized": finite and len(paths) == 4,
        "sfh_03_path_pullback_materialized": (
            finite and len(paths) == 4 and body_descriptor_ready
        ),
        "theta_M_identified": False,
        "a_O_identified": False,
        "h_tau_materialized": False,
        "time_score_authorized": False,
        "legacy_lens_model_list": extracted["legacy_lens_model_list"],
        "runtime_lens_model_list": extracted["runtime_lens_model_list"],
        "legacy_aliases": extracted["legacy_aliases"],
        "paths": paths,
        "verdict": (
            "DESJ0408_FOUR_LOCAL_LENS_TRANSPORTS_FROZEN__BODY_PULLBACK_BLOCKED"
            if finite and len(paths) == 4 and not body_descriptor_ready
            else "DESJ0408_FOUR_IMAGE_PATH_PULLBACKS_FROZEN"
            if finite and len(paths) == 4
            else "DESJ0408_IMAGE_PATH_PULLBACK_FREEZE_FAILED"
        ),
        "claim_boundary": (
            "Local linear 4D lens transport only. Its current morphology triangle "
            "crosses source planes, so it is not yet an SFH_03 body pullback, body "
            "clock, time covector, time distortion, or Tau detection."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    REPORT.write_text(
        "# DES J0408 image-path pullbacks v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        f"Four local pullbacks are frozen with parity counts `{parity_counts}`. "
        f"The largest condition number is "
        f"`{max(path['condition_number'] for path in paths):.3f}`.\n\n"
        "These operators transport the frozen source edges into local image-plane "
        "directions. They do not define a body clock or time covector.\n"
    )
    print(result["verdict"])


if __name__ == "__main__":
    main()
