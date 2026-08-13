import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_body_ownership_v1/summary.json"
)


def test_desj0408_body_ownership_no_go() -> None:
    subprocess.run(
        [sys.executable, "scripts/audit_desj0408_body_ownership_v01.py"],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    audited = result["audited_objects"]
    assert audited["multisource_triangle"]["source_component_count"] == 3
    assert audited["multisource_triangle"]["source_plane_count"] == 2
    assert audited["multisource_triangle"]["common_body_owner"] is False
    assert audited["parametric_quasar_host"]["full_vector_model_stable"] is False
    assert audited["positive_host_moment"]["stable_scalar_only"] is True
    assert audited["four_image_path_pullbacks"]["body_coordinates"] is False
    assert result["single_source_frozen_body_descriptor_materialized"] is False
    assert result["sfh_02_relative_morphology_materialized"] is False
    assert result["time_score_authorized"] is False
