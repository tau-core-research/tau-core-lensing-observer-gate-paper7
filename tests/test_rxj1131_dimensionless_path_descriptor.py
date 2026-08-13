import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_rxj1131_dimensionless_path_descriptor_v01.py"
RESULT = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_rxj1131_dimensionless_path_descriptor_v1/summary.json"
)


def test_rxj1131_dimensionless_path_descriptor() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text())

    assert payload["vector_descriptor_materialized"] is True
    assert payload["all_components_dimensionless"] is True
    assert payload["all_values_finite"] is True
    assert len(payload["path_descriptors"]) == 4
    assert len(payload["pairwise_path_contrasts"]) == 6
    assert payload["centered_path_matrix_rank"] == 3
    assert payload["terminal_values_used"] is False
    assert payload["fitted_weights_used"] is False
    assert payload["scalar_predictor_selected"] is False
    assert payload["predictor_sign_selected"] is False
    assert payload["complete_object_level_cone_used"] is False
