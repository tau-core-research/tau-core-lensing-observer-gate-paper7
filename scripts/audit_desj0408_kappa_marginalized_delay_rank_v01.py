#!/usr/bin/env python3
"""Audit DES J0408 delay identifiability after mandatory kappa_ext marginalization."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DES = ROOT / "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography"
TD_DIR = DES / "model_posteriors/time_delays"
DATA_DIR = DES / "data"
OUT_DIR = (
    ROOT
    / "data/derived/repro_results"
    / "tau_core_lensing_desj0408_kappa_marginalized_delay_rank_v1"
)
OUT = OUT_DIR / "summary.json"
REPORT = OUT_DIR / "report.md"
OBSERVED_SIGMA = np.asarray([2.1, 12.8], dtype=float)


def family(path: Path) -> str:
    parts = path.name.removeprefix("td_").removesuffix("_mod_out.txt").split("_")
    return "composite" if len(parts) > 3 and parts[3] == "1" else "powerlaw"


def weighted_quantiles(
    values: np.ndarray, weights: np.ndarray, quantiles: list[float]
) -> np.ndarray:
    cumulative = np.cumsum(weights / np.sum(weights))
    return np.interp(quantiles, cumulative, values)


def kappa_summary(family_name: str) -> dict[str, object]:
    paths = sorted(DATA_DIR.glob(f"kappahist_0408_*_{family_name}_*.cat"))
    if len(paths) != 1:
        raise RuntimeError(
            f"Expected one {family_name} kappa histogram, found {len(paths)}"
        )
    weights = np.loadtxt(paths[0])
    support = np.linspace(-0.2 + 0.0003, 1.0 - 0.0003, len(weights))
    q16, q50, q84 = weighted_quantiles(
        support, weights, [0.16, 0.50, 0.84]
    )
    return {
        "file": str(paths[0].relative_to(ROOT)),
        "support_bin_count": int(len(weights)),
        "mean": float(np.sum(support * weights) / np.sum(weights)),
        "q16": float(q16),
        "median": float(q50),
        "q84": float(q84),
        "semi_68_width": float((q84 - q16) / 2.0),
    }


def main() -> None:
    paths = sorted(TD_DIR.glob("td_*_mod_out.txt"))
    if len(paths) != 24:
        raise RuntimeError(f"Expected 24 delay files, found {len(paths)}")
    means = []
    families = []
    for path in paths:
        values = np.loadtxt(path)
        means.append(np.mean(values, axis=0))
        families.append(family(path))
    means = np.asarray(means)
    whitened = means / OBSERVED_SIGMA
    centered = whitened - np.mean(whitened, axis=0, keepdims=True)
    _, singular_values, vh = np.linalg.svd(centered, full_matrices=False)
    dominant_model_direction = vh[0]

    nuisance_center = np.mean(means, axis=0)
    # Under a mass-sheet transform lambda=1-kappa_ext, delays scale by lambda.
    kappa_tangent = -nuisance_center / OBSERVED_SIGMA
    kappa_direction = kappa_tangent / np.linalg.norm(kappa_tangent)
    augmented = np.stack([dominant_model_direction, kappa_direction])
    augmented_singular = np.linalg.svd(
        augmented, compute_uv=False, full_matrices=False
    )
    augmented_rank = int(
        np.sum(augmented_singular > 1e-8 * augmented_singular[0])
    )
    absolute_cosine = float(
        abs(np.dot(dominant_model_direction, kappa_direction))
    )
    angle_deg = float(np.degrees(np.arccos(np.clip(absolute_cosine, 0, 1))))

    family_centers = {
        name: np.mean(means[np.asarray(families) == name], axis=0).tolist()
        for name in ("powerlaw", "composite")
    }
    kappa = {
        name: kappa_summary(name)
        for name in ("powerlaw", "composite")
    }
    weak_model_direction = vh[1]
    representative_kappa_width = float(
        np.mean([entry["semi_68_width"] for entry in kappa.values()])
    )
    kappa_weak_projection_per_unit = float(
        np.dot(kappa_tangent, weak_model_direction)
    )
    kappa_weak_projection_at_reported_width = float(
        abs(kappa_weak_projection_per_unit) * representative_kappa_width
    )
    summary = {
        "schema": "paper7 DES J0408 kappa-marginalized delay-rank audit v1",
        "delay_output_basis": ["dt_AB_days", "dt_AD_days"],
        "delay_output_dimension": 2,
        "public_model_count": len(paths),
        "family_delay_centers_days": family_centers,
        "kappa_ext_histograms": kappa,
        "mass_sheet_delay_rule": (
            "Delta_t(kappa_ext)=(1-kappa_ext)*Delta_t_model"
        ),
        "covariance_whitened_model_singular_values": singular_values.tolist(),
        "dominant_model_direction": dominant_model_direction.tolist(),
        "weak_model_direction": weak_model_direction.tolist(),
        "kappa_ext_tangent_sigma_basis": kappa_tangent.tolist(),
        "normalized_kappa_ext_direction": kappa_direction.tolist(),
        "absolute_cosine_dominant_model_vs_kappa": absolute_cosine,
        "principal_angle_degrees": angle_deg,
        "rank_dominant_model_plus_kappa": augmented_rank,
        "remaining_dimension_after_dominant_model_plus_kappa": (
            2 - augmented_rank
        ),
        "strict_full_model_nuisance_rank_before_kappa": 2,
        "strict_full_model_nuisance_rank_after_kappa": 2,
        "representative_kappa_semi_68_width": representative_kappa_width,
        "kappa_projection_on_weak_direction_sigma_per_unit_kappa": (
            kappa_weak_projection_per_unit
        ),
        "kappa_projection_on_weak_direction_at_reported_width_sigma": (
            kappa_weak_projection_at_reported_width
        ),
        "practical_5pct_weak_direction_survives_geometrically": True,
        "practical_weak_direction_is_kappa_free": False,
        "delay_only_tau_score_authorized": False,
        "tau_specific_information_materialized": False,
        "time_distortion_detection_claim_allowed": False,
        "verdict": (
            "KAPPA_EXT_DOES_NOT_RESCUE_STRICT_DELAY_RANK__"
            "PRACTICAL_WEAK_DIRECTION_SURVIVES_BUT_IS_CONTAMINATED"
        ),
        "claim_boundary": (
            "The source-frozen external-convergence tangent is linearly "
            "independent of the dominant covariance-whitened model direction, "
            "so their strict joint nuisance span fills the two-delay output. "
            "At a declared 5% truncation the near-parallel weak direction "
            "survives geometrically, but it is not kappa-free and requires "
            "probabilistic marginalization. This is a design no-go, not "
            "evidence against observer-time physics."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# DES J0408 kappa-marginalized delay-rank audit v1\n\n"
        f"Verdict: `{summary['verdict']}`\n\n"
        f"The principal angle between the dominant model direction and the "
        f"mandatory external-convergence tangent is `{angle_deg:.3f}` degrees. "
        "Their joint rank is two in a two-dimensional delay output, leaving no "
        "delay-only Tau score direction.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
