# WGD2038 HST-to-lenstronomy reconstruction recipe

This note records how the WGD2038 HST image inputs were reconstructed into
the lenstronomy notebook input format during the Paper 7 public-data audit.
It is a provenance recipe, not a redistribution of raw payloads.

## Claim boundary

This reconstruction establishes only:

- public HST products can be obtained for WGD2038-4008;
- the HST SCI/WHT extensions can be split into the filenames expected by the
  WGD2038 preprocessing notebooks;
- the three-band lenstronomy HDF5 inputs can be generated locally;
- the multiband notebook data/setup path can be loaded in a bounded preflight.
- a bounded one-step PEMD/SHEAR model-plumbing smoke run can execute from
  those inputs under explicitly documented compatibility constraints.
- a second bounded one-step PEMD/SHEAR smoke run can execute with the
  physical `fastell4py` PEMD backend installed locally.
- a minimal fastell-backed `emcee` posterior-plumbing pilot can execute and
  write an output artifact.
- a short fastell-backed diagnostic pilot can execute and, when inspected in
  the lenstronomy venv, yields a finite `(4240, 53)` sample payload with finite
  log-probabilities.
- a longer bounded diagnostic60 run yields a finite `(12720, 53)` sample
  payload, but visible split-half drift remains.
- a diagnostic120 run yields a finite `(25440, 53)` sample payload, but
  split-half drift increases rather than disappearing.
- a diagnostic120 continuation run can start from the previous chain endpoint
  and yields another finite `(25440, 53)` sample payload, but visible
  split-half drift remains.
- a second diagnostic120 continuation from the first continuation endpoint
  also yields a finite `(25440, 53)` sample payload, but drift does not improve.
- a cold diagnostic120 continuation with `sigma_scale=0.02` also yields a
  finite `(25440, 53)` payload, but drift worsens rather than improving.
- a parameter-level drift diagnostic shows that the remaining visible drift is
  concentrated in nuisance-heavy light-profile and image-position directions.
- a nuisance-stabilization plan identifies a first bounded
  `profile_freeze_v1_bounded_diagnostic` follow-up, while keeping mass/shear
  and T2 claims protected.
- the `profile_freeze_v1` bounded diagnostic runs with 42 active parameters and
  reduces median drift, but it is still not a converged no-T2 posterior.
- the more aggressive `profile_freeze_v2` run is finite with 35 active
  parameters, but worsens drift; simply freezing more light-profile parameters
  is not the next clean route.

It does not establish:

- a full cluster/MCMC posterior reproduction;
- image-wise Fermat/parity posterior samples;
- a no-T2 Ddt/null posterior reproduction;
- a physical PEMD posterior reproduction or posterior convergence;
- real-data T2 evidence or authorization to sample a T2 perturbation.

## Raw payload policy

Raw payloads are intentionally not versioned in this repository.  The local
cache used for the audit lives under `data/external/` and is ignored by git.
The reproducibility package records source names, hashes, scripts, and derived
summary artifacts instead of redistributing FITS images, notebooks, cloned
source trees, or large intermediate files.

## Source products

The HST products were queried from MAST for proposal `15320`, target
`DESJ2038-4008`, yielding these files:

- `hst_15320_08_wfc3_ir_f160w_idgc08_drz.fits`
- `hst_15320_08_wfc3_uvis_f475x_idgc08_drc.fits`
- `hst_15320_08_wfc3_uvis_f814w_idgc08_drc.fits`

The WGD2038 notebook/source route was inspected from the public
`TDCOSMO/WGD2038-4008` tree.  The support payload route was inspected from
the public TDCOSMO2025/WGD2038 products and the target WGD2038 notebooks.

## Reconstruction steps

1. Download the HST products into a local cache under `data/external/`.
2. Split each HST FITS product into the notebook-expected SCI/WHT files:
   `DESJ2038-4008_F160W_drz_sci.fits`,
   `DESJ2038-4008_F160W_drz_wht.fits`,
   `DESJ2038-4008_F475X_drc_sci.fits`,
   `DESJ2038-4008_F475X_drc_wht.fits`,
   `DESJ2038-4008_F814W_drc_sci.fits`, and
   `DESJ2038-4008_F814W_drc_wht.fits`.
