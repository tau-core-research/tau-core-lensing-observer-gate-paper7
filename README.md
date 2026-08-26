# Paper 7: Tau-Core Lensing Observer-Gate Feasibility Study

This repository is the public reproducibility package for:

**Observer-Gated Tau-Core Lensing: A Public-Data Feasibility Study, Synthetic Identifiability Test, and Static-Control Falsification Protocol**

The package is intentionally small. It contains only the files needed to
compile the manuscript, rebuild the arXiv-oriented source package, and verify
the publication-facing derived checks.

## Theory Context

This paper is a theory-method and feasibility paper. It does not require
accepting Tau Core as a completed physical theory. It tests whether a
restricted observer-channel lensing operator can be stated in a falsifiable
way, while preserving explicit claim boundaries.

The paper-level candidate is the weak-field thin-lens leading term

$$
\delta\Phi_i =
\epsilon_\tau \pi_i |\Delta\phi_i| .
$$

The longer reciprocity, covariant-measurable, screen-interaction, and
dynamical-closure proof program is maintained in the Tau Core theory hub, not
inside this reproducibility repository.

## Main Claim

The publication-facing claim is deliberately narrow:

```text
The tau-core lensing observer-gate operator is a falsifiable, conditionally
motivated, weak-field candidate whose current public-data status is blocked
pending evidence-grade no-T2 time-delay model products.
```

It does not claim:

```text
T2 has been detected in real lensing data;
Tau Core is proven;
the reciprocity theorem is fully proven;
the screen interaction has been derived from an action;
the parent theory uniquely predicts the lensing operator.
```

## Source-Transport Boundary

The T2 operator is a terminal discriminator, not a reconstructed parent
connection. The current Tau Core source audit permits smooth non-scalar
optical transport only conditionally through either an independently sourced
full body connection or Kato transport `[dP_O,P_O]` of a varying,
constant-rank, source-owned access projector. Scalar `U(1)` phase/clock
holonomy does not determine normalized non-scalar optical orientation, and
direct full-rank access has zero Kato generator. No lensing endpoint or fitted
T2 amplitude is used to select the missing source arrows.

## Relation to Later Photon-Lensing MAR Work

Paper 18 adds a separate photon-lensing Morphological Alignment Residual (MAR)
protocol with a source-side template `T_tau = B_env A_f M_bf`.  Its v2 package
also adds out-of-sample scale validation, physical shear mocks, and a toy
Null-Matter Link diagnostic.  That later protocol complements this
observer-gated time-delay lensing gate by giving a non-circular
morphology-template route for convergence/shear residual searches.  It does
not change this paper's status: Paper 7 remains a T2 feasibility and
falsification protocol, not a real-data lensing detection or Tau Core proof.
Any future MAR/shear/null-matter signal must also pass Paper 17-style
shared-parent versus orientation controls before it can strengthen the lensing
branch.

## Main Files

```text
LICENSE
CITATION.cff
DATA_NOTICE.md
requirements.txt
README.md
paper7_submission_source/main.tex
paper7_submission_source/refs.bib
paper7_submission_source/main.pdf
paper7_submission_source/figures/
figures/
data/derived/
scripts/build_arxiv_source.py
scripts/audit_wgd2038_lenstronomy_hst_reproduction.py
scripts/reproduce.py
tests/
```

## Included Data

The repository includes only derived tables and compact JSON summaries needed
for the paper-critical checks. It does not redistribute raw lensing, HST,
Chandra, or private working products.

Raw acquisition/cache directories such as `data/external/` are intentionally
git-ignored.  The package records reconstruction scripts, source provenance,
hashes, and compact audit summaries instead of committing FITS images, cloned
source trees, notebooks, or large intermediate payloads.

Key derived artifacts:

```text
data/derived/public_deep_repository_target_status.csv
data/derived/he0435_public_repro_model_level_psf_validation.csv
data/derived/real_data_t2_eligibility_audit_v1.csv
data/derived/wgd2038_field_level_payload_audit_v1.csv
data/derived/wgd2038_public_payload_acquisition_manifest_v1.csv
data/derived/hff_static_control_scorecard.csv
data/derived/static_control_report_card_gates.csv
data/derived/repro_results/*/summary.json
```

## Current Real-Data T2 Eligibility Update

A refreshed source-family audit is included in:

```text
data/derived/repro_results/tau_core_lensing_real_data_t2_eligibility_audit_v1/summary.json
```

It inspects public TDCOSMO/H0LiCOW-style source families for the specific
Paper 7 requirement: an evidence-grade no-T2 image/model reproduction gate
before any T2 perturbation is sampled.  The audit identifies
`TDCOSMO2025_public` as the best current follow-up source family and
`TDCOSMO_WGD2038_4008` as the best single-target acquisition candidate, but it
does not authorize real-data T2 sampling.  The next finite step is a
field-level payload audit for image labels, parity/order, Fermat-potential
samples, time-delay observations, and nuisance/model-ensemble membership.

The first WGD2038 field-level audit is also recorded in:

```text
data/derived/repro_results/tau_core_lensing_wgd2038_field_level_payload_audit_v1/summary.json
```

It finds useful public ingredients (`Ddt` samples, weights,
kappa/environment support, and a Fermat-potential notebook hook), but keeps the
real-data branch blocked because image parity/order and image-wise
Fermat-difference samples are not yet available as an extracted audit table.
The notebook does contain the relevant `dphi_AB`, `dphi_AC`, and `dphi_AD`
design-vector hooks, so the next blocker is payload-level: acquire or
reconstruct the model-posterior/joblib products that feed the notebook and
materialize the per-sample image/model table.

A first acquisition manifest is recorded in:

```text
data/derived/repro_results/tau_core_lensing_wgd2038_public_payload_acquisition_v1/summary.json
```

This manifest hashes the locally acquired public support files copied from
the public TDCOSMO2025/WGD2038 source trees: the processed WGD2038 pickle, the
`Ddt`/weight CSV, the kappa/environment support file, the WGD2038 metadata
README, and the two relevant WGD2038 notebooks.  The repository-declared
Google Drive folder for the missing target-specific payload was not
retrievable from the current environment, so the model-posterior/joblib
payload is still marked as missing.  The manifest extracts 36 concrete
`lenstronomy_modeling/temp/<model_id>_out.txt` joblib targets from the Fermat
notebook, making the next acquisition step explicit.  Follow-up checks against
the declared Google Drive folder, the WGD2038 GitHub tree, the TDCOSMO2025
GitHub tree, paper/source supplementary routes, and Zenodo did not produce a
publicly retrievable copy of the model-posterior/joblib payload.  Therefore the
updated status is: support payload acquired, physical no-T2 image/model
reproduction still blocked, real-data T2 sampling still not authorized.

The WGD2038 arXiv source-table payload is recorded in:

```text
data/derived/repro_results/tau_core_lensing_wgd2038_arxiv_source_table_payload_v1/summary.json
```

This acquisition pulls the official arXiv `2406.02683` source bundle and
materializes the three WGD2038 source tables for published `Ddt` and flat-LCDM
`H0` constraints. It adds 27 structured rows, including the final published
`Ddt = 1.68^{+0.40}_{-0.38}` Gpc and `H0 = 65^{+23}_{-14} km/s/Mpc` summary
values. This is useful source-backed summary payload, but it is not the missing
posterior/Fermat table: it contains no image-wise Fermat differences, sample
IDs, parity/order, or model posterior rows.

A bounded HST-to-lenstronomy reproduction audit is recorded in:

```text
data/derived/repro_results/tau_core_lensing_wgd2038_lenstronomy_hst_reproduction_v1/summary.json
data/derived/repro_results/tau_core_lensing_wgd2038_lenstronomy_hst_reproduction_v1/RECONSTRUCTION.md
```

This moves the WGD2038 route one step forward: public HST inputs were reduced
into the three-band lenstronomy HDF5 input format, the F160W notebook raw-cell
save issue was isolated as a compatibility/detail problem, and the multiband
notebook data/setup path passed a local preflight. A bounded one-step
PEMD/SHEAR model-plumbing smoke run also completed under documented
compatibility constraints (`suppress_fastell=True`, no PSF iteration, no
alignment, no MCMC). After repairing the local venv build toolchain and
installing `fastell4py`, a second one-step PEMD/SHEAR smoke run completed with
the physical PEMD backend, still without PSF iteration, alignment, MCMC, or
posterior analysis. A follow-up minimal `emcee` posterior-plumbing pilot also
completed and wrote an output artifact. A short diagnostic pilot then produced
a finite `(4240, 53)` sample payload in the lenstronomy venv, with finite
log-probabilities and modest split-half mean shifts. A 60-step diagnostic run
then produced a finite `(12720, 53)` payload; its split-half drift remains
visible, so it is useful chain-health evidence but not convergence. A 120-step
diagnostic produced `(25440, 53)` finite samples, but the split-half drift
increased, which is a negative convergence diagnostic. This is still not a
no-T2 image/model posterior reproduction. A diagnostic120 continuation run
started from the previous chain endpoint also produced `(25440, 53)` finite
samples with finite log-probabilities, confirming continuation plumbing, but
visible split-half drift remains. A second endpoint continuation also produced
finite samples, but its drift did not improve. A cold continuation with
`sigma_scale=0.02` was also finite, but the drift worsened rather than
stabilizing. A parameter-level drift diagnostic shows that the remaining
instability is concentrated in nuisance-heavy lens/source-light and
image-position directions. The resulting nuisance-stabilization plan selects a
bounded `profile_freeze_v1_bounded_diagnostic` follow-up: stabilize the
highest-drift light-profile nuisance directions first, keep image positions
under audit, and keep mass/shear and T2 claims protected. The remaining blocker
is a converged and validated physical posterior, or the original full
cluster/MCMC joblib output, before any real-data T2 perturbation may be sampled.
The first `profile_freeze_v1` bounded diagnostic has now run with 42 active
parameters and finite samples/log-probabilities; it improves median split-half
drift to about 0.633 sigma, but high-quantile drift remains, so the no-T2
posterior gate is still not cleared. A more aggressive `profile_freeze_v2`
run with 35 active parameters remained finite but worsened drift, so the next
route should not be blind additional profile freezing.

Because the WGD2038 route is now blocked by nuisance-posterior stabilization
rather than by raw data access alone, an alternate-source audit is recorded in:

```text
data/derived/repro_results/tau_core_lensing_alternate_source_candidate_audit_v1/summary.json
```

The audit promotes `DESJ0408_time_delay_cosmography` to the best current
bounded no-T2 follow-up candidate.  The cached public repository contains five
notebooks, six processed data/PSF HDF5 files, 24 lens-model posterior files,
24 time-delay posterior files, and a velocity-dispersion grid.  This is a
stronger follow-up route than a compressed distance-posterior source, but it is
not a real-data T2 result: the next step is a compatibility extractor and a
bounded no-T2 baseline reproduction.  Real-data T2 sampling remains
unauthorized.

