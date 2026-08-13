import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_scalar_clock_nonidentifiability_v1"
    / "summary.json"
)


def test_scalar_clock_counterfamily_blocks_theta_identification():
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_scalar_clock_nonidentifiability_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert payload["all_candidates_monotone_rank_one"] is True
    assert payload["all_candidates_have_same_local_null_as_dq"] is True
    assert payload["candidate_clock_covectors_are_nonunique"] is True
    assert (
        payload["sfh_01_representation_compatible_scalar_class_materialized"]
        is True
    )
    assert payload["theta_M_identified"] is False
    assert payload["a_O_identified"] is False
    assert payload["h_tau_materialized"] is False
    assert payload["time_score_authorized"] is False
