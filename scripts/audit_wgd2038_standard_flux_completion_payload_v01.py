#!/usr/bin/env python3
"""Audit public standard-physics payloads for the WGD2038 OIII terminal."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
OIII = RESULTS / "tau_core_lensing_wgd2038_oiii_distinct_terminal_v1/summary.json"
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_standard_flux_completion_payload_v1"
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"


def main() -> None:
    oiii = json.loads(OIII.read_text(encoding="utf-8"))

    sources = {
        "lenslikelihood": {
            "repository": "https://github.com/dangilman/lenslikelihood",
            "commit": "d01be7e4277881066beafa699eb53eaf5f6d7c69",
            "role": "published multi-lens dark-substructure hyperparameter likelihood",
            "wgd2038_measurement_present": True,
            "wgd2038_flux_posterior_samples_in_repository": False,
            "external_precomputed_likelihood_link_live_at_audit": False,
            "preserves_object_level_flux_predictions": False,
        },
        "samana": {
            "repository": "https://github.com/dangilman/samana",
            "commit": "fc0f595730197a8869f5d12f37acbd0788f2659a",
            "role": "forward-model framework and target-specific smooth lens model",
            "wgd2038_data_class_present": True,
            "epl_m1_m3_m4_shear_model_present": True,
            "baseline_notebook_present": True,
            "baseline_notebook_runs_pso_only": True,
            "baseline_notebook_mcmc_disabled": True,
            "source_frozen_production_configuration_present": True,
            "production_configuration_archive_sha256": (
                "48ea376853847a863a2a6b3447ddbf5a2aa86ef0bd9d1cf142b6411a7e65e360"
            ),
            "production_configuration_terminal": "JWST warm-dust flux ratios",
            "production_configuration_is_oiii_specific": False,
            "production_configuration_uses_measured_fluxes": True,
            "wgd2038_posterior_chain_present": False,
            "substructure_posterior_predictive_ensemble_present": False,
        },
    }

    checks = {
        "oiii_terminal_was_materialized": oiii[
            "distinct_fourth_terminal_type_materialized"
        ],
        "public_target_specific_smooth_model_code_exists": sources["samana"][
            "epl_m1_m3_m4_shear_model_present"
        ],
        "source_frozen_warm_dust_production_config_exists": sources["samana"][
            "source_frozen_production_configuration_present"
        ],
        "warm_dust_config_is_not_oiii_completion": not sources["samana"][
            "production_configuration_is_oiii_specific"
        ],
        "public_target_specific_posterior_chain_is_absent": not sources["samana"][
            "wgd2038_posterior_chain_present"
        ],
        "public_target_specific_substructure_predictive_is_absent": not sources[
            "samana"
        ]["substructure_posterior_predictive_ensemble_present"],
        "aggregate_likelihood_does_not_restore_object_predictions": not sources[
            "lenslikelihood"
        ]["preserves_object_level_flux_predictions"],
        "standard_posterior_predictive_probability_not_identifiable": True,
        "tau_scoring_remains_forbidden": True,
    }

    summary = {
        "schema": "paper7 WGD2038 standard flux-completion payload audit v1",
        "audit_date": "2026-07-27",
        "sources": sources,
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "smooth_model_component_tension_sigma": oiii[
            "largest_absolute_component_sigma"
        ],
        "standard_nuisance_model_family_materialized": True,
        "source_frozen_warm_dust_forward_configuration_materialized": True,
        "oiii_specific_forward_configuration_materialized": False,
        "standard_nuisance_posterior_predictive_materialized": False,
        "standard_completion_reproducible_from_public_payload": False,
        "standard_model_explains_or_fails_oiii_decidable": False,
        "tau_specific_coordinate_materialized": False,
        "confirmatory_tau_score_allowed": False,
        "time_distortion_detection_claim_allowed": False,
        "verdict": (
            "STANDARD_WGD2038_FLUX_MODEL_FAMILY_IS_PUBLIC__"
            "TARGET_POSTERIOR_PREDICTIVE_IS_NOT__"
            "OIII_TENSION_REMAINS_UNCLASSIFIED_AND_TAU_SCORING_FORBIDDEN"
        ),
        "claim_boundary": (
            "The public sources establish standard smooth multipoles and dark "
            "substructure as concrete completion mechanisms and now supply an "
            "exact WGD2038 warm-dust production configuration. They do not "
            "expose its accepted simulations, and the configuration is not an "
            "OIII-specific completion. Consequently the 2.24-sigma diagonal "
            "OIII component cannot yet be assigned either to standard "
            "structure or to a Tau-specific readout. Re-fitting the opened "
            "OIII ratios would be exploratory, not an independent test."
        ),
        "next_finite_action": (
            "Freeze the samana/pyHalo priors from their published population "
            "analysis before looking at the WGD2038 residual, then generate and "
            "release a target-specific accepted-simulation ensemble. Score only "
            "a predeclared joint delay-plus-flux statistic against that ensemble."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# WGD2038 standard flux-completion payload audit v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        "The public code supplies the target data and an "
        "`EPL+M1+M3+M4+shear` model, while the multi-lens likelihood records "
        "the WGD2038 flux measurement. Neither source supplies the "
        "target-specific posterior-predictive flux ensemble needed to classify "
        "the opened OIII discrepancy. Standard completion is therefore "
        "physically specified but not publicly scoreable; Tau scoring remains "
        "forbidden.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
