import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_ab_relative_clock_rate_null_calibration_v1/"
    "summary.json"
)


def test_relative_clock_rate_null_calibration_is_conditional() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/calibrate_desj0408_ab_relative_clock_rate_null_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["mock_count"] == 128
    assert result["null_hypothesis"] == "relative_clock_rate_B_over_A=1"
    assert 0 < result["empirical_two_sided_rate_p_value"] <= 1
    assert 0 < result["empirical_improvement_p_value"] <= 1
    assert result["tau_time_distortion_claim_allowed"] is False
    assert "misspecification" in result["claim_boundary"]
