import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_paper8_source_forward_time_handoff_v1"
    / "summary.json"
)


def test_source_forward_handoff_claim_boundary():
    subprocess.run(
        [sys.executable, "scripts/build_paper8_source_forward_time_handoff.py"],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert payload["theory_contract"]["complete_descriptor"] == (
        "R_O^body=(Theta_M,U_BF Phi_M)"
    )
    assert payload["identifiability"]["delay_only_orthogonal_dimension"] == 0
    assert payload["identifiability"]["rank_repair_required"] is True
    assert payload["authorization"]["source_forward_h_tau_materialized"] is False
    assert (
        payload["authorization"]["extended_nuisance_orthogonality_score_authorized"]
        is False
    )
    assert payload["authorization"]["real_data_T2_sampling_authorized"] is False
    assert payload["authorization"]["time_distortion_detection_claim_allowed"] is False
    target = payload["target_local_materialization"]
    assert target["single_source_frozen_body_descriptor_materialized"] is False
    assert target["multisource_triangle_common_body_owner"] is False
    assert target["image_paths_are_body_coordinates"] is False
    assert target["direct_relative_clock_rate_central_estimate"] > 1
    assert target["direct_relative_clock_rate_stable"] is False
    assert target["direct_relative_clock_rate_tau_claim_allowed"] is False
    assert target["direct_relative_clock_rate_null_rate_p_value"] > 0.05
    assert target["direct_relative_clock_rate_null_improvement_p_value"] > 0.05
    assert target["unit_stretch_rejected_under_parametric_mock"] is False
    assert target["direct_relative_clock_correlated_rate_p_value"] > 0.05
    assert target["direct_relative_clock_correlated_improvement_p_value"] > 0.05
    assert (
        target["direct_relative_clock_supported_after_correlated_null"] is False
    )
    assert abs(target["independent_he0435_relative_clock_rate"] - 1) < 0.01
    assert target["independent_he0435_clock_rate_p_value"] > 0.05
    assert target["independent_he0435_path_clock_supported"] is False
    assert target["differential_clock_null_is_control_only"] is True
    assert target["strict_unlensed_pair_matching_ready"] is False
    assert target["strict_unlensed_control_count"] == 2
    assert target["common_mode_clock_test_executed"] is False
    assert target["stable_scalar_host_trace_materialized"] is True
    assert target["scalar_transport_exactly_factorizes"] is True
    assert target["independent_scalar_body_path_information_materialized"] is False
    assert target["ordinal_tensor_path_interaction_materialized"] is True
    assert target["amplitude_stable_tensor_path_interaction_materialized"] is False
    assert target["internal_model_holdout_ordinal_signature_replicated"] is True
    assert target["independent_target_replication"] is False
    assert target["coordinate_free_morphology_path_control_materialized"] is True
    assert (
        target["tau_specific_information_beyond_standard_lensing_materialized"]
        is False
    )
    assert (
        target["sfh_01_representation_compatible_scalar_class_materialized"]
        is True
    )
    assert target["physical_body_clock_identified"] is False
    assert target["logarithmic_clock_shape_conditionally_selected"] is True
    assert target["multiplicative_body_composition_physically_proved"] is False
    assert target["absolute_clock_scale_selected"] is False
    assert target["moment_area_multiplicative_character_exact"] is True
    assert target["trace_stable_on_expanded_model_family"] is False
    assert target["area_character_stable_on_expanded_model_family"] is False
    assert target["local_endpoint_log_area_clock_branch_closed"] is True
    assert target["log_area_contrast_reduces_to_standard_magnification"] is True
    assert target["full_causal_support_clock_still_open"] is True
    assert target["modeled_cone_descriptor_materialized"] is True
    assert target["modeled_cone_component_counts"] == [8]
    assert target["modeled_cone_lens_plane_counts"] == [3]
    assert (
        target["complete_physical_light_cone_morphology_materialized"] is False
    )
    assert target["standard_multiplane_lensing_information_only"] is True
    assert target["observed_los_morphology_materialized"] is True
    assert target["materialized_spectroscopic_galaxy_row_count"] == 198
    assert target["identified_los_group_count"] == 10
    assert target["reported_spectroscopic_completeness"]["fraction"] == 0.68
    assert target["los_physical_path_transport_assigned"] is False
    assert target["redshift_dependent_four_path_geometry_materialized"] is True
    assert target["los_path_geometry_row_count"] == 9504
    assert target["published_leading_order_flexion_transport_materialized"] is True
    assert target["complete_physical_environment_transport_materialized"] is False
    assert target["all_above_threshold_objects_already_explicitly_modeled"] is True
    assert target["collective_oriented_subthreshold_structure_nonzero"] is True
    assert target["subthreshold_not_representable_by_spin0_spin2_summary"] is True
    assert target["subthreshold_standard_higher_order_lensing_information"] is True
    assert target["naive_sis_population_physical_completion_rejected"] is True
    assert target["local_higher_order_or_truncated_halo_transport_required"] is True
    assert target["local_non_tidal_transport_nonzero_after_affine_projection"] is True
    assert target["local_cubic_models_above_conservative_flexion_scale"] == 12
    assert target["local_cubic_transport_is_standard_conditional_completion"] is True
    assert target["direct_astrometric_endpoint_authorized"] is False
    assert target["extended_arc_endpoint_preferred"] is True
    assert target["f814w_arc_template_materialized"] is True
    assert target["f814w_endpoint_previously_opened"] is True
    assert target["f814w_confirmatory_evidence_allowed"] is False
    assert target["f814w_template_residual_cosine"] < 0
    assert target["f814w_fixed_amplitude_fractional_sse_reduction"] < 0
    assert target["f814w_exploratory_alignment_positive"] is False
    assert target["reported_kappa_ext_median_interval"] == [-0.05, -0.04]
    assert target["reported_kappa_ext_approximate_width"] == 0.03
    assert target["new_f814w_template_from_kappa_ext_authorized"] is False
    assert target["kappa_ext_time_delay_nuisance_required"] is True
    assert target["strict_delay_dimension_after_kappa_marginalization"] == 0
    assert target["practical_weak_direction_survives_geometrically"] is True
    assert target["practical_weak_direction_is_kappa_free"] is False
    assert target["kappa_weak_projection_at_reported_width_sigma"] < 0.1
    assert target["wgd2038_published_summary_nuisance_rank"] == 2
    assert target["wgd2038_remaining_summary_delay_dimension"] == 1
    assert abs(target["wgd2038_observed_candidate_projection_sigma"]) > 2.5
    assert target["wgd2038_candidate_frozen_before_endpoint_projection"] is True
    assert target["wgd2038_posterior_level_nuisance_span_materialized"] is False
    assert target["wgd2038_confirmatory_tau_score_allowed"] is False
    assert len(payload["rows"]) == 8
