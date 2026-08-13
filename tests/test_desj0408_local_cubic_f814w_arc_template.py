import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_local_cubic_f814w_arc_template_v1"
    / "summary.json"
)


def test_local_cubic_f814w_arc_template():
    subprocess.run(
        [sys.executable, "scripts/score_desj0408_local_cubic_f814w_arc_template_v01.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(OUT.read_text(encoding="utf-8"))
    assert payload["subthreshold_galaxy_count"] == 178
    assert payload["source_forward_template_materialized"] is True
    assert payload["endpoint_was_previously_opened"] is True
    assert payload["confirmatory_evidence_allowed"] is False
    assert payload["template_residual_cosine"] < 0
    assert payload["fixed_amplitude_fractional_unweighted_sse_reduction"] < 0
    assert payload["exploratory_alignment_positive"] is False
    assert payload["tau_specific_information_materialized"] is False
    assert payload["time_score_authorized"] is False
