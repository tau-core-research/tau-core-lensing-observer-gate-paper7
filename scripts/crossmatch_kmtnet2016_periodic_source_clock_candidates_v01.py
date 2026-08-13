#!/usr/bin/env python3
"""Residual-blind KMTNet 2016 versus OGLE periodic-source crossmatch."""

from __future__ import annotations

import hashlib
import io
import json
import tarfile
import urllib.request
from pathlib import Path

import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data/external/kmt2016_ogle_periodic_crossmatch"
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_kmtnet2016_periodic_source_crossmatch_v1"
)

SOURCES = {
    "kmt_events": (
        "https://kmtnet.kasi.re.kr/ulens/event/2016/listpage.dat",
        "67581754cff39f815b20084d174846d3600087b03ca1531ef85f8015fd3253bb",
    ),
    "ecl_ident": (
        "https://www.astrouw.edu.pl/ogle/ogle4/OCVS/blg/ecl/ident.dat",
        "f8cf930b47ae33d0271d9da26f7d06adfc6269543f7bb9cf8ebb7338f3ba762a",
    ),
    "rrlyr_ident": (
        "https://www.astrouw.edu.pl/ogle/ogle4/OCVS/blg/rrlyr/ident.dat",
        "24516c93a2c302f1ee92d6696a24a20adf471c30548637553ddc619d951d2f12",
    ),
    "cep_ident": (
        "https://www.astrouw.edu.pl/ogle/ogle4/OCVS/blg/cep/ident.dat",
        "5cc87f34cb9abab503d53e8b7d0f0617e028eac386248c4562b03635df418334",
    ),
    "t2cep_ident": (
        "https://www.astrouw.edu.pl/ogle/ogle4/OCVS/blg/t2cep/ident.dat",
        "f0cfe2e0983107243e20a73130a0abb476ae631c80918f0a67ee264ed1278cf9",
    ),
    "dsct_ident": (
        "https://www.astrouw.edu.pl/ogle/ogle4/OCVS/blg/dsct/ident.dat",
        "26ba0a9ab40716c7a563589879c18dd56c7b96391bf597d6e0c93b67b4a3aef7",
    ),
    "rot_ident": (
        "https://www.astrouw.edu.pl/ogle/ogle4/OCVS/blg/rot/ident.dat",
        "6928254fccfcc2322ff9f5b0db40c8b1482f97ab9acd3fcacd12a10a9195939d",
    ),
}

MATCH_METADATA = {
    "KMT-2016-BLG-0141": {
        "ogle_id": "OGLE-BLG-ECL-280366",
        "period_days": 0.7074574,
        "catalog_mean_i": 17.274,
        "pysis_key": "KB160141",
        "pysis_sha256": "c728866bbe946c15066c52901ca1c8abc9ad1c2525addbf206c33a2090e3e503",
    },
    "KMT-2016-BLG-1490": {
        "ogle_id": "OGLE-BLG-ELL-023473",
        "period_days": 11.8390397,
        "catalog_mean_i": 15.427,
        "pysis_key": "KB161490",
        "pysis_sha256": "a8be6941de3c281f7ec7aad32680d17ec3df87230e0eac3a69c3351f01c0354e",
    },
    "KMT-2016-BLG-1194": {
        "ogle_id": "OGLE-BLG-RRLYR-29501",
        "period_days": 0.28348449,
        "catalog_mean_i": 17.866,
        "pysis_key": "KB161194",
        "pysis_sha256": "8e69e060c51657db5ca52f4fb856e338919552cb6f7834dd14365898dd311083",
    },
}


def acquire(name: str, url: str, digest: str) -> Path:
    path = DATA_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        urllib.request.urlretrieve(url, path)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != digest:
        raise RuntimeError(f"Unexpected SHA-256 for {name}: {actual}")
    return path


def parse_kmt(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="ascii").splitlines():
        parts = line.split()
        if len(parts) < 14:
            continue
        rows.append(
            {
                "event": parts[0],
                "ra": parts[4],
                "dec": parts[5],
                "t0": float(parts[6]),
                "tE": float(parts[7]),
                "source_i": float(parts[9]),
                "base_i": float(parts[10]),
            }
        )
    return rows


def parse_ogle(path: Path, kind: str) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="ascii").splitlines():
        parts = line.split()
        if kind == "rot" and len(parts) >= 3:
            rows.append({"ogle_id": parts[0], "ra": parts[1], "dec": parts[2]})
        elif kind != "rot" and len(parts) >= 4:
            rows.append({"ogle_id": parts[0], "ra": parts[2], "dec": parts[3]})
    return rows


def load_pysis(event: str, metadata: dict) -> np.ndarray:
    key = metadata["pysis_key"]
    url = (
        "https://kmtnet.kasi.re.kr/ulens/event/2016/data/"
        f"{key}/pysis/pysis.tar.gz"
    )
    path = acquire(f"{event}_pysis.tar.gz", url, metadata["pysis_sha256"])
    arrays = []
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            if member.name.endswith("_I.pysis"):
                handle = archive.extractfile(member)
                if handle is not None:
                    arrays.append(np.loadtxt(io.BytesIO(handle.read())))
    if not arrays:
        raise RuntimeError(f"No I-band pySIS data for {event}")
    return np.concatenate(arrays)


