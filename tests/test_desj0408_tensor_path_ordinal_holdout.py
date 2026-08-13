import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_tensor_path_ordinal_holdout_v1"
    / "summary.json"
)


def test_tensor_path_ordinal_holdout_preserves_claim_boundary():
    subprocess.run(
        [sys.executable, "scripts/validate_desj0408_tensor_path_ordinal_holdout_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert payload["holdout_model_count"] == 7
    assert payload["all_holdout_positive_solvers_valid"] is True
    assert payload["independent_target_replication"] is False
    assert payload["sfh_02_relative_morphology_materialized"] is False
    assert payload["sfh_03_body_conditioned_path_pullback_materialized"] is False
    assert payload["h_tau_materialized"] is False
    assert payload["time_score_authorized"] is False
