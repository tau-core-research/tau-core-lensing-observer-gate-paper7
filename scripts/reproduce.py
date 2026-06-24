#!/usr/bin/env python3
"""One-command reproduction check for the Paper 7 public package."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper7_submission_source"


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    print("$ " + " ".join(cmd) + f"  # cwd={cwd}")
    subprocess.run(cmd, cwd=cwd, check=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if shutil.which("tectonic") is None:
        raise SystemExit("tectonic is required to compile paper7_submission_source/main.tex")
    run([sys.executable, "scripts/audit_alternate_real_data_source_candidates.py"])
    run([sys.executable, "scripts/extract_desj0408_no_t2_baseline_smoke.py"])
    run([sys.executable, "scripts/extract_desj0408_full_posterior_compatibility_smoke.py"])
    run([sys.executable, "scripts/extract_desj0408_arrival_time_recompute_smoke.py"])
    run([sys.executable, "scripts/extract_desj0408_powerlaw_family_alignment_smoke.py"])
    run([sys.executable, "scripts/extract_desj0408_powerlaw_57_core_feature_table.py"])
    run([sys.executable, "scripts/diagnose_desj0408_powerlaw_57_core_failures.py"])
    run([sys.executable, "scripts/diagnose_desj0408_powerlaw_57_core_outlier_provenance.py"])
    run([sys.executable, "scripts/audit_desj0408_row_linkage_public_source.py"])
    run([sys.executable, "scripts/audit_desj0408_legacy_runtime_compatibility.py"])
    run([sys.executable, "scripts/build_desj0408_lensing_tau_role_constraints.py"])
    run([sys.executable, "scripts/audit_desj0408_no_t2_time_residual_candidate.py"])
    run([sys.executable, "scripts/build_desj0408_t2_null_comparison_design_freeze.py"])
    run([sys.executable, "scripts/score_desj0408_one_amplitude_t2_operator_pretest.py"])
    run([sys.executable, "scripts/audit_desj0408_t2_holdout_readiness.py"])
    run([sys.executable, "scripts/build_wgd2038_holdout_extraction_contract.py"])
    run([sys.executable, "scripts/build_wgd2038_partial_holdout_materialization.py"])
    run([sys.executable, "scripts/extract_wgd2038_bounded_local_fermat_preflight.py"])
    run([sys.executable, "scripts/build_wgd2038_observed_delay_no_t2_smoke.py"])
    run([sys.executable, "scripts/build_wgd2038_published_model_delay_shape_crosscheck.py"])
    run([sys.executable, "scripts/build_wgd2038_delay_shape_holdout_target.py"])
    run([sys.executable, "scripts/audit_wgd2038_observed_delay_linkage.py"])
    run(["tectonic", "main.tex"], cwd=SOURCE)
    run([sys.executable, "scripts/build_arxiv_source.py"])
    run([sys.executable, "-m", "pytest", "-q", "tests"])
    pdf = SOURCE / "main.pdf"
    print(f"paper7_pdf_sha256: {sha256(pdf)}")
    print("PAPER7_LENSING_OBSERVER_GATE_REPRODUCTION_COMPLETE")


if __name__ == "__main__":
    main()
