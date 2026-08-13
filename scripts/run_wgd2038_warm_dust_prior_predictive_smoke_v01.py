#!/usr/bin/env python3
"""Run a bounded source-frozen WGD2038 warm-dust prior-predictive batch.

This optional runtime requires the exact Paper III/IV environment documented
in the samana launch archive. It deliberately disables flux rejection and the
downstream image-data reconstruction. The default remains the minimal
two-realization technical smoke; larger batches require an explicit output
name and remain prior-predictive diagnostics rather than scientific scoring.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20384008)
    parser.add_argument("--n-realizations", type=int, default=2)
    parser.add_argument("--n-pso-iterations", type=int, default=10)
    parser.add_argument("--source-fwhm-min-pc", type=float, default=1.0)
    parser.add_argument("--source-fwhm-max-pc", type=float, default=10.0)
    parser.add_argument("--source-kernel-label", default="warm_dust")
    parser.add_argument(
        "--publication-fitting-sequence",
        action="store_true",
        help="Use the launch archive's align-images plus PSO sequence.",
    )
    parser.add_argument(
        "--output-name",
        default="tau_core_lensing_wgd2038_warm_dust_prior_predictive_smoke_v1",
    )
    args = parser.parse_args()
    if args.n_realizations < 2:
        parser.error("--n-realizations must be at least 2 due to the public writer bug")
    if "/" in args.output_name or args.output_name in {"", ".", ".."}:
        parser.error("--output-name must be one directory name")
    if args.n_pso_iterations < 1:
        parser.error("--n-pso-iterations must be positive")
    if (
        args.source_fwhm_min_pc <= 0
        or args.source_fwhm_max_pc <= args.source_fwhm_min_pc
    ):
        parser.error("source FWHM bounds must satisfy 0 < min < max")

    out = ROOT / "data/derived/repro_results" / args.output_name
    fitting_sequence_kwargs = None
    if args.publication_fitting_sequence:
        fitting_sequence_kwargs = [
            [
                "align_images",
                {
                    "n_particles": 10,
                    "n_iterations": 50,
                    "delta_shift": 0.03,
                    "align_offset": True,
                },
            ],
            [
                "PSO",
                {
                    "sigma_scale": 1.0,
                    "n_particles": 10,
                    "n_iterations": args.n_pso_iterations,
                    "threadCount": 1,
                },
            ],
        ]

    from samana.analysis_util import (
        default_rendering_area,
        numerics_setup,
        quick_setup,
    )
    from samana.forward_model import forward_model

    data_cls, model_cls = quick_setup("WGD2038")
    data = data_cls()
    grid_size, grid_resolution = numerics_setup("WGD2038")
    cone_angle = default_rendering_area(data_class=data, model_class=model_cls)

    data.magnifications = np.asarray([1.0, 1.209, 0.939, 0.430])
    data.flux_uncertainty = None
    data.flux_ratio_covariance_matrix = np.asarray(
        [
            [0.0013163769158846795, 0.00012240530553126578, 0.000091145427724005],
            [0.00012240530553126578, 0.0008747728497371431, 0.00005562121299135247],
            [0.000091145427724005, 0.00005562121299135247, 0.00020187066122068058],
        ]
    )
    data.keep_flux_ratio_index = [0, 1, 2]

    globular_clusters = {
        "log10_mgc_mean": 5.3,
        "log10_mgc_sigma": 0.6,
        "rendering_radius_arcsec": 0.2,
        "gc_surface_mass_density": 10**5.6,
        "gc_density_profile": "PTMASS",
        "center_x": data.x_image,
        "center_y": data.y_image,
    }
    realization_priors = {
        "log10_sigma_sub": ["UNIFORM", -2.2, 0.2],
        "log_mc": ["UNIFORM", 4.0, 10.0],
        "log_mlow": ["FIXED", 6.0],
        "log_mhigh": ["FIXED", 10.7],
        "LOS_normalization": ["UNIFORM", 0.9, 1.1],
        "shmf_log_slope": ["UNIFORM", -1.95, -1.85],
        "log_m_host": ["GAUSSIAN", 13.3, 0.3],
        "truncation_model_subhalos": ["FIXED", "TRUNCATION_GALACTICUS"],
        "add_globular_clusters": ["FIXED", True],
        "subhalo_spatial_distribution": ["FIXED", "UNIFORM"],
        "kwargs_globular_clusters": ["FIXED", globular_clusters],
        "cone_opening_angle_arcsec": ["FIXED", cone_angle],
    }
    macro_priors = {
        "gamma": ["GAUSSIAN", 2.1, 0.1],
        "OPTICAL_MULTIPOLE_PRIOR_M1": [],
        "q": ["TRUNC-HALF-GAUSS", 0.55, 0.2, 0.4, 0.999],
    }

    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    forward_model(
        str(raw) + "/",
        2,
        args.n_realizations,
        data,
        model_cls,
        "WDM",
        realization_priors,
        {
            "source_size_pc": [
                "UNIFORM",
                args.source_fwhm_min_pc,
                args.source_fwhm_max_pc,
            ]
        },
        macro_priors,
        np.inf,
        random_seed_init=args.seed,
        readout_steps=2,
        rescale_grid_resolution=grid_resolution,
        rescale_grid_size=grid_size,
        kwargs_model_class={"shapelets_order": 16},
        verbose=True,
        n_pso_particles=10,
        n_pso_iterations=args.n_pso_iterations,
        num_threads=1,
        # Keep samana's interactive plotting/debug path disabled. Numerical
        # effort is bounded explicitly by the PSO settings above.
        test_mode=False,
        use_imaging_data=False,
        parallelize=False,
        kappa_scale_subhalos=0.05,
        log10_bound_mass_cut=4.0,
        split_image_data_reconstruction=False,
        filter_subhalo_kwargs={
            "aperture_radius_arcsec": 0.25,
            "log10_mass_minimum": 7.0,
            "x_coords": data.x_image,
            "y_coords": data.y_image,
        },
        scipy_minimize_method="COBYQA_import",
        # No source-reconstruction trigger is supplied; the optional imaging
        # branch remains off independently of the infinite flux tolerance.
        fr_logL_source_reconstruction=None,
        fitting_sequence_kwargs=fitting_sequence_kwargs,
    )

    job = raw / "job_2"
    magnifications = np.loadtxt(job / "fluxes.txt")
    predicted_ratios = magnifications[:, 1:] / magnifications[:, [0]]
    parameters = np.loadtxt(job / "parameters.txt", skiprows=1)
    ratio_quantiles = np.quantile(
        predicted_ratios, [0.05, 0.16, 0.5, 0.84, 0.95], axis=0
    )
    summary = {
        "schema": "paper7 WGD2038 warm-dust bounded prior-predictive batch v1",
        "seed": args.seed,
        "n_realizations": args.n_realizations,
        "predeclared_scope": (
            "technical smoke only"
            if args.n_realizations == 2
            else "coarse prior-predictive distribution diagnostic"
        ),
        "flux_acceptance_tolerance": "infinity",
        "flux_conditioning_used": False,
        "image_data_reconstruction_used": False,
        "source_kernel_label": args.source_kernel_label,
        "source_profile": "circular Gaussian",
        "source_fwhm_pc_prior": [
            args.source_fwhm_min_pc,
            args.source_fwhm_max_pc,
        ],
        "pso_iterations": args.n_pso_iterations,
        "publication_fitting_sequence_used": args.publication_fitting_sequence,
        "predicted_magnifications": magnifications.tolist(),
        "predicted_flux_ratios": predicted_ratios.tolist(),
        "predicted_ratio_mean": np.mean(predicted_ratios, axis=0).tolist(),
        "predicted_ratio_covariance": np.cov(
            predicted_ratios, rowvar=False, ddof=1
        ).tolist(),
        "predicted_ratio_quantile_levels": [0.05, 0.16, 0.5, 0.84, 0.95],
        "predicted_ratio_quantiles": ratio_quantiles.tolist(),
        "sampled_parameter_rows": parameters.tolist(),
        "exact_environment": {
            "samana_commit": "d57329d47baf26c52ed48c1068e6697d86370bf9",
            "pyhalo_commit": "64ea7a235a474e6b90dca016f1bb2141503d3b3f",
            "lenstronomy_commit": "370d932c8ded11da8b1e3c772266a87ead143136",
            "additional_runtime_dependencies": ["tqdm", "colossus", "mcfit", "cobyqa"],
        },
        "one_sample_writer_bug_encountered": True,
        "one_sample_writer_bug_resolution": (
            "Use the minimal two-realization smoke because the exact samana "
            "commit indexes a one-row parameter array as two-dimensional."
        ),
        "binomial_worst_case_standard_error": float(
            0.5 / np.sqrt(args.n_realizations)
        ),
        "minimum_samples_for_tail_probability_claim": (
            "not established; this unconditioned batch is not a tail-probability endpoint"
        ),
        "scientific_scoring_allowed": False,
        "verdict": (
            "TECHNICAL_PRIOR_PREDICTIVE_PATH_EXECUTED__ENSEMBLE_NOT_YET_MATERIALIZED"
            if args.n_realizations == 2
            else "BOUNDED_UNCONDITIONED_PRIOR_PREDICTIVE_ENSEMBLE__NO_SCIENTIFIC_SCORING"
        ),
    }
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
