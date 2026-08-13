#!/usr/bin/env python3
"""Test whether paired OIII source-size shifts support surrogate transport."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "data/derived/repro_results"
WARM = RESULTS / "tau_core_lensing_wgd2038_warm_dust_prior_predictive_n64_v1/summary.json"
OIII = RESULTS / "tau_core_lensing_wgd2038_oiii_prior_predictive_n64_v1/summary.json"
OUT = RESULTS / "tau_core_lensing_wgd2038_oiii_source_kernel_surrogate_v1"


def main() -> None:
    warm = json.loads(WARM.read_text(encoding="utf-8"))
    oiii = json.loads(OIII.read_text(encoding="utf-8"))
    warm_ratio = np.asarray(warm["predicted_flux_ratios"], dtype=float)
    oiii_ratio = np.asarray(oiii["predicted_flux_ratios"], dtype=float)
    parameters = np.asarray(warm["sampled_parameter_rows"], dtype=float)
    features = np.column_stack([warm_ratio, parameters[:, :-1]])
    target = oiii_ratio - warm_ratio

    folds = KFold(n_splits=8, shuffle=True, random_state=20384200)
    models = {
        "ridge": make_pipeline(StandardScaler(), Ridge(alpha=10.0)),
        "random_forest": RandomForestRegressor(
            n_estimators=500,
            min_samples_leaf=3,
            max_features=0.7,
            random_state=20384201,
            n_jobs=1,
        ),
    }
    baseline_rmse = np.sqrt(np.mean(target**2, axis=0))
    audits = {}
    promoted = False
    for name, model in models.items():
        prediction = cross_val_predict(model, features, target, cv=folds)
        rmse = np.sqrt(np.mean((prediction - target) ** 2, axis=0))
        ratio = rmse / baseline_rmse
        absolute_true = np.max(np.abs(target), axis=1)
        absolute_predicted = np.max(np.abs(prediction), axis=1)
        top_count = max(1, int(np.ceil(0.1 * target.shape[0])))
        true_top = set(np.argsort(absolute_true)[-top_count:])
        predicted_top = set(np.argsort(absolute_predicted)[-top_count:])
        recall = len(true_top & predicted_top) / top_count
        eligible = bool(np.all(ratio < 0.8) and recall >= 0.5)
        promoted = promoted or eligible
        audits[name] = {
            "cross_validated_rmse": rmse.tolist(),
            "zero_shift_baseline_rmse": baseline_rmse.tolist(),
            "rmse_to_zero_baseline_ratio": ratio.tolist(),
            "largest_shift_decile_recall": recall,
            "transport_eligible": eligible,
        }

    result = {
        "schema": "paper7 WGD2038 OIII source-kernel surrogate audit v1",
        "paired_realizations": int(target.shape[0]),
        "feature_count": int(features.shape[1]),
        "cross_validation": "fixed shuffled 8-fold",
        "models": audits,
        "surrogate_transport_to_n256_authorized": promoted,
        "tau_or_observer_time_scoring_allowed": False,
        "verdict": (
            "PAIRED_SOURCE_KERNEL_SURROGATE_PROMOTED"
            if promoted
            else "SOURCE_KERNEL_SHIFT_SURROGATE_FAILS_FROZEN_TRANSFER_GATE"
        ),
        "claim_boundary": (
            "The surrogate may be used only if it improves every coordinate "
            "RMSE by at least 20% over the zero-shift baseline and recovers at "
            "least half of the largest-shift decile. Failure blocks synthetic "
            "OIII enlargement; it is not evidence for or against Tau Core."
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
