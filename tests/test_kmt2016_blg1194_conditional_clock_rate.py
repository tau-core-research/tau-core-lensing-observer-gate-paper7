import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_kmt2016_blg1194_conditional_clock_rate_v1/summary.json"
)


def test_blg1194_clock_scan_includes_exact_null() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_kmt2016_blg1194_conditional_clock_rate_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["epsilon_grid"]["points"] == 401
    assert result["epsilon_grid"]["minimum"] < 0
    assert result["epsilon_grid"]["maximum"] > 0
    assert result["data_points_after_quality_filter"] > 2000
    assert result["verdict"] in {
        "KMT1194_LOCAL_CLOCK_CANDIDATE",
        "KMT1194_CONDITIONAL_CLOCK_NULL",
    }
