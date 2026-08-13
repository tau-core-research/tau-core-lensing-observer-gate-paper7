#!/usr/bin/env python3
"""Condition DES J0408 delay nuisance span on independent kinematic shape."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DES = ROOT / "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography"
TD = DES / "model_posteriors/time_delays"
VD = DES / "model_posteriors/velocity_dispersion"
OUT = ROOT / "data/derived/repro_results/tau_core_lensing_desj0408_crr_a_kinematic_conditioned_rank_v1"
OBS_DELAY_SIGMA = np.array([2.1, 12.8])
VEL = np.array([230.0, 236.0, 220.0, 227.0])
SIG_VEL = np.array([37.0, 42.0, 21.0, 9.0])
COMMON_SIGMA = 17.0


def mid_from_td(path: Path) -> str:
    return path.name.removeprefix("td_").removesuffix("_mod_out.txt")


def load_vd(mid: str) -> np.ndarray:
    paths = sorted(
        VD.glob(f"vd_*_{mid}_mod_out.txt"),
        key=lambda path: int(path.name.split("_", 2)[1]),
    )
    if len(paths) != 20:
        raise ValueError(f"{mid}: expected 20 velocity chunks, found {len(paths)}")
    return np.vstack([np.loadtxt(path) for path in paths])


def kinematic_profile_weights(model_vd: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    covariance = np.diag(SIG_VEL**2 + COMMON_SIGMA**2) + (
        -np.eye(4) + np.ones((4, 4))
    ) * COMMON_SIGMA**2
    precision = np.linalg.inv(covariance)
    numerator = np.einsum("ni,ij,j->n", model_vd, precision, VEL)
    denominator = np.einsum("ni,ij,nj->n", model_vd, precision, model_vd)
    scale = np.maximum(numerator / denominator, 0.0)
    residual = scale[:, None] * model_vd - VEL[None, :]
    chi2 = np.einsum("ni,ij,nj->n", residual, precision, residual)
    logw = -0.5 * chi2
    weights = np.exp(logw - np.max(logw))
    weights /= np.sum(weights)
    return weights, chi2, scale


def span(matrix: np.ndarray) -> dict[str, object]:
    centered = matrix - np.mean(matrix, axis=0)
    _, singular, _ = np.linalg.svd(centered, full_matrices=False)
    ratio = singular / singular[0]
    return {
        "singular_values": singular.tolist(),
        "relative_singular_values": ratio.tolist(),
        "exact_rank": int(np.sum(singular > singular[0] * 1e-8)),
        "rank_at_1pct": int(np.sum(ratio > 0.01)),
        "rank_at_5pct": int(np.sum(ratio > 0.05)),
        "rank_at_10pct": int(np.sum(ratio > 0.10)),
    }


def main() -> None:
    rows = []
    raw_means = []
    conditioned_means = []
    for path in sorted(TD.glob("td_*_mod_out.txt")):
        mid = mid_from_td(path)
        delays = np.loadtxt(path)
        model_vd = load_vd(mid)
        if len(delays) != len(model_vd):
            raise ValueError(f"{mid}: delay/velocity row mismatch")
        weights, chi2, scale = kinematic_profile_weights(model_vd)
        raw_mean = np.mean(delays, axis=0)
        conditioned = np.sum(weights[:, None] * delays, axis=0)
        ess = 1.0 / np.sum(weights**2)
        raw_means.append(raw_mean)
        conditioned_means.append(conditioned)
        rows.append({
            "model_id": mid,
            "sample_count": len(delays),
            "effective_sample_size": float(ess),
            "median_profiled_kinematic_chi2": float(np.median(chi2)),
            "median_profiled_velocity_scale": float(np.median(scale)),
            "raw_delay_mean_days": raw_mean.tolist(),
            "kinematic_conditioned_delay_mean_days": conditioned.tolist(),
            "mean_shift_days": (conditioned - raw_mean).tolist(),
        })

    raw = np.asarray(raw_means)
    conditioned = np.asarray(conditioned_means)
    raw_white = span(raw / OBS_DELAY_SIGMA)
    conditioned_white = span(conditioned / OBS_DELAY_SIGMA)

    payload = {
        "schema": "paper7 DES J0408 CRR-A kinematic-conditioned rank audit v1",
        "freeze_policy": {
            "uses_observed_delay_values_for_conditioning": False,
            "uses_independent_stellar_kinematics": True,
            "profiles_one_positive_velocity_scale_per_sample": True,
            "uses_velocity_shape_after_scale_profile": True,
            "external_convergence_role": "common_delay_scale_nuisance_not_expected_to_reduce_two-delay_shape_rank",
            "fits_or_classifies_time_quantum_other_channel_origin": False,
        },
        "source_counts": {
            "models": len(rows),
            "delay_samples": int(sum(row["sample_count"] for row in rows)),
            "velocity_dispersion_files": len(list(VD.glob("*.txt"))),
            "velocity_apertures": 4,
        },
        "raw_covariance_whitened_span": raw_white,
        "kinematic_conditioned_covariance_whitened_span": conditioned_white,
        "effective_sample_size": {
            "minimum": min(row["effective_sample_size"] for row in rows),
            "median": float(np.median([row["effective_sample_size"] for row in rows])),
            "maximum": max(row["effective_sample_size"] for row in rows),
        },
        "rows": rows,
        "rank_repair": {
            "exact_rank_before": raw_white["exact_rank"],
            "exact_rank_after": conditioned_white["exact_rank"],
            "rank_at_5pct_before": raw_white["rank_at_5pct"],
            "rank_at_5pct_after": conditioned_white["rank_at_5pct"],
            "exact_delay_nuisance_rank_reduced": conditioned_white["exact_rank"] < raw_white["exact_rank"],
            "practical_5pct_rank_reduced": conditioned_white["rank_at_5pct"] < raw_white["rank_at_5pct"],
        },
        "verdict": "UNSET",
        "claim_boundary": "This conditions the standard delay nuisance family on independent kinematic shape. It neither detects a generic channel effect nor attributes one to time, quantum, or another origin.",
    }
    if payload["rank_repair"]["exact_delay_nuisance_rank_reduced"]:
        payload["verdict"] = "CRR_A_EXACT_NUISANCE_RANK_REPAIR_CANDIDATE"
    elif payload["rank_repair"]["practical_5pct_rank_reduced"]:
        payload["verdict"] = "CRR_A_PRACTICAL_NUISANCE_RANK_REPAIR_CANDIDATE"
    else:
        payload["verdict"] = "CRR_A_KINEMATIC_CONDITIONING_DOES_NOT_REPAIR_DELAY_RANK"

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    report = [
        "# DES J0408 CRR-A Kinematic-Conditioned Rank Audit v1",
        "",
        f"**Verdict:** `{payload['verdict']}`",
        "",
        "| measure | before | after |",
        "| --- | ---: | ---: |",
        f"| exact whitened rank | {raw_white['exact_rank']} | {conditioned_white['exact_rank']} |",
        f"| 5% whitened rank | {raw_white['rank_at_5pct']} | {conditioned_white['rank_at_5pct']} |",
        f"| s2/s1 | {raw_white['relative_singular_values'][1]:.6f} | {conditioned_white['relative_singular_values'][1]:.6f} |",
        "",
        payload["claim_boundary"],
    ]
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(payload["verdict"])


if __name__ == "__main__":
    main()
