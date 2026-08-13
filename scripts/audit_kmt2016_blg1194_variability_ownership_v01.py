#!/usr/bin/env python3
"""Equal-complexity ownership audit for KMT-2016-BLG-1194."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import crossmatch_kmtnet2016_periodic_source_clock_candidates_v01 as crossmatch


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_kmt2016_blg1194_variability_ownership_v1"
)
EVENT = "KMT-2016-BLG-1194"
PERIOD = 0.28348449
EPOCH = 7000.12282
T0 = 7601.62287
TE = 46.28
U0 = 0.356
HARMONIC_ORDERS = (4, 6, 8, 10)


def load_sites() -> list[tuple[str, np.ndarray]]:
    metadata = crossmatch.MATCH_METADATA[EVENT]
    key = metadata["pysis_key"]
    url = (
        "https://kmtnet.kasi.re.kr/ulens/event/2016/data/"
        f"{key}/pysis/pysis.tar.gz"
    )
    path = crossmatch.acquire(
        f"{EVENT}_pysis.tar.gz", url, metadata["pysis_sha256"]
    )
    import tarfile
    import io

    sites = []
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            if member.name.endswith("_I.pysis"):
                handle = archive.extractfile(member)
                if handle is not None:
                    sites.append(
                        (member.name, np.loadtxt(io.BytesIO(handle.read())))
                    )
    return sorted(sites)


def prepare(data: np.ndarray) -> tuple[np.ndarray, ...]:
    good = (
        np.isfinite(data).all(axis=1)
        & (data[:, 4] > 0.005)
        & (data[:, 4] < 0.2)
        & (data[:, 3] > 14)
        & (data[:, 3] < 22)
        & (data[:, 5] > 0)
        & (data[:, 5] < 10)
    )
    data = data[good]
    time = data[:, 0]
    magnitude = data[:, 3]
    magnitude_error = data[:, 4]
    flux = 10 ** (-0.4 * (magnitude - 18))
    flux_error = flux * np.log(10) * 0.4 * magnitude_error
    u = np.sqrt(U0**2 + ((time - T0) / TE) ** 2)
    amplification = (u**2 + 2) / (u * np.sqrt(u**2 + 4))
    phase = 2 * np.pi * (time - EPOCH) / PERIOD
    return time, flux, flux_error, amplification, phase


def fit(
    data: np.ndarray, harmonics: int, source_owned: bool
) -> tuple[float, int]:
    _, flux, error, amplification, phase = prepare(data)
    modulation = amplification if source_owned else np.ones_like(amplification)
    columns = [amplification, np.ones_like(amplification)]
    for order in range(1, harmonics + 1):
        columns.extend(
            [
                modulation * np.cos(order * phase),
                modulation * np.sin(order * phase),
            ]
        )
    design = np.column_stack(columns)
    coefficients = np.linalg.lstsq(
        design / error[:, None], flux / error, rcond=None
    )[0]
    fitted = np.sum(design * coefficients[None, :], axis=1)
    residual = (flux - fitted) / error
    return float(np.sum(np.square(residual))), len(flux)


def main() -> None:
    cells = []
    sites = load_sites()
    for harmonics in HARMONIC_ORDERS:
        for site, data in sites:
            blend_chi2, points = fit(data, harmonics, source_owned=False)
            source_chi2, _ = fit(data, harmonics, source_owned=True)
            cells.append(
                {
                    "harmonic_order": harmonics,
                    "site": site,
                    "points": points,
                    "blend_owned_chi2": blend_chi2,
                    "source_owned_chi2": source_chi2,
                    "delta_chi2_source_over_blend": blend_chi2 - source_chi2,
                    "source_preferred": source_chi2 < blend_chi2,
                }
            )

    all_source_preferred = all(row["source_preferred"] for row in cells)
    result = {
        "schema": "Paper 7 KMT-2016-BLG-1194 variability ownership v1",
        "event": EVENT,
        "models": (
            "Equal-complexity point-lens plus Fourier RRc models. In the "
            "source-owned model the periodic basis is multiplied by the "
            "microlensing amplification; in the blend-owned model it is not."
        ),
        "frozen_lens_parameters": {
            "t0_hjd_minus_2450000": T0,
            "tE_days": TE,
            "u0": U0,
        },
        "frozen_rrc_ephemeris": {
            "period_days": PERIOD,
            "maximum_epoch_hjd_minus_2450000": EPOCH,
        },
        "quality_filter": (
            "0.005 < mag_error < 0.2, 14 < I < 22, 0 < FWHM < 10"
        ),
        "cells": cells,
        "source_preferred_cells": sum(
            row["source_preferred"] for row in cells
        ),
        "total_cells": len(cells),
        "verdict": (
            "SOURCE_OWNERSHIP_SUPPORTED_ACROSS_SITES_AND_SHAPE_ORDERS"
            if all_source_preferred
            else "SOURCE_OWNERSHIP_UNRESOLVED"
        ),
        "claim_boundary": (
            "This supports assignment of the periodic RRc variability to the "
            "microlensed source under the frozen point-lens family. The large "
            "absolute chi-square indicates remaining photometric or shape "
            "misspecification, so this is not a clock anomaly or Tau signal."
        ),
        "next_finite_action": (
            "Freeze an enriched no-clock RRc plus microlensing null with "
            "site-specific calibration and slow standard residual structure; "
            "then test one event-localized phase-rate coefficient conditionally."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print(
        "source-preferred cells:",
        result["source_preferred_cells"],
        "/",
        result["total_cells"],
    )


if __name__ == "__main__":
    main()
