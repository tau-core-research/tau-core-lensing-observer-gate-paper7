import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_unlensed_control_support_v1/summary.json"
)


def test_strict_unlensed_control_is_not_widened_post_hoc() -> None:
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_unlensed_control_support_v01.py"],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    counts = [
        row["matched_control_count"] for row in result["matching_results"]
    ]
    assert counts == [2, 6, 40]
    assert result["strict_pair_matching_ready"] is False
    assert result["broad_window_authorized_for_detection"] is False
    assert result["common_mode_clock_test_executed"] is False
    assert result[
        "differential_image_clock_null_reinterpreted_as_control_only"
    ] is True
