#!/usr/bin/env python3
"""Audit whether DES J0408 supports a leakage-free held-out-band channel test."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography/notebooks/DESJ0408 Multiband Image Modeling.ipynb"
OUT = ROOT / "data/derived/repro_results/tau_core_lensing_desj0408_crr_b_leave_one_band_out_identifiability_v1"


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    text = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
    )
    checks = {
        "three_band_model_declared": "band_number = 3" in text,
        "bands_compute_switch_present": "'bands_compute': [True, True, True]" in text,
        "per_band_source_model_loop_present": "for band_num in range(band_number)" in text,
        "cross_band_source_shape_links_present": "joint_source_with_source.append" in text,
        "source_amplitudes_are_linear_nuisance": "'source_marg': True" in text,
        "per_band_linear_prior_present": "'linear_prior': [5e4, 5e4, 5e4]" in text,
        "independent_cross_band_sed_transport_present": False,
        "heldout_band_absolute_flux_predictable_without_heldout_data": False,
    }

    bands = ["F814W", "F475X", "F160W"]
    folds = []
    for heldout_index, heldout in enumerate(bands):
        train = [band for index, band in enumerate(bands) if index != heldout_index]
        compute = [index != heldout_index for index in range(3)]
        folds.append({
            "fold_id": f"LOBO-{heldout}",
            "train_bands": train,
            "heldout_band": heldout,
            "bands_compute_during_geometry_fit": compute,
            "forbidden_during_geometry_fit": [
                "heldout image pixels",
                "heldout point-source fluxes",
                "heldout PSF residual optimization",
                "full-three-band known_solution initialization",
            ],
            "allowed_heldout_evaluation_nuisance": [
                "linear component amplitudes",
                "one background offset",
                "predeclared PSF-error modes",
            ],
            "test_observables": [
                "normalized arc/profile shape residual",
                "image-wise centroid residual",
                "parity-signed profile residual",
            ],
            "absolute_flux_channel_row_allowed": False,
        })

    payload = {
        "schema": "paper7 DES J0408 CRR-B leave-one-band-out identifiability audit v1",
        "source": str(NOTEBOOK.relative_to(ROOT)),
        "source_checks": checks,
        "conditional_no_go": {
            "statement": "Without an independently frozen cross-band spectral/SED transport, two training bands do not determine the absolute held-out-band flux because held-out linear amplitudes remain free.",
            "status": "PROVED_FROM_MODEL_PARAMETERIZATION",
            "forbidden_claim": "absolute heldout flux mismatch is a generic channel effect",
        },
        "repaired_test": {
            "name": "geometry_and_normalized_profile_holdout_with_linear_amplitude_profiled",
            "principle": "Fit nonlinear lens/source geometry on two bands only; in the held-out band profile declared linear amplitudes and calibration modes, then test the remaining normalized spatial residual.",
            "generic_channel_origin_labels_used": False,
            "requires_new_sed_law": False,
            "folds": folds,
        },
        "preflight": {
            "technical_band_switch_available": checks["bands_compute_switch_present"],
            "absolute_flux_test_identifiable": False,
            "normalized_geometry_profile_test_conditionally_identifiable": True,
            "two_band_refits_executed": False,
            "heldout_residuals_opened": False,
        },
        "next_finite_action": "Create three notebook-derived two-band jobs with bands_compute set by fold, no full-three-band initialization, bounded PSO geometry fit, and held-out linear-amplitude-only evaluation.",
        "verdict": "CRR_B_ABSOLUTE_FLUX_NO_GO_NORMALIZED_PROFILE_HOLDOUT_DEFINED",
        "claim_boundary": "This audit defines a leakage-free generic-channel test but does not execute the refits or detect a channel effect.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    report = [
        "# DES J0408 CRR-B Leave-One-Band-Out Identifiability v1",
        "",
        f"**Verdict:** `{payload['verdict']}`",
        "",
        "Absolute held-out flux is not identifiable from two bands without an independent SED transport law. The repaired test profiles only held-out linear amplitudes and tests normalized spatial geometry/profile residuals.",
        "",
        "| fold | training | held out |",
        "| --- | --- | --- |",
    ]
    for fold in folds:
        report.append(f"| `{fold['fold_id']}` | {', '.join(fold['train_bands'])} | {fold['heldout_band']} |")
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(payload["verdict"])


if __name__ == "__main__":
    main()
