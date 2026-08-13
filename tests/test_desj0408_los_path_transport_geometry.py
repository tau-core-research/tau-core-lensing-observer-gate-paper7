import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_los_path_transport_geometry_v1"
)


def test_los_path_transport_geometry():
    subprocess.run(
        [sys.executable, "scripts/build_desj0408_los_path_transport_geometry_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    with (OUT / "los_path_transport_geometry.csv").open(
        encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert payload["model_count"] == 12
    assert payload["observed_los_object_count"] == 198
    assert payload["path_count"] == 4
    assert len(rows) == payload["transport_row_count"] == 12 * 198 * 4
    assert payload["redshift_dependent_four_path_geometry_materialized"] is True
    assert payload["path_discrimination_nonzero"] is True
    assert payload["published_leading_order_flexion_transport_materialized"] is True
    assert payload["complete_physical_environment_transport_materialized"] is False
    assert payload["above_threshold_object_count"] == 4
    assert payload["above_threshold_count_range_per_model_path"] == [3, 4]
    assert payload["all_above_threshold_objects_already_explicitly_modeled"] is True
    assert payload["path_dependent_threshold_membership_present"] is True
    assert payload["tau_specific_information_materialized"] is False
    assert payload["time_score_authorized"] is False
