import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_single_body_host_descriptor_v1/summary.json"
)


def test_desj0408_single_body_host_descriptor() -> None:
    result = json.loads(SUMMARY.read_text())
    assert result["eligible_model_count"] == 12
    assert result["single_body_host_descriptor_promoted"] is False
    assert result["sfh_02_relative_morphology_materialized"] is False
    assert result["time_score_authorized"] is False
