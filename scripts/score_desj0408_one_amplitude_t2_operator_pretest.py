#!/usr/bin/env python3
"""Score a bounded one-amplitude DES J0408 T2 operator against controls.

This is a closed-form pretest on already frozen no-T2 residuals. It does not
sample a posterior, tune an endpoint, or claim a Tau-specific time signal.
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
DESIGN_SUMMARY = (
    RESULTS / "tau_core_lensing_desj0408_t2_null_comparison_design_freeze_v1" / "summary.json"
)
OUT_DIR = RESULTS / "tau_core_lensing_desj0408_one_amplitude_t2_operator_pretest_v1"
CSV_PATH = DERIVED / "desj0408_one_amplitude_t2_operator_pretest_v1.csv"


def dot(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1]


def norm(a: tuple[float, float]) -> float:
    return math.sqrt(dot(a, a))


def normalize(a: tuple[float, float]) -> tuple[float, float]:
    n = norm(a)
    if n == 0:
        raise ValueError("zero vector cannot be normalized")
    return (a[0] / n, a[1] / n)


def rmse(vectors: list[tuple[float, float]]) -> float:
    return math.sqrt(sum(dot(v, v) for v in vectors) / len(vectors))


def best_nonnegative_alpha(
    residuals: list[tuple[float, float]], direction: tuple[float, float]
) -> float:
    # Minimize mean ||r + alpha u||^2 with alpha constrained to alpha >= 0.
    unconstrained = -sum(dot(r, direction) for r in residuals) / len(residuals)
    return max(0.0, unconstrained)


def apply_correction(
    residuals: list[tuple[float, float]], direction: tuple[float, float], alpha: float
) -> list[tuple[float, float]]:
    return [(r[0] + alpha * direction[0], r[1] + alpha * direction[1]) for r in residuals]


def score_row(
    row_id: str,
    role: str,
    residuals: list[tuple[float, float]],
    direction: tuple[float, float],
    alpha_source: str = "closed_form_nonnegative",
    fixed_alpha: float | None = None,
) -> dict[str, object]:
    alpha = fixed_alpha if fixed_alpha is not None else best_nonnegative_alpha(residuals, direction)
    before = rmse(residuals)
    corrected = apply_correction(residuals, direction, alpha)
    after = rmse(corrected)
    reduction = before - after
    return {
        "row_id": row_id,
        "role": role,
        "sample_count": len(residuals),
        "direction_dt1": direction[0],
        "direction_dt2": direction[1],
        "alpha_days": alpha,
        "alpha_source": alpha_source,
        "rmse_before_days": before,
        "rmse_after_days": after,
        "rmse_reduction_days": reduction,
        "fractional_rmse_reduction": reduction / before if before else 0.0,
    }


def main() -> None:
    design = json.loads(DESIGN_SUMMARY.read_text(encoding="utf-8"))
    frozen_direction = tuple(
        float(x) for x in design["frozen_design_vector"]["unweighted_unit_direction"]
    )
    frozen_direction = normalize(frozen_direction)
    orthogonal_direction = normalize((-frozen_direction[1], frozen_direction[0]))
    swapped_direction = normalize((frozen_direction[1], frozen_direction[0]))
    opposite_direction = (-frozen_direction[0], -frozen_direction[1])

    with FEATURE_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    clean_rows = [
        row
        for row in rows
        if row["rowwise_feature_row_usable_for_no_t2_baseline"] == "True"
        and row["distributional_feature_row_usable_for_no_t2_baseline"] == "True"
    ]
    nonclean_rows = [row for row in rows if row not in clean_rows]

    def residual(row: dict[str, str]) -> tuple[float, float]:
        return (
            float(row["published_dt1_residual_days"]),
            float(row["published_dt2_residual_days"]),
        )

    clean_residuals = [residual(row) for row in clean_rows]
    nonclean_residuals = [residual(row) for row in nonclean_rows]
    all_residuals = [residual(row) for row in rows]

    frozen_clean = score_row(
        "T2_FROZEN_DIRECTION_CLEAN_CORE",
        "candidate_operator",
        clean_residuals,
        frozen_direction,
    )
    frozen_alpha = float(frozen_clean["alpha_days"])
    score_rows = [
        frozen_clean,
        score_row(
            "SCRAMBLE_ORTHOGONAL_CLEAN_CORE",
            "scramble_control",
            clean_residuals,
            orthogonal_direction,
        ),
        score_row(
            "SCRAMBLE_SWAPPED_COMPONENTS_CLEAN_CORE",
            "scramble_control",
            clean_residuals,
            swapped_direction,
        ),
        score_row(
            "OPPOSITE_DIRECTION_CLEAN_CORE",
            "sign_control",
            clean_residuals,
            opposite_direction,
        ),
        score_row(
            "T2_FROZEN_DIRECTION_NONCLEAN_CONTROL",
            "negative_control",
            nonclean_residuals,
            frozen_direction,
            alpha_source="clean_core_alpha_reused",
            fixed_alpha=frozen_alpha,
        ),
        score_row(
            "T2_FROZEN_DIRECTION_ALL_FEATURE_ROWS_CONTROL",
            "sensitivity_control",
            all_residuals,
            frozen_direction,
            alpha_source="clean_core_alpha_reused",
            fixed_alpha=frozen_alpha,
        ),
    ]

    candidate_reduction = float(frozen_clean["rmse_reduction_days"])
    scramble_reductions = [
        float(row["rmse_reduction_days"])
        for row in score_rows
        if row["role"] in {"scramble_control", "sign_control"}
    ]
    nonclean_reduction = float(score_rows[4]["rmse_reduction_days"])
    frozen_beats_scrambles = candidate_reduction > max(scramble_reductions)
    nonclean_also_improves = nonclean_reduction > 0

    summary = {
        "schema": "paper7 DES J0408 one-amplitude T2 operator pretest v1",
        "purpose": (
            "Define and score the minimal one-amplitude correction along the "
            "pre-frozen DES J0408 residual direction, with scramble and non-clean "
            "controls. This is not a posterior fit or physical detection."
        ),
        "source": {
            "feature_csv": str(FEATURE_CSV.relative_to(ROOT)),
            "design_summary": str(DESIGN_SUMMARY.relative_to(ROOT)),
            "clean_model_ids": [row["model_id"] for row in clean_rows],
            "nonclean_control_model_ids": [row["model_id"] for row in nonclean_rows],
        },
        "operator": {
            "name": "T2_one_amplitude_frozen_direction_pretest",
            "formula": "Delta_t_corrected = Delta_t_noT2 + alpha * u_frozen",
            "alpha_policy": "closed_form_nonnegative_least_squares_on_clean_core",
            "u_frozen_basis": ["dt1_days", "dt2_days"],
            "u_frozen": list(frozen_direction),
            "alpha_days": frozen_alpha,
            "endpoint_blind": False,
            "tau_derived": False,
        },
        "aggregate": {
            "candidate_rmse_before_days": frozen_clean["rmse_before_days"],
            "candidate_rmse_after_days": frozen_clean["rmse_after_days"],
            "candidate_rmse_reduction_days": candidate_reduction,
            "candidate_fractional_rmse_reduction": frozen_clean[
                "fractional_rmse_reduction"
            ],
            "max_scramble_rmse_reduction_days": max(scramble_reductions),
            "frozen_direction_beats_scramble_controls": frozen_beats_scrambles,
            "nonclean_control_rmse_reduction_days": nonclean_reduction,
            "nonclean_control_also_improves": nonclean_also_improves,
        },
        "criteria": {
            "uses_pre_frozen_design_vector": True,
            "fits_or_samples_t2_posterior": False,
            "uses_closed_form_single_amplitude_score": True,
            "uses_failed_rows_for_candidate_fit": False,
            "scramble_controls_checked": True,
            "nonclean_rows_checked_as_controls": True,
            "endpoint_blind": False,
            "tau_derived_operator": False,
            "real_data_T2_sampling_authorized": False,
        },
        "verdict": {
            "desj0408_one_amplitude_t2_operator_pretest_created": True,
            "minimal_one_amplitude_operator_defined": True,
            "frozen_direction_reduces_clean_residual": candidate_reduction > 0,
            "frozen_direction_beats_scramble_controls": frozen_beats_scrambles,
            "nonclean_control_also_improves": nonclean_also_improves,
            "directional_score_supports_design_followup": frozen_beats_scrambles,
            "t2_specific_time_shift_evidence": False,
            "bounded_t2_fit_ready": False,
            "real_data_T2_sampling_authorized": False,
        },
        "rows": score_rows,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(score_rows[0]))
        writer.writeheader()
        writer.writerows(score_rows)

    print(json.dumps(summary["verdict"], indent=2, sort_keys=True))
    print(json.dumps(summary["aggregate"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
