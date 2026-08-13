import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_rxj1131_pre2026_predictor_source_packet_v1/"
    "summary.json"
)


def test_source_packet_is_geometric_and_terminal_free() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/freeze_rxj1131_pre2026_predictor_source_packet_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["image_labels"] == ["A", "B", "C", "D"]
    assert len(result["pairwise_image_separations_arcsec"]) == 6
    assert result["coordinate_free_geometry_materialized"]
    assert result["forbidden_terminal_value_tokens_found"] == []
    assert not result["complete_physical_causal_support_materialized"]
    assert not result["predictor_formula_selected"]
    assert result["next_finite_action"]
