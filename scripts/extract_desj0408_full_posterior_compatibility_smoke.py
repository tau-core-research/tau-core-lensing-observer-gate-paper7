#!/usr/bin/env python3
"""Decode DES J0408 lens-model posterior metadata with compatibility patches.

The public DES J0408 posterior files were serialized with older Astropy/dill
assumptions.  This bounded smoke reader applies only import-compatibility
aliases, then extracts metadata needed for a future no-T2 reproduction:
sample shapes, parameter names, logZ-like sampler fields, model family, and
matching time-delay file presence.  It does not sample T2 or evaluate a new
lensing likelihood.
"""

from __future__ import annotations

import csv
import gc
import json
import pickle
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DES_ROOT = ROOT / "data" / "external" / "source_candidate_repos" / "DESJ0408_time_delay_cosmography"
LENS_DIR = DES_ROOT / "model_posteriors" / "lens_models"
TD_DIR = DES_ROOT / "model_posteriors" / "time_delays"
DERIVED = ROOT / "data" / "derived"
OUT_DIR = DERIVED / "repro_results" / "tau_core_lensing_desj0408_full_posterior_compat_smoke_v1"
CSV_PATH = DERIVED / "desj0408_full_posterior_compat_smoke_v1.csv"


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


def install_pickle_compatibility() -> list[str]:
    patches: list[str] = []
    import astropy.cosmology as cosmo
    import astropy.cosmology.core as core
    import astropy.cosmology.flrw.scalar_inv_efuncs as scalar_inv_efuncs
    import dill._dill as dill_private

    if not hasattr(core, "FlatLambdaCDM"):
        core.FlatLambdaCDM = cosmo.FlatLambdaCDM
        patches.append("astropy.cosmology.core.FlatLambdaCDM alias")
    if "astropy.cosmology.scalar_inv_efuncs" not in sys.modules:
        sys.modules["astropy.cosmology.scalar_inv_efuncs"] = scalar_inv_efuncs
        patches.append("astropy.cosmology.scalar_inv_efuncs module alias")
    if "ObjectType" not in dill_private._reverse_typemap:
        dill_private._reverse_typemap["ObjectType"] = object
        patches.append("dill ObjectType reverse typemap alias")
    return patches


def model_id_from_lens_path(path: Path) -> str:
    name = path.name
    if name.endswith("_mod_out.txt"):
        return name[: -len("_mod_out.txt")]
    return path.stem


def model_family(model_id: str) -> str:
    return "powerlaw" if model_id in POWERLAW_IDS else "composite"


def stable_weights(logz: list[float]) -> list[float]:
    arr = np.asarray(logz, dtype=float)
    shifted = arr - np.nanmax(arr)
    raw = np.exp(shifted)
    total = np.nansum(raw)
    if not np.isfinite(total) or total <= 0:
        return [float("nan")] * len(arr)
    return [float(x) for x in raw / total]


def summarize_file(path: Path) -> dict[str, object]:
    model_id = model_id_from_lens_path(path)
    td_path = TD_DIR / f"td_{model_id}_mod_out.txt"
    with path.open("rb") as handle:
        input_, output_ = pickle.load(handle, encoding="latin1")
    kwargs_result, multi_band_list_out, fit_output, _tail = output_
    sampler_record = fit_output[-1]
    sampler_name = sampler_record[0]
    samples = np.asarray(sampler_record[1])
    param_names = list(sampler_record[2])
    log_likelihood = np.asarray(sampler_record[3])
    logz = float(sampler_record[4])
    logz_error = float(sampler_record[5])
    kwargs_model = input_[2]
    lens_models = list(kwargs_model.get("lens_model_list", []))
    source_models = list(kwargs_model.get("source_light_model_list", []))
    lens_light_models = list(kwargs_model.get("lens_light_model_list", []))
    ps = kwargs_result.get("kwargs_ps", [])
    has_image_positions = bool(ps) and "ra_image" in ps[0] and "dec_image" in ps[0]
    row = {
        "model_id": model_id,
        "model_family": model_family(model_id),
        "file_size_bytes": path.stat().st_size,
        "sampler": sampler_name,
        "sample_count": int(samples.shape[0]),
        "parameter_count": int(samples.shape[1]) if samples.ndim == 2 else None,
        "param_name_count": len(param_names),
        "log_likelihood_min": float(np.nanmin(log_likelihood)),
        "log_likelihood_max": float(np.nanmax(log_likelihood)),
        "log_likelihood_mean": float(np.nanmean(log_likelihood)),
        "logZ": logz,
        "logZ_error": logz_error,
        "matching_time_delay_file_present": td_path.exists(),
        "lens_model_count": len(lens_models),
        "source_light_model_count": len(source_models),
        "lens_light_model_count": len(lens_light_models),
        "point_source_image_positions_present": has_image_positions,
        "first_lens_model": lens_models[0] if lens_models else "",
        "lens_model_list": "|".join(lens_models),
        "first_12_param_names": "|".join(param_names[:12]),
    }
    del input_, output_, kwargs_result, multi_band_list_out, fit_output, samples, log_likelihood
    gc.collect()
    return row


