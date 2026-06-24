#!/usr/bin/env python3
"""Acquire WGD2038 arXiv source-table payloads.

This obtains official arXiv source tables for the WGD2038 cosmographic paper
and materializes the numeric table values that are public in the source bundle.
It does not replace the missing per-sample lens-model posterior/Fermat payload.
"""

from __future__ import annotations

import csv
import io
import json
import re
import tarfile
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_ROOT = ROOT / "data" / "external" / "wgd2038_public_payload"
TABLE_DIR = PAYLOAD_ROOT / "arxiv_2406_02683_source_tables"
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results"
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_arxiv_source_table_payload_v1"
OUT_TABLE = DERIVED / "wgd2038_arxiv_source_table_payload_v1.csv"

ARXIV_EPRINT_URL = "https://arxiv.org/e-print/2406.02683"
TABLE_NAMES = [
    "tab_2038_ddt.tex",
    "tab_2038_ddtmodel_nokext_nokin.tex",
    "tab_2038_lcdm_h0.tex",
]


VALUE_PATTERN = re.compile(
    r"(?P<label>\\sc [^&]+|\\sc glee\}\+\\sc lenstronomy\} [^&]+|\\sc lenstronomy\} composite\\footnote\\{[^}]+\\}|\\sc lenstronomy\} [^&]+)"
    r"\s*&\s*(?P<values>.+?)\\\\",
    re.DOTALL,
)
NUM_PATTERN = re.compile(
    r"\$(?P<median>[0-9.]+)_\{-(?P<minus>[0-9.]+)\}\^\{\+(?P<plus>[0-9.]+)\}\$"
)
NUM_ALT_PATTERN = re.compile(
    r"\$(?P<median>[0-9.]+)_\{-(?P<minus>[0-9.]+)\}\^\{(?P<plus>[0-9.]+)\}\$"
)


def clean_label(raw: str) -> str:
    label = re.sub(r"\\footnote\{.*", "", raw)
    label = label.replace("\\textsc", "").replace("\\sc", "")
    label = label.replace("{", "").replace("}", "")
    return " ".join(label.split())


def parse_numeric_cell(cell: str) -> dict[str, float] | None:
    match = NUM_PATTERN.search(cell) or NUM_ALT_PATTERN.search(cell)
    if not match:
        return None
    return {
        "median": float(match.group("median")),
        "minus_16": float(match.group("minus")),
        "plus_84": float(match.group("plus")),
    }


def extract_source_tables() -> dict[str, str]:
    with urllib.request.urlopen(ARXIV_EPRINT_URL, timeout=60) as response:
        archive_bytes = response.read()
    tables: dict[str, str] = {}
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        for member in archive.getmembers():
            if member.name in TABLE_NAMES:
                extracted = archive.extractfile(member)
                if extracted is None:
                    continue
                tables[member.name] = extracted.read().decode("utf-8")
    missing = sorted(set(TABLE_NAMES) - set(tables))
    if missing:
        raise RuntimeError(f"missing expected arXiv table(s): {missing}")
    return tables


def parse_rows(table_name: str, table_text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for match in VALUE_PATTERN.finditer(table_text.replace("\n", " ")):
        label = clean_label(match.group("label"))
        cells = [cell.strip() for cell in match.group("values").split("&")]
        parsed = [parse_numeric_cell(cell) for cell in cells]
        parsed = [cell for cell in parsed if cell is not None]
        if not parsed:
            continue
        if table_name == "tab_2038_lcdm_h0.tex" and len(parsed) >= 2:
            quantity_names = ["H0_km_s_Mpc", "Ddt_Gpc"]
        else:
            quantity_names = ["Ddt_Gpc"]
        for quantity, values in zip(quantity_names, parsed):
            rows.append(
                {
                    "source_table": table_name,
                    "model": label,
                    "quantity": quantity,
                    "median": values["median"],
                    "minus_16": values["minus_16"],
                    "plus_84": values["plus_84"],
                    "unit": "km/s/Mpc" if quantity == "H0_km_s_Mpc" else "Gpc",
                    "source": "arXiv:2406.02683 source bundle",
                    "posterior_level_fermat_payload": False,
                }
            )
    return rows


def main() -> None:
    tables = extract_source_tables()
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, Any]] = []
    for name, text in tables.items():
        (TABLE_DIR / name).write_text(text, encoding="utf-8")
        all_rows.extend(parse_rows(name, text))

    summary = {
        "schema": "paper7 WGD2038 arXiv source-table payload v1",
        "purpose": (
            "Materialize official arXiv source-table values for WGD2038 Ddt/H0 "
            "constraints. This narrows what is publicly available, but does not "
            "supply the missing per-sample Fermat/posterior table."
        ),
        "external_source": {
            "arxiv": "2406.02683",
            "eprint_url": ARXIV_EPRINT_URL,
            "title": (
                "TDCOSMO. XVI. Measurement of the Hubble Constant from the "
                "Lensed Quasar WGD 2038-4008"
            ),
        },
        "materialized_files": [
            str((TABLE_DIR / name).relative_to(ROOT)) for name in TABLE_NAMES
        ],
        "row_count": len(all_rows),
        "rows": all_rows,
        "verdict": {
            "wgd2038_arxiv_source_tables_acquired": True,
            "published_ddt_h0_summary_materialized": True,
            "posterior_level_fermat_payload_acquired": False,
            "score_ready_wgd_fermat_table_acquired": False,
            "can_apply_des_frozen_score_now": False,
            "real_data_T2_sampling_authorized": False,
            "t2_specific_time_shift_evidence": False,
            "claim_level": "published_source_table_payload_not_posterior_score",
        },
        "claim_boundary": [
            "The acquired source tables are official arXiv source products for published Ddt/H0 summaries.",
            "They do not include image-wise Fermat differences, sample IDs, parity/order, or model posterior rows.",
            "They cannot by themselves authorize the DES-frozen WGD score or any real-data T2 sampling.",
        ],
        "next_finite_action": (
            "Use the source-table payload as a published summary reference, while "
            "continuing to seek the per-sample WGD Fermat/posterior payload."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    with OUT_TABLE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)

    print(json.dumps(summary["verdict"], indent=2, sort_keys=True))
    print(json.dumps({"row_count": len(all_rows), "table_dir": str(TABLE_DIR)}, indent=2))


if __name__ == "__main__":
    main()
