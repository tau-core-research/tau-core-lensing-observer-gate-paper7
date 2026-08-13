import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_source_morphology_triangle_v1/summary.json"
)


def test_desj0408_source_morphology_triangle() -> None:
    result = json.loads(SUMMARY.read_text())
    assert result["target"] == "DES J0408-5354"
    assert result["eligible_model_count"] == 12
    assert result["single_source_plane"] is False
    assert result["observer_field_geometry_calibrator_materialized"] is True
    assert result["sfh_02_relative_morphology_materialized"] is False
    assert result["path_pullback_identified"] is False
    assert result["time_score_authorized"] is False
