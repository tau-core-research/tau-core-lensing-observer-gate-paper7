import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_kmt2016_blg1194_variability_ownership_v1/summary.json"
)


def test_blg1194_source_ownership_is_resolution_stable() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_kmt2016_blg1194_variability_ownership_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["total_cells"] == 12
    assert result["source_preferred_cells"] == 12
    assert result["verdict"] == (
        "SOURCE_OWNERSHIP_SUPPORTED_ACROSS_SITES_AND_SHAPE_ORDERS"
    )
