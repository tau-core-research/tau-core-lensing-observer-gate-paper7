import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_ogle2004_blg081_finite_source_clock_discriminator_v1/"
    "summary.json"
)


def test_finite_source_discriminator_preserves_claim_boundary() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_ogle2004_blg081_finite_source_clock_discriminator_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["exact_binary_source_finite_source_model_executed"] is False
    assert len(result["models"]) == 4
    assert isinstance(result["finite_tangent_absorbs_clock_candidate"], bool)
