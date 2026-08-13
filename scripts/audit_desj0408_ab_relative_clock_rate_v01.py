#!/usr/bin/env python3
"""Exploratory A/B relative clock-rate audit for DES J0408-5354."""

from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from pathlib import Path

import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.optimize import differential_evolution, minimize_scalar


ROOT = Path(__file__).resolve().parents[1]
URL = (
    "https://www.epfl.ch/labs/lastro/wp-content/uploads/2019/08/"
    "DESJ0408_Courbin2017.rdb_-1.txt"
)
EXPECTED_SHA256 = (
    "18ab7cef9bb014c4fc9a7613c24fd1bb7ead9ae7cd24fecd05b97ba8d06a051d"
)
RAW = ROOT / "data/external/cosmograil/DESJ0408_Courbin2017.rdb.txt"
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_desj0408_ab_relative_clock_rate_v1"
)


def acquire() -> None:
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if not RAW.exists():
        urllib.request.urlretrieve(URL, RAW)
    digest = hashlib.sha256(RAW.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError(f"Unexpected COSMOGRAIL payload SHA-256: {digest}")


def load_wfi() -> dict[str, np.ndarray]:
    rows = []
    with RAW.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        next(reader)  # RDB type separator.
        for row in reader:
            if row["telescope"] == "WFI":
                rows.append(row)
    return {
        key: np.asarray([float(row[key]) for row in rows])
        for key in ("mhjd", "mag_A", "magerr_A", "mag_B", "magerr_B")
    }


def fit_spec(
    data: dict[str, np.ndarray], smoothing_factor: float, trend_degree: int
) -> dict:
    t = data["mhjd"]
    pivot = float(np.mean(t))
    spline = UnivariateSpline(
        t,
        data["mag_A"],
        w=1.0 / data["magerr_A"],
        s=smoothing_factor * len(t),
    )

    def objective(values: tuple[float, float] | np.ndarray) -> float:
        delay, stretch = values
        source_t = pivot + (t - delay - pivot) / stretch
        mask = (source_t >= np.min(t)) & (source_t <= np.max(t))
        if np.count_nonzero(mask) < 20:
            return 1e9
        x = (t[mask] - pivot) / 100.0
        design = np.stack(
            [x**power for power in range(trend_degree + 1)], axis=1
        )
        residual_target = data["mag_B"][mask] - spline(source_t[mask])
        variance = data["magerr_B"][mask] ** 2 + 0.005**2
        whiten = 1.0 / np.sqrt(variance)
        beta = np.linalg.lstsq(
            design * whiten[:, None],
            residual_target * whiten,
            rcond=None,
        )[0]
        residual = residual_target - design @ beta
        return float(np.sum(residual**2 / variance))

    shift = minimize_scalar(
        lambda delay: objective((delay, 1.0)),
        bounds=(100.0, 122.0),
        method="bounded",
    )
    stretch = differential_evolution(
        objective,
        bounds=[(100.0, 122.0), (0.9, 1.1)],
        seed=20380408 + 10 * trend_degree + int(2 * smoothing_factor),
        popsize=10,
        tol=1e-8,
        polish=True,
    )
    return {
        "smoothing_factor_times_n": smoothing_factor,
        "microlensing_polynomial_degree": trend_degree,
        "shift_only_delay_days": float(shift.x),
        "shift_only_chi_square": float(shift.fun),
        "shift_stretch_delay_days": float(stretch.x[0]),
        "relative_clock_rate_B_over_A": float(stretch.x[1]),
        "shift_stretch_chi_square": float(stretch.fun),
        "delta_chi_square_one_extra_parameter": float(
            shift.fun - stretch.fun
        ),
        "stretch_at_search_boundary": bool(
            abs(stretch.x[1] - 0.9) < 1e-3
            or abs(stretch.x[1] - 1.1) < 1e-3
        ),
    }


def main() -> None:
    acquire()
    data = load_wfi()
    rows = [
        fit_spec(data, smoothing, degree)
        for smoothing in (0.5, 1.0, 2.0, 4.0)
        for degree in (0, 1, 2)
    ]
    central = next(
        row
        for row in rows
        if row["smoothing_factor_times_n"] == 1.0
        and row["microlensing_polynomial_degree"] == 1
    )
    rates = np.asarray(
        [row["relative_clock_rate_B_over_A"] for row in rows]
    )
    improvements = np.asarray(
        [row["delta_chi_square_one_extra_parameter"] for row in rows]
    )
    robust = bool(
        np.all(improvements > 3.84)
        and np.all(np.abs(rates - 1.0) > 0.01)
        and np.ptp(rates) < 0.02
        and not any(row["stretch_at_search_boundary"] for row in rows)
    )
    result = {
        "schema": "paper7 DES J0408 A/B relative clock-rate audit v1",
        "source": {
            "url": URL,
            "sha256": EXPECTED_SHA256,
            "publication": "Courbin et al. 2017, arXiv:1706.09424",
        },
        "data_scope": {
            "telescope": "WFI only",
            "image_pair": "A/B",
            "epoch_count": len(data["mhjd"]),
            "mhjd_range": [
                float(np.min(data["mhjd"])),
                float(np.max(data["mhjd"])),
            ],
            "published_AB_delay_days": -112.1,
            "published_AB_delay_uncertainty_days": 2.1,
        },
        "model": (
            "B(t)=offset+slow_polynomial(t)+A_spline("
            "pivot+(t-delay-pivot)/stretch)"
        ),
        "central_exploratory_fit": central,
        "declared_robustness_grid": {
            "source_spline_smoothing_factors_times_n": [0.5, 1.0, 2.0, 4.0],
            "microlensing_polynomial_degrees": [0, 1, 2],
            "rows": rows,
        },
        "relative_clock_rate_range": [
            float(np.min(rates)),
            float(np.max(rates)),
        ],
        "delta_chi_square_range": [
            float(np.min(improvements)),
            float(np.max(improvements)),
        ],
        "path_dependent_clock_rate_stable": robust,
        "tau_time_distortion_claim_allowed": False,
        "verdict": (
            "DESJ0408_AB_PATH_CLOCK_RATE_STABLE"
            if robust
            else "DESJ0408_AB_STRETCH_CANDIDATE_NOT_ROBUST_TO_SOURCE_AND_MICROLENSING_MODEL"
        ),
        "claim_boundary": (
            "Exploratory endpoint-opened relative time-scale test. The central "
            "fit is not a significance claim because source smoothing and "
            "microlensing flexibility are not independently frozen and the "
            "D image is not informative enough for a four-path replication."
        ),
        "next_finite_action": (
            "Calibrate the identical frozen shift-versus-stretch estimator on "
            "publication-grade mock light curves with known unit stretch, then "
            "apply it unchanged to at least one additional high-cadence lens."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    with (OUT_DIR / "fit_grid.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(result["verdict"])


if __name__ == "__main__":
    main()
