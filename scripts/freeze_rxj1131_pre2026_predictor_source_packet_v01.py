#!/usr/bin/env python3
"""Freeze coordinate-free RXJ1131 predictor-side data without terminal leakage."""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/external/rxj1131_pre2026_predictor_source_manifest.json"
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_rxj1131_pre2026_predictor_source_packet_v1"
)


def main() -> None:
    source = json.loads(MANIFEST.read_text())
    astrometry = source["relative_astrometry_arcsec_from_image_A"]
    image_labels = ["A", "B", "C", "D"]
    lens = astrometry["G"]

    lens_centered = {}
    for label in image_labels:
        point = astrometry[label]
        dx = point["dra_cosdec"] - lens["dra_cosdec"]
        dy = point["ddec"] - lens["ddec"]
        lens_centered[label] = {
            "dx_arcsec": dx,
            "dy_arcsec": dy,
            "radius_arcsec": math.hypot(dx, dy),
            "polar_angle_rad": math.atan2(dy, dx),
        }

    pairwise = {}
    for left, right in itertools.combinations(image_labels, 2):
        dx = astrometry[left]["dra_cosdec"] - astrometry[right]["dra_cosdec"]
        dy = astrometry[left]["ddec"] - astrometry[right]["ddec"]
        pairwise[f"{left}_{right}"] = math.hypot(dx, dy)

    satellite = astrometry["S_or_X"]
    satellite_dx = satellite["dra_cosdec"] - lens["dra_cosdec"]
    satellite_dy = satellite["ddec"] - lens["ddec"]
    forbidden_tokens = (
        "b_over_a",
        "c_over_a",
        "d_over_a",
        "9071",
        "9533",
        "terminal_value",
    )
    serialized_source = json.dumps(source).lower()
    leakage_tokens = [
        token for token in forbidden_tokens if token in serialized_source
    ]

    result = {
        "schema": "Paper 7 RXJ1131 pre-2026 predictor-source packet v1",
        "target": source["target"],
        "source_manifest": str(MANIFEST.relative_to(ROOT)),
        "source_arxiv_ids": [
            row["arxiv_id"] for row in source["sources"]
        ],
        "image_labels": image_labels,
        "lens_centered_image_geometry": lens_centered,
        "pairwise_image_separations_arcsec": pairwise,
        "satellite_relation": {
            "dx_from_lens_arcsec": satellite_dx,
            "dy_from_lens_arcsec": satellite_dy,
            "separation_from_lens_arcsec": math.hypot(
                satellite_dx, satellite_dy
            ),
            "einstein_radius_arcsec": source["blind_hst_lens_model_summary"][
                "satellite_einstein_radius_arcsec"
            ],
        },
        "body_and_environment_inputs": {
            "lens_model": source["blind_hst_lens_model_summary"],
            "line_of_sight": source["line_of_sight_summary"],
            "redshifts": source["redshifts"],
        },
        "terminal_embargo_present": bool(source["terminal_embargo"]),
        "forbidden_terminal_value_tokens_found": leakage_tokens,
        "coordinate_free_geometry_materialized": (
            len(pairwise) == 6
            and min(pairwise.values()) > 0
            and len({round(value, 8) for value in pairwise.values()}) > 1
        ),
        "complete_physical_causal_support_materialized": False,
        "predictor_formula_selected": False,
        "verdict": (
            "RXJ1131_PRE2026_SOURCE_PACKET_MATERIALIZED__OBJECT_LEVEL_CONE_INCOMPLETE"
        ),
        "next_finite_action": (
            "Construct one dimensionless path-relational descriptor from the "
            "lens-centered image geometry, satellite relation, shear/gradient "
            "axes, and LOS summaries without opening any terminal residual."
        ),
        "claim_boundary": (
            "This packet freezes predictor-side observables and invariants. "
            "It is not a full cone, a Tau law, a fitted flux predictor, or "
            "observer-time evidence."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("pairwise coordinates:", len(pairwise))


if __name__ == "__main__":
    main()
