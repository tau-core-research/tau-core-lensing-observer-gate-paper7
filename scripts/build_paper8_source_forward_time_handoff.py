#!/usr/bin/env python3
"""Build the Paper 8 -> Paper 7 source-forward observer-time handoff.

This artifact defines the inputs required before a new Tau time-delay score is
allowed. It does not construct values from observed delay residuals.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data/derived"
OUT_DIR = DERIVED / "repro_results/tau_core_lensing_paper8_source_forward_time_handoff_v1"
CSV_PATH = DERIVED / "paper8_source_forward_time_handoff_v1.csv"


def main() -> None:
    morphology_path = DERIVED / (
        "repro_results/tau_core_lensing_desj0408_source_morphology_triangle_v1/"
        "summary.json"
    )
    morphology = json.loads(morphology_path.read_text(encoding="utf-8"))
    morphology_ready = bool(
        morphology["sfh_02_relative_morphology_materialized"]
    )
    pullback_path = DERIVED / (
        "repro_results/tau_core_lensing_desj0408_image_path_pullbacks_v1/"
        "summary.json"
    )
    pullback = json.loads(pullback_path.read_text(encoding="utf-8"))
    pullback_ready = bool(pullback["sfh_03_path_pullback_materialized"])
    host_path = DERIVED / (
        "repro_results/tau_core_lensing_desj0408_single_body_host_descriptor_v1/"
        "summary.json"
    )
    host = json.loads(host_path.read_text(encoding="utf-8"))
    ownership_path = DERIVED / (
        "repro_results/tau_core_lensing_desj0408_body_ownership_v1/"
        "summary.json"
    )
    ownership = json.loads(ownership_path.read_text(encoding="utf-8"))
    relative_clock_path = DERIVED / (
        "repro_results/tau_core_lensing_desj0408_ab_relative_clock_rate_v1/"
        "summary.json"
    )
    relative_clock = json.loads(
        relative_clock_path.read_text(encoding="utf-8")
    )
    relative_clock_null_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_ab_relative_clock_rate_null_calibration_v1/"
        "summary.json"
    )
    relative_clock_null = json.loads(
        relative_clock_null_path.read_text(encoding="utf-8")
    )
    correlated_clock_null_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_ab_correlated_clock_null_v1/summary.json"
    )
    correlated_clock_null = json.loads(
        correlated_clock_null_path.read_text(encoding="utf-8")
    )
    he0435_clock_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_he0435_bc_relative_clock_rate_v1/summary.json"
    )
    he0435_clock = json.loads(
        he0435_clock_path.read_text(encoding="utf-8")
    )
    common_clock_support_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_unlensed_control_support_v1/summary.json"
    )
    common_clock_support = json.loads(
        common_clock_support_path.read_text(encoding="utf-8")
    )
    positive_host_path = DERIVED / (
        "repro_results/tau_core_lensing_desj0408_positive_host_moment_v1/"
        "summary.json"
    )
    positive_host = json.loads(positive_host_path.read_text(encoding="utf-8"))
    scalar_coupling_path = DERIVED / (
        "repro_results/tau_core_lensing_desj0408_scalar_body_path_coupling_v1/"
        "summary.json"
    )
    scalar_coupling = json.loads(
        scalar_coupling_path.read_text(encoding="utf-8")
    )
    tensor_path_path = DERIVED / (
        "repro_results/tau_core_lensing_desj0408_joint_tensor_path_interaction_v1/"
        "summary.json"
    )
    tensor_path = json.loads(tensor_path_path.read_text(encoding="utf-8"))
    tensor_holdout_path = DERIVED / (
        "repro_results/tau_core_lensing_desj0408_tensor_path_ordinal_holdout_v1/"
        "summary.json"
    )
    tensor_holdout = json.loads(
        tensor_holdout_path.read_text(encoding="utf-8")
    )
    canonical_path_signature_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_coordinate_free_path_signature_v1/"
        "summary.json"
    )
    canonical_path_signature = json.loads(
        canonical_path_signature_path.read_text(encoding="utf-8")
    )
    scalar_clock_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_scalar_clock_nonidentifiability_v1/"
        "summary.json"
    )
    scalar_clock = json.loads(
        scalar_clock_path.read_text(encoding="utf-8")
    )
    log_clock_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_log_clock_composition_selection_v1/"
        "summary.json"
    )
    log_clock = json.loads(log_clock_path.read_text(encoding="utf-8"))
    area_character_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_moment_area_character_v1/"
        "summary.json"
    )
    area_character = json.loads(
        area_character_path.read_text(encoding="utf-8")
    )
    log_area_path_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_log_area_path_contrast_v1/"
        "summary.json"
    )
    log_area_path = json.loads(
        log_area_path_path.read_text(encoding="utf-8")
    )
    modeled_cone_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_modeled_cone_morphology_v1/"
        "summary.json"
    )
    modeled_cone = json.loads(
        modeled_cone_path.read_text(encoding="utf-8")
    )
    strides_los_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_strides_los_morphology_v1/"
        "summary.json"
    )
    strides_los = json.loads(
        strides_los_path.read_text(encoding="utf-8")
    )
    los_transport_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_los_path_transport_geometry_v1/"
        "summary.json"
    )
    los_transport = json.loads(
        los_transport_path.read_text(encoding="utf-8")
    )
    collective_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_subthreshold_collective_flexion_v1/"
        "summary.json"
    )
    collective = json.loads(
        collective_path.read_text(encoding="utf-8")
    )
    sis_countermodel_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_subthreshold_exact_multiplane_v1/"
        "summary.json"
    )
    sis_countermodel = json.loads(
        sis_countermodel_path.read_text(encoding="utf-8")
    )
    local_cubic_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_local_cubic_los_transport_v1/"
        "summary.json"
    )
    local_cubic = json.loads(
        local_cubic_path.read_text(encoding="utf-8")
    )
    astrometric_endpoint_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_local_cubic_astrometric_endpoint_v1/"
        "summary.json"
    )
    astrometric_endpoint = json.loads(
        astrometric_endpoint_path.read_text(encoding="utf-8")
    )
    arc_template_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_local_cubic_f814w_arc_template_v1/"
        "summary.json"
    )
    arc_template = json.loads(
        arc_template_path.read_text(encoding="utf-8")
    )
    collective_completion_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_collective_los_completion_decision_v1/"
        "summary.json"
    )
    collective_completion = json.loads(
        collective_completion_path.read_text(encoding="utf-8")
    )
    kappa_rank_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_desj0408_kappa_marginalized_delay_rank_v1/"
        "summary.json"
    )
    kappa_rank = json.loads(kappa_rank_path.read_text(encoding="utf-8"))
    wgd_summary_rank_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_wgd2038_published_summary_nuisance_rank_v1/"
        "summary.json"
    )
    wgd_summary_rank = json.loads(
        wgd_summary_rank_path.read_text(encoding="utf-8")
    )
    wgd_family_rank_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_wgd2038_mass_family_delay_rank_v1/"
        "summary.json"
    )
    wgd_family_rank = json.loads(
        wgd_family_rank_path.read_text(encoding="utf-8")
    )
    wgd_kinematic_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_wgd2038_kinematic_holdout_independence_v1/"
        "summary.json"
    )
    wgd_kinematic = json.loads(
        wgd_kinematic_path.read_text(encoding="utf-8")
    )
    wgd_oiii_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_wgd2038_oiii_distinct_terminal_v1/"
        "summary.json"
    )
    wgd_oiii = json.loads(wgd_oiii_path.read_text(encoding="utf-8"))
    wgd_flux_completion_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_wgd2038_standard_flux_completion_payload_v1/"
        "summary.json"
    )
    wgd_flux_completion = json.loads(
        wgd_flux_completion_path.read_text(encoding="utf-8")
    )
    wgd_cross_amplitude_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_wgd2038_cross_amplitude_stability_v1/"
        "summary.json"
    )
    wgd_cross_amplitude = json.loads(
        wgd_cross_amplitude_path.read_text(encoding="utf-8")
    )
    wgd_prior_smoke_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_wgd2038_warm_dust_prior_predictive_smoke_v1/"
        "summary.json"
    )
    wgd_prior_smoke = json.loads(
        wgd_prior_smoke_path.read_text(encoding="utf-8")
    )
    wgd_prior_n64_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_wgd2038_warm_dust_prior_predictive_n64_v1/"
        "summary.json"
    )
    wgd_prior_n64 = json.loads(
        wgd_prior_n64_path.read_text(encoding="utf-8")
    )
    wgd_reweighted_n256_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_wgd2038_warm_dust_likelihood_reweighting_n256_v1/"
        "summary.json"
    )
    wgd_reweighted_n256 = json.loads(
        wgd_reweighted_n256_path.read_text(encoding="utf-8")
    )
    wgd_oiii_compatibility_path = DERIVED / (
        "repro_results/"
        "tau_core_lensing_wgd2038_oiii_prior_predictive_compatibility_v1/"
        "summary.json"
    )
    wgd_oiii_compatibility = json.loads(
        wgd_oiii_compatibility_path.read_text(encoding="utf-8")
    )
    remaining = ["SFH_01"]
    if not morphology_ready:
        remaining.append("SFH_02")
    if not pullback_ready:
        remaining.append("SFH_03")
    remaining.append("SFH_04")
    rows = [
        {
            "field_id": "SFH_01_BODY_CLOCK",
            "symbol": "Theta_M",
            "source_owner": "stabilized_morphological_body",
            "required_shape": "one source-frozen scalar per evaluated body/path section",
            "endpoint_blind_requirement": "must not use measured time-delay residuals",
            "current_status": (
                "rank_one_common_scalar_class_materialized_but_clock_law_nonunique"
                if scalar_clock[
                    "sfh_01_representation_compatible_scalar_class_materialized"
                ]
                else "theory_defined_numeric_lens_map_missing"
            ),
        },
        {
            "field_id": "SFH_02_RELATIVE_MORPHOLOGY",
            "symbol": "U_BF_Phi_M",
            "source_owner": "paper8_morphology_forward_readout",
            "required_shape": "three relative coordinates in one frozen common frame",
            "endpoint_blind_requirement": "must be frozen from morphology/source data before delay opening",
            "current_status": (
                "DESJ0408_delay_blind_morphology_triangle_materialized"
                if morphology_ready
                else "paper8_bridge_mapping_required"
            ),
        },
        {
            "field_id": "SFH_03_PATH_PULLBACK",
            "symbol": "R_gamma_i",
            "source_owner": "observer_source_path_geometry",
            "required_shape": "one declared pullback for every lens image path",
            "endpoint_blind_requirement": "image order, parity and path rule fixed before delay scoring",
            "current_status": (
                "DESJ0408_four_local_image_path_pullbacks_materialized"
                if pullback_ready
                else "formula_required"
            ),
        },
        {
            "field_id": "SFH_04_TIME_COVECTOR",
            "symbol": "a_O",
            "source_owner": "body_descriptor_descent",
            "required_shape": "quotient-basic one-form or discrete path cochain",
            "endpoint_blind_requirement": "derived from Theta_M and U_BF_Phi_M without fitted delay direction",
            "current_status": "numeric_source_forward_map_missing",
        },
        {
            "field_id": "SFH_05_TAU_PREDICTOR",
            "symbol": "h_tau",
            "source_owner": "equal_endpoint_path_contrast",
            "required_shape": "one contrast per independent image path against a frozen reference",
            "endpoint_blind_requirement": "h_tau fixed before observed delays enter the analysis",
            "current_status": "blocked_by_SFH_01_to_SFH_04",
        },
        {
            "field_id": "SFH_06_NUISANCE_JACOBIAN",
            "symbol": "J_GR",
            "source_owner": "paper7_no_T2_model_ensemble",
            "required_shape": "complete independently constrained standard-model tangent matrix",
            "endpoint_blind_requirement": "basis frozen without using h_tau fit improvement",
            "current_status": "delay_only_rank_two_DES_available_extended_joint_space_missing",
        },
        {
            "field_id": "SFH_07_RANK_REPAIR",
            "symbol": "Y_aux",
            "source_owner": "held_out_image_or_path_sensitive_readout",
            "required_shape": "at least one observable outside the two-delay nuisance span",
            "endpoint_blind_requirement": "predeclared before Tau projection",
            "current_status": "required_by_DES_delay_only_no_go",
        },
        {
            "field_id": "SFH_08_HOLDOUT",
            "symbol": "H_holdout",
            "source_owner": "independent_lens_or_frozen_band",
            "required_shape": "one untouched replication endpoint",
            "endpoint_blind_requirement": "all maps, units and decision thresholds frozen upstream",
            "current_status": "WGD2038_posterior_payload_blocked_LOBO_negative_control_available",
        },
    ]

    summary = {
        "schema": "paper7 Paper8-source-forward observer-time handoff v1",
        "purpose": (
            "Replace the residual-derived T2 direction by a source-forward handoff "
            "from the body descriptor R_O^body=(Theta_M,U_BF Phi_M)."
        ),
        "theory_contract": {
            "complete_descriptor": "R_O^body=(Theta_M,U_BF Phi_M)",
            "observer_null": "ker(D Theta_M) intersect ker(D Phi_M)",
            "path_contrast": "h_tau[i]=Integral(gamma_i,a_O)-Integral(gamma_ref,a_O)",
            "factorization_rule": "a_O must be basic on the complete body-observer null",
            "absolute_time_scale_status": "not selected by quotient geometry",
        },
        "paper_relationship": {
            "paper8_role": "source-side morphology/body coordinate supply",
            "paper7_role": "observer-path pullback, nuisance separation and held-out test",
            "paper7_old_residual_direction_role": "demoted_to_design_control_not_tau_predictor",
        },
        "identifiability": {
            "desj0408_delay_output_dimension": 2,
            "desj0408_delay_nuisance_rank": 2,
            "delay_only_orthogonal_dimension": 0,
            "delay_only_test_authorized": False,
            "rank_repair_required": True,
            "minimum_joint_output_dimension_before_possible_rank_repair": 3,
        },
        "authorization": {
            "sfh_02_relative_morphology_materialized": morphology_ready,
            "sfh_03_path_pullback_materialized": pullback_ready,
            "source_forward_h_tau_materialized": False,
            "extended_nuisance_orthogonality_score_authorized": False,
            "real_data_T2_sampling_authorized": False,
            "time_distortion_detection_claim_allowed": False,
        },
        "decision_rule": {
            "score_only_if": [
                "SFH_01 through SFH_07 are source-frozen",
                "h_tau is nonzero before endpoint opening",
                "weighted projection of h_tau outside the complete nuisance span is nonzero",
                "the same frozen construction is evaluated on SFH_08",
            ],
            "reject_or_demote_if": [
                "h_tau is created from observed delay residuals",
                "the joint nuisance span saturates the enlarged output space",
                "the signal disappears under mandatory PSF or lens-family controls",
            ],
        },
        "rows": rows,
        "target_local_materialization": {
            "target": morphology["target"],
            "sfh_02_artifact": str(morphology_path.relative_to(ROOT)),
            "sfh_03_artifact": str(pullback_path.relative_to(ROOT)),
            "single_body_host_audit_artifact": str(host_path.relative_to(ROOT)),
            "single_body_host_descriptor_promoted": host[
                "single_body_host_descriptor_promoted"
            ],
            "body_ownership_audit_artifact": str(
                ownership_path.relative_to(ROOT)
            ),
            "single_source_frozen_body_descriptor_materialized": ownership[
                "single_source_frozen_body_descriptor_materialized"
            ],
            "multisource_triangle_common_body_owner": ownership[
                "audited_objects"
            ]["multisource_triangle"]["common_body_owner"],
            "image_paths_are_body_coordinates": ownership[
                "audited_objects"
            ]["four_image_path_pullbacks"]["body_coordinates"],
            "body_descriptor_minimal_resolving_input": ownership[
                "minimal_resolving_input"
            ],
            "direct_relative_clock_rate_artifact": str(
                relative_clock_path.relative_to(ROOT)
            ),
            "direct_relative_clock_rate_central_estimate": relative_clock[
                "central_exploratory_fit"
            ]["relative_clock_rate_B_over_A"],
            "direct_relative_clock_rate_stable": relative_clock[
                "path_dependent_clock_rate_stable"
            ],
            "direct_relative_clock_rate_tau_claim_allowed": relative_clock[
                "tau_time_distortion_claim_allowed"
            ],
            "direct_relative_clock_rate_null_artifact": str(
                relative_clock_null_path.relative_to(ROOT)
            ),
            "direct_relative_clock_rate_null_rate_p_value": relative_clock_null[
                "empirical_two_sided_rate_p_value"
            ],
            "direct_relative_clock_rate_null_improvement_p_value": (
                relative_clock_null["empirical_improvement_p_value"]
            ),
            "unit_stretch_rejected_under_parametric_mock": relative_clock_null[
                "unit_stretch_rejected_under_parametric_mock"
            ],
            "direct_relative_clock_correlated_null_artifact": str(
                correlated_clock_null_path.relative_to(ROOT)
            ),
            "direct_relative_clock_correlated_rate_p_value": (
                correlated_clock_null["pooled_rate_p_value"]
            ),
            "direct_relative_clock_correlated_improvement_p_value": (
                correlated_clock_null["pooled_improvement_p_value"]
            ),
            "direct_relative_clock_supported_after_correlated_null": (
                correlated_clock_null["path_dependent_clock_rate_supported"]
            ),
            "independent_he0435_clock_artifact": str(
                he0435_clock_path.relative_to(ROOT)
            ),
            "independent_he0435_relative_clock_rate": he0435_clock[
                "observed_fit"
            ]["relative_clock_rate_C_over_B"],
            "independent_he0435_clock_rate_p_value": he0435_clock[
                "official_mock_null"
            ]["empirical_two_sided_rate_p_value"],
            "independent_he0435_path_clock_supported": he0435_clock[
                "path_dependent_clock_rate_supported"
            ],
            "common_mode_unlensed_control_artifact": str(
                common_clock_support_path.relative_to(ROOT)
            ),
            "differential_clock_null_is_control_only": common_clock_support[
                "differential_image_clock_null_reinterpreted_as_control_only"
            ],
            "strict_unlensed_pair_matching_ready": common_clock_support[
                "strict_pair_matching_ready"
            ],
            "strict_unlensed_control_count": common_clock_support[
                "matching_results"
            ][0]["matched_control_count"],
            "common_mode_clock_test_executed": common_clock_support[
                "common_mode_clock_test_executed"
            ],
            "positive_host_moment_artifact": str(
                positive_host_path.relative_to(ROOT)
            ),
            "stable_scalar_host_trace_materialized": positive_host[
                "stable_scalar_trace_materialized"
            ],
            "scalar_body_path_coupling_artifact": str(
                scalar_coupling_path.relative_to(ROOT)
            ),
            "scalar_transport_exactly_factorizes": scalar_coupling[
                "exact_scalar_body_path_factorization"
            ],
            "independent_scalar_body_path_information_materialized": (
                scalar_coupling[
                    "independent_body_path_interaction_materialized"
                ]
            ),
            "joint_tensor_path_interaction_artifact": str(
                tensor_path_path.relative_to(ROOT)
            ),
            "ordinal_tensor_path_interaction_materialized": tensor_path[
                "ordinal_tensor_path_interaction_materialized"
            ],
            "amplitude_stable_tensor_path_interaction_materialized": tensor_path[
                "amplitude_stable_tensor_path_interaction_materialized"
            ],
            "tensor_path_ordinal_holdout_artifact": str(
                tensor_holdout_path.relative_to(ROOT)
            ),
            "internal_model_holdout_ordinal_signature_replicated": tensor_holdout[
                "exact_ordinal_signature_replication"
            ],
            "independent_target_replication": tensor_holdout[
                "independent_target_replication"
            ],
            "coordinate_free_path_signature_artifact": str(
                canonical_path_signature_path.relative_to(ROOT)
            ),
            "coordinate_free_morphology_path_control_materialized": (
                canonical_path_signature[
                    "coordinate_free_morphology_path_control_materialized"
                ]
            ),
            "tau_specific_information_beyond_standard_lensing_materialized": (
                canonical_path_signature[
                    "tau_specific_information_beyond_standard_lensing_materialized"
                ]
            ),
            "scalar_clock_nonidentifiability_artifact": str(
                scalar_clock_path.relative_to(ROOT)
            ),
            "sfh_01_representation_compatible_scalar_class_materialized": (
                scalar_clock[
                    "sfh_01_representation_compatible_scalar_class_materialized"
                ]
            ),
            "physical_body_clock_identified": scalar_clock[
                "theta_M_identified"
            ],
            "log_clock_composition_selection_artifact": str(
                log_clock_path.relative_to(ROOT)
            ),
            "logarithmic_clock_shape_conditionally_selected": log_clock[
                "logarithmic_shape_conditionally_selected"
            ],
            "multiplicative_body_composition_physically_proved": log_clock[
                "measured_source_trace_proved_to_obey_parent_multiplicative_composition"
            ],
            "absolute_clock_scale_selected": log_clock[
                "absolute_reference_scale_q_star_selected"
            ],
            "moment_area_character_artifact": str(
                area_character_path.relative_to(ROOT)
            ),
            "moment_area_multiplicative_character_exact": area_character[
                "moment_area_positive_character_materialized"
            ],
            "trace_stable_on_expanded_model_family": area_character[
                "trace_stable_on_expanded_model_family"
            ],
            "area_character_stable_on_expanded_model_family": area_character[
                "area_character_stable_on_expanded_model_family"
            ],
            "log_area_path_contrast_artifact": str(
                log_area_path_path.relative_to(ROOT)
            ),
            "local_endpoint_log_area_clock_branch_closed": log_area_path[
                "local_endpoint_log_area_clock_branch_closed"
            ],
            "log_area_contrast_reduces_to_standard_magnification": log_area_path[
                "exact_reduction_to_standard_log_magnification_ratio"
            ],
            "full_causal_support_clock_still_open": log_area_path[
                "full_causal_support_clock_still_open"
            ],
            "modeled_cone_morphology_artifact": str(
                modeled_cone_path.relative_to(ROOT)
            ),
            "modeled_cone_descriptor_materialized": modeled_cone[
                "modeled_cone_descriptor_materialized"
            ],
            "modeled_cone_component_counts": modeled_cone["component_counts"],
            "modeled_cone_lens_plane_counts": modeled_cone[
                "lens_plane_counts"
            ],
            "complete_physical_light_cone_morphology_materialized": modeled_cone[
                "complete_physical_light_cone_morphology_materialized"
            ],
            "standard_multiplane_lensing_information_only": modeled_cone[
                "standard_multiplane_lensing_information_only"
            ],
            "observed_los_morphology_artifact": str(
                strides_los_path.relative_to(ROOT)
            ),
            "observed_los_morphology_materialized": strides_los[
                "observed_los_morphology_materialized"
            ],
            "materialized_spectroscopic_galaxy_row_count": strides_los[
                "materialized_spectroscopic_galaxy_row_count"
            ],
            "identified_los_group_count": strides_los[
                "identified_group_count"
            ],
            "reported_spectroscopic_completeness": strides_los[
                "reported_spectroscopic_completeness"
            ],
            "los_physical_path_transport_assigned": strides_los[
                "path_specific_transport_assigned"
            ],
            "los_path_transport_geometry_artifact": str(
                los_transport_path.relative_to(ROOT)
            ),
            "redshift_dependent_four_path_geometry_materialized": los_transport[
                "redshift_dependent_four_path_geometry_materialized"
            ],
            "los_path_geometry_row_count": los_transport[
                "transport_row_count"
            ],
            "published_leading_order_flexion_transport_materialized": los_transport[
                "published_leading_order_flexion_transport_materialized"
            ],
            "complete_physical_environment_transport_materialized": los_transport[
                "complete_physical_environment_transport_materialized"
            ],
            "all_above_threshold_objects_already_explicitly_modeled": los_transport[
                "all_above_threshold_objects_already_explicitly_modeled"
            ],
            "subthreshold_collective_flexion_artifact": str(
                collective_path.relative_to(ROOT)
            ),
            "collective_oriented_subthreshold_structure_nonzero": collective[
                "collective_oriented_subthreshold_structure_nonzero"
            ],
            "subthreshold_not_representable_by_spin0_spin2_summary": collective[
                "not_representable_by_spin0_spin2_tidal_summary"
            ],
            "subthreshold_standard_higher_order_lensing_information": collective[
                "standard_higher_order_lensing_information"
            ],
            "naive_sis_population_countermodel_artifact": str(
                sis_countermodel_path.relative_to(ROOT)
            ),
            "naive_sis_population_physical_completion_rejected": sis_countermodel[
                "physical_completion_rejected"
            ],
            "local_higher_order_or_truncated_halo_transport_required": True,
            "local_cubic_los_transport_artifact": str(
                local_cubic_path.relative_to(ROOT)
            ),
            "local_non_tidal_transport_nonzero_after_affine_projection": local_cubic[
                "local_non_tidal_transport_nonzero_after_affine_projection"
            ],
            "local_cubic_models_above_conservative_flexion_scale": local_cubic[
                "models_with_maximum_path_residual_above_threshold"
            ],
            "local_cubic_transport_is_standard_conditional_completion": True,
            "local_cubic_astrometric_endpoint_artifact": str(
                astrometric_endpoint_path.relative_to(ROOT)
            ),
            "direct_astrometric_endpoint_authorized": astrometric_endpoint[
                "direct_astrometric_endpoint_authorized"
            ],
            "extended_arc_endpoint_preferred": astrometric_endpoint[
                "extended_arc_endpoint_preferred"
            ],
            "local_cubic_f814w_arc_template_artifact": str(
                arc_template_path.relative_to(ROOT)
            ),
            "f814w_arc_template_materialized": arc_template[
                "source_forward_template_materialized"
            ],
            "f814w_endpoint_previously_opened": arc_template[
                "endpoint_was_previously_opened"
            ],
            "f814w_confirmatory_evidence_allowed": arc_template[
                "confirmatory_evidence_allowed"
            ],
            "f814w_template_residual_cosine": arc_template[
                "template_residual_cosine"
            ],
            "f814w_fixed_amplitude_fractional_sse_reduction": arc_template[
                "fixed_amplitude_fractional_unweighted_sse_reduction"
            ],
            "f814w_exploratory_alignment_positive": arc_template[
                "exploratory_alignment_positive"
            ],
            "collective_los_completion_artifact": str(
                collective_completion_path.relative_to(ROOT)
            ),
            "collective_los_role": collective_completion[
                "subthreshold_population_role"
            ],
            "reported_kappa_ext_median_interval": collective_completion[
                "reported_kappa_ext_median_interval"
            ],
            "reported_kappa_ext_approximate_width": collective_completion[
                "reported_kappa_ext_approximate_width"
            ],
            "new_f814w_template_from_kappa_ext_authorized": (
                collective_completion[
                    "new_f814w_spatial_template_authorized_from_kappa_ext"
                ]
            ),
            "kappa_ext_time_delay_nuisance_required": collective_completion[
                "kappa_ext_time_delay_nuisance_required"
            ],
            "kappa_marginalized_delay_rank_artifact": str(
                kappa_rank_path.relative_to(ROOT)
            ),
            "kappa_model_principal_angle_degrees": kappa_rank[
                "principal_angle_degrees"
            ],
            "strict_delay_dimension_after_kappa_marginalization": kappa_rank[
                "remaining_dimension_after_dominant_model_plus_kappa"
            ],
            "practical_weak_direction_survives_geometrically": kappa_rank[
                "practical_5pct_weak_direction_survives_geometrically"
            ],
            "practical_weak_direction_is_kappa_free": kappa_rank[
                "practical_weak_direction_is_kappa_free"
            ],
            "kappa_weak_projection_at_reported_width_sigma": kappa_rank[
                "kappa_projection_on_weak_direction_at_reported_width_sigma"
            ],
            "wgd2038_published_summary_rank_artifact": str(
                wgd_summary_rank_path.relative_to(ROOT)
            ),
            "wgd2038_published_summary_nuisance_rank": wgd_summary_rank[
                "published_summary_nuisance_rank"
            ],
            "wgd2038_remaining_summary_delay_dimension": wgd_summary_rank[
                "remaining_published_summary_dimension"
            ],
            "wgd2038_observed_candidate_projection_sigma": wgd_summary_rank[
                "observed_projection_on_candidate_sigma"
            ],
            "wgd2038_candidate_frozen_before_endpoint_projection": (
                wgd_summary_rank[
                    "candidate_direction_materialized_before_endpoint_projection"
                ]
            ),
            "wgd2038_posterior_level_nuisance_span_materialized": (
                wgd_summary_rank[
                    "posterior_level_nuisance_span_materialized"
                ]
            ),
            "wgd2038_confirmatory_tau_score_allowed": wgd_summary_rank[
                "confirmatory_tau_score_allowed"
            ],
            "wgd2038_mass_family_rank_artifact": str(
                wgd_family_rank_path.relative_to(ROOT)
            ),
            "wgd2038_mass_family_nuisance_rank": wgd_family_rank[
                "median_mass_family_nuisance_rank"
            ],
            "wgd2038_remaining_delay_dimension_after_family_resolution": (
                wgd_family_rank[
                    "remaining_dimension_after_mass_family_resolution"
                ]
            ),
            "wgd2038_prior_candidate_absorbed_fraction": wgd_family_rank[
                "prior_two_summary_candidate_absorbed_fraction"
            ],
            "wgd2038_independent_delay_shape_candidate_survives": (
                wgd_family_rank[
                    "independent_delay_shape_candidate_survives"
                ]
            ),
            "wgd2038_kinematic_holdout_artifact": str(
                wgd_kinematic_path.relative_to(ROOT)
            ),
            "wgd2038_xshooter_gmos_difference_sigma": wgd_kinematic[
                "xshooter_minus_primary_gmos_sigma"
            ],
            "wgd2038_xshooter_is_independent_terminal_type": (
                wgd_kinematic[
                    "terminal_type_independent_of_prior_kinematics"
                ]
            ),
            "wgd2038_xshooter_can_append_as_fourth_coordinate": (
                wgd_kinematic[
                    "can_append_xshooter_as_naive_fourth_coordinate"
                ]
            ),
            "wgd2038_oiii_distinct_terminal_artifact": str(
                wgd_oiii_path.relative_to(ROOT)
            ),
            "wgd2038_oiii_distinct_fourth_terminal_materialized": wgd_oiii[
                "distinct_fourth_terminal_type_materialized"
            ],
            "wgd2038_oiii_largest_smooth_model_residual_sigma": wgd_oiii[
                "largest_absolute_component_sigma"
            ],
            "wgd2038_oiii_joint_delay_flux_ensemble_materialized": wgd_oiii[
                "joint_delay_flux_model_ensemble_materialized"
            ],
            "wgd2038_oiii_confirmatory_tau_score_allowed": wgd_oiii[
                "confirmatory_tau_score_allowed"
            ],
            "wgd2038_standard_flux_completion_artifact": str(
                wgd_flux_completion_path.relative_to(ROOT)
            ),
            "wgd2038_standard_flux_model_family_materialized": (
                wgd_flux_completion[
                    "standard_nuisance_model_family_materialized"
                ]
            ),
            "wgd2038_standard_flux_posterior_predictive_materialized": (
                wgd_flux_completion[
                    "standard_nuisance_posterior_predictive_materialized"
                ]
            ),
            "wgd2038_standard_flux_completion_publicly_reproducible": (
                wgd_flux_completion[
                    "standard_completion_reproducible_from_public_payload"
                ]
            ),
            "wgd2038_cross_amplitude_artifact": str(
                wgd_cross_amplitude_path.relative_to(ROOT)
            ),
            "wgd2038_cross_amplitude_mahalanobis_squared": (
                wgd_cross_amplitude["mahalanobis_squared"]
            ),
            "wgd2038_cross_amplitude_gaussian_p_value": (
                wgd_cross_amplitude[
                    "gaussian_chi_square_survival_probability"
                ]
            ),
            "wgd2038_cross_amplitude_same_source_region": (
                wgd_cross_amplitude["same_physical_source_region"]
            ),
            "wgd2038_cross_amplitude_tau_coordinate_identified": (
                wgd_cross_amplitude["shared_tau_or_time_coordinate_identified"]
            ),
            "wgd2038_prior_predictive_smoke_artifact": str(
                wgd_prior_smoke_path.relative_to(ROOT)
            ),
            "wgd2038_prior_predictive_runtime_executed": (
                wgd_prior_smoke["n_realizations"] == 2
            ),
            "wgd2038_prior_predictive_flux_conditioning_used": (
                wgd_prior_smoke["flux_conditioning_used"]
            ),
            "wgd2038_prior_predictive_scientific_scoring_allowed": (
                wgd_prior_smoke["scientific_scoring_allowed"]
            ),
            "wgd2038_prior_predictive_n64_artifact": str(
                wgd_prior_n64_path.relative_to(ROOT)
            ),
            "wgd2038_prior_predictive_n64_empirical_rank": int(
                np.linalg.matrix_rank(
                    np.asarray(
                        wgd_prior_n64["predicted_ratio_covariance"],
                        dtype=float,
                    )
                )
            ),
            "wgd2038_prior_predictive_n64_flux_conditioning_used": (
                wgd_prior_n64["flux_conditioning_used"]
            ),
            "wgd2038_prior_predictive_n64_scientific_scoring_allowed": (
                wgd_prior_n64["scientific_scoring_allowed"]
            ),
            "wgd2038_warm_dust_reweighted_n256_artifact": str(
                wgd_reweighted_n256_path.relative_to(ROOT)
            ),
            "wgd2038_warm_dust_reweighted_effective_sample_size": (
                wgd_reweighted_n256["effective_sample_size"]
            ),
            "wgd2038_warm_dust_reweighted_covariance_rank": (
                wgd_reweighted_n256["weighted_covariance_rank"]
            ),
            "wgd2038_warm_dust_reweighted_tau_scoring_allowed": (
                wgd_reweighted_n256["tau_or_observer_time_scoring_allowed"]
            ),
            "wgd2038_oiii_standard_compatibility_artifact": str(
                wgd_oiii_compatibility_path.relative_to(ROOT)
            ),
            "wgd2038_oiii_standard_survival_probability": (
                wgd_oiii_compatibility[
                    "gaussian_moment_survival_probability"
                ]
            ),
            "wgd2038_oiii_tau_specific_excess_materialized": (
                wgd_oiii_compatibility["tau_specific_excess_materialized"]
            ),
            "relative_morphology_coordinates": morphology[
                "relative_morphology_coordinates"
            ],
            "remaining_required_before_h_tau": remaining,
        },
        "verdict": (
            "SOURCE_MORPHOLOGY_AND_LOCAL_PATH_PULLBACKS_MATERIALIZED__"
            "SCORING_BLOCKED_PENDING_BODY_CLOCK_AND_TIME_COVECTOR"
            if morphology_ready and pullback_ready
            else "MULTISOURCE_GEOMETRY_CALIBRATOR_ONLY__"
            "SCORING_BLOCKED_PENDING_SINGLE_BODY_DESCRIPTOR"
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps({
        "verdict": summary["verdict"],
        "field_count": len(rows),
        "score_authorized": summary["authorization"][
            "extended_nuisance_orthogonality_score_authorized"
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
