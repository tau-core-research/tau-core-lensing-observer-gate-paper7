#!/usr/bin/env python3
"""Audit matched unlensed-quasar support for the DES J0408 common clock."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
import urllib.request
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://faculty.washington.edu/ivezic/cmacleod/qso_dr7"
DB = ROOT / "data/external/stripe82/DB_QSO_S82.dat.gz"
DRW = ROOT / "data/external/stripe82/s82drw.tar.gz"
DB_SHA256 = "28e74c84be7489dc68059c8e0079f07edc642079ac34de786ca4d07a3e0b4030"
DRW_SHA256 = "83c738d8ef39d468d217632add4982261f3f99559c24fc361a01a304090935dd"
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_unlensed_control_support_v1"
)


def acquire(name: str, path: Path, digest: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        urllib.request.urlretrieve(f"{BASE_URL}/{name}", path)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != digest:
        raise RuntimeError(f"Unexpected SHA-256 for {path}: {actual}")


def main() -> None:
    acquire("DB_QSO_S82.dat.gz", DB, DB_SHA256)
    acquire("s82drw.tar.gz", DRW, DRW_SHA256)
    with gzip.open(DB, "rt", encoding="utf-8") as handle:
        catalog = np.loadtxt(handle)
    with tarfile.open(DRW, "r:gz") as archive:
        member = archive.extractfile("s82drw_r.dat")
        if member is None:
            raise RuntimeError("Missing r-band DRW catalog")
        drw = np.loadtxt(io.BytesIO(member.read()))

    physical_by_id = {int(row[3]): row for row in catalog}
    joined = [(row, physical_by_id[int(row[0])]) for row in drw]
    target = {"redshift": 2.375, "log10_mass_bh": 8.41, "log10_lbol": 47.04}
    windows = [
        ("strict", 0.15, 0.30, 0.30),
        ("moderate", 0.25, 0.40, 0.40),
        ("broad_diagnostic", 0.35, 0.50, 0.50),
    ]
    rows = []
    for label, dz, dm, dl in windows:
        selected = []
        for fit, physical in joined:
            quality = (
                fit[13] == 0
                and fit[14] - fit[15] > 2
                and fit[14] - fit[16] > 0.05
                and fit[7] > -9
            )
            matched = (
                abs(fit[3] - target["redshift"]) <= dz
                and abs(fit[5] - target["log10_mass_bh"]) <= dm
                and abs(physical[8] - target["log10_lbol"]) <= dl
            )
            if quality and matched:
                selected.append(fit)
        rest_tau = np.asarray(
            [10 ** fit[7] / (1 + fit[3]) for fit in selected]
        )
        rows.append(
            {
                "label": label,
                "redshift_half_width": dz,
                "log10_mass_half_width": dm,
                "log10_lbol_half_width": dl,
                "matched_control_count": len(selected),
                "median_rest_frame_tau_days": (
                    float(np.median(rest_tau)) if len(rest_tau) else None
                ),
            }
        )

    strict_ready = rows[0]["matched_control_count"] >= 20
    result = {
        "schema": "paper7 DES J0408 unlensed control support audit v1",
        "target": {
            **target,
            "mass_uncertainty_dex": 0.27,
            "source_references": [
                "Shajib et al. 2020, MNRAS 494, 6072",
                "Scholtz et al. 2022, MNRAS 517, 3377",
            ],
        },
        "unlensed_catalog": {
            "name": "SDSS Stripe 82 MacLeod et al. DRW r-band catalog",
            "object_count": len(drw),
            "db_sha256": DB_SHA256,
            "drw_sha256": DRW_SHA256,
        },
        "quality_rule": (
            "edge=0, Plike-Pnoise>2, Plike-Pinf>0.05, valid fitted tau"
        ),
        "matching_results": rows,
        "strict_pair_matching_ready": strict_ready,
        "broad_window_authorized_for_detection": False,
        "common_mode_clock_test_executed": False,
        "differential_image_clock_null_reinterpreted_as_control_only": True,
        "verdict": (
            "STRICT_UNLENSED_MATCHED_CONTROL_READY"
            if strict_ready
            else "STRICT_MATCHED_CONTROL_UNDERPOWERED__POPULATION_REGRESSION_REQUIRED"
        ),
        "claim_boundary": (
            "Support audit only. The broad window cannot be used as a "
            "detection sample because redshift, mass, luminosity and rest-frame "
            "wavelength affect quasar variability timescales."
        ),
        "next_finite_action": (
            "Fit a source-frozen population relation for rest-frame log tau "
            "from the full quality-controlled Stripe 82 sample, then evaluate "
            "a reconstructed lensed-source tau against its posterior "
            "predictive distribution without widening match windows."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])


if __name__ == "__main__":
    main()