The first DES J0408 no-T2 time-delay extraction smoke is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_no_t2_baseline_smoke_v1/summary.json
```

It reads all 24 public DES J0408 time-delay posterior files, each with 10,000
two-delay samples, and compares them to the observed delay constants declared
in the public post-processing class.  The best unweighted smoke diagnostic is a
composite model (`0408_run917_1_1_0_0_0_1_1_0`) with mean chi-square about
3.657 against the two observed delays and 99.28% of samples inside the
two-dimensional 2-sigma box.  This is a useful no-T2 compatibility result, not
an evidence-grade reproduction: the full lens posterior, model weights/logZ,
and image/model quantities still require a compatibility reader or notebook
runner.

The DES J0408 full posterior compatibility smoke is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_full_posterior_compat_smoke_v1/summary.json
```

This adds the compatibility reader for the older Astropy/dill posterior files.
All 24 public lens-model posterior files load successfully; each has 10,000
samples, 57--62 active parameters, a matched public time-delay posterior file,
and point-source image-position records.  The smoke also exposes logZ-like
sampler fields and model-configuration metadata.  The current global best
logZ-like record is a composite model (`0408_run918_1_1_1_0_0_1_1_0`).  This
still does not recompute image-level Fermat or arrival-time quantities, so the
next finite step is to use the decoded samples/configuration to compute those
features under the no-T2 baseline.

The DES J0408 arrival-time recomputation smoke is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_arrival_time_recompute_smoke_v1/summary.json
```

For the compatible power-law model `0408_run1001_0_0_0_0_0_1_1_0`, the current
lenstronomy reader can turn decoded posterior samples into finite image-level
arrival-time differences.  However, the recomputed first 128 samples do not
match the public DES time-delay table for the same model.  The mean absolute
differences are about 87 and 136 days for the two delay columns.  A follow-up
pair audit shows that simple image-pair relabeling does not resolve the raw
modern-reader mismatch: the best direct pair choice still has an RMSE of about
90 days.

The mismatch is then resolved at the bounded power-law smoke level by an
occurrence-aware old-to-modern parameter alignment.  The old posterior has 57
stored parameters; modern lenstronomy expects 58 because it inserts
`s_scale_lens0` after `gamma_lens0`, and duplicate `ra_image`/`dec_image`
names must be matched by occurrence rather than by plain dictionary key.  With
`tau0 -> tau0_list` aliasing and `s_scale_lens0 = 0`, the recomputed table
matches the public time-delay table with RMSE about 0.0145 days on the first
128 samples.  This is still not a T2 result; it is a compatibility recovery
that makes the next no-T2 DES J0408 extraction step much more concrete.

The DES J0408 power-law family alignment smoke is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_powerlaw_family_alignment_smoke_v1/summary.json
```

It applies the same occurrence-aware recovery to all 12 public power-law
posterior files.  The raw modern reader mismatch is confirmed across the
family.  The 57-parameter core subset is largely recovered: 5 of 6 models pass
the strict public-table match criterion, with a median aligned RMSE of about
0.017 days.  The 60-parameter legacy subset remains blocked: 0 of 6 models pass
under the current alignment rule, with median aligned RMSE about 8.22 days.
Therefore the current DES status is not a complete no-T2 baseline, but a
sharper split: the 57-parameter power-law path is usable for the next bounded
feature-table extraction, while the 60-parameter and composite paths need
separate legacy compatibility handling.

The DES J0408 57-parameter core feature-table extraction is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_powerlaw_57_core_feature_table_v1/summary.json
```

This promotes the family smoke into a longer-prefix feature audit on the
validated 57-parameter core, still without T2.  The result is more restrictive
than the 128-sample smoke: on a 1,024-sample recomputed prefix, only 2 of the
5 previously recovered core models remain clean under both row-wise and
distributional feature checks.  The best model by public observed-delay
chi-square and by core-relative logZ weight is
`0408_run1001_0_0_0_0_0_1_1_0`; it reproduces the public prefix with RMSE
about 0.015 days.  The artifact therefore creates a useful strict DES
no-T2 feature table, but it also preserves the negative result that the full
57-parameter core is not yet a completed no-T2 baseline.

The DES J0408 57-core failure diagnostic is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_powerlaw_57_core_failure_diagnostic_v1/summary.json
```

It shows why the failed core models should not simply be promoted.  The four
failed 57-parameter models are outlier-dominated under the current alignment:
typical rows remain close to the public table, but one or two catastrophic
legacy rows drive the strict RMSE failure.  No broad ordinary-row failure is
detected.  This narrows the blocker to a row-level provenance/outlier-policy
problem.  Until such a policy is independently justified, the strict DES
no-T2 feature core remains the two clean models only.

The row-level outlier provenance audit is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_powerlaw_57_core_outlier_provenance_v1/summary.json
```

This audit inspects the worst rows from the four failed 57-parameter models.
The top catastrophic rows are not parameter outliers, not low-likelihood
samples, and not runtime-warning rows.  They therefore look like ordinary
posterior rows whose public/recomputed table pairing breaks.  This supports a
row-linkage/provenance interpretation of the blocker, but it still does not
authorize row removal or promotion of the failed models.  The next finite
DES-specific step is to find an independent row-linkage rule in the public
notebooks or serialized sampler records.

The public-source row-linkage audit is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_row_linkage_public_source_audit_v1/summary.json
```

The public `output_class.py` supports intended index-order linkage:
`compute_model_time_delays()` loops over `samples_mcmc[i]`, appends the
corresponding `[dt_AB, dt_AD]` row, and `load_time_delays()` loads the saved
table without reordering while asserting the same length as the chain.  The
distance-posterior notebook also loads the public `td_` tables through this
path.  However, the public source does not contain an independent outlier
removal or row-recovery policy.  Therefore the blocker is narrowed but not
cleared: either the original legacy lenstronomy row semantics must be
reconstructed, or the strict two-model DES no-T2 core remains the only promoted
baseline.

The legacy-runtime compatibility audit is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_legacy_runtime_compatibility_audit_v1/summary.json
```

The distance-posterior notebook explicitly notes that it runs with
`lenstronomy v0.9.2`, and its notebook metadata records Python `2.7.15`.  The
current helper runtime is Python `3.9.6`, `lenstronomy 1.14.1`, Astropy
`6.0.1`, and dill `0.4.1`.  This is a plausible source for the few
row-level legacy defects, but it is not proof.  No old environment has been
reconstructed, and no failed model is promoted from this audit.

An optional local `lenstronomy 0.9.2` compatibility probe is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_lenstronomy092_probe_v1/summary.json
```

The probe constructs a Python `3.9.6` compatibility environment with
`lenstronomy 0.9.2`, NumPy `1.23.5`, SciPy `1.9.3`, Astropy `5.0.8`, and a
small SciPy private-API shim required by the old reader.  It imports and runs,
but it does not recover the public DES J0408 time-delay rows: all six
57-parameter core models fail the rowwise check over the first 128 samples,
with the best RMSE still about 622 days.  This does not refute the original
Python `2.7.15` environment, but it is negative evidence against using the
Python-3.9 `lenstronomy 0.9.2` workaround to promote the four failed models.
The strict DES no-T2 baseline therefore remains the two clean 57-parameter
models.

The DES J0408 lensing-feature to Tau-role constraint artifact is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_tau_role_constraints_v1/summary.json
```

It converts the two strict clean no-T2 feature rows into weak constraints on
the common Tau morphology candidate.  The artifact forces six lensing roles for
the strict DES core: endpoint-blind provenance, internal mid/mass geometry,
line-of-sight/environment structure, source-readout anchoring, rowwise closure
stability, and observed-delay scale compatibility.  It also preserves one
negative constraint: the failed DES models cannot be promoted without an
independent row-recovery or null-policy proof.  This narrows the lensing role
cover of the common morphology candidate, but it does not derive
`Response_tau_lens`, does not introduce T2, and does not authorize real-data T2
sampling.

The DES J0408 no-T2 time-residual candidate pretest is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_no_t2_time_residual_candidate_v1/summary.json
```

It asks the original Paper 7 question in the currently permitted form: do the
strict clean no-T2 lens models leave a coherent time-delay residual direction?
For the two clean DES J0408 57-parameter rows, the unweighted model-minus-
observed residual vector is approximately `(-3.43, +19.84)` days, while the
logZ-weighted vector is approximately `(-2.81, +19.95)` days. The residual
signs agree across both clean models and the pairwise residual-vector cosine is
about `0.998`. This is a bounded design target for a later T2 test, not a
Tau-specific time-shift detection: no T2 parameter is fitted or sampled, the
failed DES rows are excluded, and real-data T2 sampling remains unauthorized.
The same audit also checks the non-clean DES feature rows as a negative
control. Those rows show a similar residual direction, so coherence alone is
not specific enough for a T2 claim. The result should therefore be used only as
a pre-registered design vector for later null/T2 comparison, preferably with an
independent lens-system check.

The DES J0408 null-versus-T2 design freeze is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_t2_null_comparison_design_freeze_v1/summary.json
```

It freezes the correction direction that a later bounded T2 comparison would
have to explain: observed-minus-model is approximately `(+3.43, -19.84)` days
in the two-delay basis. It also freezes the competing null explanations:
ordinary no-T2 nuisance freedom, lens/source-family mismatch, DES row/runtime
systematics, and the non-clean-row coherence control. This artifact still does
not authorize a T2 fit or sampling step; it only prevents a future comparison
from choosing the target direction after seeing the result.

The DES J0408 one-amplitude T2 operator pretest is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_one_amplitude_t2_operator_pretest_v1/summary.json
```

It defines the minimal closed-form score operator
`Delta_t_corrected = Delta_t_noT2 + alpha * u_frozen`, with nonnegative
least-squares `alpha` on the two strict clean DES rows. The frozen direction
reduces the clean-core residual RMSE from about `20.15` days to about `0.62`
days, while the simple orthogonal/swapped/opposite controls do not improve the
score under the same nonnegative-alpha rule. However, applying the same frozen
alpha to the non-clean DES control rows also improves their RMSE strongly. The
artifact therefore supports a bounded design follow-up, but it is explicitly
not endpoint-blind, not Tau-derived, not a posterior fit, and not T2 evidence.

