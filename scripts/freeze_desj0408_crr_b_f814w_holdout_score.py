#!/usr/bin/env python3
"""Freeze the CRR-B F814W heldout score before residual evaluation."""

from __future__ import annotations

import hashlib
import json
import pickle
from pathlib import Path

import h5py
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography"
RUN_DIR = ROOT / "data/derived/repro_results/tau_core_lensing_desj0408_crr_b_f814w_holdout_freeze_v1"
PREFLIGHT_AUDIT = ROOT / (
    "data/derived/repro_results/tau_core_lensing_desj0408_crr_b_lobo_preflight_v1/"
    "execution_audit_f814w.json"
)
PREFLIGHT_OUTPUT = ROOT / (
    "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography/temp/"
    "tau_core_crr_b_lobo_f814w_preflight_out.txt"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dataset_meta(path: Path) -> dict[str, object]:
    with h5py.File(path, "r") as handle:
        return {
            key: {"shape": list(handle[key].shape), "dtype": str(handle[key].dtype)}
            for key in sorted(handle.keys())
        }


def main() -> None:
    data_path = PUBLIC / "data/data_f814w.hdf5"
    psf_path = PUBLIC / "data/psf_f814w.hdf5"
    # Metadata only: no image value, model residual, or endpoint score is read here.
    with h5py.File(data_path, "r") as handle:
        image_shape = list(handle["image_data"].shape)
    with PREFLIGHT_OUTPUT.open("rb") as handle:
        input_, _ = pickle.load(handle)
    mask = np.asarray(input_[4]["image_likelihood_mask_list"][0])
    if list(mask.shape) != image_shape:
        raise ValueError("frozen mask and F814W image shape differ")
    mask_hash = hashlib.sha256(np.ascontiguousarray(mask).tobytes()).hexdigest()

    preflight = json.loads(PREFLIGHT_AUDIT.read_text(encoding="utf-8"))
    if preflight["verdict"] != "CRR_B_F814W_LEAKAGE_GUARDED_GEOMETRY_PREFLIGHT_PASS":
        raise ValueError("geometry preflight has not passed")

    payload = {
        "schema": "paper7 DES J0408 CRR-B F814W heldout score freeze v1",
        "status": "PREFLIGHT_NOT_ENDPOINT",
        "fold": "LOBO-F814W",
        "training_bands": ["F475X", "F160W"],
        "heldout_band": "F814W",
        "geometry_source": preflight["model_output"],
        "frozen_inputs": {
            "heldout_data": {"path": str(data_path.relative_to(ROOT)), "sha256": sha256(data_path), "datasets": dataset_meta(data_path)},
            "heldout_psf": {"path": str(psf_path.relative_to(ROOT)), "sha256": sha256(psf_path), "datasets": dataset_meta(psf_path)},
            "heldout_mask": {
                "source": "geometry preflight image_likelihood_mask_list[0]",
                "sha256_array_bytes": mask_hash,
                "shape": list(mask.shape),
                "active_pixels": int(np.count_nonzero(mask)),
            },
        },
        "allowed_heldout_nuisance": [
            "linear amplitudes of the frozen lens-light, source-light, and point-source templates",
            "one constant additive background mode",
        ],
        "forbidden_after_opening": [
            "nonlinear lens or source geometry refit",
            "heldout-dependent model-family choice",
            "PSF kernel optimization against heldout residuals",
            "mask, threshold, sign, or spatial-window retuning",
            "time, quantum, or other-readout attribution",
        ],
        "psf_uncertainty_rule": {
            "kernel": "public fixed F814W kernel_point_source",
            "uncertainty": "public psf_error_map propagated as a frozen covariance contribution",
            "free_psf_modes": 0,
        },
        "primary_statistic": {
            "name": "profiled_whitened_spatial_residual_energy",
            "definition": "Q = r_profiled^T C_frozen^{-1} r_profiled / nu",
            "residual": "heldout pixels minus frozen-geometry templates after allowed linear profiling",
            "covariance": "declared image noise plus propagated public PSF-error covariance",
            "mask": "preflight image_likelihood_mask_list[0], frozen by array hash",
        },
        "diagnostics_not_detection_tests": [
            "normalized residual radial profile",
            "quadrant residual coherence",
            "image-centroid residual",
            "parity-signed residual after image-role mapping is independently frozen",
        ],
        "required_controls_before_channel_candidate": [
            "same score on all three LOBO folds",
            "null calibration by noise realizations or posterior predictive simulations",
            "wrong-band and PSF-stress controls",
            "replication on an independent lens system",
        ],
        "heldout_image_values_read_by_freeze": False,
        "heldout_score_computed": False,
        "channel_effect_claim_allowed": False,
        "verdict": "CRR_B_F814W_HOLDOUT_SCORE_FROZEN_EVALUATION_NOT_YET_RUN",
    }
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(payload["verdict"])


if __name__ == "__main__":
    main()
