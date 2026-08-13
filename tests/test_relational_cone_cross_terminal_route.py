import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_relational_cone_cross_terminal_route_v1/summary.json"
)


def test_route_audit_blocks_residual_selected_clock_reopening() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_relational_cone_cross_terminal_route_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["admissible_routes"] == []
    assert result["selected_terminal_class"]
    assert len(result["routes"]) == 2
    assert all(
        not route["route_admissible_for_time_reopening"]
        for route in result["routes"]
    )
    assert result["verdict"] == (
        "NO_CURRENT_ROUTE_SATISFIES_COMPLETE_CONE_AND_BLIND_NONCLOCK_TEST"
    )