The DES J0408 independent holdout readiness audit is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_t2_holdout_readiness_v1/summary.json
```

It asks whether the DES-frozen one-amplitude score can already be tested on an
independent lens. The answer is no. WGD2038-4008 is the best current holdout
route with readiness score `3/6`, but it still lacks the extracted image-wise
Fermat/arrival table, image parity/order, original joblib posterior payload, and
a converged no-T2 posterior. Therefore the DES score remains design-only. The
next finite action is to extract or reconstruct the WGD2038 per-sample
image/model table with image labels, parity/order, `dphi_AB/dphi_AC/dphi_AD`,
model sample IDs, and observed-delay/Ddt linkage.

The full 24-model DES J0408 MD1/F1 output-rank audit is recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_full24_md1_f1_rank_v1/summary.json
data/derived/repro_results/tau_core_lensing_desj0408_full24_md1_f1_rank_v1/report.md
data/derived/desj0408_full24_md1_f1_rank_v1.csv
```

This audit uses all 24 public no-T2 time-delay posterior files (`240,000`
samples total) and freezes their empirical nuisance-response span before
projecting the observed `dt_AB,dt_AD` vector. The two singular values of the
24 model means are `13.1185` and `1.3553` days, so the second direction remains
`10.33%` of the first and the nuisance span has rank two even at a `10%`
relative threshold. The power-law and composite families separately have rank
two; all 24 leave-one-model-out audits retain rank two; and all 2,000 posterior
bootstrap replicates retain rank two at the `5%` threshold.

After whitening by the published delay uncertainties, the second-to-first
singular ratio is smaller, `0.03095`. The exact whitened rank remains two, but
a declared `5%` truncation retains only one nuisance direction and leaves one
practical weak direction. The observed offset projects onto that weak direction
with norm `1.7665` sigma. This is below a detection claim and is retained only
as a sensitivity target whose stability requires independent nuisance
constraints and lens replication.

The measured delay space is itself two-dimensional. Consequently its
nuisance-orthogonal complement has dimension zero: a delay-only DES J0408
measurement cannot identify an independent `F1` observer-path row under this
declared no-T2 model ensemble. This is a measurement-design identifiability
no-go, not evidence that observer-path physics or physical time distortion is
zero. The covariance-whitened weak direction does not change that structural
verdict and is not a detection. Rank repair requires either a genuinely third
path-sensitive observable or independent constraints that reduce the effective
nuisance rank below two.

The channel-first rank-repair atlas and first conditioning result are recorded
in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_channel_first_rank_repair_v1/summary.json
data/derived/repro_results/tau_core_lensing_desj0408_crr_a_kinematic_conditioned_rank_v1/summary.json
```

The atlas forbids assigning a time, quantum, or other-readout origin before a
generic nuisance-orthogonal channel component is established. `CRR-A` uses all
480 four-aperture velocity-dispersion products to condition the 24 model delay
posteriors without using the observed delays. One positive velocity scale is
profiled per sample, leaving only kinematic shape as a constraint. The
conditioning does not repair rank: exact whitened rank remains `2`, practical
`5%` rank remains `1`, and `s2/s1` changes only from `0.030951` to `0.030961`.
The median effective sample size is `9999.34/10000`, showing that the available
kinematic shape barely reweights the posterior. The active repair route is now
`CRR-B`, a two-band fit followed by prediction in a genuinely held-out HST
band.

The first `CRR-B` execution gate now passes for the `LOBO-F814W` fold. A
single bounded PSO step (`4` particles, `1` iteration) fitted the shared
geometry using only `F475X+F160W`, with `bands_compute=[False,True,True]` and
no full-three-band initialization. The machine-readable audit is:

```text
data/derived/repro_results/tau_core_lensing_desj0408_crr_b_lobo_preflight_v1/execution_audit_f814w.json
```

This is a geometry-path preflight only. The held-out F814W pixels have not
been scored, fit quality has not been validated, and the compatibility run
omits the legacy `psf_error_map`; PSF uncertainty must return as a nuisance
contribution before endpoint scoring. No channel effect, time effect, quantum
effect, or Tau Core signal is claimed.

The pre-frozen `LOBO-F814W` score has now also been evaluated. With the public
PSF uncertainty propagated through the held-out linear solve, the profiled
whitened residual has `chi2/nu = 0.7723` (`21075` degrees of freedom), so this
first fold shows no excess channel residual. Omitting the PSF uncertainty
raises the same diagnostic to `chi2/nu = 5.7988`. The apparent excess is
therefore not robust to a mandatory instrumental-channel nuisance and cannot
be promoted to a generic channel effect. The freeze and score are recorded in:

```text
data/derived/repro_results/tau_core_lensing_desj0408_crr_b_f814w_holdout_freeze_v1/summary.json
data/derived/repro_results/tau_core_lensing_desj0408_crr_b_f814w_holdout_score_v1/summary.json
```

This is a preserved first-fold negative result. The other two LOBO folds,
population null calibration, and independent-lens replication remain open.

## DES J0408 Relative Clock-Rate Audit

The public COSMOGRAIL WFI A/B light curves permit a more direct observer-time
test than comparing measured delays with a lens-model residual. After a
constant delay is fitted, the alternative model allows one relative time
stretch:

```math
m_B(t)=c+p_{\rm micro}(t)+
m_A\!\left(t_*+\frac{t-\Delta t-t_*}{a_{B/A}}\right).
```

The central exploratory specification gives
`a_B/A=1.0594` and `Delta chi-square=6.08` relative to shift only. This is not
stable. Across the declared source-spline and slow-microlensing grid,
`a_B/A` spans the full search interval `[0.90,1.10]`, while the improvement
spans `[0.84,20.63]`. The result is therefore a materialized direct clock-rate
test but not evidence for path-dependent time distortion. The next finite
step is unit-stretch mock calibration followed by unchanged application to an
independent high-cadence lens.

```text
python scripts/audit_desj0408_ab_relative_clock_rate_v01.py

data/derived/repro_results/tau_core_lensing_desj0408_ab_relative_clock_rate_v1/summary.json
```

The first unit-stretch calibration uses 128 deterministic-seed parametric
mocks with the observed epochs and heteroscedastic errors. The observed
`a_B/A=1.0594` has empirical two-sided rate `p=0.124`; its
`Delta chi-square=6.08` has improvement `p=0.225`. Hence the observed
candidate is not unusual under this finite-sampling null. This closes a simple
estimator-bias interpretation but remains conditional on the same
spline-plus-linear-extrinsic model. Correlated residual and microlensing mocks
are still required before an independent lens is opened.

```text
python scripts/calibrate_desj0408_ab_relative_clock_rate_null_v01.py

data/derived/repro_results/tau_core_lensing_desj0408_ab_relative_clock_rate_null_calibration_v1/summary.json
```

The conservative correlated-null grid adds a common source residual and an
independent slower B-image extrinsic process. Four predeclared correlation
scenarios with 64 mocks each give pooled `p=0.300` for the rate magnitude and
`p=0.537` for the fit improvement. The observed stretch is therefore even
less distinctive once time-correlated residuals are admitted. DES J0408 is
closed as a positive path-clock result; the calibrated estimator is ready for
unchanged transfer to one independent public high-cadence lens.

```text
python scripts/calibrate_desj0408_ab_correlated_clock_null_v01.py

data/derived/repro_results/tau_core_lensing_desj0408_ab_correlated_clock_null_v1/summary.json
```

The frozen estimator was then transferred to the independent 13-year
COSMOGRAIL HE 0435-1223 B/C light curves. Only the externally published B/C
delay sets the target-specific search window. The observed relative rate is
`a_C/B=1.000898`. Against the first predeclared 128 official PyCS unit-stretch
mocks, its two-sided rate value is `p=0.791` and its fit-improvement value is
`p=0.450`. HE 0435 is therefore consistent with a common clock rate. Together
with the calibrated DES null, the current public-light-curve branch provides
no positive path-dependent time-stretch evidence.

```text
python scripts/transfer_he0435_bc_relative_clock_rate_v01.py

data/derived/repro_results/tau_core_lensing_he0435_bc_relative_clock_rate_v1/summary.json
```

These image-to-image nulls constrain only differential path stretch. A clock
factor shared by all images cancels in their ratio. The primary common-mode
test must instead compare the reconstructed intrinsic lensed-source timescale
with physically matched unlensed quasars.

The first support audit uses the 9,258-object MacLeod et al. SDSS Stripe 82
r-band DRW catalog and published DES J0408 source properties:
`z=2.375`, `log10(M_BH/M_sun)=8.41+/-0.27`, and
`log10(L_bol/[erg/s])=47.04`. Quality-controlled strict, moderate, and broad
windows contain only `2`, `6`, and `40` controls. Strict pair matching is
underpowered, while widening to 40 objects is not authorized for detection.
The finite continuation is a frozen full-population rest-frame `log(tau)`
regression followed by posterior-predictive evaluation of the reconstructed
lensed source.

```text
python scripts/audit_desj0408_unlensed_control_support_v01.py

data/derived/repro_results/tau_core_lensing_desj0408_unlensed_control_support_v1/summary.json
```

An orthogonal same-source route avoids both image-ratio common-mode
cancellation and cross-object population matching. Wyrzykowski et al. (2006)
identified periodic variable sources during OGLE-III microlensing events.
Eight corresponding public EWS archives are now checksum-frozen and audited
using a predeclared cadence/phase-support rule. Four events pass. The strongest
is the eclipsing source `OGLE-2004-BLG-081`: 120 measurements lie within one
Einstein-radius crossing time of peak, 207 lie outside two crossing times, and
all 12 phase bins are occupied.

```text
python scripts/audit_ogle_periodic_microlensing_clock_support_v01.py

data/derived/repro_results/tau_core_lensing_ogle_periodic_microlensing_clock_support_v1/summary.json
```

A first central diagnostic jointly profiles standard point-lens
magnification, an eight-harmonic eclipsing waveform, linear ephemeris
correction, slow quadratic phase drift, and one event-localized fractional
phase-rate coefficient. Source
variability is preferred over blend variability under the null model. Adding
the localized coefficient improves the central profiled fit, but its fitted
values are only approximately ownership-stable and the absolute fit remains
strongly misspecified. No clock claim follows from the central fit alone.

```text
python scripts/audit_ogle2004_blg081_local_clock_rate_v01.py

data/derived/repro_results/tau_core_lensing_ogle2004_blg081_local_clock_rate_v1/summary.json
```

The first unit-clock calibration uses 64 parametric and 64 circular
block-residual mocks per ownership model, preserving the observed epochs and
heteroscedastic errors. The observed improvement exceeds every mock in all
four null families (`p=1/65=0.0154`). The rate magnitude also exceeds every
source-owned mock and every parametric blend mock; the conservative
block-residual blend value is `p=3/65=0.0462`. Thus cadence and the measured
short-range residual structure do not explain the candidate.

This is statistical-null survival, not physical identification. A
microlensed eclipsing binary is an extended two-component source.
Differential/finite-source magnification can change eclipse depths and shapes
without changing its clock. The current point-source Fourier model omits that
standard nuisance and has a large absolute misfit. No Tau time-distortion
claim is authorized until a fixed-ephemeris binary-source finite-source lens
model fails to absorb the candidate.

```text
python scripts/calibrate_ogle2004_blg081_local_clock_null_v01.py

