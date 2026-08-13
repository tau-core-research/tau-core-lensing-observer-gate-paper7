#!/usr/bin/env python3
"""Rank public periodic-source microlensing events for a clock-rate test."""

from __future__ import annotations

import hashlib
import io
import json
import re
import tarfile
import urllib.request
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data/external/ogle_ews_periodic"
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle_periodic_microlensing_clock_support_v1"
)
BASE_URL = "https://www.astrouw.edu.pl/ogle/ogle3/ews"

# Periods and source coordinates are frozen from Wyrzykowski et al. (2006),
# Table 2. Archive hashes freeze the public OGLE EWS payloads used here.
EVENTS = {
    "2003-BLG-428": {
        "period_days": 0.36380,
        "source": "OGLE174448.21-335605.4",
        "sha256": "475c627e84164a84b45e26fc96a7ba3881831de571acaf5354f47a7aa1ec4090",
    },
    "2002-BLG-103": {
        "period_days": 0.82756,
        "source": "OGLE175239.94-322613.3",
        "sha256": "f1a2b2461aab1e7b61f020c81f8f69722e98d628a90d0a8639987354bc6d957a",
    },
    "2003-BLG-452": {
        "period_days": 4.026575,
        "source": "OGLE175554.26-301826.7",
        "sha256": "feb91c2598fd494a5c5b49e590c779750788af79a5ff717aeedbcf6586574d76",
    },
    "2004-BLG-390": {
        "period_days": 0.34825,
        "source": "OGLE175828.21-304717.4",
        "sha256": "05e4f627586a544795bf39fb3a2ac96b4ccbd8a1032670e7c20730f97dafb886",
    },
    "2004-BLG-101": {
        "period_days": 0.86193,
        "source": "OGLE175907.77-305519.1",
        "sha256": "76a24fa17853fc88437437aaae8dc9b80fe6683cdd187078213cd1a6919e79a7",
    },
    "2002-BLG-093": {
        "period_days": 0.62610,
        "source": "OGLE180950.21-260542.7",
        "sha256": "37d06c14d6a600537f992aedc03dbf2272b0d38170a317dd90ace3409e8f002b",
    },
    "2003-BLG-139": {
        "period_days": 53.2198,
        "source": "OGLE181322.09-294846.4",
        "sha256": "a3501ee74c3cbfc15c8b94020dfbceaba12d2ae42180f7dda0e486c4d4c77ccc",
    },
    "2004-BLG-081": {
        "period_days": 3.96628,
        "source": "OGLE180540.47-273427.5",
        "sha256": "a98857bf7f2f4d7fca6ea554822557fe31111771ee01ed89af328abfe701184f",
    },
}


def acquire(event: str, digest: str) -> Path:
    year, _, number = event.partition("-BLG-")
    path = DATA_DIR / f"{event}.tar.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        urllib.request.urlretrieve(
            f"{BASE_URL}/{year}/blg-{number}.tar.gz", path
        )
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != digest:
        raise RuntimeError(f"Unexpected SHA-256 for {event}: {actual}")
    return path


def member_bytes(archive: tarfile.TarFile, suffix: str) -> bytes:
    names = [name for name in archive.getnames() if name.endswith(suffix)]
    if len(names) != 1:
        raise RuntimeError(f"Expected one {suffix} member, found {names}")
    handle = archive.extractfile(names[0])
    if handle is None:
        raise RuntimeError(f"Cannot extract {names[0]}")
    return handle.read()


def parse_parameter(text: str, name: str) -> float:
    match = re.search(rf"^\s*{name}\s+([0-9.]+)", text, re.MULTILINE)
    if match is None:
        raise RuntimeError(f"Missing {name} in params.dat")
    return float(match.group(1))


def main() -> None:
    rows = []
    for event, frozen in EVENTS.items():
        path = acquire(event, frozen["sha256"])
        with tarfile.open(path, "r:gz") as archive:
            phot = np.loadtxt(io.BytesIO(member_bytes(archive, "phot.dat")))
            params = member_bytes(archive, "params.dat").decode("ascii")

        t0 = parse_parameter(params, "Tmax")
        t_e = parse_parameter(params, "tau")
        period = frozen["period_days"]
        event_mask = np.abs(phot[:, 0] - t0) <= t_e
        control_mask = np.abs(phot[:, 0] - t0) >= 2 * t_e
        event_phase = np.mod((phot[event_mask, 0] - t0) / period, 1)
        occupied_bins = int(
            np.unique(np.minimum((12 * event_phase).astype(int), 11)).size
        )
        event_points = int(event_mask.sum())
        control_points = int(control_mask.sum())
        cycles_under_lens = 2 * t_e / period
        ready = (
            event_points >= 30
            and control_points >= 100
            and occupied_bins >= 8
            and cycles_under_lens >= 5
        )
        rows.append(
            {
                "event": event,
                "source": frozen["source"],
                "period_days": period,
                "t0_hjd": t0,
                "einstein_radius_crossing_days": t_e,
                "total_points": int(len(phot)),
                "event_points_within_one_tE": event_points,
                "control_points_outside_two_tE": control_points,
                "event_phase_bins_occupied_of_12": occupied_bins,
                "cycles_within_two_tE": cycles_under_lens,
                "clock_audit_ready": ready,
                "archive_sha256": frozen["sha256"],
            }
        )

    rows.sort(
        key=lambda row: (
            row["clock_audit_ready"],
            row["event_phase_bins_occupied_of_12"],
            row["event_points_within_one_tE"],
        ),
        reverse=True,
    )
    ready = [row["event"] for row in rows if row["clock_audit_ready"]]
    result = {
        "schema": "Paper 7 OGLE periodic microlensing clock support audit v1",
        "question": (
            "Can the same periodic source provide unlensed-baseline versus "
            "microlensed-interval clock information?"
        ),
        "selection_rule": {
            "event_window": "absolute(t-t0) <= tE",
            "control_window": "absolute(t-t0) >= 2*tE",
            "minimum_event_points": 30,
            "minimum_control_points": 100,
            "minimum_occupied_phase_bins_of_12": 8,
            "minimum_cycles_within_two_tE": 5,
        },
        "events": rows,
        "ready_events": ready,
        "preferred_event": ready[0] if ready else None,
        "clock_rate_test_executed": False,
        "verdict": (
            "PUBLIC_SAME_SOURCE_CLOCK_AUDIT_SUPPORT_EXISTS"
            if ready
            else "PUBLIC_SAMPLE_UNDERPOWERED_FOR_CLOCK_AUDIT"
        ),
        "claim_boundary": (
            "This audit selects data support only. Periodic variability can "
            "belong to the source or a blend, and magnification changes "
            "photometric precision. Neither a phase anomaly nor a Tau Core "
            "clock effect has been measured here."
        ),
        "next_finite_action": (
            "Freeze the periodic waveform and ephemeris outside the lensing "
            "window; jointly fit standard microlensing magnification under a "
            "zero-clock-stretch null; then test one localized phase-rate "
            "coefficient with source/blend and cadence controls."
        ),
        "references": [
            "Wyrzykowski et al. 2006, Acta Astronomica 56, 145",
            "OGLE-III Early Warning System public event archives",
        ],
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("ready_events:", ", ".join(ready) if ready else "none")


if __name__ == "__main__":
    main()
