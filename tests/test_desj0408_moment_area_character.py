import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_moment_area_character_v1"
    / "summary.json"
)


def test_moment_area_character_is_natural_but_not_parent_identified():
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_moment_area_character_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert payload["model_count"] == 12
    assert payload["moment_area_positive_character_materialized"] is True
    assert payload["sequential_deformation_character_error"] < 1e-12
    assert payload["area_character_stable_on_expanded_model_family"] is False
    assert payload["trace_stable_on_expanded_model_family"] is False
    assert (
        payload["trace_not_multiplicative_under_natural_additive_moment_composition"]
        is True
    )
    assert payload["parent_common_load_identified_with_moment_area_character"] is False
    assert payload["absolute_reference_area_selected"] is False
    assert payload["physical_theta_M_identified"] is False
    assert payload["h_tau_materialized"] is False
    assert payload["time_score_authorized"] is False
