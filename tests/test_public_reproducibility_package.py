import json
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper7_submission_source"
DATA = ROOT / "data/derived"
RESULTS = DATA / "repro_results"


def load_result(name: str) -> dict[str, object]:
    return json.loads((RESULTS / name / "summary.json").read_text(encoding="utf-8"))


def test_publication_files_exist():
    required = [
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "CITATION.cff",
        ROOT / "DATA_NOTICE.md",
        ROOT / "requirements.txt",
        SOURCE / "main.tex",
        SOURCE / "refs.bib",
        SOURCE / "main.pdf",
        SOURCE / "figures",
        ROOT / "figures",
        ROOT / "scripts/build_arxiv_source.py",
        ROOT / "scripts/reproduce.py",
        ROOT / "scripts/audit_wgd2038_lenstronomy_hst_reproduction.py",
        ROOT / "scripts/analyze_wgd2038_mcmc_drift.py",
        ROOT / "scripts/build_wgd2038_nuisance_stabilization_plan.py",
        ROOT / "scripts/audit_alternate_real_data_source_candidates.py",
        ROOT / "scripts/extract_desj0408_no_t2_baseline_smoke.py",
        ROOT / "scripts/extract_desj0408_full_posterior_compatibility_smoke.py",
        ROOT / "scripts/extract_desj0408_arrival_time_recompute_smoke.py",
        ROOT / "scripts/extract_desj0408_powerlaw_family_alignment_smoke.py",
        ROOT / "scripts/extract_desj0408_powerlaw_57_core_feature_table.py",
        ROOT / "scripts/diagnose_desj0408_powerlaw_57_core_failures.py",
        ROOT / "scripts/diagnose_desj0408_powerlaw_57_core_outlier_provenance.py",
        ROOT / "scripts/audit_desj0408_row_linkage_public_source.py",
        ROOT / "scripts/audit_desj0408_legacy_runtime_compatibility.py",
        ROOT / "scripts/build_desj0408_lensing_tau_role_constraints.py",
        ROOT / "scripts/audit_desj0408_no_t2_time_residual_candidate.py",
        ROOT / "scripts/build_desj0408_t2_null_comparison_design_freeze.py",
        ROOT / "scripts/score_desj0408_one_amplitude_t2_operator_pretest.py",
        ROOT / "scripts/audit_desj0408_t2_holdout_readiness.py",
        ROOT / "scripts/build_wgd2038_holdout_extraction_contract.py",
        ROOT / "scripts/build_wgd2038_partial_holdout_materialization.py",
        ROOT / "scripts/extract_wgd2038_bounded_local_fermat_preflight.py",
        ROOT / "scripts/build_wgd2038_observed_delay_no_t2_smoke.py",
        ROOT / "scripts/build_wgd2038_arxiv_source_table_payload.py",
        ROOT / "scripts/build_wgd2038_published_model_delay_shape_crosscheck.py",
        ROOT / "scripts/build_wgd2038_delay_shape_holdout_target.py",
        ROOT / "scripts/audit_wgd2038_observed_delay_linkage.py",
        RESULTS / "tau_core_lensing_wgd2038_lenstronomy_hst_reproduction_v1" / "RECONSTRUCTION.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_paper_source_is_scoped_and_formula_renderable():
    source = (SOURCE / "main.tex").read_text(encoding="utf-8")
    assert "Testing the Tau-Core Observer Principle" in source
    assert "No real-data T2 posterior was sampled" in source
    assert "WGD2038 public HST route now passes" in source
    assert "DES J0408 is promoted to bounded no-T2 follow-up" in source
    assert "DES J0408 no-T2 time-delay extraction smoke" in source
    assert "DES J0408 full posterior compatibility smoke" in source
    assert "DES J0408 arrival-time recomputation smoke" in source
    assert "DES J0408 power-law family alignment smoke" in source
    assert "57-parameter core feature-table" in source
    assert "lensing-feature to" in source
    assert "Tau-role constraint artifact" in source
    assert "no-T2 time-residual candidate pretest" in source
    assert "null-versus-T2 design freeze" in source
    assert "one-amplitude T2 operator pretest" in source
    assert "independent holdout readiness audit" in source
    assert "WGD2038 holdout extraction contract" in source
    assert "WGD2038 partial holdout materialization" in source
    assert "WGD2038 bounded local Fermat preflight" in source
    assert "WGD2038 observed-delay no-T2 smoke" in source
    assert "WGD2038 arXiv source-table payload" in source
    assert "WGD2038 published-model delay-shape crosscheck" in source
    assert "WGD2038 delay-shape holdout target" in source
    assert "WGD2038 observed-delay linkage audit" in source
    assert "epsilon_\\tau\\pi_i|\\Delta\\phi_i|" in source
    assert "Tau Core is proven" not in source
    assert "\\includegraphics" in source
    assert (SOURCE / "refs.bib").exists()


def test_paper_critical_verdicts_match_summary_artifacts():
    public_deep = load_result("tau_core_lensing_public_deep_repository_search_v0")
    method = load_result("tau_core_lensing_public_only_method_validation_v0")
    blind = load_result("tau_core_lensing_synthetic_blind_challenge_expansion_v0_quick")
    noise_mc = load_result("tau_core_lensing_noise_failure_monte_carlo_cached_v0")
    joint = load_result("tau_core_lensing_joint_stress_grid_cached_v0")
    he0435 = load_result("tau_core_lensing_he0435_public_repro_model_level_psf_correction_fit_v0")
    static_closure = load_result("tau_core_lensing_static_control_branch_closure_v0")
    real_data_t2 = load_result("tau_core_lensing_real_data_t2_eligibility_audit_v1")
    wgd2038_field = load_result("tau_core_lensing_wgd2038_field_level_payload_audit_v1")
    wgd2038_acquired = load_result("tau_core_lensing_wgd2038_public_payload_acquisition_v1")
    wgd2038_hst_repro = load_result("tau_core_lensing_wgd2038_lenstronomy_hst_reproduction_v1")
    alternate_sources = load_result("tau_core_lensing_alternate_source_candidate_audit_v1")
    desj0408_smoke = load_result("tau_core_lensing_desj0408_no_t2_baseline_smoke_v1")
    desj0408_full = load_result("tau_core_lensing_desj0408_full_posterior_compat_smoke_v1")
    desj0408_arrival = load_result("tau_core_lensing_desj0408_arrival_time_recompute_smoke_v1")
    desj0408_powerlaw = load_result("tau_core_lensing_desj0408_powerlaw_family_alignment_smoke_v1")
    desj0408_core_features = load_result(
        "tau_core_lensing_desj0408_powerlaw_57_core_feature_table_v1"
    )
    desj0408_core_failures = load_result(
        "tau_core_lensing_desj0408_powerlaw_57_core_failure_diagnostic_v1"
    )
    desj0408_outlier_provenance = load_result(
        "tau_core_lensing_desj0408_powerlaw_57_core_outlier_provenance_v1"
    )
    desj0408_row_linkage = load_result(
        "tau_core_lensing_desj0408_row_linkage_public_source_audit_v1"
    )
    desj0408_runtime = load_result(
        "tau_core_lensing_desj0408_legacy_runtime_compatibility_audit_v1"
    )
    desj0408_tau_roles = load_result(
        "tau_core_lensing_desj0408_tau_role_constraints_v1"
    )
    desj0408_time_residual = load_result(
        "tau_core_lensing_desj0408_no_t2_time_residual_candidate_v1"
    )
    desj0408_t2_design = load_result(
        "tau_core_lensing_desj0408_t2_null_comparison_design_freeze_v1"
    )
    desj0408_t2_score = load_result(
        "tau_core_lensing_desj0408_one_amplitude_t2_operator_pretest_v1"
    )
    desj0408_holdout = load_result(
        "tau_core_lensing_desj0408_t2_holdout_readiness_v1"
    )
    wgd2038_contract = load_result(
        "tau_core_lensing_wgd2038_holdout_extraction_contract_v1"
    )
    wgd2038_partial = load_result(
        "tau_core_lensing_wgd2038_partial_holdout_materialization_v1"
    )
    wgd2038_fermat_preflight = load_result(
        "tau_core_lensing_wgd2038_bounded_local_fermat_preflight_v1"
    )
    wgd2038_observed_smoke = load_result(
        "tau_core_lensing_wgd2038_observed_delay_no_t2_smoke_v1"
    )
    wgd2038_published_shape = load_result(
        "tau_core_lensing_wgd2038_published_model_delay_shape_crosscheck_v1"
    )
    wgd2038_shape_target = load_result(
        "tau_core_lensing_wgd2038_delay_shape_holdout_target_v1"
    )
    wgd2038_delay_linkage = load_result(
        "tau_core_lensing_wgd2038_observed_delay_linkage_audit_v1"
    )

    assert public_deep["carried_forward_verdict"] == "NO_PUBLIC_EVIDENCE_GRADE_TIME_DELAY_MODEL_PRODUCTS_FOUND"
    assert public_deep["evidence_grade_target_found"] is False
    assert method["evidence_status"] == "METHOD_ONLY_NOT_REAL_DATA_EVIDENCE"
    assert abs(float(method["t2_best_epsilon_hat"]) - 0.0499193089) <= 1e-12
    assert blind["strict_identified_count"] == 4
    assert abs(float(blind["max_abs_epsilon_error"]) - 0.00038902503227167956) <= 1e-15
    assert abs(float(noise_mc["stable_noise_max"]) - 0.008) <= 1e-15
    assert noise_mc["transition_noise_min"] == 0.01
    assert joint["stable_count"] == 6
    assert joint["transition_count"] == 2
    assert he0435["carried_forward_verdict"] == "HE0435_PUBLIC_REPRO_PSF_POLICY_EDGE_SEEKING_OR_RESIDUAL_FAILS"
    assert he0435["selected_hard_bound_solution_count"] == 6
    assert static_closure["verdict"] == "STATIC_CONTROL_BRANCH_CLOSED"
    assert static_closure["sampling_status"] == "BLOCKED"
    assert real_data_t2["verdict"]["real_data_T2_sampling_authorized"] is False
    assert real_data_t2["verdict"]["evidence_grade_target_found"] is False
    assert real_data_t2["verdict"]["best_followup_target"] == "TDCOSMO_WGD2038_4008"
    assert real_data_t2["verdict"]["best_followup_source"] == "TDCOSMO2025_public"
    assert wgd2038_field["verdict"]["WGD2038_field_level_payload_audited"] is True
    assert wgd2038_field["criteria"]["ddt_samples_available"] is True
    assert wgd2038_field["criteria"]["fermat_notebook_available"] is True
    assert wgd2038_field["criteria"]["notebook_defines_t2_design_vector_fields"] is True
    assert wgd2038_field["criteria"]["notebook_requires_external_model_payload"] is True
    assert wgd2038_field["criteria"]["image_parity_available"] is False
    assert wgd2038_field["criteria"]["image_wise_fermat_samples_available"] is False
    assert wgd2038_field["verdict"]["real_data_T2_sampling_authorized"] is False
    assert wgd2038_acquired["criteria"]["local_public_partial_payload_acquired"] is True
    assert wgd2038_acquired["criteria"]["arxiv_2406_02683_source_tables_acquired"] is True
    assert wgd2038_acquired["criteria"]["model_posterior_joblib_payload_acquired"] is False
    assert wgd2038_acquired["criteria"]["image_wise_t2_table_acquired"] is False
    assert wgd2038_acquired["counts"]["expected_joblib_targets_from_fermat_notebook"] == 36
    assert wgd2038_acquired["counts"]["present_files"] >= 9
    assert (
        wgd2038_acquired["google_drive_acquisition_status"]
        == "blocked_inaccessible_or_unretrievable_from_current_environment"
    )
    assert wgd2038_acquired["verdict"]["real_data_T2_sampling_authorized"] is False
    assert wgd2038_hst_repro["criteria"]["hst_mast_products_downloaded"] is True
    assert wgd2038_hst_repro["criteria"]["sci_wht_reduced_data_prepared"] is True
    assert wgd2038_hst_repro["criteria"]["all_required_lenstronomy_hdf5_recorded"] is True
    assert wgd2038_hst_repro["criteria"]["f160w_raw_cell_reproduction_patch_documented"] is True
    assert wgd2038_hst_repro["criteria"]["multiband_data_setup_preflight_executed"] is True
    assert wgd2038_hst_repro["criteria"]["bounded_pemd_smoke_notebook_executed"] is True
    assert wgd2038_hst_repro["criteria"]["bounded_pemd_smoke_job_output_recorded"] is True
    assert wgd2038_hst_repro["criteria"]["bounded_pemd_fastell_smoke_notebook_executed"] is True
    assert wgd2038_hst_repro["criteria"]["bounded_pemd_fastell_smoke_job_output_recorded"] is True
    assert wgd2038_hst_repro["criteria"]["bounded_pemd_fastell_mcmc_pilot_notebook_executed"] is True
    assert wgd2038_hst_repro["criteria"]["bounded_pemd_fastell_mcmc_pilot_output_recorded"] is True
    assert wgd2038_hst_repro["criteria"]["bounded_pemd_fastell_mcmc_diagnostic_notebook_executed"] is True
    assert wgd2038_hst_repro["criteria"]["bounded_pemd_fastell_mcmc_diagnostic_output_recorded"] is True
    assert wgd2038_hst_repro["verdict"]["hst_to_lenstronomy_preprocessing_reproduced"] is True
    assert wgd2038_hst_repro["verdict"]["multiband_setup_smoke_preflight_passed"] is True
    assert wgd2038_hst_repro["verdict"]["bounded_model_plumbing_smoke_passed"] is True
    assert wgd2038_hst_repro["verdict"]["bounded_physical_pemd_backend_smoke_passed"] is True
    assert wgd2038_hst_repro["verdict"]["physical_pemd_backend_available"] is True
    assert wgd2038_hst_repro["verdict"]["bounded_mcmc_posterior_plumbing_pilot_passed"] is True
    assert wgd2038_hst_repro["verdict"]["bounded_mcmc_diagnostic_pilot_passed"] is True
    assert wgd2038_hst_repro["verdict"]["bounded_mcmc_diagnostic60_payload_summarized"] is True
    assert (
        wgd2038_hst_repro["bounded_fastell_mcmc_diagnostic60_summary"]["emcee_sample_shape"]
        == [12720, 53]
    )
    assert wgd2038_hst_repro["verdict"]["bounded_mcmc_diagnostic120_payload_summarized"] is True
    assert (
        wgd2038_hst_repro["bounded_fastell_mcmc_diagnostic120_summary"]["emcee_sample_shape"]
        == [25440, 53]
    )
    assert wgd2038_hst_repro["verdict"]["bounded_mcmc_diag120_cont_notebook_executed"] is True
    assert wgd2038_hst_repro["verdict"]["bounded_mcmc_diag120_cont_payload_summarized"] is True
    assert (
        wgd2038_hst_repro["bounded_fastell_mcmc_diag120_cont_summary"]["emcee_sample_shape"]
        == [25440, 53]
    )
    assert (
        wgd2038_hst_repro["bounded_fastell_mcmc_diag120_cont_summary"][
            "uses_previous_chain_endpoint_start"
        ]
        is True
    )
    assert wgd2038_hst_repro["verdict"]["bounded_mcmc_diag120_cont2_notebook_executed"] is True
    assert wgd2038_hst_repro["verdict"]["bounded_mcmc_diag120_cont2_payload_summarized"] is True
    assert (
        wgd2038_hst_repro["bounded_fastell_mcmc_diag120_cont2_summary"]["emcee_sample_shape"]
        == [25440, 53]
    )
    assert (
        wgd2038_hst_repro["bounded_fastell_mcmc_diag120_cont2_summary"][
            "uses_previous_chain_endpoint_start"
        ]
        is True
    )
    assert (
        wgd2038_hst_repro["verdict"]["bounded_mcmc_diag120_cont3_cold_notebook_executed"]
        is True
    )
    assert (
        wgd2038_hst_repro["verdict"]["bounded_mcmc_diag120_cont3_cold_payload_summarized"]
        is True
    )
    assert (
        wgd2038_hst_repro["bounded_fastell_mcmc_diag120_cont3_cold_summary"][
            "emcee_sample_shape"
        ]
        == [25440, 53]
    )
    assert (
        wgd2038_hst_repro["bounded_fastell_mcmc_diag120_cont3_cold_summary"][
            "mcmc_sigma_scale"
        ]
        == 0.02
    )
    assert (
        wgd2038_hst_repro["verdict"]["bounded_mcmc_parameter_drift_diagnostic_summarized"]
        is True
    )
    drift_summary = wgd2038_hst_repro["bounded_fastell_mcmc_parameter_drift_summary"]
    assert drift_summary["verdict"]["parameter_drift_diagnostic_created"] is True
    assert drift_summary["verdict"]["all_available_jobs_finite"] is True
    assert (
        drift_summary["verdict"]["simple_endpoint_or_cold_continuation_clears_blocker"]
        is False
    )
    assert len(drift_summary["persistent_top_drift_parameters"]) >= 5
    assert wgd2038_hst_repro["verdict"]["wgd2038_nuisance_stabilization_plan_created"] is True
    stabilization_plan = wgd2038_hst_repro["wgd2038_nuisance_stabilization_plan"]
    assert (
        stabilization_plan["recommended_next_run"]["name"]
        == "profile_freeze_v1_bounded_diagnostic"
    )
    assert stabilization_plan["counts"]["profile_freeze_candidates_ge_1sigma_mean"] >= 1
    assert stabilization_plan["real_data_T2_sampling_authorized"] is False
    assert wgd2038_hst_repro["verdict"]["bounded_profile_freeze_v1_payload_summarized"] is True
    profile_freeze = wgd2038_hst_repro["bounded_fastell_profile_freeze_v1_summary"]
    assert profile_freeze["emcee_sample_shape"] == [20160, 42]
    assert profile_freeze["finite_samples"] is True
    assert profile_freeze["finite_logp"] is True
    assert profile_freeze["reuses_previous_mcmc_samples"] is False
    assert profile_freeze["real_data_T2_sampling_authorized"] is False
    assert wgd2038_hst_repro["verdict"]["bounded_profile_freeze_v2_payload_summarized"] is True
    profile_freeze_v2 = wgd2038_hst_repro["bounded_fastell_profile_freeze_v2_summary"]
    assert profile_freeze_v2["emcee_sample_shape"] == [16800, 35]
    assert profile_freeze_v2["finite_samples"] is True
    assert profile_freeze_v2["finite_logp"] is True
    assert profile_freeze_v2["reuses_previous_mcmc_samples"] is False
    assert profile_freeze_v2["real_data_T2_sampling_authorized"] is False
    assert (
        wgd2038_hst_repro["bounded_fastell_mcmc_diagnostic120_summary"][
            "split_half_abs_mean_shift_sigma_quantiles"
        ]["p50"]
        > wgd2038_hst_repro["bounded_fastell_mcmc_diagnostic60_summary"][
            "split_half_abs_mean_shift_sigma_quantiles"
        ]["p50"]
    )
    assert wgd2038_hst_repro["verdict"]["converged_no_T2_posterior_reproduced"] is False
    assert wgd2038_hst_repro["verdict"]["no_T2_image_model_reproduction_authorized"] is False
    assert wgd2038_hst_repro["verdict"]["real_data_T2_sampling_authorized"] is False
    assert alternate_sources["verdict"]["alternate_source_audit_completed"] is True
    assert (
        alternate_sources["verdict"]["best_current_alternate_target"]
        == "DESJ0408_time_delay_cosmography"
    )
    assert (
        alternate_sources["verdict"]["best_current_alternate_classification"]
        == "REAL_TARGET_NOTEBOOK_AND_POSTERIOR_CANDIDATE"
    )
    assert alternate_sources["verdict"]["best_current_alternate_followup_ready"] is True
    assert alternate_sources["verdict"]["real_data_T2_sampling_authorized"] is False
    des = next(
        row
        for row in alternate_sources["sources"]
        if row["source_id"] == "DESJ0408_time_delay_cosmography"
    )
    assert des["counts"]["lens_model_posterior_files"] == 24
    assert des["counts"]["time_delay_posterior_files"] == 24
    assert des["counts"]["representative_time_delay_rows"] == 10000
    assert des["criteria"]["processed_multiband_imaging_available"] is True
    assert des["criteria"]["known_solution_pickle_available"] is True
    assert des["criteria"]["direct_t2_sampling_authorized"] is False
    assert desj0408_smoke["verdict"]["desj0408_no_t2_time_delay_extraction_smoke_passed"] is True
    assert desj0408_smoke["verdict"]["bounded_no_t2_baseline_reproduction_completed"] is False
    assert desj0408_smoke["verdict"]["real_data_T2_sampling_authorized"] is False
    assert desj0408_smoke["criteria"]["public_time_delay_posterior_files_read"] is True
    assert desj0408_smoke["criteria"]["all_models_have_10000_samples"] is True
    assert desj0408_smoke["criteria"]["full_lens_posterior_decoded"] is False
    assert desj0408_smoke["aggregate"]["model_count"] == 24
    assert desj0408_smoke["aggregate"]["sample_count_per_model_min"] == 10000
    assert desj0408_smoke["aggregate"]["best_model_family_by_mean_chi2"] == "composite"
    assert (
        desj0408_smoke["aggregate"]["best_model_id_by_mean_chi2"]
        == "0408_run917_1_1_0_0_0_1_1_0"
    )
    assert abs(float(desj0408_smoke["aggregate"]["best_mean_chi2_vs_observed"]) - 3.6573089934) < 1e-9
    assert abs(float(desj0408_smoke["aggregate"]["best_fraction_within_2sigma_box"]) - 0.9928) < 1e-12
    assert desj0408_full["verdict"]["desj0408_full_posterior_compatibility_smoke_passed"] is True
    assert desj0408_full["verdict"]["bounded_no_t2_baseline_reproduction_completed"] is False
    assert desj0408_full["verdict"]["real_data_T2_sampling_authorized"] is False
    assert desj0408_full["criteria"]["all_public_lens_model_posteriors_loaded"] is True
    assert desj0408_full["criteria"]["all_public_time_delay_files_matched"] is True
    assert desj0408_full["criteria"]["all_models_have_point_source_image_positions"] is True
    assert desj0408_full["criteria"]["image_level_fermat_or_arrival_time_recomputed"] is False
    assert desj0408_full["aggregate"]["model_count"] == 24
    assert desj0408_full["aggregate"]["sample_count_min"] == 10000
    assert desj0408_full["aggregate"]["parameter_count_min"] == 57
    assert desj0408_full["aggregate"]["parameter_count_max"] == 62
    assert desj0408_full["aggregate"]["global_best_logZ_family"] == "composite"
    assert (
        desj0408_full["aggregate"]["global_best_logZ_model_id"]
        == "0408_run918_1_1_1_0_0_1_1_0"
    )
    assert desj0408_arrival["verdict"]["desj0408_arrival_time_recompute_smoke_executed"] is True
    assert desj0408_arrival["verdict"]["current_reader_reproduces_public_time_delay_table"] is False
    assert (
        desj0408_arrival["verdict"][
            "occurrence_aware_parameter_alignment_reproduces_public_time_delay_table"
        ]
        is True
    )
    assert desj0408_arrival["verdict"]["simple_image_pair_relabeling_resolves_mismatch"] is False
    assert desj0408_arrival["verdict"]["bounded_no_t2_baseline_reproduction_completed"] is False
    assert desj0408_arrival["verdict"]["real_data_T2_sampling_authorized"] is False
    assert desj0408_arrival["criteria"]["arrival_time_recomputed_for_powerlaw_model"] is True
    assert desj0408_arrival["criteria"]["matches_public_time_delay_table_under_current_reader"] is False
    assert (
        desj0408_arrival["criteria"][
            "occurrence_aware_parameter_alignment_matches_public_table"
        ]
        is True
    )
    assert desj0408_arrival["criteria"]["simple_image_pair_relabeling_resolves_mismatch"] is False
    assert desj0408_arrival["result"]["recomputed_shape"] == [128, 2]
    assert desj0408_arrival["result"]["published_shape"] == [10000, 2]
    assert desj0408_arrival["result"]["matches_public_time_delay_table_under_current_reader"] is False
    assert desj0408_arrival["result"]["occurrence_aware_parameter_alignment_matches_public_table"] is True
    assert desj0408_arrival["result"]["old_param_count"] == 57
    assert desj0408_arrival["result"]["modern_param_count"] == 58
    assert desj0408_arrival["result"]["missing_modern_params_after_occurrence_alignment"] == [
        "s_scale_lens0"
    ]
    assert desj0408_arrival["result"]["aligned_rmse_days"] < 0.02
    assert desj0408_arrival["result"]["best_direct_pair_match"]["rmse_days"] > 80.0
    assert desj0408_powerlaw["verdict"]["desj0408_powerlaw_family_alignment_smoke_passed"] is False
    assert desj0408_powerlaw["verdict"]["desj0408_powerlaw_57_param_core_alignment_passed"] is True
    assert desj0408_powerlaw["verdict"]["desj0408_powerlaw_60_param_legacy_subset_blocked"] is True
    assert desj0408_powerlaw["verdict"]["real_data_T2_sampling_authorized"] is False
    assert desj0408_powerlaw["criteria"]["all_powerlaw_models_processed"] is True
    assert desj0408_powerlaw["criteria"]["raw_modern_reader_mismatch_confirmed"] is True
    assert desj0408_powerlaw["criteria"]["occurrence_aware_alignment_matches_all_powerlaw_tables"] is False
    assert desj0408_powerlaw["criteria"]["occurrence_aware_alignment_matches_57_param_subset"] is True
    assert desj0408_powerlaw["criteria"]["legacy_60_param_subset_still_blocked"] is True
    assert desj0408_powerlaw["aggregate"]["model_count"] == 12
    assert desj0408_powerlaw["aggregate"]["alignment_match_count"] == 5
    assert desj0408_powerlaw["aggregate"]["by_old_param_count"]["57"]["alignment_match_count"] == 5
    assert desj0408_powerlaw["aggregate"]["by_old_param_count"]["60"]["alignment_match_count"] == 0
    assert (
        desj0408_core_features["verdict"]["desj0408_powerlaw_57_core_feature_table_created"]
        is True
    )
    assert (
        desj0408_core_features["verdict"]["desj0408_powerlaw_57_core_rowwise_baseline_ready"]
        is False
    )
    assert (
        desj0408_core_features["verdict"][
            "desj0408_powerlaw_57_core_distributional_baseline_ready"
        ]
        is False
    )
    assert desj0408_core_features["verdict"]["real_data_T2_sampling_authorized"] is False
    assert desj0408_core_features["criteria"]["validated_57_param_core_only"] is True
    assert (
        desj0408_core_features["criteria"][
            "all_core_rows_reproduce_public_time_delay_prefix_rowwise"
        ]
        is False
    )
    assert desj0408_core_features["criteria"]["composite_models_included"] is False
    assert desj0408_core_features["criteria"]["legacy_60_param_models_included"] is False
    assert desj0408_core_features["aggregate"]["core_model_count"] == 5
    assert desj0408_core_features["aggregate"]["rowwise_usable_feature_row_count"] == 2
    assert desj0408_core_features["aggregate"]["distributional_usable_feature_row_count"] == 2
    assert (
        desj0408_core_features["aggregate"]["best_core_model_id_by_public_mean_chi2"]
        == "0408_run1001_0_0_0_0_0_1_1_0"
    )
    assert (
        desj0408_core_features["aggregate"]["best_core_model_id_by_relative_logZ_weight"]
        == "0408_run1001_0_0_0_0_0_1_1_0"
    )
    assert (
        desj0408_core_failures["verdict"][
            "desj0408_powerlaw_57_core_failure_diagnostic_created"
        ]
        is True
    )
    assert (
        desj0408_core_failures["verdict"][
            "failures_are_outlier_dominated_under_current_alignment"
        ]
        is True
    )
    assert desj0408_core_failures["verdict"]["broad_ordinary_row_failure_detected"] is False
    assert (
        desj0408_core_failures["verdict"][
            "strict_baseline_should_remain_2_model_core_without_outlier_policy"
        ]
        is True
    )
    assert desj0408_core_failures["verdict"]["real_data_T2_sampling_authorized"] is False
    assert desj0408_core_failures["aggregate"]["model_count"] == 6
    assert desj0408_core_failures["aggregate"]["strict_rowwise_pass_count"] == 2
    assert desj0408_core_failures["aggregate"]["failed_model_count"] == 4
    assert desj0408_core_failures["aggregate"]["outlier_dominated_failure_count"] == 4
    assert desj0408_core_failures["aggregate"]["broad_ordinary_row_failure_count"] == 0
    assert (
        desj0408_outlier_provenance["verdict"][
            "desj0408_powerlaw_57_core_outlier_provenance_created"
        ]
        is True
    )
    assert (
        desj0408_outlier_provenance["verdict"]["top_worst_rows_look_like_pairing_defects"]
        is True
    )
    assert (
        desj0408_outlier_provenance["verdict"][
            "top_worst_rows_look_like_parameter_outliers"
        ]
        is False
    )
    assert (
        desj0408_outlier_provenance["verdict"][
            "top_worst_rows_look_like_low_loglike_samples"
        ]
        is False
    )
    assert desj0408_outlier_provenance["verdict"]["real_data_T2_sampling_authorized"] is False
    assert desj0408_outlier_provenance["aggregate"]["failed_model_count"] == 4
    assert (
        desj0408_outlier_provenance["aggregate"][
            "top_worst_row_pairing_defect_candidate_count"
        ]
        == 4
    )
    assert desj0408_outlier_provenance["aggregate"]["top_worst_row_runtime_warning_count"] == 0
    assert (
        desj0408_row_linkage["verdict"]["desj0408_row_linkage_public_source_audit_created"]
        is True
    )
    assert desj0408_row_linkage["verdict"]["public_code_intends_index_order_linkage"] is True
    assert (
        desj0408_row_linkage["verdict"][
            "public_code_contains_no_independent_outlier_removal_policy"
        ]
        is True
    )
    assert desj0408_row_linkage["verdict"]["row_linkage_blocker_narrowed_but_not_cleared"] is True
    assert desj0408_row_linkage["verdict"]["real_data_T2_sampling_authorized"] is False
    assert (
        desj0408_row_linkage["criteria"][
            "compute_model_time_delays_iterates_by_sample_index"
        ]
        is True
    )
    assert desj0408_row_linkage["criteria"]["saved_time_delays_loaded_without_reordering"] is True
    assert desj0408_row_linkage["criteria"]["independent_row_removal_policy_found"] is False
    assert (
        desj0408_runtime["verdict"][
            "desj0408_legacy_runtime_compatibility_audit_created"
        ]
        is True
    )
    assert desj0408_runtime["verdict"]["runtime_mismatch_is_plausible_row_defect_source"] is True
    assert desj0408_runtime["verdict"]["legacy_runtime_not_reconstructed"] is True
    assert desj0408_runtime["verdict"]["real_data_T2_sampling_authorized"] is False
    assert desj0408_runtime["public_runtime_evidence"]["notebook_mentions_lenstronomy_0_9_2"] is True
    assert desj0408_runtime["public_runtime_evidence"]["notebook_language_info_python_version"] == "2.7.15"
    assert desj0408_runtime["current_helper_runtime"]["lenstronomy"] != "0.9.2"
    assert desj0408_runtime["criteria"]["legacy_semantics_reconstructed"] is False
    assert desj0408_tau_roles["verdict"]["desj0408_tau_role_constraints_created"] is True
    assert desj0408_tau_roles["verdict"]["common_morphology_lensing_role_cover_narrowed"] is True
    assert desj0408_tau_roles["verdict"]["physical_response_tau_lens_derived"] is False
    assert desj0408_tau_roles["criteria"]["introduces_t2_parameter"] is False
    assert desj0408_tau_roles["criteria"]["promotes_failed_models"] is False
    assert desj0408_tau_roles["aggregate"]["strict_clean_model_count"] == 2
    assert desj0408_tau_roles["aggregate"]["constraint_count"] == 7
    assert desj0408_tau_roles["aggregate"]["forced_constraint_count"] == 6
    assert (
        desj0408_time_residual["verdict"][
            "desj0408_no_t2_time_residual_candidate_audit_created"
        ]
        is True
    )
    assert (
        desj0408_time_residual["verdict"][
            "coherent_no_t2_time_residual_direction_observed"
        ]
        is True
    )
    assert desj0408_time_residual["verdict"]["bounded_t2_design_motivated"] is True
    assert (
        desj0408_time_residual["verdict"]["coherent_residual_is_clean_core_unique"]
        is False
    )
    assert desj0408_time_residual["verdict"]["coherence_alone_supports_t2_claim"] is False
    assert desj0408_time_residual["verdict"]["tau_specific_time_shift_evidence"] is False
    assert desj0408_time_residual["verdict"]["real_data_T2_sampling_authorized"] is False
    assert desj0408_time_residual["criteria"]["uses_only_strict_clean_no_t2_models"] is True
    assert desj0408_time_residual["criteria"]["fits_or_samples_t2"] is False
    assert desj0408_time_residual["criteria"]["uses_failed_desj0408_models"] is False
    assert desj0408_time_residual["criteria"]["negative_control_rows_checked"] is True
    assert (
        desj0408_time_residual["criteria"]["coherence_alone_is_specific_enough_for_t2_claim"]
        is False
    )
    assert desj0408_time_residual["aggregate"]["strict_clean_model_count"] == 2
    assert desj0408_time_residual["aggregate"]["min_pairwise_residual_cosine"] > 0.99
    assert (
        desj0408_time_residual["negative_controls"]["coherence_not_unique_to_clean_core"]
        is True
    )
    assert (
        desj0408_time_residual["negative_controls"]["nonclean_feature_rows"][
            "coherent_residual_direction_present"
        ]
        is True
    )
    assert desj0408_time_residual["negative_controls"]["nonclean_feature_rows"]["count"] == 3
    assert (
        abs(
            float(
                desj0408_time_residual["aggregate"][
                    "unweighted_model_minus_observed_dt1_days"
                ]
            )
            + 3.42512010294044
        )
        < 1e-12
    )
    assert (
        abs(
            float(
                desj0408_time_residual["aggregate"][
                    "unweighted_model_minus_observed_dt2_days"
                ]
            )
            - 19.844028900219328
        )
        < 1e-12
    )
    assert (
        desj0408_t2_design["verdict"][
            "desj0408_t2_null_comparison_design_freeze_created"
        ]
        is True
    )
    assert desj0408_t2_design["verdict"]["residual_direction_frozen_before_t2_fit"] is True
    assert desj0408_t2_design["verdict"]["null_competitors_frozen_before_t2_fit"] is True
    assert desj0408_t2_design["verdict"]["coherence_only_claim_blocked"] is True
    assert desj0408_t2_design["verdict"]["bounded_t2_fit_ready"] is False
    assert desj0408_t2_design["verdict"]["tau_specific_time_shift_evidence"] is False
    assert desj0408_t2_design["verdict"]["real_data_T2_sampling_authorized"] is False
    assert desj0408_t2_design["decision_policy"]["t2_fit_allowed_by_this_artifact"] is False
    assert desj0408_t2_design["decision_policy"]["real_data_T2_sampling_authorized"] is False
    assert (
        desj0408_t2_design["controls"]["coherent_residual_is_clean_core_unique"]
        is False
    )
    assert (
        desj0408_t2_design["controls"]["coherence_alone_supports_t2_claim"]
        is False
    )
    assert (
        abs(
            float(
                desj0408_t2_design["frozen_design_vector"][
                    "unweighted_observed_minus_model_days"
                ][0]
            )
            - 3.42512010294044
        )
        < 1e-12
    )
    assert len(desj0408_t2_design["rows"]) == 5
    assert (
        desj0408_t2_score["verdict"][
            "desj0408_one_amplitude_t2_operator_pretest_created"
        ]
        is True
    )
    assert desj0408_t2_score["verdict"]["minimal_one_amplitude_operator_defined"] is True
    assert desj0408_t2_score["verdict"]["frozen_direction_reduces_clean_residual"] is True
    assert desj0408_t2_score["verdict"]["frozen_direction_beats_scramble_controls"] is True
    assert desj0408_t2_score["verdict"]["nonclean_control_also_improves"] is True
    assert desj0408_t2_score["verdict"]["directional_score_supports_design_followup"] is True
    assert desj0408_t2_score["verdict"]["t2_specific_time_shift_evidence"] is False
    assert desj0408_t2_score["verdict"]["bounded_t2_fit_ready"] is False
    assert desj0408_t2_score["verdict"]["real_data_T2_sampling_authorized"] is False
    assert desj0408_t2_score["criteria"]["fits_or_samples_t2_posterior"] is False
    assert desj0408_t2_score["criteria"]["endpoint_blind"] is False
    assert desj0408_t2_score["criteria"]["tau_derived_operator"] is False
    assert desj0408_t2_score["operator"]["endpoint_blind"] is False
    assert desj0408_t2_score["operator"]["tau_derived"] is False
    assert desj0408_t2_score["aggregate"]["candidate_rmse_after_days"] < (
        desj0408_t2_score["aggregate"]["candidate_rmse_before_days"]
    )
    assert desj0408_t2_score["aggregate"]["nonclean_control_also_improves"] is True
    assert len(desj0408_t2_score["rows"]) == 6
    assert (
        desj0408_holdout["verdict"]["desj0408_t2_holdout_readiness_audit_created"]
        is True
    )
    assert desj0408_holdout["verdict"]["independent_holdout_score_ready_now"] is False
    assert desj0408_holdout["verdict"]["best_current_holdout_target"] == "WGD2038-4008"
    assert desj0408_holdout["verdict"]["best_current_holdout_readiness_score_0_to_6"] == 3
    assert desj0408_holdout["verdict"]["wgd2038_is_best_next_holdout_route"] is True
    assert desj0408_holdout["verdict"]["des_one_amplitude_score_remains_design_only"] is True
    assert desj0408_holdout["verdict"]["real_data_T2_sampling_authorized"] is False
    assert (
        desj0408_holdout["best_current_holdout_target"]["can_apply_des_frozen_score_now"]
        is False
    )
    assert len(desj0408_holdout["rows"]) == 3
    assert (
        wgd2038_contract["verdict"]["wgd2038_holdout_extraction_contract_created"]
        is True
    )
    assert wgd2038_contract["verdict"]["per_sample_contract_defined"] is True
    assert wgd2038_contract["verdict"]["expected_joblib_targets_identified"] is True
    assert wgd2038_contract["verdict"]["can_extract_holdout_table_now"] is False
    assert wgd2038_contract["verdict"]["can_apply_des_frozen_score_now"] is False
    assert wgd2038_contract["verdict"]["real_data_T2_sampling_authorized"] is False
    assert wgd2038_contract["contract_counts"]["required_field_count"] == 15
    assert wgd2038_contract["contract_counts"]["expected_joblib_target_count"] == 36
    assert len(wgd2038_contract["rows"]) == 15
    assert wgd2038_partial["verdict"]["wgd2038_partial_holdout_materialized"] is True
    assert wgd2038_partial["verdict"]["public_model_level_manifest_created"] is True
    assert wgd2038_partial["verdict"]["public_ddt_kappa_support_materialized"] is True
    assert wgd2038_partial["verdict"]["per_sample_score_table_materialized"] is False
    assert wgd2038_partial["verdict"]["can_apply_des_frozen_score_now"] is False
    assert wgd2038_partial["verdict"]["real_data_T2_sampling_authorized"] is False
    assert wgd2038_partial["materialization_counts"]["expected_model_target_count"] == 36
    assert wgd2038_partial["materialization_counts"]["materialized_model_manifest_rows"] == 36
    assert wgd2038_partial["materialization_counts"]["score_ready_model_rows"] == 0
    assert wgd2038_partial["public_payload_stats"]["ddt_sample_count"] == 567880
    assert (
        wgd2038_fermat_preflight["verdict"][
            "wgd2038_bounded_local_fermat_preflight_created"
        ]
        is True
    )
    assert (
        wgd2038_fermat_preflight["verdict"][
            "bounded_local_image_fermat_table_materialized"
        ]
        is True
    )
    assert (
        wgd2038_fermat_preflight["verdict"]["uses_converged_or_published_wgd_posterior"]
        is False
    )
    assert wgd2038_fermat_preflight["verdict"]["can_apply_des_frozen_score_now"] is False
    assert wgd2038_fermat_preflight["verdict"]["real_data_T2_sampling_authorized"] is False
    assert wgd2038_fermat_preflight["counts"]["successful_job_count"] == 3
    assert wgd2038_fermat_preflight["counts"]["image_row_count"] == 12
    assert wgd2038_fermat_preflight["counts"]["score_ready_row_count"] == 0
    assert (
        wgd2038_observed_smoke["verdict"]["wgd2038_observed_delay_vector_materialized"]
        is True
    )
    assert (
        wgd2038_observed_smoke["verdict"][
            "wgd2038_observed_delay_covariance_materialized"
        ]
        is True
    )
    assert (
        wgd2038_observed_smoke["verdict"]["wgd2038_no_t2_residual_smoke_computed"]
        is True
    )
    assert (
        wgd2038_observed_smoke["verdict"]["uses_converged_or_published_wgd_posterior"]
        is False
    )
    assert wgd2038_observed_smoke["verdict"]["can_apply_des_frozen_score_now"] is False
    assert wgd2038_observed_smoke["verdict"]["real_data_T2_sampling_authorized"] is False
    assert wgd2038_observed_smoke["verdict"]["t2_specific_time_shift_evidence"] is False
    assert (
        wgd2038_observed_smoke["published_time_delay_vector"]["values"]["AB"]
        == -12.4
    )
    assert (
        wgd2038_observed_smoke["published_time_delay_vector"]["values"]["AC"]
        == -5.3
    )
    assert (
        wgd2038_observed_smoke["published_time_delay_vector"]["values"]["AD"]
        == -33.3
    )
    assert wgd2038_observed_smoke["published_time_delay_covariance"]["pair_order"] == [
        "AB",
        "AC",
        "AD",
    ]
    assert wgd2038_observed_smoke["counts"]["delay_pair_row_count"] == 9
    assert wgd2038_observed_smoke["counts"]["score_ready_row_count"] == 0
    assert (
        wgd2038_published_shape["verdict"][
            "published_model_delay_shape_crosscheck_created"
        ]
        is True
    )
    assert wgd2038_published_shape["verdict"]["uses_published_model_predictions"] is True
    assert (
        wgd2038_published_shape["verdict"]["uses_published_observed_delay_measurement"]
        is True
    )
    assert wgd2038_published_shape["verdict"]["uses_missing_posterior_payload"] is False
    assert wgd2038_published_shape["verdict"]["single_scale_shape_residual_present"] is True
    assert wgd2038_published_shape["verdict"]["can_apply_des_frozen_score_now"] is False
    assert wgd2038_published_shape["verdict"]["real_data_T2_sampling_authorized"] is False
    assert wgd2038_published_shape["verdict"]["t2_specific_time_shift_evidence"] is False
    best_shape = wgd2038_published_shape["best_scalar_shape_match"]
    assert best_shape["model_id"] == "lenstronomy_combined_h0_70_flat_lcdm"
    assert abs(float(best_shape["best_scalar_scale"]) - 1.1015098079922812) < 1e-12
    assert (
        abs(float(best_shape["normalized_shape_rmse_sigma_units"]) - 2.28949269020861)
        < 1e-12
    )
    assert (
        abs(float(best_shape["implied_h0_if_pure_scale_from_h0_70"]) - 63.549139092632146)
        < 1e-12
    )
    assert len(wgd2038_published_shape["rows"]) == 6
    assert (
        wgd2038_shape_target["verdict"]["wgd2038_delay_shape_holdout_target_created"]
        is True
    )
    assert (
        wgd2038_shape_target["verdict"]["target_frozen_before_posterior_level_wgd_score"]
        is True
    )
    assert wgd2038_shape_target["verdict"]["posterior_level_score"] is False
    assert wgd2038_shape_target["verdict"]["endpoint_blind"] is False
    assert wgd2038_shape_target["verdict"]["real_data_T2_sampling_authorized"] is False
    assert wgd2038_shape_target["verdict"]["t2_specific_time_shift_evidence"] is False
    target_values = wgd2038_shape_target["target_values"]
    assert (
        abs(float(target_values["target_residual_days"]["AB"]) + 6.892450960038595)
        < 1e-12
    )
    assert (
        abs(float(target_values["target_residual_days"]["AC"]) - 5.715098079922812)
        < 1e-12
    )
    assert (
        abs(float(target_values["target_residual_days"]["AD"]) + 6.643462646586794)
        < 1e-12
    )
    assert (
        abs(float(target_values["covariance_metric_norm_sigma_units"]) - 3.237831613447079)
        < 1e-12
    )
    assert len(wgd2038_shape_target["rows"]) == 3
    assert (
        wgd2038_delay_linkage["verdict"]["wgd2038_observed_delay_linkage_audit_created"]
        is True
    )
    assert wgd2038_delay_linkage["verdict"]["published_observed_delay_measurement_exists"] is True
    assert (
        wgd2038_delay_linkage["verdict"][
            "local_machine_readable_observed_delay_vector_present"
        ]
        is True
    )
    assert wgd2038_delay_linkage["verdict"]["bounded_no_t2_residual_smoke_present"] is True
    assert (
        wgd2038_delay_linkage["verdict"][
            "predeclared_delay_shape_holdout_target_present"
        ]
        is True
    )
    assert (
        wgd2038_delay_linkage["verdict"][
            "predeclared_delay_shape_holdout_target_endpoint_blind"
        ]
        is False
    )
    assert (
        wgd2038_delay_linkage["verdict"][
            "predeclared_delay_shape_holdout_target_posterior_level_score"
        ]
        is False
    )
    assert (
        wgd2038_delay_linkage["verdict"]["missing_score_ready_component"]
        == "converged_or_published_wgd_fermat_posterior_table"
    )
    assert wgd2038_delay_linkage["verdict"]["local_bounded_fermat_parity_preflight_present"] is True
    assert wgd2038_delay_linkage["verdict"]["can_compute_wgd_no_t2_residual_vector_now"] is True
    assert wgd2038_delay_linkage["verdict"]["can_apply_des_frozen_score_now"] is False
    assert wgd2038_delay_linkage["verdict"]["real_data_T2_sampling_authorized"] is False

    reconstruction = (
        RESULTS / "tau_core_lensing_wgd2038_lenstronomy_hst_reproduction_v1" / "RECONSTRUCTION.md"
    ).read_text(encoding="utf-8")
    assert "Raw payloads are intentionally not versioned" in reconstruction
    assert "bounded local model-plumbing smoke" in reconstruction
    assert "physical PEMD backend is available" in reconstruction
    assert "posterior-plumbing pilot" in reconstruction
    assert "finite `(4240, 53)` sample payload" in reconstruction
    assert "finite `(12720, 53)` sample" in reconstruction
    assert "finite `(25440, 53)` sample" in reconstruction
    assert "diagnostic120 continuation" in reconstruction
    assert "second diagnostic120 continuation" in reconstruction
    assert "cold diagnostic120 continuation" in reconstruction
    assert "parameter-level split-half drift diagnostic" in reconstruction
    assert "profile_freeze_v1_bounded_diagnostic" in reconstruction
    assert "profile_freeze_v1" in reconstruction
    assert "profile_freeze_v2" in reconstruction
    assert "real-data T2 evidence" in reconstruction


def test_derived_tables_exist():
    required = [
        DATA / "public_deep_repository_target_status.csv",
        DATA / "he0435_public_repro_model_level_psf_validation.csv",
        DATA / "hff_static_control_scorecard.csv",
        DATA / "static_control_null_stress_sweep.csv",
        DATA / "static_control_report_card_gates.csv",
        DATA / "static_control_systematic_template_sweep.csv",
        DATA / "real_data_t2_eligibility_audit_v1.csv",
        DATA / "wgd2038_field_level_payload_audit_v1.csv",
        DATA / "wgd2038_public_payload_acquisition_manifest_v1.csv",
        DATA / "wgd2038_lenstronomy_hst_reproduction_manifest_v1.csv",
        DATA / "wgd2038_mcmc_parameter_drift_diagnostic_v1.csv",
        DATA / "wgd2038_nuisance_stabilization_plan_v1.csv",
        DATA / "alternate_real_data_source_candidate_audit_v1.csv",
        DATA / "desj0408_no_t2_baseline_smoke_v1.csv",
        DATA / "desj0408_full_posterior_compat_smoke_v1.csv",
        DATA / "desj0408_powerlaw_family_alignment_smoke_v1.csv",
        DATA / "desj0408_powerlaw_57_core_feature_table_v1.csv",
        DATA / "desj0408_powerlaw_57_core_failure_diagnostic_v1.csv",
        DATA / "desj0408_powerlaw_57_core_outlier_provenance_v1.csv",
        DATA / "desj0408_row_linkage_public_source_audit_v1.csv",
        DATA / "desj0408_legacy_runtime_compatibility_audit_v1.csv",
        DATA / "desj0408_tau_role_constraints_v1.csv",
        DATA / "desj0408_no_t2_time_residual_candidate_v1.csv",
        DATA / "desj0408_t2_null_comparison_design_freeze_v1.csv",
        DATA / "desj0408_one_amplitude_t2_operator_pretest_v1.csv",
        DATA / "desj0408_t2_holdout_readiness_v1.csv",
        DATA / "wgd2038_holdout_extraction_contract_v1.csv",
        DATA / "wgd2038_partial_holdout_materialization_v1.csv",
        DATA / "wgd2038_bounded_local_fermat_preflight_v1.csv",
        DATA / "wgd2038_arxiv_source_table_payload_v1.csv",
        DATA / "wgd2038_observed_delay_no_t2_smoke_v1.csv",
        DATA / "wgd2038_published_model_delay_shape_crosscheck_v1.csv",
        DATA / "wgd2038_delay_shape_holdout_target_v1.csv",
        DATA / "wgd2038_observed_delay_linkage_audit_v1.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_arxiv_source_package_exists_and_is_source_only():
    archive_path = ROOT / "arxiv_submission_source.zip"
    assert archive_path.exists()
    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())
    assert "main.tex" in names
    assert "refs.bib" in names
    assert "main.pdf" not in names
    assert "figures/fig01_observer_principle_lensing_schematic.png" in names
    assert not any(name.endswith((".aux", ".log", ".out", ".toc", ".blg", ".bbl")) for name in names)


def test_reproduction_script_reports_completion():
    result = subprocess.run(
        ["python", "scripts/build_arxiv_source.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "arxiv_submission_source.zip" in result.stdout
