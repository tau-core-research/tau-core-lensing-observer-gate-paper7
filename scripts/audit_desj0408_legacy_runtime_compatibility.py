#!/usr/bin/env python3
"""Audit legacy runtime compatibility for DES J0408 row reproduction.

The DES row-linkage audit shows that the public source intends index-order
linkage between posterior rows and saved time-delay rows.  The remaining
question is whether modern lenstronomy execution is semantically identical to
the legacy environment that generated the public tables.

This audit records public notebook/runtime evidence and the current helper
runtime.  It does not install old packages, recompute T2, or promote failed
models.
"""

from __future__ import annotations

import json
import subprocess
import sys
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DES_ROOT = ROOT / "data" / "external" / "source_candidate_repos" / "DESJ0408_time_delay_cosmography"
NOTEBOOK = DES_ROOT / "notebooks" / "Distance posterior from combining lensing, kinematics, and external convergence.ipynb"
VENV = ROOT / ".venv_wgd2038_repro" / "bin" / "python"
CSV_PATH = ROOT / "data" / "derived" / "desj0408_legacy_runtime_compatibility_audit_v1.csv"
OUT_DIR = ROOT / "data" / "derived" / "repro_results" / "tau_core_lensing_desj0408_legacy_runtime_compatibility_audit_v1"


def notebook_contains(text: str) -> bool:
    return text in NOTEBOOK.read_text(encoding="utf-8", errors="replace")


def notebook_kernel_version() -> str | None:
    data = json.loads(NOTEBOOK.read_text(encoding="utf-8", errors="replace"))
    return data.get("metadata", {}).get("language_info", {}).get("version")


def current_runtime() -> dict[str, str]:
    proc = subprocess.run(
        [
            str(VENV),
            "-c",
            (
                "import sys, lenstronomy, astropy, dill; "
                "print(sys.version.split()[0]); "
                "print(lenstronomy.__version__); "
                "print(astropy.__version__); "
                "print(dill.__version__)"
            ),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    lines = proc.stdout.splitlines()
    return {
        "python": lines[0],
        "lenstronomy": lines[1],
        "astropy": lines[2],
        "dill": lines[3],
    }


def main() -> None:
    runtime = current_runtime()
    public_mentions_lenstronomy_092 = notebook_contains("lenstronomy # runs with v0.9.2")
    public_kernel_version = notebook_kernel_version()
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "public_lenstronomy",
                "public_python",
                "current_lenstronomy",
                "current_python",
                "current_astropy",
                "current_dill",
                "runtime_mismatch_is_plausible_row_defect_source",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "public_lenstronomy": "0.9.2" if public_mentions_lenstronomy_092 else "",
                "public_python": public_kernel_version,
                "current_lenstronomy": runtime["lenstronomy"],
                "current_python": runtime["python"],
                "current_astropy": runtime["astropy"],
                "current_dill": runtime["dill"],
                "runtime_mismatch_is_plausible_row_defect_source": (
                    public_mentions_lenstronomy_092 and runtime["lenstronomy"] != "0.9.2"
                ),
            }
        )
    summary = {
        "schema": "paper7 DES J0408 legacy runtime compatibility audit v1",
        "purpose": (
            "Record whether the modern helper runtime matches the public DES "
            "notebook runtime evidence relevant to row-level time-delay reproduction."
        ),
        "source": {
            "source_id": "DESJ0408_time_delay_cosmography",
            "notebook_file": str(NOTEBOOK.relative_to(ROOT)),
            "helper_python": str(VENV),
        },
        "public_runtime_evidence": {
            "notebook_mentions_lenstronomy_0_9_2": public_mentions_lenstronomy_092,
            "notebook_language_info_python_version": public_kernel_version,
        },
        "current_helper_runtime": runtime,
        "criteria": {
            "public_notebook_runtime_evidence_found": (
                public_mentions_lenstronomy_092 and public_kernel_version is not None
            ),
            "current_helper_runtime_recorded": True,
            "current_lenstronomy_matches_public_0_9_2": runtime["lenstronomy"] == "0.9.2",
            "current_python_matches_public_kernel": runtime["python"] == public_kernel_version,
            "legacy_semantics_reconstructed": False,
            "failed_models_promoted_to_baseline": False,
            "real_data_T2_sampling_authorized": False,
        },
        "verdict": {
            "desj0408_legacy_runtime_compatibility_audit_created": True,
            "runtime_mismatch_is_plausible_row_defect_source": (
                public_mentions_lenstronomy_092 and runtime["lenstronomy"] != "0.9.2"
            ),
            "legacy_runtime_not_reconstructed": True,
            "strict_baseline_should_remain_2_model_core": True,
            "real_data_T2_sampling_authorized": False,
        },
        "claim_boundary": [
            "This audit identifies a plausible compatibility source; it does not prove the mismatch is caused by lenstronomy version drift.",
            "No old environment is installed and no failed model is promoted.",
            "No T2 posterior, Bayes factor, or operator-necessity claim is introduced.",
        ],
        "next_finite_action": (
            "Attempt a separate, isolated lenstronomy 0.9.2 compatibility probe only if "
            "dependency resolution is feasible; otherwise keep the strict two-model core."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["verdict"], indent=2))
    print(json.dumps(summary["public_runtime_evidence"], indent=2))
    print(json.dumps(summary["current_helper_runtime"], indent=2))


if __name__ == "__main__":
    main()
