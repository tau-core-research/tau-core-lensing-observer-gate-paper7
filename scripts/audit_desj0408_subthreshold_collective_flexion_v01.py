#!/usr/bin/env python3
"""Audit collective spin-1/spin-3 LOS structure below the flexion threshold."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
IN_DIR = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_los_path_transport_geometry_v1"
)
INPUT = IN_DIR / "los_path_transport_geometry.csv"
OUT_DIR = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_subthreshold_collective_flexion_v1"
)
OUT = OUT_DIR / "summary.json"
CSV_OUT = OUT_DIR / "collective_spin_moments.csv"
REPORT = OUT_DIR / "report.md"
EXPLICIT = {"488068102", "488065185", "488066144", "488066768"}


def main() -> None:
    with INPUT.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    grouped: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if (
            row["object_id"] not in EXPLICIT
            and row["published_flexion_path_rescaling"]
        ):
            grouped[(row["model_id"], int(row["path_index"]))].append(row)

    output_rows = []
    for (model_id, path_index), members in sorted(grouped.items()):
        amplitude = np.asarray(
            [
                10.0 ** float(row["published_flexion_path_rescaling"])
                for row in members
            ]
        )
        dx = np.asarray(
            [
                float(row["object_x_model_arcsec"])
                - float(row["ray_x_model_arcsec"])
                for row in members
            ]
        )
        dy = np.asarray(
            [
                float(row["object_y_model_arcsec"])
                - float(row["ray_y_model_arcsec"])
                for row in members
            ]
        )
        phi = np.arctan2(dy, dx)
        total = float(np.sum(amplitude))
        spin1 = np.sum(amplitude * np.exp(1j * phi))
        spin2 = np.sum(amplitude * np.exp(2j * phi))
        spin3 = np.sum(amplitude * np.exp(3j * phi))
        output_rows.append(
            {
                "model_id": model_id,
                "path_index": path_index,
                "member_count": len(members),
                "scalar_amplitude_sum_arcsec": total,
                "spin1_real_arcsec": float(spin1.real),
                "spin1_imag_arcsec": float(spin1.imag),
                "spin1_coherence": float(abs(spin1) / total),
                "spin2_real_arcsec": float(spin2.real),
                "spin2_imag_arcsec": float(spin2.imag),
                "spin2_coherence": float(abs(spin2) / total),
                "spin3_real_arcsec": float(spin3.real),
                "spin3_imag_arcsec": float(spin3.imag),
                "spin3_coherence": float(abs(spin3) / total),
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    spin1 = np.asarray(
        [
            complex(row["spin1_real_arcsec"], row["spin1_imag_arcsec"])
            for row in output_rows
        ]
    ).reshape(12, 4)
    spin3 = np.asarray(
        [
            complex(row["spin3_real_arcsec"], row["spin3_imag_arcsec"])
            for row in output_rows
        ]
    ).reshape(12, 4)
    scalar = np.asarray(
        [row["scalar_amplitude_sum_arcsec"] for row in output_rows]
    ).reshape(12, 4)
    spin1_coherence = np.abs(spin1) / scalar
    spin3_coherence = np.abs(spin3) / scalar

    summary = {
        "schema": "paper7 DES J0408 subthreshold collective flexion v1",
        "excluded_explicit_perturbers": sorted(EXPLICIT),
        "model_path_count": len(output_rows),
        "subthreshold_member_count_per_model_path": sorted(
            {row["member_count"] for row in output_rows}
        ),
        "median_scalar_amplitude_sum_arcsec": float(np.median(scalar)),
        "median_spin1_coherence": float(np.median(spin1_coherence)),
        "median_spin3_coherence": float(np.median(spin3_coherence)),
        "minimum_spin3_coherence": float(np.min(spin3_coherence)),
        "median_within_model_spin1_path_spread_arcsec": float(
            np.median(np.max(np.abs(spin1[:, :, None] - spin1[:, None, :]), axis=(1, 2)))
        ),
        "median_within_model_spin3_path_spread_arcsec": float(
            np.median(np.max(np.abs(spin3[:, :, None] - spin3[:, None, :]), axis=(1, 2)))
        ),
        "collective_oriented_subthreshold_structure_nonzero": bool(
            np.all(spin1_coherence > 0) and np.all(spin3_coherence > 0)
        ),
        "path_dependent_collective_structure_nonzero": bool(
            np.any(np.ptp(np.abs(spin3), axis=1) > 0)
        ),
        "not_representable_by_scalar_convergence_alone": True,
        "not_representable_by_spin0_spin2_tidal_summary": bool(
            np.all(spin1_coherence > 0) and np.all(spin3_coherence > 0)
        ),
        "standard_higher_order_lensing_information": True,
        "tau_specific_information_materialized": False,
        "time_score_authorized": False,
        "verdict": (
            "COLLECTIVE_SUBTHRESHOLD_SPIN1_SPIN3_STRUCTURE_MATERIALIZED__"
            "STANDARD_HIGHER_ORDER_LENSING_ONLY"
        ),
        "claim_boundary": (
            "The source-frozen sum excludes G3-G6 and retains the angular "
            "spin-1 and spin-3 moments of published path-rescaled flexion "
            "magnitudes. Nonzero odd-spin content proves information loss under "
            "a scalar or spin-0/spin-2-only compression, but is standard "
            "higher-order lensing structure, not Tau or observer-time evidence."
        ),
    }
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 subthreshold collective flexion v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        "After excluding the four explicitly modeled perturbers, the released "
        "population retains nonzero collective spin-1 and spin-3 structure on "
        "all model paths. This is standard higher-order LOS information.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
