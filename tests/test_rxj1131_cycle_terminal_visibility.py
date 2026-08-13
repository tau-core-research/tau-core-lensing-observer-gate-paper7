import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_rxj1131_cycle_terminal_visibility_v01.py"
RESULT = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_rxj1131_cycle_terminal_visibility_v1/summary.json"
)


def test_rxj1131_cycle_terminal_visibility() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text())

    assert payload["pair_space_dimension"] == 6
    assert payload["cut_space_rank"] == 3
    assert payload["cycle_space_rank"] == 3
    assert payload["cut_cycle_projector_overlap_norm"] < 1e-12
    assert payload["synthetic_exact_terminal_cycle_norm"] < 1e-12
    assert payload["nonexact_cycle_boundary_norm"] < 1e-12
    assert abs(payload["nonexact_cycle_exact_terminal_pairing"]) < 1e-12
    assert payload["nonexact_cycle_directly_visible_in_flux_ratios"] is False
    assert payload["terminal_values_used"] is False
