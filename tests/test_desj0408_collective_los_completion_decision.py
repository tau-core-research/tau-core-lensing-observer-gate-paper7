import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_collective_los_completion_decision_v1"
    / "summary.json"
)


def test_collective_los_completion_decision():
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_desj0408_collective_los_completion_decision_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert payload["explicit_multiplane_perturbers"] == ["G3", "G4", "G5", "G6"]
    assert payload["reported_kappa_ext_median_interval"] == [-0.05, -0.04]
    assert payload["new_f814w_spatial_template_authorized_from_kappa_ext"] is False
    assert payload["kappa_ext_time_delay_nuisance_required"] is True
    assert payload["tau_specific_information_materialized"] is False
    assert payload["time_score_authorized"] is False
