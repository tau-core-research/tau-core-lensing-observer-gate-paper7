import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_blind_cross_terminal_identifiability_theorem_v1/"
    "summary.json"
)


def test_exact_adaptive_fit_and_frozen_novelty_condition() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_blind_cross_terminal_identifiability_theorem_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    witness = result["exact_counterexample"]
    assert witness["design_rank"] == witness["output_dimension"]
    assert witness["maximum_interpolation_error"] < 1e-12
    assert result["frozen_predictor_check"]["novel_direction_exists"]
    assert result["not_proved"]
    assert result["verdict"] == (
        "BLIND_CROSS_TERMINAL_PROTOCOL_IS_MATHEMATICALLY_NECESSARY"
    )
