#!/usr/bin/env python3
"""Assign RXJ1131 its admissible post-no-go development role."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/external/rxj1131_nirspec_2026_source_manifest.json"
RESULTS = ROOT / "data/derived/repro_results"
OUT_DIR = RESULTS / "tau_core_lensing_rxj1131_relational_cone_development_role_v1"


def main() -> None:
    source = json.loads(MANIFEST.read_text())
    route = json.loads(
        (
            RESULTS
            / "tau_core_lensing_relational_cone_cross_terminal_route_v1"
            / "summary.json"
        ).read_text()
    )
    ratios = source["terminal"]["ratios"]
    result = {
        "schema": "Paper 7 RXJ1131 relational-cone development-role audit v1",
        "target": source["target"],
        "source_manifest": str(MANIFEST.relative_to(ROOT)),
        "new_information_since_prior_paper7_probe": [
            "public JWST NIRSpec raw data from GO-1794",
            "published nuclear narrow-line flux-ratio terminal",
            "public lensqso-specfit spectral-modeling code",
        ],
        "terminal_coordinate_count": len(ratios),
        "terminal_is_non_clock": True,
        "terminal_is_path_sensitive_amplitude": True,
        "terminal_measurement_uses_same_cube_lens_model": True,
        "terminal_values_opened_before_tau_predictor_freeze": True,
        "historical_hst_lens_and_environment_inputs_predate_terminal": True,
        "complete_physical_causal_support_available": False,
        "full_terminal_covariance_materialized": False,
        "standard_substructure_completion_required": True,
        "development_use_allowed": True,
        "confirmatory_blind_use_allowed": False,
        "forbidden_operations": [
            "choose predictor sign from the published SIII residual",
            "fit cone weights to the published SIII ratios",
            "call the smooth-model anomaly a Tau excess",
            "reopen observer time on RXJ1131 alone",
        ],
        "allowed_construction": (
            "Build one predictor using only pre-2026 HST lens, astrometry, "
            "redshift, and environment products; treat the published SIII "
            "vector only as a development endpoint after the complete formula, "
            "sign, nuisance projection, and covariance policy are frozen."
        ),
        "required_external_validation": (
            "Apply the unchanged predictor to a second lens whose non-clock "
            "terminal remains sealed during predictor construction."
        ),
        "upstream_route_verdict": route["verdict"],
        "verdict": (
            "RXJ1131_SELECTED_AS_DEVELOPMENT_TARGET_NOT_BLIND_VALIDATION"
        ),
        "claim_boundary": (
            "The new source materially improves endpoint availability. It "
            "does not repair complete-cone incompleteness or retrospective "
            "terminal opening and therefore cannot confirm Tau Core."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])


if __name__ == "__main__":
    main()
