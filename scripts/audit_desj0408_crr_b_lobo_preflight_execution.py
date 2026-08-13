#!/usr/bin/env python3
"""Audit the leakage-guarded DES J0408 CRR-B F814W preflight execution."""

from __future__ import annotations

import hashlib
import json
import pickle
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "data/derived/repro_results/tau_core_lensing_desj0408_crr_b_lobo_preflight_v1"
NOTEBOOK = RUN_DIR / "desj0408_crr_b_lobo_f814w_preflight_executed.ipynb"
MODEL_OUTPUT = ROOT / (
    "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography/temp/"
    "tau_core_crr_b_lobo_f814w_preflight_out.txt"
)
EXPECTED_MASK = [False, True, True]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    with MODEL_OUTPUT.open("rb") as handle:
        input_, output_ = pickle.load(handle)

    fitting_list, multi_band_list, _, _, kwargs_likelihood, _, init_samples = input_
    kwargs_result, multi_band_list_out, fit_output, _ = output_
    mask = kwargs_likelihood.get("bands_compute")
    pso_steps = [step for step in fitting_list if step[0] == "PSO"]
    guards = {
        "heldout_f814w_excluded_from_likelihood": mask == EXPECTED_MASK,
        "no_full_three_band_initialization": init_samples is None,
        "single_bounded_pso_step": len(pso_steps) == 1
        and pso_steps[0][1] == {
            "sigma_scale": 1.0,
            "n_particles": 4,
            "n_iterations": 1,
            "threadCount": 1,
        },
        "three_band_container_preserved": len(multi_band_list) == len(multi_band_list_out) == 3,
        "fit_output_present": bool(fit_output) and fit_output[0][0] == "PSO",
        "best_fit_present": bool(kwargs_result.get("kwargs_lens")),
    }
    passed = all(guards.values())
    payload = {
        "schema": "paper7 DES J0408 CRR-B LOBO execution audit v1",
        "fold": "LOBO-F814W",
        "training_bands": ["F475X", "F160W"],
        "heldout_band": "F814W",
        "bands_compute": mask,
        "fitting_sequence": fitting_list,
        "guards": guards,
        "executed_notebook": {
            "path": str(NOTEBOOK.relative_to(ROOT)),
            "sha256": sha256(NOTEBOOK),
            "bytes": NOTEBOOK.stat().st_size,
        },
        "model_output": {
            "path": str(MODEL_OUTPUT.relative_to(ROOT)),
            "sha256": sha256(MODEL_OUTPUT),
            "bytes": MODEL_OUTPUT.stat().st_size,
        },
        "psf_error_map_in_geometry_preflight": False,
        "heldout_pixels_scored": False,
        "channel_effect_test_performed": False,
        "interpretation": (
            "The leakage-guarded two-band geometry path executes. This does not validate "
            "the fit, score the heldout image, or detect a channel effect. PSF uncertainty "
            "must be restored as a nuisance contribution before endpoint scoring."
        ),
        "verdict": (
            "CRR_B_F814W_LEAKAGE_GUARDED_GEOMETRY_PREFLIGHT_PASS"
            if passed
            else "CRR_B_F814W_GEOMETRY_PREFLIGHT_AUDIT_FAIL"
        ),
    }
    output_path = RUN_DIR / "execution_audit_f814w.json"
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(payload["verdict"])
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