3. Run the WGD2038 preprocessing notebooks for F475X and F814W.
4. Run a compatibility copy of the F160W preprocessing notebook in which the
   two standard HDF5 save cells are converted from `raw` to `code`.  The cell
   contents are unchanged; this is an execution-format patch, not a physical
   or modeling change.
5. Apply the lenstronomy API compatibility adjustment
   `shapelet_basis_2d(numPix=...) -> shapelet_basis_2d(num_pix=...)` in the
   temporary notebook copies.
6. Verify the generated HDF5 products:
   `data_f160w.hdf5`, `psf_f160w.hdf5`, `psf_f160w_hires.hdf5`,
   `data_f475x.hdf5`, `psf_f475x.hdf5`, `data_f814w.hdf5`,
   `psf_f814w.hdf5`.
7. Run a bounded multiband notebook preflight that keeps only data loading and
   setup cells, omitting cluster submission, posterior download, and MCMC
   analysis cells.
8. Run a bounded local model-plumbing smoke notebook with one tiny PSO step,
   no PSF iteration, no image alignment, no MCMC, and no posterior analysis.
   Because `fastell4py` was unavailable in the local environment, the PEMD
   smoke copy used `suppress_fastell=True`; this is a dependency bypass for
   smoke testing only.  Legacy lenstronomy API differences were also isolated:
   `check_matched_source_position`, `source_position_tolerance`, and
   `psf_error_map` were removed in the temporary smoke copy.
9. Repair the local venv build toolchain by downgrading `setuptools` from
   `82.0.1` to `69.5.1`, then install `fastell4py` from
   `https://github.com/sibirrer/fastell4py.git` at commit
   `3448d58033ebbf1c0ac3047459d6c999ba6701fe`.  Rerun the bounded
   PEMD/SHEAR smoke notebook without `suppress_fastell`; this verifies the
   physical PEMD backend is available for model-plumbing, not that a posterior
   has been reproduced.
10. Run a minimal posterior-plumbing pilot with the physical PEMD backend:
    one tiny PSO step followed by a deliberately tiny `emcee` path.  This
    verifies the local MCMC route can execute and write an output artifact; it
    is not a convergence, posterior-quality, or evidence claim.
11. Run a short diagnostic pilot with one tiny PSO step followed by a 20-step
    `emcee` path.  The lenstronomy venv inspection found `(4240, 53)` samples,
    `(4240,)` log-probabilities, all finite samples/log-probabilities, and
    split-half mean shifts of about `0.093` sigma median and `0.426` sigma max.
    This is a chain-health diagnostic only, not a convergence certificate.
12. Run a diagnostic60 pilot with one tiny PSO step followed by a 60-step
    `emcee` path.  The derived payload summary records `(12720, 53)` finite
    samples, finite log-probabilities, and split-half mean-shift quantiles of
    about `0.377` sigma median, `0.833` sigma p90, and `0.943` sigma max.
    This is stronger plumbing evidence but still shows chain drift, so it is
    not a converged no-T2 posterior.
13. Run a diagnostic120 pilot with one tiny PSO step followed by a 120-step
    `emcee` path.  The derived payload summary records `(25440, 53)` finite
    samples, finite log-probabilities, and split-half mean-shift quantiles of
    about `0.820` sigma median, `1.398` sigma p90, and `1.493` sigma max.
    The increased drift relative to diagnostic60 is a negative convergence
    diagnostic, not a failure of model execution.
14. Run a diagnostic120 continuation from the previous chain endpoint.  This
    omits the new PSO step and starts the `emcee` walkers from the endpoint of
    `tau_core_mcmc_diag120_pemd_fastell_backend`.  The derived payload summary
    records `(25440, 53)` finite samples, finite log-probabilities, and
    split-half mean-shift quantiles of about `0.817` sigma median, `1.261`
    sigma p90, and `1.412` sigma max.  This confirms continuation plumbing,
    but it remains a bounded chain-health diagnostic, not a converged posterior.
15. Run a second diagnostic120 continuation from the first continuation
    endpoint.  The derived payload summary records `(25440, 53)` finite
    samples, finite log-probabilities, and split-half mean-shift quantiles of
    about `0.873` sigma median, `1.375` sigma p90, and `1.526` sigma max.
    This confirms repeated endpoint continuation plumbing, but it does not
    clear the convergence blocker.
