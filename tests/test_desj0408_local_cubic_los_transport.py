import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_local_cubic_los_transport_v1"
    / "summary.json"
)


def test_local_cubic_los_transport():
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_local_cubic_los_transport_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT.read_text(encoding="utf-8"))
    assert payload["model_count"] == 12
    assert payload["subthreshold_object_count"] == 178
    assert payload["affine_nuisance_dimension"] == 6
    assert payload["local_non_tidal_transport_nonzero_after_affine_projection"] is True
    assert payload["tau_specific_information_materialized"] is False
    assert payload["time_score_authorized"] is False
