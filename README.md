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