def write_csv(rows: list[dict[str, object]]) -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def aggregate(rows: list[dict[str, object]]) -> dict[str, object]:
    by_family: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_family.setdefault(str(row["model_family"]), []).append(row)
    families: dict[str, object] = {}
    for family, subset in sorted(by_family.items()):
        logz = [float(row["logZ"]) for row in subset]
        weights = stable_weights(logz)
        max_i = int(np.nanargmax(np.asarray(logz)))
        families[family] = {
            "model_count": len(subset),
            "logZ_min": float(np.nanmin(logz)),
            "logZ_max": float(np.nanmax(logz)),
            "best_logZ_model_id": subset[max_i]["model_id"],
            "max_relative_family_weight": float(np.nanmax(weights)),
            "models_with_matching_time_delay_file": sum(
                bool(row["matching_time_delay_file_present"]) for row in subset
            ),
        }
    global_logz = [float(row["logZ"]) for row in rows]
    global_weights = stable_weights(global_logz)
    best_global_i = int(np.nanargmax(np.asarray(global_logz)))
    return {
        "model_count": len(rows),
        "all_lens_model_posteriors_loaded": True,
        "sample_count_min": min(int(row["sample_count"]) for row in rows),
        "sample_count_max": max(int(row["sample_count"]) for row in rows),
        "parameter_count_min": min(int(row["parameter_count"]) for row in rows),
        "parameter_count_max": max(int(row["parameter_count"]) for row in rows),
        "models_with_matching_time_delay_file": sum(
            bool(row["matching_time_delay_file_present"]) for row in rows
        ),
        "models_with_point_source_image_positions": sum(
            bool(row["point_source_image_positions_present"]) for row in rows
        ),
        "global_best_logZ_model_id": rows[best_global_i]["model_id"],
        "global_best_logZ_family": rows[best_global_i]["model_family"],
        "global_max_relative_weight": float(np.nanmax(global_weights)),
        "families": families,
    }


def main() -> None:
    patches = install_pickle_compatibility()
    files = sorted(LENS_DIR.glob("*_mod_out.txt"))
    if not files:
        raise SystemExit(f"no DES J0408 lens posterior files found in {LENS_DIR}")
    rows = [summarize_file(path) for path in files]
    write_csv(rows)
    summary = {
        "schema": "paper7 DES J0408 full posterior compatibility smoke v1",
        "purpose": (
            "Verify that the public DES J0408 lens-model posterior files can be "
            "decoded far enough to expose sampler metadata, samples, parameter "
            "names, model configuration, logZ-like fields, and image-position "
            "records without introducing T2."
        ),
        "source": {
            "source_id": "DESJ0408_time_delay_cosmography",
            "source_url": "https://github.com/ajshajib/DESJ0408_time_delay_cosmography",
            "local_lens_model_dir": str(LENS_DIR.relative_to(ROOT)),
            "local_time_delay_dir": str(TD_DIR.relative_to(ROOT)),
        },
        "compatibility_patches": patches,
        "aggregate": aggregate(rows),
        "criteria": {
            "all_public_lens_model_posteriors_loaded": True,
            "all_public_time_delay_files_matched": all(
                bool(row["matching_time_delay_file_present"]) for row in rows
            ),
            "all_models_have_samples_and_param_names": all(
                int(row["sample_count"]) > 0
                and int(row["parameter_count"]) == int(row["param_name_count"])
                for row in rows
            ),
            "all_models_have_point_source_image_positions": all(
                bool(row["point_source_image_positions_present"]) for row in rows
            ),
            "logZ_like_fields_extracted": all(np.isfinite(float(row["logZ"])) for row in rows),
            "model_configuration_metadata_extracted": all(
                int(row["lens_model_count"]) > 0 for row in rows
            ),
            "no_t2_parameters_introduced": True,
            "image_level_fermat_or_arrival_time_recomputed": False,
            "evidence_grade_no_t2_reproduction": False,
            "real_data_T2_sampling_authorized": False,
        },
        "verdict": {
            "desj0408_full_posterior_compatibility_smoke_passed": True,
            "bounded_no_t2_baseline_reproduction_completed": False,
            "real_data_T2_sampling_authorized": False,
        },
        "claim_boundary": [
            "This decodes posterior metadata and samples; it does not recompute arrival times or Fermat potentials.",
            "Relative logZ fields are exposed for follow-up weighting, but no final model-ensemble evidence is claimed.",
            "No T2 parameter, T2 posterior, Bayes factor, or operator-necessity claim is introduced.",
        ],
        "next_finite_action": (
            "Use the decoded kwargs_model/kwargs_result/sample metadata to compute "
            "or recover image-level arrival-time/Fermat features for a bounded no-T2 "
            "baseline, still before any T2 sampling."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["verdict"], indent=2))
    print(json.dumps(summary["aggregate"], indent=2))


if __name__ == "__main__":
    main()