data/derived/repro_results/tau_core_lensing_ogle2004_blg081_local_clock_null_v1/summary.json
```

The required finite-source discriminator changes the conclusion. A
first-order standard shape tangent allows every Fourier eclipse coefficient
to vary with both normalized lens strength and signed lens position. It
reduces the no-clock chi-square from `52805` to `18668`. A globally refitted
clock model reaches `13960`, but its fitted rate changes sign and magnitude to
`epsilon=-0.02445`, showing strong coupling to the nuisance geometry.

The decisive conditional audit freezes the observed finite-tangent null
geometry and profiles the complete linear source shape while scanning the
clock coefficient. On the real data its optimum is exactly `epsilon=0` with
`Delta chi-square=0`. Parametric and block-residual mocks therefore return
`p=1`. The apparent global improvement exists only through a joint jump to a
different lens/ephemeris optimum; it is not a locally identifiable clock
component.

OGLE-2004-BLG-081 is consequently closed as a positive time-distortion result.
It remains a useful same-source method prototype. An exact binary-source model
is not warranted as a rescue fit for this event; a new event must first show a
locally nonzero clock coefficient after finite-source shape conditioning.

```text
python scripts/audit_ogle2004_blg081_finite_source_clock_discriminator_v01.py
python scripts/calibrate_ogle2004_blg081_finite_tangent_clock_null_v01.py

data/derived/repro_results/tau_core_lensing_ogle2004_blg081_finite_source_clock_discriminator_v1/summary.json
data/derived/repro_results/tau_core_lensing_ogle2004_blg081_finite_tangent_clock_null_v1/summary.json
```

The frozen local-identifiability rule was transferred unchanged to the two
remaining public source candidates. `2002-BLG-103` gives exactly
`epsilon=0` and `Delta chi-square=0`. `2004-BLG-390` survives the precheck
with `epsilon=0.03082` and `Delta chi-square=64.43`. On 64 parametric and 64
block-residual finite-tangent null mocks, both its improvement and rate
magnitude give `p=1/65=0.0154`.

The same-source premise nevertheless remains unresolved. Equal-complexity
fits favor a variable lensed source over a variable unlensed blend by only
`Delta BIC=3.95`, below the frozen strong-evidence threshold of 10. The EWS
fit has `f_bl=1`, which is supportive but does not establish ownership, and
the 2006 paper did not uniquely fit this event's variable-source/blend
assignment. `2004-BLG-390` is therefore retained as a conditional statistical
candidate at this stage, not observer-time evidence.

The frozen robustness grid then closes that candidate. All nine combinations
of harmonic order `(4,6,8)` and symmetric time window
`(+/-4,+/-8,+/-16) tE` return a formally nonzero local component, but its sign
is unstable: fitted values occupy negative branches near `-0.011` and
`-0.030` as well as a positive branch near `+0.030`. A physical clock rate
cannot reverse under these source-model resolutions. The predeclared
sign-stability requirement therefore fails despite a `9/9` nonzero rate.
Residual block-length calibration is not opened.

The current public OGLE sample contains no ownership-certified or
model-robust positive clock event. BLG-390 is demoted from conditional
candidate to a preserved multimodal-fit negative control.

A finite replacement-data audit prevents this null branch from turning into
open-ended refitting. MACHO-97-SMC-1 is not a clean successor: although its
source variability was used in a historical joint MACHO/EROS/OGLE model, a
later OGLE review records strong blending, possible artefactual variability in
the MACHO data, and only a fading event segment in OGLE-II. Published
pulsating-source microlensing studies supply the required finite-source,
chromatic, radius, temperature, and centroid nuisance physics, but not a new
observed public event. KMTNet, UKIRT, and VVV remain discovery corpora rather
than preidentified same-source clock events.

The present executable replacement set is therefore empty. The empirical
branch reopens only for a named event with independently established
source-clock ownership, public pointwise photometry, both lensed and control
phase coverage, and enough information to condition standard source-shape
effects. This is a data-frontier stop verdict, not a falsification of a
common-mode observer clock.

The prescribed residual-blind catalog crossmatch has now been executed on all
2,588 rows of the public KMTNet 2016 event list against six independent OGLE
periodic-variable families. It returns only three matches within one arcsec.
KMT-2016-BLG-0141 is blend-dominated: its OGLE eclipsing-binary mean magnitude
matches the KMT baseline, while the fitted microlensed source is 2.34 mag
fainter. KMT-2016-BLG-1490 is source-compatible, but only 2.74 cycles occur
within the two-`tE` event interval, below the frozen five-cycle threshold.

KMT-2016-BLG-1194 is the first new preflight candidate. It matches
OGLE-BLG-RRLYR-29501, an RRc source with period `0.28348449` d, at
`0.442` arcsec. The checksum-frozen KMT pySIS data provide 1,197 event-window
points, 613 outer controls, all 12 phase bins, and 326.5 cycles within
two `tE`. Its source magnitude is also as compatible with the OGLE mean as the
baseline magnitude. No residual or clock fit was used to select it.

This does not yet establish same-source ownership. The field is crowded, and
the coordinate/magnitude match must be tested with equal-complexity
variable-source and variable-blend likelihoods before any time-rate parameter
is opened.

That equal-complexity ownership audit now supports the source assignment. In
the source-owned model the frozen RRc Fourier basis is multiplied by the
standard point-lens amplification; in the blend-owned model it is not. The
source-owned model has lower chi-square independently in KMTA, KMTC, and KMTS
for every frozen harmonic order `(4,6,8,10)`, a `12/12` directional result.
The periodic clock is therefore eligible for a conditional local-rate test.
The absolute fits remain strongly misspecified, so no clock anomaly follows
from ownership alone.

The enriched conditional rate test is now complete. Its no-clock model
profiles the standard point lens, the frozen RRc ephemeris, slow frequency and
quadratic phase corrections, and separate source/blend/calibration/Fourier
coefficients for KMTA, KMTC, and KMTS. A dense phase-wrap-safe scan over the
single localized rate coefficient finds
`epsilon=0.00001` and only `Delta chi-square=1.316`. This fails the frozen
local-identifiability threshold `Delta chi-square>3.84`; no mock calibration is
opened. The no-clock reduced chi-square remains `28.26`, so the event is
preserved as an ownership-supported but shape-misspecified negative control,
not as a precision null or observer-time signal.

An independent-template transfer removes the remaining concern that the
site-specific KMT Fourier model was too flexible. The 867-point,
checksum-frozen long-baseline OGLE I-band light curve of
OGLE-BLG-RRLYR-29501 defines the eight-harmonic source waveform without using
the lensing data. KMT then receives only one waveform amplitude per site in
addition to source, blend, and calibration terms. After site-wise error
rescaling, the dense localized rate scan selects exactly `epsilon=0` with
`Delta chi-square=0`. The event is therefore closed without further waveform
enrichment. It remains a useful ownership-certified negative control, not
evidence against every possible common-mode observer clock.

The direct observer-clock branch is now consolidated rather than extended by
another event-specific fit. Six targets in two independent measurement
geometries give no robust positive result: DES J0408 and HE 0435 reject a
detectable differential image-rate stretch, while BLG-081, BLG-103, BLG-390,
and KMT-1194 reject or destabilize a scalar magnification-localized
same-source rate term. The resulting conditional no-go is narrow:

```text
simple directly identifiable scalar observer-clock deformation
-> not supported by the current frozen public tests
```

It does not exclude a common factor canceled by the comparisons, a
non-scalar observer-source response, a dependence on complete causal-support
morphology, a subthreshold effect, or another terminal readout. Closed events
must not be rescued by new source-shape freedom. The next admissible empirical
construction requires one source-frozen relational predictor derived from the
complete observer-source cone and tested first on an independent non-clock
terminal.

```text
python scripts/audit_ogle_replacement_same_source_clock_candidates_v01.py
python scripts/calibrate_ogle2004_blg390_finite_tangent_clock_null_v01.py
python scripts/audit_ogle2004_blg390_variability_ownership_v01.py
python scripts/audit_same_source_clock_replacement_data_frontier_v01.py
python scripts/crossmatch_kmtnet2016_periodic_source_clock_candidates_v01.py
python scripts/audit_kmt2016_blg1194_variability_ownership_v01.py
python scripts/audit_kmt2016_blg1194_conditional_clock_rate_v01.py
python scripts/audit_kmt2016_blg1194_ogle_template_clock_transfer_v01.py
python scripts/audit_observer_clock_empirical_branch_consolidation_v01.py

