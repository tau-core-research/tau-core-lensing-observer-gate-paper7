import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_subthreshold_exact_multiplane_v1"
    / "summary.json"
)


def test_subthreshold_exact_multiplane_transport():
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_desj0408_subthreshold_exact_multiplane_transport_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT.read_text(encoding="utf-8"))
    assert payload["model_count"] == 12
    assert payload["added_subthreshold_sis_count"] == 178
    assert payload["naive_untruncated_sis_forward_countermodel_materialized"] is True
    assert payload["nonzero_after_best_common_affine_projection"] is True
    assert payload["naive_countermodel_nonaffine"] is True
    assert payload["physical_completion_rejected"] is True
    assert payload["completion_is_profile_and_scaling_relation_conditional"] is True
    assert payload["tau_specific_information_materialized"] is False
    assert payload["time_score_authorized"] is False
