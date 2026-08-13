import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_host_brightness_moment_preflight_v1/summary.json"
)


def test_desj0408_host_brightness_moment_preflight() -> None:
    result = json.loads(SUMMARY.read_text())
    assert result["negative_to_positive_ratio"] > 1.0
    assert result["direct_nonparametric_moment_authorized"] is False
    assert result["sfh_02_relative_morphology_materialized"] is False
    assert result["time_score_authorized"] is False
