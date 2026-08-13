import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg081_local_clock_rate_v1/summary.json"
)


def test_clock_rate_fit_remains_diagnostic_before_null_calibration() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_ogle2004_blg081_local_clock_rate_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["clock_rate_test_executed"] is True
    assert result["null_calibration_executed"] is False
    assert len(result["fits"]) == 4
    assert result["verdict"] == "CENTRAL_DIAGNOSTIC_ONLY__NULL_CALIBRATION_REQUIRED"
