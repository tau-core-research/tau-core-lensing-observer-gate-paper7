import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_ab_relative_clock_rate_v1/summary.json"
)


def test_desj0408_ab_relative_clock_rate_is_not_overpromoted() -> None:
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_ab_relative_clock_rate_v01.py"],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["data_scope"]["epoch_count"] == 96
    assert result["central_exploratory_fit"]["relative_clock_rate_B_over_A"] > 1
    assert result["central_exploratory_fit"][
        "delta_chi_square_one_extra_parameter"
    ] > 3.84
    assert result["relative_clock_rate_range"][0] <= 0.901
    assert result["relative_clock_rate_range"][1] >= 1.099
    assert result["path_dependent_clock_rate_stable"] is False
    assert result["tau_time_distortion_claim_allowed"] is False
