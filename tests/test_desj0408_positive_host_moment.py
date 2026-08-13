import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_positive_host_moment_v1/summary.json"
)


def test_desj0408_positive_host_moment() -> None:
    result = json.loads(SUMMARY.read_text())
    assert result["model_count"] == 5
    assert result["stable_scalar_trace_materialized"] is True
    assert result["positive_common_host_moment_promoted"] is False
    assert result["theta_M_identified"] is False
    assert result["time_score_authorized"] is False