data/derived/repro_results/tau_core_lensing_ogle_replacement_same_source_clock_candidates_v1/summary.json
data/derived/repro_results/tau_core_lensing_ogle2004_blg390_finite_tangent_clock_null_v1/summary.json
data/derived/repro_results/tau_core_lensing_ogle2004_blg390_variability_ownership_v1/summary.json
data/derived/repro_results/tau_core_lensing_ogle2004_blg390_clock_robustness_grid_v1/summary.json
data/derived/repro_results/tau_core_lensing_same_source_clock_replacement_data_frontier_v1/summary.json
data/derived/repro_results/tau_core_lensing_kmtnet2016_periodic_source_crossmatch_v1/summary.json
data/derived/repro_results/tau_core_lensing_kmt2016_blg1194_variability_ownership_v1/summary.json
data/derived/repro_results/tau_core_lensing_kmt2016_blg1194_conditional_clock_rate_v1/summary.json
data/derived/repro_results/tau_core_lensing_kmt2016_blg1194_ogle_template_clock_transfer_v1/summary.json
data/derived/repro_results/tau_core_lensing_observer_clock_empirical_branch_consolidation_v1/summary.json
```

The required post-no-go cross-terminal step is now audited against the two
public routes already present in this repository:

```bash
python scripts/audit_relational_cone_cross_terminal_route_v01.py
```

Neither route currently permits reopening the clock branch. DES J0408 has a
source-forward, path-resolved local-cubic LOS predictor, but the physical cone
is incomplete and the F814W endpoint was opened before this predictor was
frozen. Its negative alignment is therefore exploratory. WGD2038 supplies a
genuinely distinct OIII amplitude terminal, but no source-frozen relational
cone predictor has been constructed for that system, and the coarse standard
substructure/multipole/source-size completion already makes the observed
vector compatible.

The finite decision is to use a new lens system. Imaging, redshift,
environment, and lens-model information must freeze one path-resolved
relational predictor and its sign before a predeclared non-clock amplitude or
extended-source morphology terminal and covariance are opened. Predictor
coefficients may not be selected from that terminal residual, and time remains
closed until the cross-terminal test succeeds.

```text
data/derived/repro_results/tau_core_lensing_relational_cone_cross_terminal_route_v1/summary.json
```

The blindness requirement is not merely procedural. Let `X` denote
source-side cone data, `N` the frozen standard nuisance design, `Y` the
held-out non-clock terminal, and `P_theta=f_theta(X)` the relational
predictor. If `theta` is selected after opening `Y`, a rank-`m` predictor menu
on an `m`-dimensional output can interpolate any terminal vector exactly.
The resulting in-sample alignment is not independent evidence. If `theta` and
the sign are frozen without `Y`, the only identifiable new direction is

```math
P_\perp =
\left(I-\Pi_{\operatorname{col}N}\right)P_\theta .
```

The finite exact witness and nuisance-projection check are reproduced by:

```bash
python scripts/audit_blind_cross_terminal_identifiability_theorem_v01.py
```

It proves why source freezing, terminal blindness, nonzero nuisance-orthogonal
rank, and a predeclared covariance are necessary. It does not prove that
nature realizes a nonzero Tau cone law.

The June 2026 JWST/NIRSpec measurement of RXJ1131-1231 materially changes the
development frontier. It supplies six published `[S III]` narrow-line
flux-ratio coordinates, public GO-1794 raw data, and the public
`lensqso-specfit` package. The terminal is non-clock and path-sensitive, but
it is not available for a new blind confirmation in this project: its values
were opened before a Tau relational predictor was frozen, and its extraction
uses a lens model of the same NIRSpec cube to remove extended emission.

```bash
python scripts/audit_rxj1131_relational_cone_development_role_v01.py
```

RXJ1131 is therefore selected as the development target. One predictor may be
built from pre-2026 HST lens, astrometry, redshift, and environment products.
Its sign and weights may not use the published `[S III]` residual. Confirmation
requires applying the unchanged construction to a second lens whose non-clock
terminal remains sealed.

The predictor-side packet is now frozen independently:

```bash
python scripts/freeze_rxj1131_pre2026_predictor_source_packet_v01.py
```

It combines the 2006 HST relative astrometry with the 2012 blind HST lens and
line-of-sight summary. The materialized invariants include four lens-centered
image vectors, all six pairwise image separations, the satellite relation,
main-lens scale and shape, external shear, convergence gradient, relative
galaxy count, and the reported foreground-cluster summary. A machine check
rejects the packet if any 2026 `[S III]` terminal coordinate or wavelength
appears.

This is a genuine source-side improvement, but not yet a complete cone. The
object-level wide-field redshift and group catalogs are recorded by provenance
but have not been materialized into a path-resolved mass transport here. No
scalar Tau predictor or sign has yet been selected.

```text
data/derived/repro_results/tau_core_lensing_rxj1131_pre2026_predictor_source_packet_v1/summary.json
```

The first terminal-blind path descriptor is now built from that packet:

```bash
python scripts/build_rxj1131_dimensionless_path_descriptor_v01.py
```

For image path \(i\), it freezes the dimensionless vector

```text
d_i = (
  r_i/theta_E,
  gamma cos(2(phi_i-phi_gamma)),
  theta_E grad(kappa) cos(phi_i-phi_grad),
  b_sat/|r_i-r_sat|
)
```

and the six pair descriptors `Delta_ij=d_i-d_j`. The four centered path
vectors have rank three, the maximum possible after removing their common
mode. No terminal value, fitted component weight, scalar law, or predictor
sign enters the construction. The vector is therefore a source-frozen
coordinate system for the next nuisance-projection audit, not yet a flux
predictor or Tau signal. Its local environment remains incomplete because no
object-level, path-resolved cone catalog has been inserted.

```text
data/derived/repro_results/tau_core_lensing_rxj1131_dimensionless_path_descriptor_v1/summary.json
```

The required nuisance-span audit gives an exact linear no-go:

```bash
python scripts/audit_rxj1131_standard_nuisance_span_v01.py
```

All four columns are constructed from declared standard lens coordinates.
Consequently the conservative standard nuisance design contains the full
descriptor column space:

```text
(I-Pi_col(N)) P = 0.
```

The six-by-four pair matrix has rank three, while its nuisance-orthogonal
projection has rank zero; its largest surviving entry is
`6.7e-16`. Therefore no linear weighting of the current descriptor can be
identified as extra Tau information. The result does not exclude a
source-derived nonlinear relation or an object-level, path-resolved cone
coordinate. It forbids manufacturing either from the opened terminal.

```text
data/derived/repro_results/tau_core_lensing_rxj1131_standard_nuisance_span_v1/summary.json
```

The apparent nonlinear escape is also closed for every endpoint-local scalar,
not only for the ten quadratic monomials. Let \(B\) be the oriented incidence
matrix of the six pairs of four image paths. Then

```text
rank(B) = 3,
P = B D,
rank(P) = 3,
col(P) = im(B).
```

For any scalar function `f` evaluated separately at each path,
`Delta_f=B f(D)` lies in `im(B)=col(P)`. Therefore

```text
(I-Pi_col(P)) B f(D) = 0
```

for linear, polynomial, and arbitrary nonlinear `f`. The explicit audit
enumerates all ten quadratic monomials and an independent nonpolynomial
witness; both project to zero at machine precision. A useful RXJ1131
extension must therefore be genuinely path-interior or pair-nonlocal, prove a
lower-rank physical nuisance design, or enter a predictor frozen jointly
across several lens systems.

```bash
python scripts/audit_rxj1131_path_local_nonlinear_no_go_v01.py
```

```text
data/derived/repro_results/tau_core_lensing_rxj1131_path_local_nonlinear_no_go_v1/summary.json
```

The remaining non-exact cycle sector is not directly visible in this terminal
either. For the same incidence matrix \(B\),

```text
R^6 = im(B) direct-sum ker(B^T),
dim im(B) = dim ker(B^T) = 3.
```

Taking logarithms makes every scalar flux ratio exact:

```text
log(F_i/F_j) = log(F_i)-log(F_j).
```

It therefore lies in `im(B)` and is orthogonal to every non-exact cycle in
`ker(B^T)`. A physical path holonomy could affect these data only through a
separately derived holonomy-to-flux terminal map. Once converted into four
endpoint flux changes, the measured pair ratios are exact again and do not,
by themselves, identify their non-exact origin.

```bash
python scripts/audit_rxj1131_cycle_terminal_visibility_v01.py
```

```text
data/derived/repro_results/tau_core_lensing_rxj1131_cycle_terminal_visibility_v1/summary.json
```

The minimal holonomy-to-flux terminal map has now been derived. For one
resolved path,

```text
A_i = sqrt(mu_i) exp(alpha_i+i phi_i) A_source,
F_i = |A_i|^2 = mu_i exp(2 alpha_i) |A_source|^2.
```

A pure `U(1)` holonomy has `alpha_i=0`, so its phase cancels exactly from the
isolated intensity. The finite audit confirms phase variation below
`4.5e-15`. Relative phase becomes visible in a coherent sum of two amplitudes,
and a real nonunitary gain changes intensity directly. A third possible route
is a separately derived conversion

```text
holonomy -> lens Jacobian -> magnification -> flux.
```

Therefore resolved narrow-line flux ratios are not direct pure-phase
holonomy terminals. They require coherent branch interference, a sourced
nonunitary amplitude sector, or a sourced holonomy-to-magnification
connector. Flux data alone cannot select among those origins.

```bash
python scripts/audit_holonomy_to_flux_terminal_map_v01.py
```

```text
data/derived/repro_results/tau_core_lensing_holonomy_to_flux_terminal_map_v1/summary.json
```

The source-ownership audit decides both remaining routes for the current Tau
packet. The conditional positive-body amplitude

```text
A_B = 2 sqrt(rho_B)
```

is a normalized Hilbert--Schmidt positive-cone representative. Unitary
transport preserves its norm exactly, so it is not the path-wise positive
gain `exp(alpha_i)` required by the flux map. PBAL/PSFR also remains a
conditional, not currently selected, representation.

The current support-separated `PJR-X0` packet has a stronger obstruction on
the geometric route: its relevant mixed Hessian vanishes throughout the
frozen source neighborhood, so the holonomy--Jacobian cross derivative and
all its source derivatives are zero. A positive counterfamily

```text
H_epsilon = [[1,epsilon],[epsilon,1]], |epsilon|<1
```

preserves both pure-axis Hessians while allowing zero and both coupling signs.
Thus positivity and existing pure source data cannot select a nonzero
completion.

```bash
python scripts/audit_tau_amplitude_jacobian_source_ownership_v01.py
```

```text
data/derived/repro_results/tau_core_lensing_amplitude_jacobian_source_ownership_v1/summary.json
```

The theory repository now contains the corresponding minimal conditional
completion. It introduces one post-body Gram residual

```text
rho_HJ = p_J-J_0(M_s)-nu U_HJ h
```

between a rank-three protected holonomy coordinate and a rank-three terminal
screen-Jacobian response. Stationarity fixes
`p_J=J_0+nu U_HJ h`; the positive row scale cancels and its Schur complement
is zero. The induced flux differential is

```text
D_h log(F) = -nu tr(J_0^-1 U_HJ(.)).
```

This is a coefficient-free conditional construction, not a selected physical
Tau branch. The current parent still does not own `U_HJ`, choose `nu`, or
realize nonzero `h`, so no RXJ1131 terminal value enters it.

The companion source-symmetry theorem further proves that if the holonomy and
screen-Jacobian carriers are two source-owned copies of one multiplicity-one
standard `S_4` module, the equivariant Hodge intertwiner is fixed to
`+/-U_0`. The separate signs of `nu` and `U_HJ` are conventional because only
their product enters the response. One odd common-source anchor is needed to
select that composite sign relative to the standard Jacobian. The current
parent supplies none of these three ownership statements, so the completion
remains endpoint-blind and conditional.

## Paper 8 Source-Forward Time Handoff

The current Tau theory no longer permits the observed-delay residual direction
to stand in for a physical T2 predictor. The complete local body descriptor is

```text
R_O^body = (Theta_M, U_BF Phi_M),
N_O^body = ker(D Theta_M) intersect ker(D Phi_M).
```

Paper 8 is assigned the source-side morphology/body-coordinate role. Paper 7
retains observer-path pullback, standard-model nuisance separation, and
held-out testing. Their machine-readable handoff is generated by:

The first target-local geometry candidate is frozen directly for DES J0408
from its public lens/image posterior ensemble. Three modeled source components
define a translation- and rotation-invariant triangle. The highest
imaging-evidence exactly reconstructible model supplies the coordinates, while
the top five models provide a delay-blind stability audit. The components span
redshifts `2.375`, `2.228`, and `2.375`, so this is a multisource observer-field
calibrator, not one morphological-body descriptor and not `SFH_02`.

```text
python scripts/freeze_desj0408_source_morphology_triangle_v01.py

