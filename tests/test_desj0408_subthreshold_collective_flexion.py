import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_subthreshold_collective_flexion_v1"
    / "summary.json"
)


def test_subthreshold_collective_flexion():
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_subthreshold_collective_flexion_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT.read_text(encoding="utf-8"))
    assert payload["model_path_count"] == 48
    assert payload["collective_oriented_subthreshold_structure_nonzero"] is True
    assert payload["path_dependent_collective_structure_nonzero"] is True
    assert payload["not_representable_by_spin0_spin2_tidal_summary"] is True
    assert payload["standard_higher_order_lensing_information"] is True
    assert payload["tau_specific_information_materialized"] is False
    assert payload["time_score_authorized"] is False
