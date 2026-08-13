import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_local_cubic_astrometric_endpoint_v1"
    / "summary.json"
)


def test_local_cubic_astrometric_endpoint():
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_local_cubic_astrometric_endpoint_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT.read_text(encoding="utf-8"))
    assert payload["public_positions_are_model_fitted_not_independent_holdout"] is True
    assert payload["independent_sub_mas_astrometric_covariance_materialized"] is False
    assert payload["direct_astrometric_endpoint_authorized"] is False
    assert payload["extended_arc_endpoint_preferred"] is True
    assert payload["tau_specific_information_materialized"] is False
    assert payload["time_score_authorized"] is False
