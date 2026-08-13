import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_tau_amplitude_jacobian_source_ownership_v01.py"
RESULT = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_amplitude_jacobian_source_ownership_v1/summary.json"
)


def test_tau_amplitude_jacobian_source_ownership() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text())

    assert (
        payload["positive_body_amplitude"]["unitary_orbit_norm_change"]
        < 1e-12
    )
    assert (
        payload["positive_body_amplitude"][
            "supplies_optical_real_gain_alpha_i"
        ]
        is False
    )
    assert (
        payload["current_holonomy_jacobian_cross_jet"][
            "mixed_hessian_norm"
        ]
        == 0.0
    )
    assert (
        payload["admissible_counterfamily"][
            "zero_and_both_signs_positive_definite"
        ]
        is True
    )
    assert payload["real_gain_source_owned"] is False
    assert (
        payload["holonomy_jacobian_cross_derivative_source_owned"] is False
    )
    assert payload["terminal_values_used"] is False
