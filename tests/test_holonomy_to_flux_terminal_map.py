import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_holonomy_to_flux_terminal_map_v01.py"
RESULT = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_holonomy_to_flux_terminal_map_v1/summary.json"
)


def test_holonomy_to_flux_terminal_map() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text())

    assert (
        payload["pure_u1_isolated_path"]["intensity_variation_over_phase"]
        < 1e-12
    )
    assert payload["pure_u1_isolated_path"]["phase_visible"] is False
    assert (
        payload["coherent_two_path_control"]["relative_phase_visible"] is True
    )
    assert payload["nonunitary_control"]["amplitude_sector_visible"] is True
    assert (
        payload["pure_u1_holonomy_to_isolated_flux_map_nontrivial"] is False
    )
    assert payload["terminal_values_used"] is False
