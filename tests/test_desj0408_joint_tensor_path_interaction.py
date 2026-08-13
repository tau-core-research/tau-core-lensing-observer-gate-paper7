import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_joint_tensor_path_interaction_v1"
    / "summary.json"
)


def test_joint_tensor_path_interaction_keeps_time_claim_blocked():
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_joint_tensor_path_interaction_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert payload["model_count"] == 5
    assert payload["path_count"] == 4
    assert payload["all_joint_transports_finite"] is True
    assert payload["maximum_decomposition_error"] < 1e-12
    assert payload["parity_morse_only_explanation_excluded_on_target"] is True
    assert payload["same_parity_morse_class_opposite_sign_paths"] == [[2, 3]]
    assert payload["amplitude_stable_tensor_path_interaction_materialized"] is False
    assert payload["sfh_02_relative_morphology_materialized"] is False
    assert payload["sfh_03_body_conditioned_path_pullback_materialized"] is False
    assert payload["h_tau_materialized"] is False
    assert payload["time_score_authorized"] is False
