import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_he0435_bc_relative_clock_rate_v1/summary.json"
)


def test_he0435_transfer_uses_official_unit_stretch_mocks() -> None:
    subprocess.run(
        [sys.executable, "scripts/transfer_he0435_bc_relative_clock_rate_v01.py"],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["image_pair"] == "B/C"
    assert result["epoch_count"] == 884
    assert result["official_unit_stretch_mock_count"] == 128
    assert 0.9 <= result["observed_fit"]["relative_clock_rate_C_over_B"] <= 1.1
    assert 0 < result["official_mock_null"][
        "empirical_two_sided_rate_p_value"
    ] <= 1
    assert result["tau_time_distortion_claim_allowed"] is False
