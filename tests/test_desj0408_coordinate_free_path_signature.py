import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_coordinate_free_path_signature_v1"
    / "summary.json"
)


def test_coordinate_free_signature_is_standard_control_only():
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_coordinate_free_path_signature_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert payload["model_count"] == 12
    assert payload["negative_parity_sign_split_count"] == 12
    assert payload["label_permutation_invariant_signature_materialized"] is True
    assert payload["coordinate_free_morphology_path_control_materialized"] is True
    assert (
        payload["tau_specific_information_beyond_standard_lensing_materialized"]
        is False
    )
    assert payload["independent_target_replication"] is False
    assert payload["h_tau_materialized"] is False
    assert payload["time_score_authorized"] is False
