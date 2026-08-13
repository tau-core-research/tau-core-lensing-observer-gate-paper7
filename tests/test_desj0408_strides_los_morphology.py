import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_strides_los_morphology_v1"
)


def test_strides_los_morphology_freeze():
    subprocess.run(
        [sys.executable, "scripts/acquire_desj0408_strides_los_morphology_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    with (OUT / "desj0408_spectroscopic_galaxies.csv").open(
        encoding="utf-8"
    ) as handle:
        galaxies = list(csv.DictReader(handle))
    with (OUT / "desj0408_groups.csv").open(encoding="utf-8") as handle:
        groups = list(csv.DictReader(handle))

    assert (
        len(galaxies)
        == payload["materialized_spectroscopic_galaxy_row_count"]
        == 198
    )
    assert payload["reported_spectroscopic_galaxy_count"] == 199
    assert payload["reported_vs_materialized_row_count_discrepancy"] == 1
    assert len(groups) == payload["identified_group_count"] == 10
    assert payload["observed_los_morphology_materialized"] is True
    assert payload["complete_observed_spectroscopic_cone"] is False
    assert (
        payload["complete_physical_light_cone_morphology_materialized"] is False
    )
    assert payload["path_specific_transport_assigned"] is False
    assert payload["tau_specific_information_materialized"] is False
    assert payload["time_score_authorized"] is False