data/derived/repro_results/tau_core_lensing_desj0408_source_morphology_triangle_v1/summary.json
```

The corresponding four local image-path transports use the same selected
imaging model. Each operator is the inverse source-from-image lens Jacobian at
one quasar image, acting on the frozen oriented source-triangle edges. The
result preserves two positive- and two negative-parity paths without opening a
time-delay file. Because the triangle crosses source planes, these transports
are not yet promoted to body-conditioned `SFH_03` pullbacks.

The same-plane quasar-host-only fallback is also audited. Its Sérsic radius,
index, ellipticity magnitude, and axial angle are compared across the five
highest-evidence exactly reconstructible models. The scalar coefficients of
variation are `0.54`, `0.67`, and `0.79`, with axial-angle RMS `0.342` rad.
The parametric single-body descriptor is therefore not promoted.

```text
python scripts/audit_desj0408_single_body_host_descriptor_v01.py

data/derived/repro_results/tau_core_lensing_desj0408_single_body_host_descriptor_v1/summary.json
```

The finite body-ownership audit now closes the tempting merge repair. The
three source components occupy two source planes, while the four lensed images
are downstream path readouts rather than additional intrinsic body
coordinates. The same-plane host vector is model-family unstable and the
positive reconstruction supplies only one stable scalar. Therefore these
objects cannot jointly be promoted to one source-frozen `SFH_02` descriptor.
This is a no-go for the current payload, not for the existence of a body
descriptor. The resolving input is one uncertainty-propagated, same-source
intrinsic reconstruction with at least three stable relative coordinates.

```text
python scripts/audit_desj0408_body_ownership_v01.py

