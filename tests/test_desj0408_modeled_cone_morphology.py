import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_modeled_cone_morphology_v1"
    / "summary.json"
)


def test_modeled_cone_is_materialized_but_physical_cone_is_incomplete():
    subprocess.run(
        [sys.executable, "scripts/freeze_desj0408_modeled_cone_morphology_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert payload["model_count"] == 12
    assert payload["component_counts"] == [8]
    assert payload["lens_plane_counts"] == [3]
    assert payload["all_values_finite"] is True
    assert payload["multi_plane_loco_nonadditivity_nonzero"] is True
    assert payload["modeled_cone_descriptor_materialized"] is True
    assert payload["complete_physical_light_cone_morphology_materialized"] is False
    assert payload["standard_multiplane_lensing_information_only"] is True
    assert payload["tau_specific_cone_information_materialized"] is False
    assert payload["h_tau_materialized"] is False
    assert payload["time_score_authorized"] is False
