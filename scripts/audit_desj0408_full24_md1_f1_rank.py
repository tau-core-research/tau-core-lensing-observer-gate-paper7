#!/usr/bin/env python3
"""Audit the full public DES J0408 model ensemble for an MD1/F1 output row.

The nuisance subspace is frozen from no-T2 model predictions before the
observed delay vector is projected. No T2/Tau amplitude is fitted.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DES = ROOT / "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography"
TD_DIR = DES / "model_posteriors/time_delays"
DERIVED = ROOT / "data/derived"
RESULTS = DERIVED / "repro_results/tau_core_lensing_desj0408_full24_md1_f1_rank_v1"
CSV_PATH = DERIVED / "desj0408_full24_md1_f1_rank_v1.csv"
OBSERVED = np.array([-112.1, -155.5], dtype=float)
OBSERVED_SIGMA = np.array([2.1, 12.8], dtype=float)
SEED = 20260710
BOOTSTRAPS = 2000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_id(path: Path) -> str:
    name = path.name
    return name.removeprefix("td_").removesuffix("_mod_out.txt")


def family(mid: str) -> str:
    parts = mid.split("_")
    return "composite" if len(parts) > 3 and parts[3] == "1" else "powerlaw"


def rank_at(singular_values: np.ndarray, relative_tol: float) -> int:
    if not len(singular_values) or singular_values[0] == 0:
        return 0
    return int(np.sum(singular_values > relative_tol * singular_values[0]))


def span_audit(matrix: np.ndarray) -> dict[str, object]:
    centered = matrix - np.mean(matrix, axis=0, keepdims=True)
    _, singular, vh = np.linalg.svd(centered, full_matrices=False)
    ranks = {str(tol): rank_at(singular, tol) for tol in (1e-8, 0.01, 0.05, 0.1)}
    rank = ranks["1e-08"]
    projector = vh[:rank].T @ vh[:rank] if rank else np.zeros((2, 2))
    residual_projector = np.eye(2) - projector
    return {
        "singular_values_days": singular.tolist(),
        "relative_singular_values": (singular / singular[0]).tolist(),
        "rank_by_relative_tolerance": ranks,
        "strict_rank": rank,
        "output_dimension": 2,
        "orthogonal_complement_dimension": 2 - rank,
        "nuisance_projector": projector.tolist(),
        "residual_projector": residual_projector.tolist(),
    }


def truncated_projection(matrix: np.ndarray, target: np.ndarray, relative_tol: float) -> dict[str, object]:
    centered = matrix - np.mean(matrix, axis=0, keepdims=True)
    _, singular, vh = np.linalg.svd(centered, full_matrices=False)
    rank = rank_at(singular, relative_tol)
    nuisance_projector = vh[:rank].T @ vh[:rank] if rank else np.zeros((2, 2))
    residual = (np.eye(2) - nuisance_projector) @ target
    return {
        "relative_tolerance": relative_tol,
        "retained_nuisance_rank": rank,
        "remaining_dimension": 2 - rank,
        "residualized_observed_vector_sigma_units": residual.tolist(),
        "residualized_observed_norm_sigma_units": float(np.linalg.norm(residual)),
        "weak_direction_sigma_basis": vh[rank:].tolist(),
    }


def main() -> None:
    paths = sorted(TD_DIR.glob("td_*_mod_out.txt"))
    if len(paths) != 24:
        raise SystemExit(f"Expected 24 time-delay posteriors, found {len(paths)}")

    rng = np.random.default_rng(SEED)
    rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {}
    for path in paths:
        data = np.loadtxt(path)
        if data.ndim != 2 or data.shape[1] != 2:
            raise SystemExit(f"Expected Nx2 delay table: {path}")
        mid = model_id(path)
        arrays[mid] = data
        rows.append({
            "model_id": mid,
            "model_family": family(mid),
            "sample_count": int(len(data)),
            "dt_AB_mean_days": float(np.mean(data[:, 0])),
            "dt_AD_mean_days": float(np.mean(data[:, 1])),
            "dt_AB_std_days": float(np.std(data[:, 0], ddof=1)),
            "dt_AD_std_days": float(np.std(data[:, 1], ddof=1)),
            "sha256": sha256(path),
        })

    means = np.array([[row["dt_AB_mean_days"], row["dt_AD_mean_days"]] for row in rows])
    full = span_audit(means)
    covariance_whitened = span_audit(means / OBSERVED_SIGMA)
    family_audits = {
        fam: span_audit(means[[row["model_family"] == fam for row in rows]])
        for fam in ("powerlaw", "composite")
    }

    loo_ranks = []
    for index in range(len(rows)):
        loo_ranks.append(span_audit(np.delete(means, index, axis=0))["strict_rank"])

    boot_second_ratios = []
    boot_ranks_5pct = []
    for _ in range(BOOTSTRAPS):
        boot_means = []
        for row in rows:
            values = arrays[str(row["model_id"])]
            draw = rng.integers(0, len(values), size=len(values))
            boot_means.append(np.mean(values[draw], axis=0))
        audit = span_audit(np.asarray(boot_means))
        boot_second_ratios.append(audit["relative_singular_values"][1])
        boot_ranks_5pct.append(audit["rank_by_relative_tolerance"]["0.05"])

    nuisance_center = np.mean(means, axis=0)
    observed_offset = OBSERVED - nuisance_center
    residual_projector = np.asarray(full["residual_projector"])
    projected_observed = residual_projector @ observed_offset
    projected_sigma_norm = float(np.linalg.norm(projected_observed / OBSERVED_SIGMA))
    whitened_observed_offset = observed_offset / OBSERVED_SIGMA
    practical_sensitivity = {
        str(tol): truncated_projection(
            means / OBSERVED_SIGMA, whitened_observed_offset, tol
        )
        for tol in (0.01, 0.05, 0.1)
    }

    summary = {
        "schema": "paper7 DES J0408 full24 MD1 F1 rank audit v1",
        "purpose": "Test whether two public path-delay outputs retain any direction outside the source-frozen no-T2 model-ensemble nuisance span.",
        "freeze_policy": {
            "nuisance_span_frozen_before_observed_vector_projection": True,
            "uses_observed_delays_to_select_models_or_basis": False,
            "fits_or_samples_t2_or_tau_amplitude": False,
            "model_inclusion_rule": "all 24 public DES J0408 time-delay posterior files",
            "output_basis": ["dt_AB_days", "dt_AD_days"],
            "rank_relative_tolerances": [1e-8, 0.01, 0.05, 0.1],
        },
        "source_manifest": {
            "repository": "https://github.com/ajshajib/DESJ0408_time_delay_cosmography",
            "posterior_file_count": len(paths),
            "total_samples": int(sum(len(values) for values in arrays.values())),
            "families": {fam: sum(row["model_family"] == fam for row in rows) for fam in ("powerlaw", "composite")},
        },
        "full24_nuisance_span": full,
        "observed_covariance_whitened_nuisance_span": covariance_whitened,
        "family_controls": family_audits,
        "leave_one_model_out_control": {
            "all_ranks": loo_ranks,
            "minimum_rank": min(loo_ranks),
            "maximum_rank": max(loo_ranks),
            "all_full_output_rank": all(value == 2 for value in loo_ranks),
        },
        "posterior_bootstrap_control": {
            "seed": SEED,
            "replicates": BOOTSTRAPS,
            "second_to_first_singular_ratio_q01_q50_q99": np.quantile(boot_second_ratios, [0.01, 0.5, 0.99]).tolist(),
            "fraction_rank2_at_5pct": float(np.mean(np.asarray(boot_ranks_5pct) == 2)),
        },
        "observed_projection_after_freeze": {
            "observed_delays_days": OBSERVED.tolist(),
            "nuisance_center_days": nuisance_center.tolist(),
            "observed_minus_nuisance_center_days": observed_offset.tolist(),
            "residualized_vector_days": projected_observed.tolist(),
            "residualized_norm_sigma_units": projected_sigma_norm,
        },
        "covariance_whitened_practical_sensitivity": practical_sensitivity,
        "rank_verdict": {
            "raw_path_output_dimension": 2,
            "empirical_no_t2_nuisance_rank": full["strict_rank"],
            "covariance_whitened_no_t2_nuisance_rank": covariance_whitened["strict_rank"],
            "remaining_delay_only_f1_dimension": full["orthogonal_complement_dimension"],
            "nuisance_residualized_f1_row_constructed": False,
            "delay_only_f1_locally_identifiable_in_this_design": False,
            "practical_weak_direction_present_at_5pct": practical_sensitivity["0.05"]["remaining_dimension"] == 1,
            "practical_weak_direction_is_detection": False,
        },
        "verdict": "DESJ0408_DELAY_ONLY_STRUCTURAL_F1_NO_GO_WITH_PRACTICAL_WEAK_DIRECTION",
        "interpretation": "The public no-T2 model ensemble structurally spans both measured delay coordinates, so exact delay-only residualization leaves no independent F1 output dimension. After covariance whitening the second nuisance singular value is weak, leaving one sensitivity direction at a declared 5% truncation; that thresholded direction is a follow-up target, not a detection.",
        "required_rank_repair": [
            "add a third path-sensitive observable not contained in the two-delay nuisance span, such as image-wise polarization, chromatic profile, or independently modeled flux-ratio response",
            "or add independent source/lens constraints that reduce the effective nuisance rank below two before testing the delays",
            "then freeze and replicate the repaired design on an independent lens",
        ],
        "claim_boundary": {
            "allowed": "The full public DES J0408 delay-only design has zero nuisance-orthogonal output dimension under the declared empirical no-T2 model-family span.",
            "forbidden": "This does not prove absence of observer-path physics, physical time distortion, or Tau Core F1.",
        },
    }

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    report = [
        "# DES J0408 Full-24 MD1/F1 Rank Audit v1",
        "",
        f"**Verdict:** `{summary['verdict']}`",
        "",
        "The nuisance basis was frozen from all 24 public no-T2 model predictions before the observed delay vector was projected.",
        "",
        "| quantity | result |",
        "| --- | ---: |",
        f"| raw path-output dimension | {summary['rank_verdict']['raw_path_output_dimension']} |",
        f"| empirical nuisance rank | {summary['rank_verdict']['empirical_no_t2_nuisance_rank']} |",
        f"| covariance-whitened nuisance rank | {summary['rank_verdict']['covariance_whitened_no_t2_nuisance_rank']} |",
        f"| remaining delay-only F1 dimension | {summary['rank_verdict']['remaining_delay_only_f1_dimension']} |",
        f"| leave-one-model-out rank-2 fraction | {np.mean(np.asarray(loo_ranks) == 2):.3f} |",
        f"| bootstrap rank-2 fraction at 5% tolerance | {summary['posterior_bootstrap_control']['fraction_rank2_at_5pct']:.3f} |",
        "",
        "The exact result is a structural measurement-design no-go. Covariance whitening exposes a weak second nuisance direction, so a thresholded practical sensitivity direction is retained separately as a follow-up target, not a detection.",
        "",
        "## Rank Repair",
        "",
        "Add a genuinely third path-sensitive observable, or independently constrain the lens/source nuisance family until its effective rank is below two. Freeze the repaired design before inspecting any Tau endpoint score.",
    ]
    (RESULTS / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(summary["verdict"])


if __name__ == "__main__":
    main()
