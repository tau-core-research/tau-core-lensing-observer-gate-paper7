import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_log_area_path_contrast_v1"
    / "summary.json"
)


def test_log_area_path_contrast_is_standard_magnification_only():
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_log_area_path_contrast_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert payload["model_count"] == 12
    assert payload["maximum_path_contrast_identity_error"] < 1e-12
    assert payload["exact_reduction_to_standard_log_magnification_ratio"] is True
    assert payload["source_area_and_reference_scale_cancel_from_path_contrast"] is True
    assert payload["tau_specific_path_information_materialized"] is False
    assert payload["local_endpoint_log_area_clock_branch_closed"] is True
    assert payload["full_causal_support_clock_still_open"] is True
    assert payload["h_tau_materialized"] is False
    assert payload["time_score_authorized"] is False
