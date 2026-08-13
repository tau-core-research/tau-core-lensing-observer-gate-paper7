#!/usr/bin/env python3
"""Decide whether current DES J0408 objects form one source-frozen body."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_body_ownership_v1"


def load(name: str) -> dict:
    return json.loads((RESULTS / name / "summary.json").read_text())


def main() -> None:
    triangle = load("tau_core_lensing_desj0408_source_morphology_triangle_v1")
    host = load("tau_core_lensing_desj0408_single_body_host_descriptor_v1")
    moment = load("tau_core_lensing_desj0408_positive_host_moment_v1")
    pullback = load("tau_core_lensing_desj0408_image_path_pullbacks_v1")

    source_count = len(triangle["component_roles"])
    plane_count = len(set(triangle["source_component_redshifts"]))
    triangle_has_common_owner = source_count == 1 and plane_count == 1
    host_vector_stable = bool(host["single_body_host_descriptor_promoted"])
    scalar_only = (
        bool(moment["stable_scalar_trace_materialized"])
        and not bool(moment["positive_common_host_moment_promoted"])
    )
    paths_are_body_coordinates = False
    complete_descriptor = (
        triangle_has_common_owner and host_vector_stable and not scalar_only
    )

    result = {
        "schema": "paper7 DES J0408 body ownership audit v1",
        "target": triangle["target"],
        "ontology_rule": (
            "A single-body descriptor must be intrinsic to one source owner "
            "on one source support and frozen before observer-path transport. "
            "Multiple lensed paths are downstream readouts of that body and "
            "cannot be counted as additional body coordinates."
        ),
        "audited_objects": {
            "multisource_triangle": {
                "source_component_count": source_count,
                "source_plane_count": plane_count,
                "common_body_owner": triangle_has_common_owner,
                "role": "observer_field_geometry_calibrator",
            },
            "parametric_quasar_host": {
                "single_source_owner": True,
                "full_vector_model_stable": host_vector_stable,
                "role": "unpromoted_intrinsic_body_candidate",
            },
            "positive_host_moment": {
                "single_source_owner": True,
                "stable_scalar_only": scalar_only,
                "full_tensor_model_stable": bool(
                    moment["positive_common_host_moment_promoted"]
                ),
                "role": "partial_intrinsic_body_descriptor",
            },
            "four_image_path_pullbacks": {
                "path_count": pullback["path_count"],
                "body_coordinates": paths_are_body_coordinates,
                "role": "downstream_standard_lens_transport",
            },
        },
        "single_source_frozen_body_descriptor_materialized": complete_descriptor,
        "sfh_02_relative_morphology_materialized": complete_descriptor,
        "sfh_03_body_conditioned_path_pullback_materialized": (
            complete_descriptor
            and bool(pullback["sfh_03_path_pullback_materialized"])
        ),
        "forbidden_repairs": [
            "merge different source redshift planes into one body",
            "count multiple lensed images as independent body coordinates",
            "select one preferred unstable host model",
            "promote a stable scalar into an unmeasured morphology vector",
        ],
        "minimal_resolving_input": (
            "One uncertainty-propagated, same-source-plane intrinsic source "
            "reconstruction with at least three stable relative morphology "
            "coordinates; only after that freeze may the four path pullbacks "
            "act on the descriptor."
        ),
        "time_score_authorized": False,
        "verdict": (
            "DESJ0408_SINGLE_BODY_DESCRIPTOR_MATERIALIZED"
            if complete_descriptor
            else "DESJ0408_CURRENT_OBJECTS_CANNOT_FORM_ONE_BODY_DESCRIPTOR"
        ),
        "claim_boundary": (
            "Finite ownership/no-go audit of the current public DES J0408 "
            "objects. It does not prove that no single-body descriptor exists; "
            "it forbids constructing one by combining current multisource or "
            "downstream path objects."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    (OUT_DIR / "report.md").write_text(
        "# DES J0408 body-ownership audit v1\n\n"
        f"Verdict: `{result['verdict']}`\n\n"
        "The public triangle contains three modeled sources on two source "
        "planes. The same-plane quasar-host vector is model-family unstable; "
        "only one scalar positive moment is stable. The four image paths are "
        "downstream lens transports, not four additional body coordinates.\n\n"
        "Therefore the current objects cannot be merged into one source-frozen "
        "`SFH_02` descriptor without reversing the body-to-readout direction.\n",
        encoding="utf-8",
    )
    print(result["verdict"])


if __name__ == "__main__":
    main()
