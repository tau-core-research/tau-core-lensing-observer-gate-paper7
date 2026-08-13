import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_same_source_clock_replacement_data_frontier_v1/"
    "summary.json"
)


def test_replacement_frontier_has_a_finite_stop_verdict() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_same_source_clock_replacement_data_frontier_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert len(result["frozen_eligibility_criteria"]) == 4
    assert result["executable_replacements"] == []
    assert result["verdict"] == "NO_CURRENTLY_IDENTIFIED_PUBLIC_REPLACEMENT_EVENT"
    assert "Do not refit" in result["stop_rule"]
