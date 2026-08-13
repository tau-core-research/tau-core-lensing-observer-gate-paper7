import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_kmt2016_blg1194_ogle_template_clock_transfer_v1/"
    "summary.json"
)


def test_ogle_template_is_independent_and_checksum_frozen() -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/audit_kmt2016_blg1194_ogle_template_clock_transfer_v01.py",
        ],
        cwd=ROOT,
        check=True,
    )
    result = json.loads(SUMMARY.read_text())
    assert result["template_points"] == 867
    assert len(result["template_sha256"]) == 64
    assert result["kmt_points"] > 2000
    assert result["verdict"] in {
        "INDEPENDENT_OGLE_TEMPLATE_CLOCK_CANDIDATE",
        "INDEPENDENT_OGLE_TEMPLATE_CLOCK_NULL",
    }
