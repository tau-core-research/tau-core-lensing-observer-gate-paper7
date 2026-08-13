import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_image_path_pullbacks_v1/summary.json"
)


def test_desj0408_image_path_pullbacks() -> None:
    result = json.loads(SUMMARY.read_text())
    assert result["path_count"] == 4
    assert result["parity_counts"] == {"positive": 2, "negative": 2}
    assert result["local_lens_transport_materialized"] is True
    assert result["sfh_03_path_pullback_materialized"] is False
    assert result["a_O_identified"] is False
    assert result["time_score_authorized"] is False
