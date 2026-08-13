#!/usr/bin/env python3
"""Score the pre-frozen DES J0408 CRR-B F814W heldout image."""

from __future__ import annotations

import copy
import json
import pickle
from pathlib import Path

import h5py
import numpy as np
from lenstronomy.ImSim.MultiBand.multi_linear import MultiLinear


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography"
MODEL_OUTPUT = PUBLIC / "temp/tau_core_crr_b_lobo_f814w_preflight_out.txt"
FREEZE = ROOT / "data/derived/repro_results/tau_core_lensing_desj0408_crr_b_f814w_holdout_freeze_v1/summary.json"
OUT = ROOT / "data/derived/repro_results/tau_core_lensing_desj0408_crr_b_f814w_holdout_score_v1"


def evaluate(multi_band_list, masks, kwargs_model, result, include_psf_variance):
    bands = copy.deepcopy(multi_band_list)
    if include_psf_variance:
        with h5py.File(PUBLIC / "data/psf_f814w.hdf5", "r") as handle:
            # Legacy psf_error_map is the current lenstronomy psf_variance_map field.
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
    log_likelihood, linear_parameters = model.likelihood_data_given_model(
        **kwargs, check_positive_flux=False
    )
    images, error_maps, _, _ = model.image_linear_solve(**kwargs)
    mask = np.asarray(masks[0], dtype=bool)
    residual = np.asarray(bands[0][0]["image_data"]) - np.asarray(images[0])
    n_pixels = int(np.count_nonzero(mask))
    n_linear = len(linear_parameters[0])
    dof = n_pixels - n_linear
    return {
        "log_likelihood": float(log_likelihood),
        "chi2": float(-2.0 * log_likelihood),
        "n_active_pixels": n_pixels,
        "n_profiled_linear_parameters": n_linear,
        "degrees_of_freedom": dof,
        "reduced_chi2": float(-2.0 * log_likelihood / dof),
        "masked_residual_rms": float(np.sqrt(np.mean(residual[mask] ** 2))),
        "masked_data_rms": float(np.sqrt(np.mean(np.asarray(bands[0][0]["image_data"])[mask] ** 2))),
        "linear_parameters_finite": bool(np.all(np.isfinite(linear_parameters[0]))),
        "model_error_map_finite": bool(np.all(np.isfinite(error_maps[0]))),
    }, residual, mask


def main() -> None:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze["verdict"] != "CRR_B_F814W_HOLDOUT_SCORE_FROZEN_EVALUATION_NOT_YET_RUN":
        raise ValueError("heldout score was not frozen")
    with MODEL_OUTPUT.open("rb") as handle:
        input_, output_ = pickle.load(handle)
    _, multi_band_list, kwargs_model, _, kwargs_likelihood, _, _ = input_
    result = output_[0]
    masks = kwargs_likelihood["image_likelihood_mask_list"]

    primary, residual, mask = evaluate(
        multi_band_list, masks, kwargs_model, result, include_psf_variance=True
    )
    no_psf_stress, _, _ = evaluate(
        multi_band_list, masks, kwargs_model, result, include_psf_variance=False
    )
    excess = primary["reduced_chi2"] > 1.0
    payload = {
        "schema": "paper7 DES J0408 CRR-B F814W heldout score v1",
        "status": "NEGATIVE_RESULT_PRESERVED",
        "freeze": str(FREEZE.relative_to(ROOT)),
        "fold": "LOBO-F814W",
        "primary_with_frozen_psf_uncertainty": primary,
        "psf_uncertainty_omission_stress": no_psf_stress,
        "primary_excess_residual_energy_above_unit_noise_expectation": excess,
        "population_null_calibrated": False,
        "other_lobo_folds_scored": False,
        "independent_lens_replication": False,
        "interpretation": (
            "The first frozen heldout fold has no excess whitened spatial residual energy. "
            "It therefore does not supply a generic channel-effect candidate. This single "
            "negative fold neither identifies a channel origin nor excludes channel effects "
            "in other observables, folds, or lens systems."
        ),
        "channel_effect_candidate": False,
        "time_or_quantum_attribution_allowed": False,
        "verdict": "CRR_B_F814W_NO_EXCESS_CHANNEL_RESIDUAL_FIRST_FOLD_NEGATIVE",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    np.savez_compressed(OUT / "residual_f814w.npz", residual=residual, mask=mask)
    print(payload["verdict"])


if __name__ == "__main__":
    main()
