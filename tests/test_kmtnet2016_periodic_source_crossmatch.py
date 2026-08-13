import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_kmtnet2016_periodic_source_crossmatch_v1/summary.json"
)


def test_kmtnet_crossmatch_is_residual_blind_and_finite() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/crossmatch_kmtnet2016_periodic_source_clock_candidates_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["selection"]["residual_or_clock_fit_used_for_selection"] is False
    assert len(result["matches"]) == 3
    assert result["preferred_event"] == "KMT-2016-BLG-1194"
    preferred = next(
        row for row in result["matches"] if row["event"] == result["preferred_event"]
    )
    assert preferred["coverage_ready"] is True
    assert preferred["clock_preflight_ready"] is True
