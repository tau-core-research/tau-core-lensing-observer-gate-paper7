#!/usr/bin/env python3
"""Extract a bounded DES J0408 no-T2 time-delay baseline smoke summary.

This is a deliberately narrow compatibility extractor.  It reads the public
DES J0408 time-delay posterior text files and compares their two modeled delay
columns against the observed delay constants declared in the repository's
post-processing class.  It does not decode the full lens posterior pickle,
compute a new likelihood, sample T2, or claim real-data evidence.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DES_ROOT = ROOT / "data" / "external" / "source_candidate_repos" / "DESJ0408_time_delay_cosmography"
TD_DIR = DES_ROOT / "model_posteriors" / "time_delays"
DERIVED = ROOT / "data" / "derived"
OUT_DIR = DERIVED / "repro_results" / "tau_core_lensing_desj0408_no_t2_baseline_smoke_v1"
CSV_PATH = DERIVED / "desj0408_no_t2_baseline_smoke_v1.csv"


# Declared in DESJ0408_time_delay_cosmography/notebooks/process_output/output_class.py.
OBSERVED_DELAYS = np.array([-112.1, -155.5], dtype=float)
OBSERVED_SIGMA = np.array([2.1, 12.8], dtype=float)

POWERLAW_IDS = {
    "0408_run1001_0_0_0_0_0_1_1_0",
    "0408_run902_0_0_1_0_0_1_1_0",
    "0408_run903_0_0_0_1_0_1_1_0",
    "0408_run904_0_0_1_1_0_1_1_0",
    "0408_run905_0_1_0_0_0_1_1_0",
    "0408_run1006_0_1_1_0_0_1_1_0",
    "0408_run907_0_1_0_1_0_1_1_0",
    "0408_run908_0_1_1_1_0_1_1_0",
    "0408_run909_0_2_0_0_0_1_1_0",
    "0408_run910_0_2_1_0_0_1_1_0",
    "0408_run911_0_2_0_1_0_1_1_0",
    "0408_run912_0_2_1_1_0_1_1_0",
}


def model_id_from_path(path: Path) -> str:
    name = path.name
    if name.startswith("td_"):
        name = name[3:]
    if name.endswith("_mod_out.txt"):
        name = name[: -len("_mod_out.txt")]
    return name


def model_family(model_id: str) -> str:
    return "powerlaw" if model_id in POWERLAW_IDS else "composite"


def summarize_file(path: Path) -> dict[str, object]:
    samples = np.loadtxt(path)
    if samples.ndim != 2 or samples.shape[1] != 2:
        raise ValueError(f"expected two delay columns in {path}, got shape {samples.shape}")
    mean = np.mean(samples, axis=0)
    std = np.std(samples, axis=0, ddof=1)
    residual = mean - OBSERVED_DELAYS
    pull = residual / OBSERVED_SIGMA
    per_sample_chi2 = np.sum(((samples - OBSERVED_DELAYS) / OBSERVED_SIGMA) ** 2, axis=1)
    model_id = model_id_from_path(path)
    return {
        "model_id": model_id,
        "model_family": model_family(model_id),
        "sample_count": int(samples.shape[0]),
        "dt1_mean": float(mean[0]),
        "dt2_mean": float(mean[1]),
        "dt1_std": float(std[0]),
        "dt2_std": float(std[1]),
        "dt1_residual_days": float(residual[0]),
        "dt2_residual_days": float(residual[1]),
        "dt1_pull_sigma": float(pull[0]),
        "dt2_pull_sigma": float(pull[1]),
        "mean_chi2_vs_observed": float(np.mean(per_sample_chi2)),
        "median_chi2_vs_observed": float(np.median(per_sample_chi2)),
        "fraction_within_1sigma_box": float(
            np.mean(np.all(np.abs(samples - OBSERVED_DELAYS) <= OBSERVED_SIGMA, axis=1))
        ),
        "fraction_within_2sigma_box": float(
            np.mean(np.all(np.abs(samples - OBSERVED_DELAYS) <= 2 * OBSERVED_SIGMA, axis=1))
        ),
    }


def write_csv(rows: list[dict[str, object]]) -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def aggregate(rows: list[dict[str, object]]) -> dict[str, object]:
    chi2 = np.array([float(row["mean_chi2_vs_observed"]) for row in rows])
    frac2 = np.array([float(row["fraction_within_2sigma_box"]) for row in rows])
    best = rows[int(np.argmin(chi2))]
    families: dict[str, dict[str, object]] = {}
    for family in sorted({str(row["model_family"]) for row in rows}):
        subset = [row for row in rows if row["model_family"] == family]
        f_chi2 = np.array([float(row["mean_chi2_vs_observed"]) for row in subset])
        f_frac2 = np.array([float(row["fraction_within_2sigma_box"]) for row in subset])
        families[family] = {
            "model_count": len(subset),
            "mean_chi2_min": float(np.min(f_chi2)),
            "mean_chi2_median": float(np.median(f_chi2)),
            "fraction_within_2sigma_box_max": float(np.max(f_frac2)),
            "best_model_id": subset[int(np.argmin(f_chi2))]["model_id"],
        }
    return {
        "model_count": len(rows),
        "sample_count_per_model_min": min(int(row["sample_count"]) for row in rows),
        "sample_count_per_model_max": max(int(row["sample_count"]) for row in rows),
        "best_model_id_by_mean_chi2": best["model_id"],
        "best_model_family_by_mean_chi2": best["model_family"],
        "best_mean_chi2_vs_observed": best["mean_chi2_vs_observed"],
        "best_fraction_within_2sigma_box": best["fraction_within_2sigma_box"],
        "median_mean_chi2_vs_observed": float(np.median(chi2)),
        "max_fraction_within_2sigma_box": float(np.max(frac2)),
        "families": families,
    }


def main() -> None:
    files = sorted(TD_DIR.glob("td_*_mod_out.txt"))
    if not files:
        raise SystemExit(f"no DES J0408 time-delay posterior files found in {TD_DIR}")
    rows = [summarize_file(path) for path in files]
    write_csv(rows)
    summary = {
        "schema": "paper7 DES J0408 no-T2 baseline smoke v1",
        "purpose": (
            "Verify that the public DES J0408 time-delay posterior files can be "
            "read and compared to declared observed delays without introducing T2."
        ),
        "source": {
            "source_id": "DESJ0408_time_delay_cosmography",
            "source_url": "https://github.com/ajshajib/DESJ0408_time_delay_cosmography",
            "local_time_delay_dir": str(TD_DIR.relative_to(ROOT)),
            "observed_delays_days": OBSERVED_DELAYS.tolist(),
            "observed_sigma_days": OBSERVED_SIGMA.tolist(),
        },
        "aggregate": aggregate(rows),
        "criteria": {
            "public_time_delay_posterior_files_read": True,
            "all_models_have_10000_samples": all(int(row["sample_count"]) == 10000 for row in rows),
            "two_delay_columns_confirmed": True,
            "no_t2_parameters_introduced": True,
            "full_lens_posterior_decoded": False,
            "model_weights_or_logZ_applied": False,
            "evidence_grade_no_t2_reproduction": False,
            "real_data_T2_sampling_authorized": False,
        },
        "verdict": {
            "desj0408_no_t2_time_delay_extraction_smoke_passed": True,
            "bounded_no_t2_baseline_reproduction_completed": False,
            "real_data_T2_sampling_authorized": False,
        },
        "claim_boundary": [
            "This is a time-delay posterior extraction smoke test, not a full lens-model reproduction.",
            "The full lens posterior pickle and model weights/logZ still require a compatibility extractor.",
            "No T2 term, T2 posterior, Bayes factor, or operator-necessity claim is introduced.",
        ],
        "next_finite_action": (
            "Implement a DES J0408 full-posterior compatibility reader or notebook "
            "runner that recovers model weights/logZ and image/model quantities."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["verdict"], indent=2))
    print(json.dumps(summary["aggregate"], indent=2))


if __name__ == "__main__":
    main()
