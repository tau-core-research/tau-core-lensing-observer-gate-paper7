#!/usr/bin/env python3
"""Freeze the finite public-data frontier for a same-source clock replacement."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_same_source_clock_replacement_data_frontier_v1"
)

CRITERIA = {
    "source_clock_ownership": (
        "The periodic clock must be assigned to the magnified source rather "
        "than an unresolved blend."
    ),
    "pointwise_public_photometry": (
        "Epoch, flux or magnitude, and uncertainty must be publicly reusable."
    ),
    "lensed_and_control_phase_coverage": (
        "The same clock must be sampled both under appreciable magnification "
        "and in an outer baseline interval."
    ),
    "standard_shape_conditioning": (
        "Finite-source, chromatic, and source-shape changes must be separable "
        "from a phase-rate coefficient."
    ),
}

CANDIDATES = [
    {
        "candidate": "OGLE periodic-variable EWS sample (2001-2004)",
        "source_clock_ownership": "partial",
        "pointwise_public_photometry": True,
        "lensed_and_control_phase_coverage": True,
        "standard_shape_conditioning": True,
        "paper7_status": (
            "EXHAUSTED: BLG-081 and BLG-103 are conditional clock nulls; "
            "BLG-390 fails source ownership and sign robustness."
        ),
        "executable_replacement": False,
        "references": [
            "https://acta.astrouw.edu.pl/Vol56/n2/pap_56_2_1.pdf",
            "https://www.astrouw.edu.pl/ogle/ogle3/ews/ews.html",
        ],
    },
    {
        "candidate": "MACHO-97-SMC-1 / EROS2-SMC-1",
        "source_clock_ownership": "historically_modelled_but_contested",
        "pointwise_public_photometry": False,
        "lensed_and_control_phase_coverage": "multi-survey_but_not_one_frozen_payload",
        "standard_shape_conditioning": False,
        "paper7_status": (
            "REJECTED: later OGLE review reports strong blending, possible "
            "artefactual MACHO variability, and only a fading event segment "
            "in OGLE-II. It would reopen the ownership problem."
        ),
        "executable_replacement": False,
        "references": [
            "https://arxiv.org/abs/astro-ph/0604147",
            "https://academic.oup.com/mnras/article/407/1/189/984572",
        ],
    },
    {
        "candidate": "Published pulsating-source microlensing simulations",
        "source_clock_ownership": "defined_in_simulation",
        "pointwise_public_photometry": "synthetic_only",
        "lensed_and_control_phase_coverage": True,
        "standard_shape_conditioning": "physics_requirement_available",
        "paper7_status": (
            "METHOD CONTROL ONLY: the literature proves that finite-source, "
            "temperature, radius, color, and centroid changes can mimic "
            "phase-local structure, but supplies no observed replacement event."
        ),
        "executable_replacement": False,
        "references": [
            "https://arxiv.org/abs/2003.10318",
            "https://arxiv.org/abs/2008.04171",
            "https://arxiv.org/abs/2108.08650",
        ],
    },
    {
        "candidate": "Generic KMTNet/UKIRT/VVV public survey archives",
        "source_clock_ownership": "not_preidentified",
        "pointwise_public_photometry": True,
        "lensed_and_control_phase_coverage": "must_be_crossmatched",
        "standard_shape_conditioning": "event_dependent",
        "paper7_status": (
            "DISCOVERY CORPUS, NOT A CANDIDATE: a new residual-blind catalog "
            "crossmatch would be required before any event-level clock fit."
        ),
        "executable_replacement": False,
        "references": [
            "https://www.microlensing-source.org/public-data/",
        ],
    },
]


def main() -> None:
    executable = [
        row["candidate"] for row in CANDIDATES if row["executable_replacement"]
    ]
    result = {
        "schema": "Paper 7 same-source clock replacement data frontier v1",
        "question": (
            "Does the currently identified public literature contain a clean "
            "replacement event for the frozen same-source clock protocol?"
        ),
        "frozen_eligibility_criteria": CRITERIA,
        "candidates": CANDIDATES,
        "executable_replacements": executable,
        "verdict": (
            "PUBLIC_REPLACEMENT_EVENT_READY"
            if executable
            else "NO_CURRENTLY_IDENTIFIED_PUBLIC_REPLACEMENT_EVENT"
        ),
        "stop_rule": (
            "Do not refit the exhausted OGLE events or relax source ownership. "
            "Reopen the empirical branch only when one named event satisfies "
            "all four frozen criteria."
        ),
        "next_finite_action": (
            "Run one residual-blind catalog crossmatch between public "
            "microlensing events and independently classified periodic-source "
            "catalogs; acquire pointwise photometry only for matches that pass "
            "ownership and phase-coverage checks."
        ),
        "claim_boundary": (
            "This is a finite data-frontier verdict, not evidence against an "
            "observer-dependent common clock and not evidence for Tau Core."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(result["verdict"])
    print("executable_replacements:", executable or "none")


if __name__ == "__main__":
    main()
