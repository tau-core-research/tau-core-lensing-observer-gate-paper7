import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_scalar_body_path_coupling_v1"
    / "summary.json"
)


def test_scalar_body_path_coupling_is_factorized_control():
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_scalar_body_path_coupling_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert payload["exact_scalar_body_path_factorization"] is True
    assert payload["partial_single_body_scalar_descriptor_materialized"] is True
    assert payload["source_information_survives_normalized_path_contrast"] is False
    assert payload["independent_body_path_interaction_materialized"] is False
    assert payload["sfh_02_relative_morphology_materialized"] is False
    assert payload["sfh_03_body_conditioned_path_pullback_materialized"] is False
    assert payload["h_tau_materialized"] is False
    assert payload["time_score_authorized"] is False
    assert len(payload["rows"]) == 4
    assert payload["maximum_factorization_error"] < 1e-12
