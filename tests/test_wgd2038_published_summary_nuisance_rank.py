import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_wgd2038_published_summary_nuisance_rank_v1"
    / "summary.json"
)


def test_wgd2038_published_summary_nuisance_rank():
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_wgd2038_published_summary_nuisance_rank_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert payload["output_dimension"] == 3
    assert payload["published_summary_nuisance_rank"] == 2
    assert payload["remaining_published_summary_dimension"] == 1
    assert payload["candidate_direction_materialized_before_endpoint_projection"] is True
    assert payload["posterior_level_nuisance_span_materialized"] is False
    assert payload["confirmatory_tau_score_allowed"] is False
    assert payload["tau_specific_information_materialized"] is False