def main() -> None:
    acquired = {
        key: acquire(f"{key}.dat", url, digest)
        for key, (url, digest) in SOURCES.items()
    }
    kmt = parse_kmt(acquired["kmt_events"])
    kmt_coords = SkyCoord(
        [row["ra"] for row in kmt],
        [row["dec"] for row in kmt],
        unit=(u.hourangle, u.deg),
    )
    matches = []
    catalog_counts = {}
    for key in ("ecl", "rrlyr", "cep", "t2cep", "dsct", "rot"):
        ogle = parse_ogle(acquired[f"{key}_ident"], key)
        catalog_counts[key] = len(ogle)
        coords = SkyCoord(
            [row["ra"] for row in ogle],
            [row["dec"] for row in ogle],
            unit=(u.hourangle, u.deg),
        )
        index, separation, _ = kmt_coords.match_to_catalog_sky(coords)
        for kmt_index, sep_arcsec in enumerate(separation.arcsec):
            if sep_arcsec <= 1.0:
                matches.append(
                    {
                        **kmt[kmt_index],
                        **ogle[index[kmt_index]],
                        "catalog_family": key,
                        "separation_arcsec": float(sep_arcsec),
                    }
                )

    enriched = []
    for row in matches:
        metadata = MATCH_METADATA.get(row["event"])
        if metadata is None or row["ogle_id"] != metadata["ogle_id"]:
            raise RuntimeError(f"Unfrozen match encountered: {row}")
        phot = load_pysis(row["event"], metadata)
        times = phot[:, 0]
        event_mask = np.abs(times - row["t0"]) <= row["tE"]
        control_mask = np.abs(times - row["t0"]) >= 2 * row["tE"]
        phase = np.mod(
            (times[event_mask] - row["t0"]) / metadata["period_days"], 1
        )
        occupied_bins = int(
            np.unique(np.minimum((12 * phase).astype(int), 11)).size
        )
        cycles = 2 * row["tE"] / metadata["period_days"]
        source_delta = abs(row["source_i"] - metadata["catalog_mean_i"])
        base_delta = abs(row["base_i"] - metadata["catalog_mean_i"])
        source_compatible = source_delta <= base_delta + 0.05
        coverage_ready = (
            int(event_mask.sum()) >= 30
            and int(control_mask.sum()) >= 100
            and occupied_bins >= 8
            and cycles >= 5
        )
        enriched.append(
            {
                **row,
                "period_days": metadata["period_days"],
                "catalog_mean_i": metadata["catalog_mean_i"],
                "source_catalog_magnitude_delta": source_delta,
                "base_catalog_magnitude_delta": base_delta,
                "source_magnitude_compatible": source_compatible,
                "event_points_within_one_tE": int(event_mask.sum()),
                "control_points_outside_two_tE": int(control_mask.sum()),
                "event_phase_bins_occupied_of_12": occupied_bins,
                "cycles_within_two_tE": cycles,
                "coverage_ready": coverage_ready,
                "clock_preflight_ready": source_compatible and coverage_ready,
                "pysis_sha256": metadata["pysis_sha256"],
            }
        )

    enriched.sort(
        key=lambda row: (
            row["clock_preflight_ready"],
            -row["separation_arcsec"],
        ),
        reverse=True,
    )
    ready = [row["event"] for row in enriched if row["clock_preflight_ready"]]
    result = {
        "schema": "Paper 7 KMTNet 2016 periodic-source crossmatch v1",
        "selection": {
            "match_radius_arcsec": 1.0,
            "residual_or_clock_fit_used_for_selection": False,
            "minimum_event_points": 30,
            "minimum_control_points": 100,
            "minimum_phase_bins_of_12": 8,
            "minimum_cycles_within_two_tE": 5,
            "source_magnitude_compatibility": (
                "abs(Isource-Icatalog) <= abs(Ibase-Icatalog)+0.05 mag"
            ),
        },
        "kmt_event_rows": len(kmt),
        "ogle_catalog_rows": catalog_counts,
        "matches": enriched,
        "clock_preflight_ready_events": ready,
        "preferred_event": ready[0] if ready else None,
        "verdict": (
            "RESIDUAL_BLIND_PERIODIC_SOURCE_PREFLIGHT_CANDIDATE_FOUND"
            if ready
            else "NO_PERIODIC_SOURCE_PREFLIGHT_CANDIDATE"
        ),
        "ownership_boundary": (
            "Coordinate and magnitude compatibility do not prove that the "
            "periodic component and the microlensed source are identical in a "
            "crowded field. The preferred event must pass an explicit "
            "variable-source versus variable-blend likelihood comparison."
        ),
        "next_finite_action": (
            "For KMT-2016-BLG-1194, fit the independently frozen OGLE RRc "
            "ephemeris jointly with standard microlensing under equal-complexity "
            "source-owned and blend-owned variability models. Do not fit a "
            "clock-rate coefficient until ownership is resolved."
        ),
        "references": [
            "Kim et al. 2018, The KMTNet 2016 Data Release, arXiv:1804.03352",
            "OGLE Collection of Variable Stars public catalogs",
        ],
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("matches:", len(enriched))
    print("ready:", ", ".join(ready) if ready else "none")


if __name__ == "__main__":
    main()
