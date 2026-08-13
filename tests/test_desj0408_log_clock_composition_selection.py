import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_log_clock_composition_selection_v1"
    / "summary.json"
)


def test_log_clock_selection_remains_conditional():
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_log_clock_composition_selection_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert payload["passing_candidates"] == ["logarithmic"]
    assert payload["logarithmic_shape_conditionally_selected"] is True
    assert (
        payload[
            "measured_source_trace_proved_to_obey_parent_multiplicative_composition"
        ]
        is False
    )
    assert payload["absolute_reference_scale_q_star_selected"] is False
    assert payload["physical_theta_M_identified"] is False
    assert payload["a_O_identified"] is False
    assert payload["h_tau_materialized"] is False
    assert payload["time_score_authorized"] is False
