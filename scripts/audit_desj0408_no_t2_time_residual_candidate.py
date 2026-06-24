#!/usr/bin/env python3
"""Audit DES J0408 no-T2 time-delay residuals as a bounded T2-candidate pretest.

This script uses only the strict clean DES J0408 no-T2 feature rows.  It asks
whether a coherent residual direction remains between the public no-T2 model
time-delay distributions and the observed DES time delays.

It does not fit, sample, or claim a Tau/T2 signal.  The output is a residual
candidate pretest and a claim-boundary artifact.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results"
FEATURE_CSV = DERIVED / "desj0408_powerlaw_57_core_feature_table_v1.csv"
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_no_t2_time_residual_candidate_v1"
CSV_PATH = DERIVED / "desj0408_no_t2_time_residual_candidate_v1.csv"

OBSERVED_DELAYS = (-112.1, -155.5)
OBSERVED_SIGMA = (2.1, 12.8)


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def cosine(a: tuple[float, float], b: tuple[float, float]) -> float:
    dot = a[0] * b[0] + a[1] * b[1]
    norm_a = math.sqrt(a[0] ** 2 + a[1] ** 2)
    norm_b = math.sqrt(b[0] ** 2 + b[1] ** 2)
    if norm_a == 0 or norm_b == 0:
        return float("nan")
    return dot / (norm_a * norm_b)


def weighted_mean(values: list[float], weights: list[float]) -> float:
    total = sum(weights)
    if total <= 0:
        return float("nan")
    return sum(v * w for v, w in zip(values, weights)) / total


def residual_vector(row: dict[str, str]) -> tuple[float, float]:
    return (
        f(row, "published_dt1_mean_days") - OBSERVED_DELAYS[0],
        f(row, "published_dt2_mean_days") - OBSERVED_DELAYS[1],
    )


def residual_coherence(vectors: list[tuple[float, float]]) -> dict[str, object]:
    pair_cosines = [
        cosine(vectors[i], vectors[j])
        for i in range(len(vectors))
        for j in range(i + 1, len(vectors))
    ]
    same_sign_dt1 = len({math.copysign(1, v[0]) for v in vectors}) == 1 if vectors else False
    same_sign_dt2 = len({math.copysign(1, v[1]) for v in vectors}) == 1 if vectors else False
    coherent = bool(
        len(vectors) >= 2
        and same_sign_dt1
        and same_sign_dt2
        and pair_cosines
        and min(pair_cosines) > 0.98
    )
    return {
        "count": len(vectors),
        "same_sign_dt1_residual": same_sign_dt1,
        "same_sign_dt2_residual": same_sign_dt2,
        "min_pairwise_residual_cosine": min(pair_cosines) if pair_cosines else None,
        "coherent_residual_direction_present": coherent,
        "unweighted_model_minus_observed_dt1_days": (
            sum(v[0] for v in vectors) / len(vectors) if vectors else None
        ),
        "unweighted_model_minus_observed_dt2_days": (
            sum(v[1] for v in vectors) / len(vectors) if vectors else None
        ),
    }


def main() -> None:
    with FEATURE_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    clean = [
        row
        for row in rows
        if row["rowwise_feature_row_usable_for_no_t2_baseline"] == "True"
        and row["distributional_feature_row_usable_for_no_t2_baseline"] == "True"
    ]
    if len(clean) < 2:
        raise SystemExit("Need at least two strict clean no-T2 rows for residual coherence audit")
    nonclean_controls = [
        row
        for row in rows
        if not (
            row["rowwise_feature_row_usable_for_no_t2_baseline"] == "True"
            and row["distributional_feature_row_usable_for_no_t2_baseline"] == "True"
        )
    ]

    audit_rows: list[dict[str, object]] = []
    residual_vectors: list[tuple[float, float]] = []
    logz_weights: list[float] = []
    for row in clean:
        model_dt = (
            f(row, "published_dt1_mean_days"),
            f(row, "published_dt2_mean_days"),
        )
        model_std = (
            f(row, "published_dt1_std_days"),
            f(row, "published_dt2_std_days"),
        )
        model_minus_observed = (
            model_dt[0] - OBSERVED_DELAYS[0],
            model_dt[1] - OBSERVED_DELAYS[1],
        )
        observed_minus_model = (
            -model_minus_observed[0],
            -model_minus_observed[1],
        )
        combined_sigma = (
            math.sqrt(OBSERVED_SIGMA[0] ** 2 + model_std[0] ** 2),
            math.sqrt(OBSERVED_SIGMA[1] ** 2 + model_std[1] ** 2),
        )
        combined_pull = (
            model_minus_observed[0] / combined_sigma[0],
            model_minus_observed[1] / combined_sigma[1],
        )
        residual_vectors.append(model_minus_observed)
        logz_weights.append(f(row, "relative_core_logZ_weight"))
        audit_rows.append(
            {
                "model_id": row["model_id"],
                "model_dt1_mean_days": model_dt[0],
                "model_dt2_mean_days": model_dt[1],
                "observed_dt1_days": OBSERVED_DELAYS[0],
                "observed_dt2_days": OBSERVED_DELAYS[1],
                "model_minus_observed_dt1_days": model_minus_observed[0],
                "model_minus_observed_dt2_days": model_minus_observed[1],
                "observed_minus_model_dt1_days": observed_minus_model[0],
                "observed_minus_model_dt2_days": observed_minus_model[1],
                "combined_sigma_dt1_days": combined_sigma[0],
                "combined_sigma_dt2_days": combined_sigma[1],
                "combined_pull_dt1": combined_pull[0],
                "combined_pull_dt2": combined_pull[1],
                "published_mean_chi2_vs_observed": f(row, "published_mean_chi2_vs_observed"),
                "published_fraction_within_2sigma_box": f(row, "published_fraction_within_2sigma_box"),
                "relative_core_logZ_weight": f(row, "relative_core_logZ_weight"),
                "clean_no_t2_row": True,
            }
        )

    clean_coherence = residual_coherence(residual_vectors)
    coherent_direction = bool(clean_coherence["coherent_residual_direction_present"])
    nonclean_vectors = [residual_vector(row) for row in nonclean_controls]
    nonclean_coherence = residual_coherence(nonclean_vectors)
    all_feature_vectors = residual_vectors + nonclean_vectors
    all_feature_coherence = residual_coherence(all_feature_vectors)
    coherence_not_unique_to_clean_core = bool(
        nonclean_coherence["coherent_residual_direction_present"]
    )

    unweighted_common = (
        sum(v[0] for v in residual_vectors) / len(residual_vectors),
        sum(v[1] for v in residual_vectors) / len(residual_vectors),
    )
    logz_common = (
        weighted_mean([v[0] for v in residual_vectors], logz_weights),
        weighted_mean([v[1] for v in residual_vectors], logz_weights),
    )
    clean_model_ids = [row["model_id"] for row in audit_rows]

    summary = {
        "schema": "paper7 DES J0408 no-T2 time-residual candidate pretest v1",
        "purpose": (
            "Search the strict clean DES J0408 no-T2 baseline for a coherent "
            "time-delay residual direction that could motivate a later bounded "
            "T2 design, without fitting or sampling T2."
        ),
        "source": {
            "feature_csv": str(FEATURE_CSV.relative_to(ROOT)),
            "clean_model_ids": clean_model_ids,
            "observed_delays_days": list(OBSERVED_DELAYS),
            "observed_sigma_days": list(OBSERVED_SIGMA),
        },
        "aggregate": {
            "strict_clean_model_count": len(clean),
            "same_sign_dt1_residual": clean_coherence["same_sign_dt1_residual"],
            "same_sign_dt2_residual": clean_coherence["same_sign_dt2_residual"],
            "min_pairwise_residual_cosine": clean_coherence["min_pairwise_residual_cosine"],
            "coherent_no_t2_residual_direction_present": coherent_direction,
            "unweighted_model_minus_observed_dt1_days": unweighted_common[0],
            "unweighted_model_minus_observed_dt2_days": unweighted_common[1],
            "logz_weighted_model_minus_observed_dt1_days": logz_common[0],
            "logz_weighted_model_minus_observed_dt2_days": logz_common[1],
            "unweighted_observed_minus_model_dt1_days": -unweighted_common[0],
            "unweighted_observed_minus_model_dt2_days": -unweighted_common[1],
            "logz_weighted_observed_minus_model_dt1_days": -logz_common[0],
            "logz_weighted_observed_minus_model_dt2_days": -logz_common[1],
        },
        "negative_controls": {
            "nonclean_feature_rows": {
                "model_ids": [row["model_id"] for row in nonclean_controls],
                **nonclean_coherence,
            },
            "all_feature_rows": {
                "model_ids": [row["model_id"] for row in rows],
                **all_feature_coherence,
            },
            "coherence_not_unique_to_clean_core": coherence_not_unique_to_clean_core,
        },
        "criteria": {
            "uses_only_strict_clean_no_t2_models": True,
            "fits_or_samples_t2": False,
            "uses_failed_desj0408_models": False,
            "uses_endpoint_retuning": False,
            "coherent_residual_required_for_candidate": True,
            "negative_control_rows_checked": True,
            "coherence_alone_is_specific_enough_for_t2_claim": False,
            "independent_lens_system_confirmation_available": False,
            "physical_tau_time_law_available": False,
            "real_data_T2_sampling_authorized": False,
        },
        "verdict": {
            "desj0408_no_t2_time_residual_candidate_audit_created": True,
            "coherent_no_t2_time_residual_direction_observed": coherent_direction,
            "bounded_t2_design_motivated": coherent_direction,
            "coherent_residual_is_clean_core_unique": not coherence_not_unique_to_clean_core,
            "coherence_alone_supports_t2_claim": False,
            "tau_specific_time_shift_evidence": False,
            "real_data_T2_sampling_authorized": False,
        },
        "rows": audit_rows,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audit_rows[0]))
        writer.writeheader()
        writer.writerows(audit_rows)

    print(json.dumps(summary["verdict"], indent=2, sort_keys=True))
    print(json.dumps(summary["aggregate"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
