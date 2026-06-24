#!/usr/bin/env python3
"""Prepare WGD2038 HST reduced_data files for the lenstronomy notebooks.

The WGD2038 notebooks expect split SCI/WHT FITS files in
``lenstronomy_modeling/data/reduced_data``.  MAST provides combined drizzled
products with SCI and WHT extensions.  This script extracts those extensions
into the expected filenames.  It does not run lens modelling.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from astropy.io import fits


ROOT = Path(__file__).resolve().parents[1]
MAST_DIR = ROOT / "data" / "external" / "hst_wgd2038_mast"
WGD_REPO = Path("/tmp/paper7_tdc_sources/WGD2038-4008")
REDUCED_DIR = WGD_REPO / "lenstronomy_modeling" / "data" / "reduced_data"
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results" / "tau_core_lensing_wgd2038_hst_reduced_data_prep_v1"
OUT_SUMMARY = RESULTS / "summary.json"


PRODUCTS = [
    {
        "source": "hst_15320_08_wfc3_ir_f160w_idgc08_drz.fits",
        "sci": "DESJ2038-4008_F160W_drz_sci.fits",
        "wht": "DESJ2038-4008_F160W_drz_wht.fits",
        "filter": "F160W",
    },
    {
        "source": "hst_15320_08_wfc3_uvis_f475x_idgc08_drc.fits",
        "sci": "DESJ2038-4008_F475X_drc_sci.fits",
        "wht": "DESJ2038-4008_F475X_drc_wht.fits",
        "filter": "F475X",
    },
    {
        "source": "hst_15320_08_wfc3_uvis_f814w_idgc08_drc.fits",
        "sci": "DESJ2038-4008_F814W_drc_sci.fits",
        "wht": "DESJ2038-4008_F814W_drc_wht.fits",
        "filter": "F814W",
    },
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_obj(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def write_extension(source: Path, extname: str, destination: Path) -> dict[str, Any]:
    structural_keys = {
        "SIMPLE",
        "BITPIX",
        "NAXIS",
        "NAXIS1",
        "NAXIS2",
        "NAXIS3",
        "PCOUNT",
        "GCOUNT",
        "XTENSION",
        "EXTEND",
        "EXTNAME",
        "EXTVER",
        "CHECKSUM",
        "DATASUM",
    }
    with fits.open(source, memmap=True) as hdul:
        hdu = hdul[extname]
        primary_header = hdul[0].header.copy()
        ext_header = hdu.header.copy()
        header = primary_header
        for key, value in ext_header.items():
            if key not in structural_keys:
                header[key] = value
        fits.PrimaryHDU(data=hdu.data, header=header).writeto(destination, overwrite=True)
    return {
        "path": str(destination),
        "exists": destination.exists(),
        "size_bytes": destination.stat().st_size if destination.exists() else None,
        "sha256": sha256_file(destination) if destination.exists() else None,
    }


def build_outputs() -> dict[str, Any]:
    REDUCED_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for product in PRODUCTS:
        source = MAST_DIR / product["source"]
        row: dict[str, Any] = {
            "filter": product["filter"],
            "source": str(source),
            "source_exists": source.exists(),
            "source_sha256": sha256_file(source) if source.exists() else None,
        }
        if source.exists():
            row["sci_output"] = write_extension(source, "SCI", REDUCED_DIR / product["sci"])
            row["wht_output"] = write_extension(source, "WHT", REDUCED_DIR / product["wht"])
        rows.append(row)
    summary: dict[str, Any] = {
        "schema": "paper7 WGD2038 HST reduced-data prep v1",
        "purpose": (
            "Prepare public MAST HST products into the split SCI/WHT filenames "
            "expected by the WGD2038 lenstronomy preprocessing notebooks."
        ),
        "mast_dir": str(MAST_DIR),
        "wgd_repo": str(WGD_REPO),
        "reduced_dir": str(REDUCED_DIR),
        "rows": rows,
        "criteria": {
            "all_mast_sources_present": all(row["source_exists"] for row in rows),
            "all_sci_wht_outputs_present": all(
                row.get("sci_output", {}).get("exists") and row.get("wht_output", {}).get("exists")
                for row in rows
            ),
            "lenstronomy_model_posterior_reproduced": False,
            "real_data_T2_sampling_authorized": False,
        },
        "claim_boundary": {
            "allowed": [
                "Public HST image inputs were acquired and converted to notebook-expected SCI/WHT filenames.",
                "This prepares the image-preprocessing stage only.",
            ],
            "forbidden": [
                "Claiming the lenstronomy posterior has been reproduced.",
                "Claiming image-wise Fermat/parity samples exist before the modelling chain is run and validated.",
            ],
        },
    }
    summary["content_hash"] = sha256_obj(summary)
    return summary


def main() -> None:
    summary = build_outputs()
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT_SUMMARY)
    print(summary["criteria"])


if __name__ == "__main__":
    main()