data/derived/repro_results/tau_core_lensing_desj0408_body_ownership_v1/summary.json
```

The direct reconstructed-brightness moment fallback is also closed. Re-solving
the public linear amplitudes produces a signed host reconstruction whose
absolute negative-to-positive integrated brightness ratio is `1.64`.
Zero-clipping would therefore define the morphology by an analyst choice
rather than by the source model.

```text
python scripts/audit_desj0408_host_brightness_moment_preflight_v01.py
```

The finite repair solves the image fit again with nonnegative total host
brightness on a frozen `41x41` source grid. All five model solves converge and
the scalar moment trace is stable (`CV=0.160`, mean `0.02533 arcsec^2`).
However, moment ellipticity remains unstable (`CV=0.503`) and axial-angle RMS
is `0.246 rad`. This materializes one scalar morphology invariant, not the full
`SFH_02` descriptor and not `Theta_M`.

```text
python scripts/solve_desj0408_positive_host_moment_v01.py
```

The stable scalar has also been transported through the four local lens
Jacobians using

```math
Q_s^{\mathrm{iso}}=\frac{q_s}{2}I,\qquad
Q_i=R_iQ_s^{\mathrm{iso}}R_i^\mathsf{T}.
```

Its image trace factorizes exactly:

```math
\operatorname{tr}(Q_i)
=q_s\,\frac{\operatorname{tr}(R_iR_i^\mathsf{T})}{2}.
```

The maximum numerical factorization error is `1.11e-16`. Consequently,
normalizing by the source trace removes all source information and leaves the
standard local Jacobian stretch. This is a useful scalar control and partial
single-body descriptor, but it does not supply an independent body-path
interaction, complete `SFH_02`/`SFH_03`, or `h_tau`.

```text
python scripts/audit_desj0408_scalar_body_path_coupling_v01.py
```

Retaining the full positive source tensor produces a different result. For
each of the five source models, the tensor is paired with the local Jacobians
from the same lens model and evaluated through

```math
c_{mi}
=
\frac{\operatorname{tr}(R_{mi}Q_mR_{mi}^{\mathsf T})}
{\operatorname{tr}(Q_m)\operatorname{tr}(R_{mi}R_{mi}^{\mathsf T})/2}
-1.
```

This quantity vanishes for an isotropic source. Paths 2 and 3 have stable
negative and positive signs, respectively, across all five matched models;
the orderings `(0,1)`, `(0,2)`, and `(2,3)` are also sign-stable. Thus a
non-scalar ordinal body-path structure survives the model-family audit.
Its amplitude is not stable, so this remains a source-forward morphology
control rather than promoted `SFH_02`/`SFH_03` or an observer-time signal.

```text
python scripts/audit_desj0408_joint_tensor_path_interaction_v01.py
```

The five ordinal inequalities were then frozen and evaluated on the seven
remaining eligible SPEMD imaging models. Their positive source solves all
converge, and the complete signature replicates in `7/7` holdout models. This
upgrades the result from a discovery-set pattern to an internal model-family
replication. It remains a one-target result: no independent lens system has
yet reproduced the signature, and no delay endpoint was used.

```text
python scripts/validate_desj0408_tensor_path_ordinal_holdout_v01.py
```

Because image indices are not portable physical labels, the replicated
signature was finally canonicalized as a sorted multiset within each parity
class. The coordinate-free statement is that the two negative-parity paths
straddle zero interaction. This holds in `12/12` eligible models.

The result is robust morphology/path geometry, but its exact decomposition

```math
c=e_Qe_R\cos(2\Delta\phi)
```

uses only the source second-moment tensor and standard local lens Jacobian.
It therefore supplies a label-invariant control, not Tau-specific information
beyond standard lensing and not an observer-time score.

```text
python scripts/audit_desj0408_coordinate_free_path_signature_v01.py
```

The stable source trace also has the invariant rank-one representation type
required of the common body coordinate. That type match does not identify a
physical clock. Explicit linear, logarithmic, square-root, and quadratic
functions of the same dimensionless trace all have rank one and the same
local null as `dq_s`, while inducing different clock covectors. Neither the
image-only data nor rank/null symmetry selects the function or its absolute
scale.

This materializes an `SFH_01`-compatible scalar class, not `Theta_M`.

```text
python scripts/audit_desj0408_scalar_clock_nonidentifiability_v01.py
```

The existing parent composition principle removes the functional ambiguity
conditionally. If the positive dimensionless body load
`x=q_s/q_*` composes multiplicatively while the clock coordinate composes
additively, continuity and unit normalization give the unique solution

```math
\Theta_M=\log(q_s/q_*).
```

A finite functional-equation audit rejects the linear, square-root, and
quadratic members of the earlier counterfamily and retains only the
logarithm. The DES J0408 image data do not prove the multiplicative
body-composition premise or determine `q_*`; the result therefore selects a
conditional clock shape, not the physical clock.

```text
python scripts/audit_desj0408_log_clock_composition_selection_v01.py
```

The natural morphology composition check changes the empirical status of the
scalar carrier. Moment traces compose additively under the usual independent
covariance composition, not multiplicatively. The positive deformation
character is instead

```math
m(Q)=\sqrt{\det Q},
\qquad
\frac{m(AQA^\mathsf T)}{m(Q)}=|\det A|.
```

This character law and its composition under successive deformations hold to
`1.11e-16`. However, opening all twelve eligible models removes the earlier
top-five stability: trace CV becomes `0.286` and area-character CV `0.290`,
both above the frozen `0.25` threshold. Thus the logarithmic shape retains a
natural mathematical carrier class, but DES J0408 does not materialize a
model-family-stable clock amplitude.

```text
python scripts/audit_desj0408_moment_area_character_v01.py
```

The corresponding local endpoint clock is also closed analytically and on all
twelve models:

```math
\Theta_i
=
\log\frac{m(R_iQ_sR_i^\mathsf T)}{m_*}
=
\log\frac{m(Q_s)}{m_*}+\log|\det R_i|.
```

Hence

```math
\Theta_i-\Theta_j
=
\log\frac{|\det R_i|}{|\det R_j|},
```

with maximum numerical error `8.88e-16`. Source morphology amplitude and the
unknown reference scale cancel, leaving exactly the standard logarithmic
magnification ratio. This closes the local endpoint log-area realization as a
separate Tau-specific clock candidate: it contains no information beyond
standard magnification. It does not close a clock functional depending on the
complete causal-support morphology between source and observer.

The next finite step therefore resolves the modeled cone interior rather than
adding another endpoint scalar:

```bash
python scripts/freeze_desj0408_modeled_cone_morphology_v01.py
```

Across all twelve eligible DES J0408 posterior models, the resulting artifact
freezes a path-by-component `2 x 2` effective-Jacobian response for eight
deflecting components on three lens planes. Its leave-one-component-out
nonadditivity reaches `0.0751` of the full Jacobian departure in the largest
case, so the cone cannot be represented as a simple sum of isolated objects.
This is ordinary standard multi-plane lens coupling, not Tau-specific
evidence. The descriptor covers the interior represented by the published
model, but not the complete physical light cone: unmodeled line-of-sight
matter and parent morphology are absent. It supplies a concrete `SFH_02`
scaffold, not `Theta_M`, `a_O`, `h_tau`, or an observer-time score.

```text
data/derived/repro_results/tau_core_lensing_desj0408_modeled_cone_morphology_v1/summary.json
```

The published line-of-sight environment is acquired separately from the
checksum-frozen arXiv source of STRIDES `2003.12117`:

```bash
python scripts/acquire_desj0408_strides_los_morphology_v01.py
```

This materializes 198 released DES J0408 spectroscopic galaxy rows and ten
identified groups, including sky position, redshift, stellar-mass proxy,
separation, and flexion-shift information. The paper reports 199 galaxies, so
the one-row source discrepancy is preserved rather than silently repaired.
The reported spectroscopic completeness is `0.68` for
`18 <= i < 23` and `5 arcsec <= radius < 3 arcmin`. This materially enriches
the cone morphology, but remains observationally incomplete. It does not yet
assign each object a four-path transport law and does not identify a Tau
clock.

The next artifact performs the redshift-dependent geometric assignment:

```bash
python scripts/build_desj0408_los_path_transport_geometry_v01.py
```

For twelve posterior models, 198 observed objects, and four image paths it
freezes `9504` ray-object intersections. Each ray is propagated to the
object's own redshift before its angular separation is evaluated. The median
spread between the four path separations is `2.981 arcsec`, so the environment
is genuinely path-discriminating and cannot be represented by one common
line-of-sight scalar. Within the published flexion-shift approximation, the
inverse-cube rescaling is the leading non-tidal path transport. Depending on
model and path, three or four objects cross the standard explicit-modeling
threshold. Their union is exactly G3--G6, the four perturbers already included
in the posterior lens model. Thus this order adds path resolution but no new
above-threshold mass component. Complete transport still requires the
collective subthreshold population, diffuse matter, and incompleteness.

The source-frozen collective audit excludes G3--G6 and retains the angular
spin structure of the remaining 178 objects:

```bash
python scripts/audit_desj0408_subthreshold_collective_flexion_v01.py
```

The median scalar amplitude sum is `3.417e-4 arcsec`, while median spin-1 and
spin-3 coherences are `0.506` and `0.539`. Odd-spin structure is nonzero on
all 48 model paths and varies between paths. Therefore a scalar convergence,
or even a spin-0/spin-2 convergence-plus-shear summary, discards measured
catalog morphology. These moments are a standard higher-order lensing
descriptor, not the vector sum of actual image shifts and not Tau evidence.

A deliberately stronger countermodel then inserts all 178 objects as
simultaneous untruncated SIS halos using the same Auger mass calibration. It
produces a median Jacobian change of `1.540` and leaves a median `0.920`
fraction after the best common affine subtraction. Such an order-unity LOS
correction is incompatible with treating these objects as individually weak
subthreshold perturbers. The construction is therefore rejected: STRIDES uses
SIS here to calibrate a local flexion diagnostic, not to authorize a global
sum of 178 infinite halos. The admissible next model must use local
higher-order tensors or independently calibrated truncated halos and must not
double count external convergence.

The admissible alternative keeps the far-perturber point-mass expansion local
and removes a full six-parameter common affine vector field across the four
images:

```bash
python scripts/audit_desj0408_local_cubic_los_transport_v01.py
```

This absorbs `99.875%` of the effective environmental deflection while leaving
a stable median non-tidal residual norm of `2.329e-4 arcsec`. The median
largest single-path residual is `1.725e-4 arcsec`, above the conservative
`1e-4 arcsec` flexion scale in all twelve posteriors. This is a source-frozen
standard higher-order LOS prediction suitable for a later held-out astrometric
endpoint. It is not a measured residual and carries no Tau/time attribution.

The direct point-source endpoint is presently blocked. The frozen prediction
has median maximum scale `0.172 mas`, whereas the twelve public models have
`1.335 mas` coordinate RMS and the F814W/F160W detector scales are
`40/80 mas`. Subpixel centroiding can beat a pixel, so this is not an
instrumental impossibility theorem. The decisive limitation is independence:
the public quasar positions are fitted model inputs/outputs and no separate
sub-mas astrometric covariance is available. Scoring them would be circular.
The branch is therefore redirected to a held-out extended-arc image endpoint.

The source-forward local-cubic field has now also been propagated into an
F814W extended-arc image template:

```bash
python scripts/score_desj0408_local_cubic_f814w_arc_template_v01.py
```

After excluding `0.16 arcsec` around each quasar image, the template-residual
cosine is `-0.0393`. The fixed, source-forward unit amplitude changes the
unweighted residual SSE by `-1.013e-4`, so it slightly worsens rather than
improves the image. The sign remains negative for exclusion radii from
`0.12` to `0.24 arcsec`. A freely profiled amplitude would have to reverse
the sign (`-30.99`) to obtain even a `0.1545%` SSE reduction. This is therefore
a stable exploratory null/negative result for this particular local
point-mass completion. It does not show that complete light-cone morphology is
irrelevant: the spectroscopic cone remains incomplete, diffuse structure and
halo truncation are absent, and the F814W endpoint had already been opened.
It supplies neither confirmatory standard-lensing evidence nor Tau/time
evidence.

The published STRIDES treatment also fixes what the admissible collective
completion is. G3--G6 are modeled explicitly, while the remaining low-impact
population enters through a weighted-count, Millennium-Simulation-calibrated
external-convergence distribution rather than as 178 independently summed
halos:

```bash
python scripts/audit_desj0408_collective_los_completion_decision_v01.py
```

For DES J0408 the reported distribution has median approximately
`-0.05 <= kappa_ext <= -0.04` and width about `0.03`. Through
`H0 = H0_model * (1-kappa_ext)` this corresponds to a median scale factor of
about `1.04--1.05`. A uniform external-convergence sheet is mass-sheet
degenerate with source rescaling in the imaging data, so it does not authorize
another independent F814W residual template. It must instead be retained as a
standard nuisance distribution in any later time-delay score. This prevents a
known LOS scaling from being misclassified as a Tau observer-time effect.

The corresponding delay-space marginalization is explicit:

```bash
python scripts/audit_desj0408_kappa_marginalized_delay_rank_v01.py
```

The external-convergence tangent is only `2.301 deg` from the dominant
covariance-whitened model direction, but it is not exactly parallel. Together
they have strict rank two in the two-delay output, so the exact delay-only
orthogonal dimension remains zero. At the previously declared `5%`
truncation, the practical weak direction survives geometrically. It is not
external-convergence-free: the published `kappa_ext` width projects about
`0.064 sigma` into it. This is far smaller than the earlier `1.77 sigma`
practical offset and therefore does not explain that offset, but the full
model-family rank still prevents treating the offset as an identified Tau
signal. A joint third observable remains necessary.

WGD 2038 supplies an independent three-delay output. Its two combined
GLEE/lenstronomy predictions were frozen before the observed delays were
measured, so they define a source-side published-summary nuisance basis:

```bash
python scripts/audit_wgd2038_published_summary_nuisance_rank_v01.py
```

The common `H0/kappa_ext/MST` scale and the GLEE--lenstronomy shape difference
have covariance-whitened rank two in the three-dimensional `(AB, AC, AD)`
delay space. They leave one frozen orthogonal direction, onto which the later
observed vector projects by `-2.703 sigma`. That candidate does not survive
the required mass-family completion:

```bash
python scripts/audit_wgd2038_mass_family_delay_rank_v01.py
```

Figure 22b/c of TDCOSMO IX separately publishes the pre-observation
power-law/composite and GLEE/lenstronomy delay distributions. Their digitized
mean, median, and mode vectors each give strict covariance-whitened rank three.
Thus the combined-summary reduction had artificially left one direction
unoccupied; at published family level the standard nuisance span fills the
entire three-delay output. The `-2.703 sigma` coordinate is not an identifiable
delay-only anomaly and no Tau or observer-time attribution is allowed. This is
a finite delay-only identifiability no-go, not evidence that the complete
observer readout is absent. A further test must add an independent observable
or impose a genuinely shared cross-lens constraint.

The first candidate fourth observable, the later X-Shooter stellar velocity
dispersion, has also been audited:

```bash
python scripts/audit_wgd2038_kinematic_holdout_independence_v01.py
```

Its `299 +/- 12 km/s` value was not used in the frozen TDCOSMO IX lens models,
so it is a genuine later observation. It agrees with the primary
`296 +/- 19 km/s` GMOS-S value by `0.133 sigma`. However, it measures the same
integrated stellar-dispersion terminal that was already used to condition the
published delay predictions. It is therefore an independent measurement, not
an independent readout coordinate. Appending it directly to the conditioned
delay vector would double count kinematic information. A viable fourth output
must instead carry spatially resolved kinematic shape or another genuinely
distinct observable.

The first public WGD2038 observable that does satisfy the distinct-terminal
condition is the narrow-line `[O III]` flux-ratio vector:

```bash
python scripts/audit_wgd2038_oiii_distinct_terminal_v01.py
```

The measured `(B/A, C/A, D/A)` ratios are `(1.16, 0.92, 0.46)`, while the
published position-only smooth macromodel predicts `(1.21, 0.99, 0.46)`.
Under the table's diagonal uncertainties, the largest component difference is
`-2.236 sigma` in `B/A`. These ratios were explicitly excluded from the
TDCOSMO IX time-delay lens constraints, so they provide a genuinely different
amplitude readout rather than a repeated delay or kinematic measurement.
They are not a Tau signal: the full ratio covariance and joint delay-flux
ensemble are unavailable, while subhalos, line-of-sight halos, deflector
multipoles, and finite narrow-line source size remain standard explanations.
The next bounded calculation is therefore a standard flux-specific nuisance
completion, not a Tau fit to three opened ratios.

The public completion payload is audited separately:

```bash
python scripts/audit_wgd2038_standard_flux_completion_payload_v01.py
```

The `samana` repository supplies WGD2038 data plumbing and an
`EPL+M1+M3+M4+shear` model, and `lenslikelihood` records the narrow-line
measurement inside a published multi-lens substructure likelihood. Neither
public repository contains a WGD2038 accepted-simulation or posterior-
predictive flux ensemble. Thus the standard model family is concrete, but the
probability of the opened `B/A` discrepancy is not reproducible from the
public payload. This is an access and identifiability result, not evidence
against standard substructure and not evidence for Tau Core.

The repository also contains a newer, source-frozen WGD2038 production
configuration from the JWST dark-matter survey. It uses the warm-dust ratios
`(1.209, 0.939, 0.430)`, a `1-10 pc` source-size prior, optical
`m=1,3,4` multipoles, and population-level halo priors. This is not an OIII
completion: it is a second amplitude terminal with a different physical
source kernel. Their measurement-level consistency is audited with:

```bash
python scripts/audit_wgd2038_cross_amplitude_terminal_stability_v01.py
```

Combining the published OIII diagonal errors with the full JWST covariance
gives `chi2=5.324` in three dimensions (`p=0.150`). The two amplitude
terminals are therefore statistically compatible at current precision, while
retaining measurable source-region dependence. This neither identifies a
common Tau coordinate nor detects observer-time distortion.

The exact published software commits were also installed in an isolated
environment and exercised through a bounded prior-predictive smoke runner:

```bash
python scripts/run_wgd2038_warm_dust_prior_predictive_smoke_v01.py
```

With fixed seed `20384008`, infinite flux acceptance tolerance, and the
optional image reconstruction disabled, two standard realizations produce
ratio vectors `(1.230, 1.025, 0.500)` and `(1.155, 0.766, 0.371)`. The exact
`samana` commit has a one-row output bug, so two realizations are the smallest
successful write test. This proves that the public prior-predictive route is
executable and generates nontrivial three-ratio variation. Two samples are
not an ensemble and authorize no probability, Tau, or time-distortion claim.

A separately named, predeclared `N=64` coarse ensemble can be reproduced with:

```bash
python scripts/run_wgd2038_warm_dust_prior_predictive_smoke_v01.py \
  --seed 20384100 \
  --n-realizations 64 \
  --output-name tau_core_lensing_wgd2038_warm_dust_prior_predictive_n64_v1
```

Its three-ratio sample mean is `(1.2086, 0.9795, 0.4538)`, and its empirical
covariance has strict rank three. Thus the unconditioned published standard
prior varies all three warm-dust amplitude coordinates; no linear complement
is automatically available for a new readout. With only 64 rows, the
worst-case binomial standard error is `0.0625`. This batch is not
flux-conditioned, is not an OIII source-kernel completion, and does not
authorize a posterior probability, anomaly significance, Tau score, or
observer-time claim.

The source launch does not define a finite flux-acceptance tolerance: its
forward tolerance is explicitly infinite, while the command-line tolerance
controls optional source-image reconstruction. The correct bounded
conditioning diagnostic is therefore Gaussian likelihood reweighting with the
published full flux covariance:

```bash
python scripts/audit_wgd2038_warm_dust_likelihood_reweighting_v01.py \
  --input-name tau_core_lensing_wgd2038_warm_dust_prior_predictive_n256_v1 \
  --output-name tau_core_lensing_wgd2038_warm_dust_likelihood_reweighting_n256_v1 \
  --minimum-effective-samples 20
