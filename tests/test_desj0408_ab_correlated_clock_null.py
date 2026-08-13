import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_ab_correlated_clock_null_v1/summary.json"
)


def test_correlated_clock_null_keeps_tau_claim_closed() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/calibrate_desj0408_ab_correlated_clock_null_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["scenario_count"] == 4
    assert result["total_mock_count"] == 256
    assert result["estimated_residual_amplitudes_mag"]["common_source"] > 0
    assert result["estimated_residual_amplitudes_mag"]["image_B_extrinsic"] > 0
    assert 0 < result["pooled_rate_p_value"] <= 1
    assert 0 < result["pooled_improvement_p_value"] <= 1
    assert result["tau_time_distortion_claim_allowed"] is False
