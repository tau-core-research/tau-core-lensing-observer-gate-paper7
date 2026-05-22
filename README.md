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
scripts/reproduce.py
tests/
```

## Included Data

The repository includes only derived tables and compact JSON summaries needed
for the paper-critical checks. It does not redistribute raw lensing, HST,
Chandra, or private working products.

Key derived artifacts:

```text
data/derived/public_deep_repository_target_status.csv
data/derived/he0435_public_repro_model_level_psf_validation.csv
data/derived/hff_static_control_scorecard.csv
data/derived/static_control_report_card_gates.csv
data/derived/repro_results/*/summary.json
```

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

## Scope

This repository is a reproducibility package for Paper 7 only. It excludes the
larger TPG workbench, raw downloads, failed product-acquisition attempts,
private notebooks, and broad Tau Core theory-hub material that is not required
to verify the paper package.
