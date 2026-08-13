#!/usr/bin/env python3
"""Acquire and freeze the published DES J0408 line-of-sight morphology."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import tarfile
import urllib.request
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
URL = "https://export.arxiv.org/e-print/2003.12117"
SOURCE_SHA256 = "9b28b2525cc4c8a3a7c4d6f33af01df7353cce65962c6d50a2f8dd6ddc81d4f6"
TABLE_SHA256 = "81ac791fb2a2becb516358cd5e2d27fb8e30a6bc1934d5d6923159383f8b6e28"
EXTERNAL = ROOT / "data/external/strides_2003_12117"
TABLE_PATH = EXTERNAL / "tables.tex"
OUT_DIR = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_strides_los_morphology_v1"
)
GALAXIES_CSV = OUT_DIR / "desj0408_spectroscopic_galaxies.csv"
GROUPS_CSV = OUT_DIR / "desj0408_groups.csv"
SUMMARY = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def central_number(value: str) -> float | None:
    cleaned = value.replace(",", "")
    match = re.search(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", cleaned)
    return float(match.group(0)) if match else None


def clean_id(value: str) -> str:
    value = value.replace("$\\dagger$", "").replace("\\dagger", "")
    return re.sub(r"\s+", "", value)


def table_rows_between(
    text: str, start: str, end: str, field_count: int
) -> list[list[str]]:
    candidates: list[list[list[str]]] = []
    for section in text.split(start)[1:]:
        if end not in section:
            continue
        rows: list[list[str]] = []
        for raw in section.split(end, 1)[0].splitlines():
            if "&" not in raw or raw.lstrip().startswith("%"):
                continue
            line = raw.split(r"\T", 1)[0].strip()
            fields = [field.strip() for field in line.split("&")]
            if len(fields) == field_count:
                rows.append(fields)
        candidates.append(rows)
    return max(candidates, key=len, default=[])


def acquire_table() -> tuple[bytes, str]:
    if TABLE_PATH.exists():
        table = TABLE_PATH.read_bytes()
        if sha256(table) != TABLE_SHA256:
            raise RuntimeError("Cached tables.tex checksum mismatch")
        return table, "checksum-verified cache"

    with urllib.request.urlopen(URL, timeout=120) as response:
        archive = response.read()
    if sha256(archive) != SOURCE_SHA256:
        raise RuntimeError("arXiv source archive checksum mismatch")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:*") as bundle:
        extracted = bundle.extractfile("tables.tex")
        if extracted is None:
            raise RuntimeError("tables.tex missing from arXiv source")
        table = extracted.read()
    if sha256(table) != TABLE_SHA256:
        raise RuntimeError("Extracted tables.tex checksum mismatch")
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    TABLE_PATH.write_bytes(table)
    return table, "downloaded checksum-verified arXiv source"


def main() -> None:
    table_bytes, acquisition = acquire_table()
    text = table_bytes.decode("utf-8")

    galaxy_start = r"\multicolumn{9}{c}{\DESone} \T \B \\"
    galaxy_end = r"\multicolumn{9}{c}{\DEStwo} \T \B \\"
    galaxy_raw = table_rows_between(text, galaxy_start, galaxy_end, 9)
    galaxies = []
    for fields in galaxy_raw:
        galaxies.append(
            {
                "object_id": clean_id(fields[0]),
                "ra_deg": float(fields[1]),
                "dec_deg": float(fields[2]),
                "redshift": float(fields[3]),
                "i_mag": central_number(fields[4]),
                "log10_stellar_mass": central_number(fields[5]),
                "separation_arcsec": float(fields[6]),
                "log10_flexion_zahid": central_number(fields[7]),
                "log10_flexion_auger": central_number(fields[8]),
                "raw_log10_stellar_mass": fields[5],
                "raw_log10_flexion_zahid": fields[7],
                "raw_log10_flexion_auger": fields[8],
            }
        )

    groups_section = text.split(r"\label{tab:groups}", 1)[1].split(
        r"\end{tabular}", 1
    )[0]
    group_start = r"\multicolumn{10}{c}{\DESone} \T \B \\"
    group_end = r"\multicolumn{10}{c}{\DEStwo} \T \B \\"
    group_raw = table_rows_between(groups_section, group_start, group_end, 10)
    groups = []
    for fields in group_raw:
        ra_text, dec_text = [part.strip() for part in fields[6].split(",")]
        groups.append(
            {
                "group_id": int(central_number(fields[0])),
                "contains_lens": r"\star" in fields[0],
                "redshift": float(fields[1]),
                "member_count": int(fields[2]),
                "rest_velocity_dispersion_km_s": central_number(fields[3]),
                "intrinsic_velocity_dispersion_km_s": central_number(fields[4]),
                "r200_mpc": central_number(fields[5]),
                "ra_deg": float(ra_text),
                "dec_deg": float(dec_text),
                "separation_arcsec": central_number(fields[8]),
                "log10_flexion_shift": central_number(fields[9]),
                "raw_log10_flexion_shift": fields[9],
            }
        )

    if len(galaxies) != 198 or len(groups) != 10:
        raise RuntimeError(
            f"Unexpected table sizes: {len(galaxies)} galaxies, {len(groups)} groups"
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, rows in ((GALAXIES_CSV, galaxies), (GROUPS_CSV, groups)):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    redshifts = np.asarray([row["redshift"] for row in galaxies])
    separations = np.asarray([row["separation_arcsec"] for row in galaxies])
    auger = np.asarray(
        [
            row["log10_flexion_auger"]
            for row in galaxies
            if row["log10_flexion_auger"] is not None
        ],
        dtype=float,
    )
    summary = {
        "schema": "paper7 DES J0408 STRIDES LOS morphology v1",
        "source": {
            "title": (
                "STRIDES: Spectroscopic and photometric characterization of "
                "the environment and effects of mass along the line of sight "
                "to DES J0408-5354 and WGD 2038-4008"
            ),
            "arxiv": "2003.12117",
            "url": URL,
            "source_archive_sha256": SOURCE_SHA256,
            "tables_tex_sha256": TABLE_SHA256,
            "acquisition": acquisition,
        },
        "target": "DES J0408-5354",
        "reported_spectroscopic_galaxy_count": 199,
        "materialized_spectroscopic_galaxy_row_count": len(galaxies),
        "reported_vs_materialized_row_count_discrepancy": 1,
        "identified_group_count": len(groups),
        "reported_spectroscopic_completeness": {
            "fraction": 0.68,
            "selection": "18 <= i < 23 and 5 arcsec <= radius < 3 arcmin",
        },
        "redshift_range": [float(redshifts.min()), float(redshifts.max())],
        "median_redshift": float(np.median(redshifts)),
        "maximum_separation_arcsec": float(separations.max()),
        "galaxies_with_auger_log10_flexion_above_minus4": int(
            np.sum(auger > -4.0)
        ),
        "galaxies_with_materialized_auger_flexion": int(len(auger)),
        "group_redshifts": [row["redshift"] for row in groups],
        "machine_readable_outputs": [
            str(GALAXIES_CSV.relative_to(ROOT)),
            str(GROUPS_CSV.relative_to(ROOT)),
        ],
        "observed_los_morphology_materialized": True,
        "complete_observed_spectroscopic_cone": False,
        "complete_physical_light_cone_morphology_materialized": False,
        "path_specific_transport_assigned": False,
        "tau_specific_information_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "PUBLISHED_LOS_GALAXY_AND_GROUP_MORPHOLOGY_MATERIALIZED__"
            "PATH_TRANSPORT_AND_COMPLETENESS_OPEN"
        ),
        "claim_boundary": (
            "The artifact is a checksum-verified machine-readable extraction "
            "of the published DES J0408 spectroscopic environment. The paper "
            "reports 199 galaxies, while its released table contains 198 "
            "materializable DES J0408 rows; the discrepancy is retained. The "
            "reported sample is 68% complete under its stated "
            "selection and does not include the full photometric population, "
            "diffuse matter, or parent morphology. It is a source-side cone "
            "descriptor, not h_tau or evidence for observer-time distortion."
        ),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 STRIDES line-of-sight morphology v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        "The published causal-support environment is frozen as 198 released "
        "spectroscopic rows and ten groups; the paper's reported count of 199 "
        "is retained as a one-row source discrepancy. It materially expands the "
        "three-plane lens model, but path-specific transport and the missing "
        "32% of the selected spectroscopic sample remain unresolved.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
