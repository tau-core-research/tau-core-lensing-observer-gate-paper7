#!/usr/bin/env python3
"""Build a source-backed DES J0408 channel-first rank-repair atlas."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import h5py


ROOT = Path(__file__).resolve().parents[1]
DES = ROOT / "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography"
OUT = ROOT / "data/derived/repro_results/tau_core_lensing_desj0408_channel_first_rank_repair_v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hdf5_fields(path: Path) -> dict[str, object]:
    with h5py.File(path, "r") as handle:
        return {
            key: list(handle[key].shape) if handle[key].shape else []
            for key in sorted(handle.keys())
        }


def main() -> None:
    bands = ["f160w", "f475x", "f814w"]
    imaging = []
    for band in bands:
        data = DES / "data" / f"data_{band}.hdf5"
        psf = DES / "data" / f"psf_{band}.hdf5"
        imaging.append({
            "band": band.upper(),
            "data_path": str(data.relative_to(ROOT)),
            "data_sha256": sha256(data),
            "data_fields": hdf5_fields(data),
            "psf_path": str(psf.relative_to(ROOT)),
            "psf_sha256": sha256(psf),
            "psf_fields": hdf5_fields(psf),
        })

    velocity_files = sorted((DES / "model_posteriors/velocity_dispersion").glob("*.txt"))
    delay_files = sorted((DES / "model_posteriors/time_delays").glob("*.txt"))
    kappa_files = sorted((DES / "data").glob("kappahist_0408_*.cat"))

    routes = [
        {
            "route_id": "CRR-A",
            "name": "kinematics_environment_nuisance_reduction",
            "role": "reduce_nuisance_rank",
            "source_support": {
                "velocity_dispersion_file_count": len(velocity_files),
                "external_convergence_file_count": len(kappa_files),
            },
            "independent_of_delay_measurement": True,
            "adds_new_channel_observable": False,
            "current_readiness": "SOURCE_PRESENT_LINKAGE_AND_CONDITIONAL_RANK_AUDIT_OPEN",
            "promotion_gate": "show that source-frozen kinematic/environment conditioning lowers covariance-whitened delay nuisance rank below two without observed-delay selection",
        },
        {
            "route_id": "CRR-B",
            "name": "leave_one_band_out_multiband_prediction",
            "role": "expand_observable_codomain",
            "source_support": {
                "hst_band_count": len(imaging),
                "bands": [row["band"] for row in imaging],
                "image_and_psf_products_complete": True,
            },
            "independent_of_delay_measurement": True,
            "adds_new_channel_observable": True,
            "current_readiness": "RAW_PRODUCTS_PRESENT_TWO_BAND_REFIT_NOT_RUN",
            "promotion_gate": "fit geometry/source on two bands, predict the third without refitting, then survive PSF/extinction/microlensing/calibration residualization",
        },
        {
            "route_id": "CRR-C",
            "name": "in_sample_astrometry_or_model_parity",
            "role": "forbidden_false_rank_repair",
            "source_support": {"delay_file_count": len(delay_files)},
            "independent_of_delay_measurement": False,
            "adds_new_channel_observable": False,
            "current_readiness": "FORBIDDEN_AS_INDEPENDENT_ROW",
            "promotion_gate": "none; model-derived or in-fit quantities remain nuisance/model coordinates",
        },
    ]

    payload = {
        "schema": "paper7 DES J0408 channel-first rank-repair atlas v1",
        "inference_order": [
            "generic_channel_effect",
            "independent_replication",
            "time_quantum_other_origin_classification",
        ],
        "source_manifest": {
            "repository": "https://github.com/ajshajib/DESJ0408_time_delay_cosmography",
            "delay_posterior_count": len(delay_files),
            "velocity_dispersion_product_count": len(velocity_files),
            "external_convergence_product_count": len(kappa_files),
            "imaging": imaging,
        },
        "routes": routes,
        "priority": ["CRR-A", "CRR-B"],
        "next_finite_action": "Run CRR-A first as a finite conditional-rank audit; if exact or declared practical nuisance rank stays two, execute a two-band fit / third-band prediction for CRR-B.",
        "verdict": "DESJ0408_CHANNEL_FIRST_RANK_REPAIR_ROUTES_SOURCE_BACKED",
        "claim_boundary": {
            "allowed": "Two source-backed routes can test a generic channel component without assuming time or quantum origin.",
            "forbidden": "No generic channel effect or origin class is detected by this atlas.",
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    report = [
        "# DES J0408 Channel-First Rank-Repair Atlas v1",
        "",
        f"**Verdict:** `{payload['verdict']}`",
        "",
        "| route | role | source state |",
        "| --- | --- | --- |",
    ]
    for row in routes:
        report.append(f"| `{row['route_id']}` | `{row['role']}` | `{row['current_readiness']}` |")
    report += [
        "",
        "CRR-A conditions the two delays on independent stellar-kinematic and environment products. CRR-B expands the codomain with a genuinely held-out HST band. Neither route assumes time, quantum, or another origin label.",
    ]
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(payload["verdict"])


if __name__ == "__main__":
    main()
