import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg081_local_clock_null_v1/summary.json"
)


def test_null_calibration_keeps_finite_source_nuisance_open() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/calibrate_ogle2004_blg081_local_clock_null_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["total_mock_light_curves"] == 256
    assert len(result["results"]) == 4
    assert result["standard_finite_source_binary_nuisance_closed"] is False
