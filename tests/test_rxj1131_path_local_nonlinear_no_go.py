import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_rxj1131_path_local_nonlinear_no_go_v01.py"
RESULT = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_rxj1131_path_local_nonlinear_no_go_v1/summary.json"
)


def test_rxj1131_path_local_nonlinear_no_go() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text())

    assert payload["incidence_rank"] == 3
    assert payload["linear_descriptor_rank"] == 3
    assert payload["linear_span_equals_full_pair_difference_space"] is True
    assert payload["quadratic_monomial_count"] == 10
    assert payload["quadratic_pair_rank"] == 3
    assert payload["nuisance_orthogonal_quadratic_rank"] == 0
    assert payload["maximum_nuisance_orthogonal_quadratic_entry"] < 1e-12
    assert (
        payload["arbitrary_nonlinear_witness"]["nuisance_orthogonal_norm"]
        < 1e-12
    )
    assert payload["path_local_nonlinear_scalar_can_escape"] is False
    assert payload["terminal_values_used"] is False
