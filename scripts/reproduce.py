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
    run([sys.executable, "scripts/audit_desj0408_ab_relative_clock_rate_v01.py"])
    run(
        [
            sys.executable,
            "scripts/calibrate_desj0408_ab_relative_clock_rate_null_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/calibrate_desj0408_ab_correlated_clock_null_v01.py",
        ]
    )
    run([sys.executable, "scripts/transfer_he0435_bc_relative_clock_rate_v01.py"])
    run(
        [
            sys.executable,
            "scripts/audit_desj0408_unlensed_control_support_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_ogle_periodic_microlensing_clock_support_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_ogle2004_blg081_local_clock_rate_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/calibrate_ogle2004_blg081_local_clock_null_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_ogle2004_blg081_finite_source_clock_discriminator_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/calibrate_ogle2004_blg081_finite_tangent_clock_null_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_ogle_replacement_same_source_clock_candidates_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/calibrate_ogle2004_blg390_finite_tangent_clock_null_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_ogle2004_blg390_variability_ownership_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_ogle2004_blg390_clock_robustness_grid_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_same_source_clock_replacement_data_frontier_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/crossmatch_kmtnet2016_periodic_source_clock_candidates_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_kmt2016_blg1194_variability_ownership_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_kmt2016_blg1194_conditional_clock_rate_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_kmt2016_blg1194_ogle_template_clock_transfer_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_observer_clock_empirical_branch_consolidation_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_relational_cone_cross_terminal_route_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_blind_cross_terminal_identifiability_theorem_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_rxj1131_relational_cone_development_role_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/freeze_rxj1131_pre2026_predictor_source_packet_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/build_rxj1131_dimensionless_path_descriptor_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_rxj1131_standard_nuisance_span_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_rxj1131_path_local_nonlinear_no_go_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_rxj1131_cycle_terminal_visibility_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_holonomy_to_flux_terminal_map_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_tau_amplitude_jacobian_source_ownership_v01.py",
        ]
    )
    run([sys.executable, "scripts/freeze_desj0408_source_morphology_triangle_v01.py"])
    run([sys.executable, "scripts/audit_desj0408_single_body_host_descriptor_v01.py"])
    run([sys.executable, "scripts/audit_desj0408_host_brightness_moment_preflight_v01.py"])
    run([sys.executable, "scripts/solve_desj0408_positive_host_moment_v01.py"])
    run([sys.executable, "scripts/freeze_desj0408_image_path_pullbacks_v01.py"])
    run([sys.executable, "scripts/audit_desj0408_body_ownership_v01.py"])
    run([sys.executable, "scripts/audit_desj0408_scalar_body_path_coupling_v01.py"])
    run([sys.executable, "scripts/audit_desj0408_joint_tensor_path_interaction_v01.py"])
    run([sys.executable, "scripts/validate_desj0408_tensor_path_ordinal_holdout_v01.py"])
    run([sys.executable, "scripts/audit_desj0408_coordinate_free_path_signature_v01.py"])
    run([sys.executable, "scripts/audit_desj0408_scalar_clock_nonidentifiability_v01.py"])
    run([sys.executable, "scripts/audit_desj0408_log_clock_composition_selection_v01.py"])
    run([sys.executable, "scripts/audit_desj0408_moment_area_character_v01.py"])
    run([sys.executable, "scripts/audit_desj0408_log_area_path_contrast_v01.py"])
    run([sys.executable, "scripts/freeze_desj0408_modeled_cone_morphology_v01.py"])
    run([sys.executable, "scripts/acquire_desj0408_strides_los_morphology_v01.py"])
    run([sys.executable, "scripts/build_desj0408_los_path_transport_geometry_v01.py"])
    run([sys.executable, "scripts/audit_desj0408_subthreshold_collective_flexion_v01.py"])
    run(
        [
            sys.executable,
            "scripts/audit_desj0408_subthreshold_exact_multiplane_transport_v01.py",
        ]
    )
    run([sys.executable, "scripts/audit_desj0408_local_cubic_los_transport_v01.py"])
    run([sys.executable, "scripts/audit_desj0408_local_cubic_astrometric_endpoint_v01.py"])
    run([sys.executable, "scripts/score_desj0408_local_cubic_f814w_arc_template_v01.py"])
    run(
        [
            sys.executable,
            "scripts/audit_desj0408_collective_los_completion_decision_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_desj0408_kappa_marginalized_delay_rank_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_wgd2038_published_summary_nuisance_rank_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_wgd2038_mass_family_delay_rank_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_wgd2038_kinematic_holdout_independence_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_wgd2038_oiii_distinct_terminal_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_wgd2038_standard_flux_completion_payload_v01.py",
        ]
    )
    run(
        [
            sys.executable,
            "scripts/audit_wgd2038_cross_amplitude_terminal_stability_v01.py",
        ]
    )
    run([sys.executable, "scripts/build_paper8_source_forward_time_handoff.py"])
    run(["tectonic", "main.tex"], cwd=SOURCE)
    run([sys.executable, "scripts/build_arxiv_source.py"])
    run([sys.executable, "-m", "pytest", "-q", "tests"])
    pdf = SOURCE / "main.pdf"
    print(f"paper7_pdf_sha256: {sha256(pdf)}")
    print("PAPER7_LENSING_OBSERVER_GATE_REPRODUCTION_COMPLETE")


if __name__ == "__main__":
    main()
