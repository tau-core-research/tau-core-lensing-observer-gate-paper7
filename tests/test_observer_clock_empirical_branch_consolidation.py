import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_observer_clock_empirical_branch_consolidation_v1/"
    "summary.json"
)


def test_clock_consolidation_preserves_narrow_claim_boundary() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_observer_clock_empirical_branch_consolidation_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["independent_measurement_geometries"] == 2
    assert result["test_targets"] == 6
    assert result["positive_robust_targets"] == []
    assert result["not_excluded"]
    assert result["verdict"] == "SIMPLE_SCALAR_OBSERVER_CLOCK_BRANCH_NOT_SUPPORTED"
