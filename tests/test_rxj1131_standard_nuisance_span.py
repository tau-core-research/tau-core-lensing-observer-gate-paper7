import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_rxj1131_standard_nuisance_span_v01.py"
RESULT = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_rxj1131_standard_nuisance_span_v1/summary.json"
)


def test_rxj1131_standard_nuisance_span() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text())

    assert payload["descriptor_rank"] == 3
    assert payload["standard_nuisance_rank"] == 3
    assert payload["nuisance_orthogonal_descriptor_rank"] == 0
    assert payload["maximum_nuisance_orthogonal_entry"] < 1e-12
    assert (
        payload["arbitrary_linear_weight_witness"][
            "nuisance_orthogonal_norm"
        ]
        < 1e-12
    )
    assert payload["linear_tau_direction_survives"] is False
    assert payload["terminal_values_used"] is False
    assert payload["nonlinear_extension_tested"] is False
