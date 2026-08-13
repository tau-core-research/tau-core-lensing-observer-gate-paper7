#!/usr/bin/env python3
"""Exploratory score of the frozen LOS template on held-out F814W arcs."""

from __future__ import annotations

import copy
import csv
import importlib.util
import json
import os
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = ROOT / ".venv_wgd2038_repro/bin/python"
if (
    importlib.util.find_spec("lenstronomy") is None
    or importlib.util.find_spec("h5py") is None
    or importlib.util.find_spec("fastell4py") is None
):
    if not VENV_PYTHON.exists():
        raise ModuleNotFoundError(
            "The complete lenstronomy backend is unavailable and the frozen "
            "DES J0408 environment "
            f"does not exist at {VENV_PYTHON}"
        )
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), *sys.argv])

import h5py
import numpy as np
from lenstronomy.ImSim.MultiBand.multi_linear import MultiLinear


PUBLIC = ROOT / "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography"
MODEL_OUTPUT = PUBLIC / "temp/tau_core_crr_b_lobo_f814w_preflight_out.txt"
GALAXIES = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_strides_los_morphology_v1"
    / "desj0408_spectroscopic_galaxies.csv"
)
OUT_DIR = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_local_cubic_f814w_arc_template_v1"
)
OUT = OUT_DIR / "summary.json"
ARRAYS = OUT_DIR / "template_score_f814w.npz"
REPORT = OUT_DIR / "report.md"
EXPLICIT = {"488068102", "488065185", "488066144", "488066768"}


def point_mass_deflection(
    x: np.ndarray, y: np.ndarray, px: float, py: float, strength: float
) -> tuple[np.ndarray, np.ndarray]:
    dx = x - px
    dy = y - py
    radius2 = dx * dx + dy * dy
    return strength * dx / radius2, strength * dy / radius2


