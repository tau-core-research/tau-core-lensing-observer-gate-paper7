import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg390_finite_tangent_clock_null_v1/"
    "summary.json"
)


def test_blg390_calibration_preserves_source_ownership_blocker() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/calibrate_ogle2004_blg390_finite_tangent_clock_null_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["total_mock_light_curves"] == 128
    assert result["source_variability_ownership_proved"] is False
    assert len(result["families"]) == 2
