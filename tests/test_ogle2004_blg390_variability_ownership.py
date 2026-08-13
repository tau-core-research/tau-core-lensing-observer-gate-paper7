import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg390_variability_ownership_v1/summary.json"
)


def test_ownership_audit_does_not_promote_bic_to_proof() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_ogle2004_blg390_variability_ownership_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["source_ownership_proved"] is False
    assert (
        result["equal_complexity_models"]["variable_lensed_source"][
            "parameter_count"
        ]
        == result["equal_complexity_models"]["variable_unlensed_blend"][
            "parameter_count"
        ]
    )
