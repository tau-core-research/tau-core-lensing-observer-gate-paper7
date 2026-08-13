import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_kappa_marginalized_delay_rank_v1"
    / "summary.json"
)


def test_kappa_marginalized_delay_rank():
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_desj0408_kappa_marginalized_delay_rank_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert payload["delay_output_dimension"] == 2
    assert payload["rank_dominant_model_plus_kappa"] == 2
    assert payload["remaining_dimension_after_dominant_model_plus_kappa"] == 0
    assert payload["practical_5pct_weak_direction_survives_geometrically"] is True
    assert payload["practical_weak_direction_is_kappa_free"] is False
    assert payload["delay_only_tau_score_authorized"] is False
    assert payload["tau_specific_information_materialized"] is False
