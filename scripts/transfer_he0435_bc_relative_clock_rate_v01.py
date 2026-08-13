#!/usr/bin/env python3
"""Frozen DES clock-rate estimator transfer to HE 0435 B/C."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import tarfile
import urllib.request
from pathlib import Path

import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.optimize import differential_evolution, minimize_scalar


ROOT = Path(__file__).resolve().parents[1]
DATA_URL = (
    "https://www.epfl.ch/labs/lastro/wp-content/uploads/2019/08/"
    "HE0435_Bonvin2016.rdb_.txt"
)
MOCK_URL = (
    "https://www.epfl.ch/labs/lastro/wp-content/uploads/2019/08/"
    "HE0435_PyCSmocks.tar.gz"
)
DATA_SHA256 = (
    "00308d9e79fb514cb5b021f80044a2307ef8b0a6eeb5e195cd67c10ca494c79e"
)
MOCK_SHA256 = (
    "fc245fae7489660608b25986384cdba68dea4308f1e7842ec34474c8fa51ce63"
)
DATA_PATH = ROOT / "data/external/cosmograil/HE0435_Bonvin2016.rdb.txt"
MOCK_PATH = ROOT / "data/external/cosmograil/HE0435_PyCSmocks.tar.gz"
OUT_DIR = ROOT / (
    "data/derived/repro_results/"
    "tau_core_lensing_he0435_bc_relative_clock_rate_v1"
)
MOCK_COUNT = 128


def acquire(url: str, path: Path, expected_hash: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        urllib.request.urlretrieve(url, path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected_hash:
        raise RuntimeError(f"Unexpected payload SHA-256 for {path}: {digest}")


def parse_rdb(text: str) -> dict[str, np.ndarray]:
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    next(reader)
    rows = list(reader)
    return {
        key: np.asarray([float(row[key]) for row in rows])
        for key in (
            "mhjd",
            "mag_B",
            "magerr_B",
            "mag_C",
            "magerr_C",
        )
    }


def fit_pair(
    data: dict[str, np.ndarray],
    delay_center: float,
    seed: int,
) -> dict:
    t = data["mhjd"]
    pivot = float(np.mean(t))
    reference = data["mag_B"]
    reference_error = data["magerr_B"]
    target = data["mag_C"]
    target_error = data["magerr_C"]
    source = UnivariateSpline(
        t, reference, w=1.0 / reference_error, s=len(t)
    )
    delay_bounds = (delay_center - 3.0, delay_center + 3.0)

    def objective(values: tuple[float, float] | np.ndarray) -> float:
        delay, stretch = values
        source_t = pivot + (t - delay - pivot) / stretch
        mask = (source_t >= np.min(t)) & (source_t <= np.max(t))
        x = (t[mask] - pivot) / 1000.0
        design = np.stack([np.ones_like(x), x], axis=1)
        residual_target = target[mask] - source(source_t[mask])
        variance = target_error[mask] ** 2 + 0.005**2
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
        bounds=delay_bounds,
        method="bounded",
    )
    stretch = differential_evolution(
        objective,
        bounds=[delay_bounds, (0.9, 1.1)],
        seed=seed,
        popsize=10,
        tol=1e-8,
        polish=True,
    )
    return {
        "delay_center_days": delay_center,
        "delay_bounds_days": list(delay_bounds),
        "shift_only_delay_days": float(shift.x),
        "shift_stretch_delay_days": float(stretch.x[0]),
        "relative_clock_rate_C_over_B": float(stretch.x[1]),
        "delta_chi_square_one_extra_parameter": float(
            shift.fun - stretch.fun
        ),
    }


def empirical_p(values: np.ndarray, threshold: float) -> float:
    return float((1 + np.count_nonzero(values >= threshold)) / (len(values) + 1))


def main() -> None:
    acquire(DATA_URL, DATA_PATH, DATA_SHA256)
    acquire(MOCK_URL, MOCK_PATH, MOCK_SHA256)
    real = parse_rdb(DATA_PATH.read_text(encoding="utf-8"))

    # Courbin et al. report Delta t(BC)=+7.8 d. In this script's mapping,
    # C(t) is evaluated against B(t-delay), hence delay_center=-7.8 d.
    observed = fit_pair(real, delay_center=-7.8, seed=430501)

    mock_rates = []
    mock_improvements = []
    with tarfile.open(MOCK_PATH, "r:gz") as archive:
        delay_handle = archive.extractfile("truedelays.txt")
        if delay_handle is None:
            raise RuntimeError("Missing truedelays.txt")
        delay_reader = csv.DictReader(
            io.StringIO(delay_handle.read().decode("utf-8")),
            delimiter="\t",
        )
        delays = {row["filename"]: row for row in delay_reader}
        for index in range(1, MOCK_COUNT + 1):
            name = f"HE0435_PyCSmocks_{index}"
            handle = archive.extractfile(f"mocks/{name}")
            if handle is None:
                raise RuntimeError(f"Missing mock {name}")
            mock = parse_rdb(handle.read().decode("utf-8"))
            row = delays[name]
            dt_ab = float(row["Dt_AB"])
            dt_ac = float(row["Dt_AC"])
            mapping_delay_bc = dt_ab - dt_ac
            fit = fit_pair(
                mock,
                delay_center=mapping_delay_bc,
                seed=4305000 + index,
            )
            mock_rates.append(fit["relative_clock_rate_C_over_B"])
            mock_improvements.append(
                fit["delta_chi_square_one_extra_parameter"]
            )

    rates = np.asarray(mock_rates)
    improvements = np.asarray(mock_improvements)
    observed_deviation = abs(observed["relative_clock_rate_C_over_B"] - 1.0)
    observed_improvement = observed[
        "delta_chi_square_one_extra_parameter"
    ]
    rate_p = empirical_p(np.abs(rates - 1.0), observed_deviation)
    improvement_p = empirical_p(improvements, observed_improvement)
    supported = rate_p < 0.05 and improvement_p < 0.05
    result = {
        "schema": "paper7 HE0435 B/C relative clock-rate transfer v1",
        "source": {
            "light_curve_url": DATA_URL,
            "light_curve_sha256": DATA_SHA256,
            "official_mock_url": MOCK_URL,
            "official_mock_sha256": MOCK_SHA256,
            "publication": "Bonvin et al. 2016, arXiv:1607.01790",
        },
        "transfer_policy": (
            "DES-frozen smoothing factor N, linear extrinsic trend, 0.005 mag "
            "noise floor, and [0.9,1.1] stretch range; only the externally "
            "published target delay fixes the target-specific +/-3 d window"
        ),
        "image_pair": "B/C",
        "epoch_count": len(real["mhjd"]),
        "published_delay_BC_days": 7.8,
        "observed_fit": observed,
        "official_unit_stretch_mock_count": MOCK_COUNT,
        "official_mock_null": {
            "rate_quantiles_2p5_50_97p5": np.quantile(
                rates, [0.025, 0.5, 0.975]
            ).tolist(),
            "improvement_quantiles_2p5_50_97p5": np.quantile(
                improvements, [0.025, 0.5, 0.975]
            ).tolist(),
            "empirical_two_sided_rate_p_value": rate_p,
            "empirical_improvement_p_value": improvement_p,
        },
        "path_dependent_clock_rate_supported": supported,
        "tau_time_distortion_claim_allowed": False,
        "verdict": (
            "HE0435_BC_NONUNIT_CLOCK_RATE_CANDIDATE_SURVIVES_OFFICIAL_MOCKS"
            if supported
            else "HE0435_BC_CLOCK_RATE_COMPATIBLE_WITH_OFFICIAL_UNIT_STRETCH_MOCKS"
        ),
        "claim_boundary": (
            "Independent-lens transfer of a frozen exploratory estimator. "
            "Even a positive result is not Tau-specific without source/path "
            "prediction, all-pair consistency, and external replication."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "verdict": result["verdict"],
        "observed_rate": observed["relative_clock_rate_C_over_B"],
        "rate_p": rate_p,
        "improvement_p": improvement_p,
    }, indent=2))


if __name__ == "__main__":
    main()
