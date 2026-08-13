import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle_replacement_same_source_clock_candidates_v1/"
    "summary.json"
)


def test_replacement_events_use_frozen_local_identifiability_rule() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_ogle_replacement_same_source_clock_candidates_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert len(result["events"]) == 2
    assert "2004-BLG-101" in result["excluded_before_fit"]
    assert all(
        isinstance(row["passes_local_clock_identifiability_precheck"], bool)
        for row in result["events"]
    )
