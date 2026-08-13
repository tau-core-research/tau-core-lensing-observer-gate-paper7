import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_rxj1131_relational_cone_development_role_v1/"
    "summary.json"
)


def test_rxj1131_is_not_promoted_to_blind_validation() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_rxj1131_relational_cone_development_role_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["terminal_coordinate_count"] == 6
    assert result["development_use_allowed"]
    assert not result["confirmatory_blind_use_allowed"]
    assert not result["complete_physical_causal_support_available"]
    assert result["required_external_validation"]
    assert result["verdict"] == (
        "RXJ1131_SELECTED_AS_DEVELOPMENT_TARGET_NOT_BLIND_VALIDATION"
    )
