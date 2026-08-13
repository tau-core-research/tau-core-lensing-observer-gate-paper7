import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg390_clock_robustness_grid_v1/summary.json"
)


def test_blg390_robustness_grid_is_complete_and_frozen() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_ogle2004_blg390_clock_robustness_grid_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["frozen_grid"]["cell_count"] == 9
    assert len(result["cells"]) == 9
    assert {row["harmonic_order"] for row in result["cells"]} == {4, 6, 8}
    assert {row["window_half_width_tE"] for row in result["cells"]} == {
        4,
        8,
        16,
    }