def main() -> None:
    with MODEL_OUTPUT.open("rb") as handle:
        input_, output_ = pickle.load(handle)
    _, multi_band_list, kwargs_model, _, kwargs_likelihood, _, _ = input_
    result = output_[0]
    masks = kwargs_likelihood["image_likelihood_mask_list"]
    bands = copy.deepcopy(multi_band_list)
    with h5py.File(PUBLIC / "data/psf_f814w.hdf5", "r") as handle:
        bands[0][1]["psf_variance_map"] = handle["psf_error_map"][()]
    model = MultiLinear(
        bands,
        kwargs_model,
        likelihood_mask_list=masks,
        compute_bool=[True, False, False],
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
    model.likelihood_data_given_model(**kwargs, check_positive_flux=False)
    images, _, _, _ = model.image_linear_solve(**kwargs)
    model_image = np.asarray(images[0], dtype=float)
    data_image = np.asarray(bands[0][0]["image_data"], dtype=float)
    residual = data_image - model_image
    mask = np.asarray(masks[0], dtype=bool)

    transform = np.asarray(bands[0][0]["transform_pix2angle"], dtype=float)
    ra0 = float(bands[0][0]["ra_at_xy_0"])
    dec0 = float(bands[0][0]["dec_at_xy_0"])
    yy, xx = np.indices(model_image.shape, dtype=float)
    ra = transform[0, 0] * xx + transform[0, 1] * yy + ra0
    dec = transform[1, 0] * xx + transform[1, 1] * yy + dec0

    center = np.asarray(
        [
            result["kwargs_lens"][0].get("center_x", 0.0),
            result["kwargs_lens"][0].get("center_y", 0.0),
        ],
        dtype=float,
    )
    ra_rel = ra - center[0]
    dec_rel = dec - center[1]
    lens_ra = 62.090417
    lens_dec = -53.899889
    cos_dec = np.cos(np.deg2rad(lens_dec))
    theta_e_main = 1.80

    alpha_x = np.zeros_like(model_image)
    alpha_y = np.zeros_like(model_image)
    galaxy_count = 0
    with GALAXIES.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["object_id"] in EXPLICIT or not row["log10_flexion_auger"]:
                continue
            px = (float(row["ra_deg"]) - lens_ra) * cos_dec * 3600.0
            py = (float(row["dec_deg"]) - lens_dec) * 3600.0
            separation = float(row["separation_arcsec"])
            delta3 = 10.0 ** float(row["log10_flexion_auger"])
            strength = delta3 * separation**3 / theta_e_main**2
            dax, day = point_mass_deflection(
                ra_rel, dec_rel, px, py, strength
            )
            alpha_x += dax
            alpha_y += day
            galaxy_count += 1

    image_positions = np.column_stack(
        [
            np.asarray(result["kwargs_ps"][0]["ra_image"]) - center[0],
            np.asarray(result["kwargs_ps"][0]["dec_image"]) - center[1],
        ]
    )
    sample_ax = []
    sample_ay = []
    with GALAXIES.open(encoding="utf-8") as handle:
        galaxy_rows = [
            row
            for row in csv.DictReader(handle)
            if row["object_id"] not in EXPLICIT and row["log10_flexion_auger"]
        ]
    for position in image_positions:
        ax = ay = 0.0
        for row in galaxy_rows:
            px = (float(row["ra_deg"]) - lens_ra) * cos_dec * 3600.0
            py = (float(row["dec_deg"]) - lens_dec) * 3600.0
            separation = float(row["separation_arcsec"])
            delta3 = 10.0 ** float(row["log10_flexion_auger"])
            strength = delta3 * separation**3 / theta_e_main**2
            dax, day = point_mass_deflection(
                np.asarray(position[0]),
                np.asarray(position[1]),
                px,
                py,
                strength,
            )
            ax += float(dax)
            ay += float(day)
        sample_ax.append(ax)
        sample_ay.append(ay)
    design = np.column_stack(
        [np.ones(4), image_positions[:, 0], image_positions[:, 1]]
    )
    coef_x = np.linalg.lstsq(design, np.asarray(sample_ax), rcond=None)[0]
    coef_y = np.linalg.lstsq(design, np.asarray(sample_ay), rcond=None)[0]
    grid_design = np.stack(
        [np.ones_like(ra_rel), ra_rel, dec_rel], axis=-1
    )
    alpha_x -= grid_design @ coef_x
    alpha_y -= grid_design @ coef_y

    grad_y_pix, grad_x_pix = np.gradient(model_image)
    grad_pix = np.stack([grad_x_pix, grad_y_pix], axis=-1)
    grad_angle = grad_pix @ np.linalg.inv(transform)
    template = -(
        grad_angle[..., 0] * alpha_x + grad_angle[..., 1] * alpha_y
    )

    def mask_out_quasars(radius: float) -> np.ndarray:
        selected = mask.copy()
        for position in image_positions:
            selected &= (
                (ra_rel - position[0]) ** 2
                + (dec_rel - position[1]) ** 2
                > radius**2
            )
        return selected

    exclusion_radius = 0.16
    arc_mask = mask_out_quasars(exclusion_radius)
    active_template = template[arc_mask]
    active_residual = residual[arc_mask]
    denominator = float(np.dot(active_template, active_template))
    fitted_amplitude = float(
        np.dot(active_template, active_residual) / denominator
    )
    cosine = float(
        np.dot(active_template, active_residual)
        / (
            np.linalg.norm(active_template)
            * np.linalg.norm(active_residual)
        )
    )
    baseline_sse = float(np.dot(active_residual, active_residual))
    corrected = active_residual - fitted_amplitude * active_template
    corrected_sse = float(np.dot(corrected, corrected))
    fractional_sse_reduction = (baseline_sse - corrected_sse) / baseline_sse
    fixed_corrected_sse = float(
        np.dot(
            active_residual - active_template,
            active_residual - active_template,
        )
    )
    fixed_fractional_sse_reduction = (
        baseline_sse - fixed_corrected_sse
    ) / baseline_sse
    radius_stress = {}
    for radius in (0.12, 0.16, 0.20, 0.24):
        stress_mask = mask_out_quasars(radius)
        stress_template = template[stress_mask]
        stress_residual = residual[stress_mask]
        stress_dot = float(np.dot(stress_template, stress_residual))
        stress_cosine = stress_dot / (
            float(np.linalg.norm(stress_template))
            * float(np.linalg.norm(stress_residual))
        )
        stress_baseline = float(np.dot(stress_residual, stress_residual))
        stress_fixed = float(
            np.dot(
                stress_residual - stress_template,
                stress_residual - stress_template,
            )
        )
        radius_stress[f"{radius:.2f}"] = {
            "active_pixel_count": int(np.count_nonzero(stress_mask)),
            "template_residual_cosine": stress_cosine,
            "fixed_amplitude_fractional_sse_reduction": (
                stress_baseline - stress_fixed
            )
            / stress_baseline,
        }

    summary = {
        "schema": "paper7 DES J0408 local cubic F814W arc template v1",
        "fold": "LOBO-F814W already opened",
        "subthreshold_galaxy_count": galaxy_count,
        "quasar_exclusion_radius_arcsec": exclusion_radius,
        "active_arc_pixel_count": int(np.count_nonzero(arc_mask)),
        "template_rms": float(np.sqrt(np.mean(active_template**2))),
        "residual_rms": float(np.sqrt(np.mean(active_residual**2))),
        "template_residual_cosine": cosine,
        "profiled_template_amplitude": fitted_amplitude,
        "fractional_unweighted_sse_reduction": float(
            fractional_sse_reduction
        ),
        "fixed_amplitude_fractional_unweighted_sse_reduction": float(
            fixed_fractional_sse_reduction
        ),
        "quasar_exclusion_radius_stress": radius_stress,
        "source_forward_template_materialized": True,
        "endpoint_was_previously_opened": True,
        "confirmatory_evidence_allowed": False,
        "exploratory_alignment_positive": bool(
            cosine > 0 and fractional_sse_reduction > 0
        ),
        "tau_specific_information_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "EXPLORATORY_F814W_ARC_TEMPLATE_ALIGNMENT_POSITIVE__"
            "CONFIRMATION_FORBIDDEN_ALREADY_OPENED_ENDPOINT"
            if cosine > 0 and fractional_sse_reduction > 0
            else "EXPLORATORY_F814W_ARC_TEMPLATE_ALIGNMENT_NULL_OR_NEGATIVE"
        ),
        "claim_boundary": (
            "The LOS template is source-derived, but the F814W endpoint was "
            "opened by the earlier generic residual analysis. The score is "
            "unweighted and exploratory; it cannot validate the standard LOS "
            "completion or Tau Core. A new band/system with frozen covariance "
            "is required for confirmation."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    np.savez_compressed(
        ARRAYS,
        template=template,
        residual=residual,
        arc_mask=arc_mask,
        alpha_x=alpha_x,
        alpha_y=alpha_y,
    )
    REPORT.write_text(
        "# DES J0408 local cubic F814W arc template v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        "The score is exploratory because F814W was already opened before this "
        "specific LOS template was frozen.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