16. Run a cold diagnostic120 continuation from the second continuation endpoint
    with `sigma_scale=0.02`.  The derived payload summary records `(25440, 53)`
    finite samples, finite log-probabilities, and split-half mean-shift
    quantiles of about `0.983` sigma median, `1.409` sigma p90, and `1.519`
    sigma max.  This is a negative proposal-scale sensitivity diagnostic:
    lowering the continuation proposal scale alone does not stabilize the
    no-T2 posterior.
17. Run a parameter-level split-half drift diagnostic across the bounded
    diagnostic120 and continuation payloads.  The persistent highest-drift
    directions are dominated by lens/source-light profile parameters and image
    position components, such as indexed `dec_image`, `R_sersic_lens_light3`,
    `n_sersic_lens_light1`, `n_sersic_source_light0`, and
    `n_sersic_lens_light0`.  This identifies where the local posterior route is
    unstable; it is not a posterior-convergence claim.
18. Build a nuisance-stabilization plan from the drift table.  The plan finds
    11 lens/source-light profile freeze candidates with mean split-half drift
    above one sigma, two image-position audit candidates, and three protected
    mass/shear parameters.  The recommended next bounded run is
    `profile_freeze_v1_bounded_diagnostic`: stabilize the highest-drift light
    profile nuisance directions first, keep image positions under audit, and do
    not promote any T2 or physical posterior claim.
19. Run `profile_freeze_v1_bounded_diagnostic`.  Because fixing nuisance
    parameters changes the active parameter set, this run uses previous
    best-fit initialization but does not reuse old MCMC samples.  It records
    `(20160, 42)` finite samples, finite log-probabilities, and split-half
    mean-shift quantiles of about `0.633` sigma median, `1.206` sigma p90,
    and `1.422` sigma max.  This improves the median drift relative to the
    continuation series, but the high-quantile drift remains visible.
20. Run a more aggressive `profile_freeze_v2` diagnostic, adding Chameleon and
    light-profile freezes from the remaining v1 drift list while still leaving
    image positions under audit and mass/shear unfrozen.  This run records
    `(16800, 35)` finite samples and finite log-probabilities, but the
    split-half mean-shift quantiles worsen to about `1.038` sigma median,
    `1.454` sigma p90, and `1.516` sigma max.  This is a negative
    stabilization diagnostic: after v1, simply freezing more light-profile
    directions transfers or worsens the drift.

## Reproducibility scripts and summaries

- `scripts/prepare_wgd2038_hst_reduced_data.py` prepares the split SCI/WHT
  files from local HST FITS products.
- `scripts/audit_wgd2038_lenstronomy_hst_reproduction.py` records the bounded
  HST-to-lenstronomy reproduction verdict.
- `summary.json` records the current bounded reproduction status.
- `data/derived/wgd2038_lenstronomy_hst_reproduction_manifest_v1.csv` records
  the generated HDF5 file names, local paths, sizes, and hashes observed in
  the audit environment.

## Current verdict

The WGD2038 route has advanced from notebook/payload hook to reproduced HST
preprocessing, multiband setup preflight, and bounded local model-plumbing
smoke execution, including a physical-fastell PEMD backend smoke.  The
route now also reaches a minimal fastell-backed MCMC/posterior-plumbing pilot.
The route now also reaches a short finite diagnostic pilot.  The remaining
blocker is still the no-T2 image/model posterior: the diagnostic60 payload is
finite and useful, while diagnostic120 shows increased drift and is also not
converged.  The diagnostic120 continuation also runs from a previous endpoint
and remains finite, but it does not remove the convergence blocker.  A second
endpoint continuation also remains finite but does not improve the drift.
The cold continuation with `sigma_scale=0.02` is also finite but worsens the
drift, so simple proposal-scale reduction is not enough.
Parameter-level drift diagnostics point to nuisance-heavy light-profile and
image-position directions as the next target.
The first concrete follow-up is a bounded profile-freeze diagnostic, not a T2
sampling run.
That profile-freeze diagnostic reduces median drift but does not clear the
posterior gate.
The more aggressive v2 freeze worsens drift, so the next route should be a
less aggressive or structurally different nuisance treatment rather than more
blind profile freezing.
Either the original WGD2038
cluster/joblib outputs must be acquired, or an equivalent bounded local
physical posterior reproduction with convergence diagnostics must be produced
before any real-data T2 sampling is allowed.
