import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle_periodic_microlensing_clock_support_v1/summary.json"
)


def test_public_periodic_microlensing_support_is_source_frozen() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_ogle_periodic_microlensing_clock_support_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert len(result["events"]) == 8
    assert result["clock_rate_test_executed"] is False
    assert result["preferred_event"] in result["ready_events"]
    assert all(
        len(row["archive_sha256"]) == 64 for row in result["events"]
    )