```

The predeclared `N=256` run reaches effective sample size `20.535`, maximum
normalized weight `0.106`, and weighted mean
`(1.2117, 0.9315, 0.4318)`. Its weighted covariance remains rank three.
An eight-seed paired control also gives exactly identical ratios between the
reduced 10-iteration runner and the launch archive's 80-iteration,
align-images numerical configuration. These results materialize a coarse
warm-dust likelihood diagnostic and support the reduced numerical effort for
this terminal. They do not create an OIII completion, posterior-predictive
tail probability, Tau score, or observer-time result.

The OIII source kernel is now frozen directly from the original narrow-line
paper rather than inferred from the opened flux residual. Nierenberg et al.
model the nuclear narrow-line source as a circular Gaussian with independently
drawn `20-50 pc` FWHM. The `samana` source-size parameter has exactly this
Gaussian-FWHM meaning. A paired `N=64` forward run and compatibility audit are
reproduced with:

```bash
python scripts/run_wgd2038_warm_dust_prior_predictive_smoke_v01.py \
  --seed 20384100 --n-realizations 64 \
  --source-fwhm-min-pc 20 --source-fwhm-max-pc 50 \
  --source-kernel-label oiii_narrow_line \
  --output-name tau_core_lensing_wgd2038_oiii_prior_predictive_n64_v1
python scripts/audit_wgd2038_oiii_source_kernel_completion_v01.py
python scripts/audit_wgd2038_oiii_prior_predictive_compatibility_v01.py
```

The finite-source change is usually small but not uniformly negligible:
paired RMS ratio shifts are `(0.0137, 0.00785, 0.00343)`, with one maximum
absolute shift of `0.0998`. A frozen surrogate-transfer gate fails, so these
64 rows are not synthetically expanded. In the direct OIII ensemble, the
observed vector has Gaussian-moment Mahalanobis square `1.986` and
three-dimensional survival probability `0.575`; 10,000 bootstrap resamples
place the central 95% range at `0.398-0.686`. Thus the earlier `2.24 sigma`
smooth-macromodel component does not survive this coarse standard
substructure/multipole/source-size completion. The missing full OIII
covariance and joint delay-flux ensemble still prohibit definitive model
selection, Tau attribution, or observer-time scoring.

```text
python scripts/audit_desj0408_log_area_path_contrast_v01.py
```

```text
python scripts/freeze_desj0408_image_path_pullbacks_v01.py

data/derived/repro_results/tau_core_lensing_desj0408_image_path_pullbacks_v1/summary.json
```

```bash
python scripts/build_paper8_source_forward_time_handoff.py
```

and recorded in:

```text
data/derived/repro_results/tau_core_lensing_paper8_source_forward_time_handoff_v1/summary.json
data/derived/paper8_source_forward_time_handoff_v1.csv
```

The handoff preserves the full-24 DES result: the two-delay output is already
spanned by two nuisance directions, so inserting another two-component T2
vector cannot establish local identifiability. A new score requires a
source-frozen numeric `h_tau` plus at least one independently constrained
image/path-sensitive observable that enlarges the output space. The old
residual-derived direction remains a design control only. No real-data T2
sampling or time-distortion claim is authorized by this handoff.

The WGD2038 holdout extraction contract is recorded in:

```text
data/derived/repro_results/tau_core_lensing_wgd2038_holdout_extraction_contract_v1/summary.json
```

It turns that next action into a concrete 15-field schema for the independent
holdout table: target/model/sample identifiers, image labels and order,
parity/Morse role, image coordinates, `dphi_AB/dphi_AC/dphi_AD`,
observed-delay or Ddt linkage, sample weights, and the no-T2 residual vector
needed by the DES-frozen score. The contract also identifies 36 expected
joblib/posterior targets from the public WGD2038 Fermat-potential notebook.
The table is not extractable yet because those posterior/joblib outputs and
the image-wise Fermat/parity/arrival table are not materialized in the current
public package. Therefore no WGD score is run and no real-data T2 sampling is
authorized.

The WGD2038 partial holdout materialization is recorded in:

```text
data/derived/repro_results/tau_core_lensing_wgd2038_partial_holdout_materialization_v1/summary.json
```

It materializes the public part of that contract into a 36-row model-level
manifest. The support now includes the expected model target IDs, public
Ddt/kappa support, redshifts, velocity-dispersion support, and lens-property
summary. The processed public payload contains `567880` Ddt samples, with a
weighted median Ddt of about `1493.69`. This is useful source-backed structure,
but it is still not a score table: there are zero rows with per-sample image
labels, parity/order, Fermat differences, and no-T2 residual vectors. The DES
frozen score therefore remains unapplied to WGD2038.

The WGD2038 bounded local Fermat preflight is recorded in:

```text
data/derived/repro_results/tau_core_lensing_wgd2038_bounded_local_fermat_preflight_v1/summary.json
```

It uses the locally generated, explicitly non-converged WGD2038 diagnostic
outputs to test the extraction path itself. Three bounded local jobs expose
four-image best-fit tables, giving 12 image rows with image coordinates,
Fermat potentials, Jacobian determinant/trace, and Morse/parity labels. For
the primary profile-freeze v2 diagnostic the notebook-basis Fermat differences
are approximately `dphi_AB=-0.0060`, `dphi_AC=-0.0294`, and
`dphi_AD=-0.0809`. This is a technical extraction preflight only: it does not
use the published/converged WGD posterior, does not produce a no-T2 residual
vector, and still leaves zero score-ready rows.

The WGD2038 observed-delay linkage audit is recorded in:

```text
data/derived/repro_results/tau_core_lensing_wgd2038_observed_delay_linkage_audit_v1/summary.json
```

The WGD2038 observed-delay no-T2 smoke is recorded in:

```text
data/derived/repro_results/tau_core_lensing_wgd2038_observed_delay_no_t2_smoke_v1/summary.json
```

It transcribes the TDCOSMO XVI Fig. 2 delay vector and covariance into a local
artifact. The publication convention is \(\Delta t_{AX}=t_A-t_X\), with
observed delays `AB=-12.4`, `AC=-5.3`, and `AD=-33.3` days, and covariance
matrix in the `AB, AC, AD` order `[[14.2, 6.1, 7.5], [6.1, 14.8, 7.1],
[7.5, 7.1, 39.9]]` days squared. The script also records the sign conversion
from the WGD notebook basis, where `dphi_AB` denotes `phi_B-phi_A`, into the
publication's A-centered basis. Combining the transcribed delay vector with the
local bounded Fermat preflight gives a no-T2 residual smoke, but not a WGD
holdout score: the Fermat table is local and explicitly non-converged, not the
published/converged WGD posterior.

The observed-delay linkage audit now reports that the local observed-delay
vector and covariance are present and that a bounded no-T2 residual smoke can
be computed. The remaining blocker has narrowed to the score-ready component:
a converged or published WGD Fermat/posterior table in the same A-centered
convention. Until that table is available, the DES-frozen score remains
unapplied to WGD2038 and no real-data T2 sampling is authorized.

The WGD2038 published-model delay-shape crosscheck is recorded in:

```text
data/derived/repro_results/tau_core_lensing_wgd2038_published_model_delay_shape_crosscheck_v1/summary.json
```

It uses the TDCOSMO IX published combined GLEE and lenstronomy no-T2 delay
predictions at `H0=70`, together with the TDCOSMO XVI observed-delay vector.
After fitting one global time-delay scale, the best published-model match is
the lenstronomy combined prediction with scale `1.1015`, an implied pure-scale
`H0=63.55 km/s/Mpc`, and a remaining normalized delay-shape residual of about
`2.29` sigma units against the observed-delay covariance. This is a useful
published-model-level shape crosscheck. It is not a posterior-level WGD score:
the model prediction uncertainties and full posterior covariance are not
propagated because the score-ready WGD posterior/Fermat table is still missing.
No T2 parameter is fitted or sampled.

The WGD2038 delay-shape holdout target is recorded in:

```text
data/derived/repro_results/tau_core_lensing_wgd2038_delay_shape_holdout_target_v1/summary.json
```

It freezes the best published-model residual direction before a posterior-level
WGD score exists. In the A-centered `AB, AC, AD` delay basis, the target
residual is `[-6.8925, 5.7151, -6.6435]` days, with covariance-metric norm
`3.2378` sigma units. A future WGD posterior/Fermat table can be compared to
this predeclared direction by the covariance-metric cosine recorded in the
artifact. This target is intentionally conservative: it is not endpoint-blind,
because it is defined from the WGD2038 observed-delay vector and published
model predictions; it is not a posterior-level score; and it is not T2
evidence.

## Full-4D Score Boundary

Observer-path access and a nonzero mixed Hessian are not by themselves a Tau
signal. The later fixed compiler scores only the complete standard excess
`E_K = (K_HH - K_std) - C K_VV^-1 C^dagger` after a common coframe push.
Paper 7 supplies feasibility gates, not that physical packet.

## Reproduce

Create an environment with Python 3.10 or newer, then install the lightweight
test dependency:

```bash
python -m pip install -r requirements.txt
```

Run the Paper 7 reproduction check:

```bash
python scripts/reproduce.py
```

This compiles `paper7_submission_source/main.tex` with `tectonic`, builds the
arXiv source ZIP, and runs the public package tests.

## arXiv Source Package

Build the arXiv source package directly with:

```bash
python scripts/build_arxiv_source.py
```

This writes:

```text
arxiv_submission_source.zip
```

The ZIP is built from `paper7_submission_source/` and excludes the compiled
PDF and temporary LaTeX build files, matching the Paper 1-6 packaging pattern.

## Zenodo Publication Status

This public repository is Zenodo-ready for version `v0.1.0`:

```text
.zenodo.json
CITATION.cff
LICENSE
arxiv_submission_source.zip
paper7_submission_source/main.pdf
```

Automatic DOI minting requires enabling the repository in the Zenodo GitHub
integration before creating or reprocessing a GitHub release. If the
integration is not enabled, the same release package can be uploaded manually
or through the Zenodo API with this metadata.

## Scope

This repository is a reproducibility package for Paper 7 only. It excludes the
larger TPG workbench, raw downloads, failed product-acquisition attempts,
private notebooks, and broad Tau Core theory-hub material that is not required
to verify the paper package.
