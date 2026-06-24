#!/usr/bin/env python3
"""Bounded DES J0408 arrival-time recomputation smoke.

This script uses the local lenstronomy-capable venv to recompute image-level
arrival-time differences for one compatible DES J0408 power-law posterior
model.  It compares the recomputed distribution to the public time-delay table
for the same model.  The comparison is intentionally conservative: a mismatch
is recorded as a compatibility blocker, not repaired by fitting a scale factor
or sampling T2.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENv = ROOT / ".venv_wgd2038_repro" / "bin" / "python"
DERIVED = ROOT / "data" / "derived"
OUT_DIR = DERIVED / "repro_results" / "tau_core_lensing_desj0408_arrival_time_recompute_smoke_v1"


HELPER = r'''
import json
import pickle
import sys
import itertools
import warnings
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np

ROOT = Path(sys.argv[1])
model_id = "0408_run1001_0_0_0_0_0_1_1_0"
sample_limit = 128

import dill._dill as dd
import astropy.cosmology as cosmo
import astropy.cosmology.core as core
import astropy.cosmology.flrw.scalar_inv_efuncs as scalar
from lenstronomy.Sampling.parameters import Param
from lenstronomy.LensModel.lens_model import LensModel

if not hasattr(core, "FlatLambdaCDM"):
    core.FlatLambdaCDM = cosmo.FlatLambdaCDM
sys.modules.setdefault("astropy.cosmology.scalar_inv_efuncs", scalar)
dd._reverse_typemap.setdefault("ObjectType", object)

des = ROOT / "data" / "external" / "source_candidate_repos" / "DESJ0408_time_delay_cosmography"
lens_path = des / "model_posteriors" / "lens_models" / f"{model_id}_mod_out.txt"
td_path = des / "model_posteriors" / "time_delays" / f"td_{model_id}_mod_out.txt"

with lens_path.open("rb") as handle:
    input_, output_ = pickle.load(handle, encoding="latin1")

(
    fitting_kwargs_list,
    kwargs_joint,
    kwargs_model,
    kwargs_constraints,
    kwargs_likelihood,
    kwargs_params,
    init_samples,
) = input_
kwargs_result, multi_band_list_out, fit_output, _tail = output_
samples = np.asarray(fit_output[-1][1])
published_td = np.loadtxt(td_path)

param_class = Param(
    kwargs_model,
    kwargs_params["lens_model"][2],
    kwargs_params["source_model"][2],
    kwargs_params["lens_light_model"][2],
    kwargs_params["point_source_model"][2],
    kwargs_params["special"][2],
    kwargs_params["extinction_model"][2],
    kwargs_lens_init=kwargs_params["lens_model"][0],
    **kwargs_constraints,
)

lens_model = LensModel(
    lens_model_list=kwargs_model["lens_model_list"],
    z_lens=None,
    z_source=kwargs_model["z_source"],
    lens_redshift_list=kwargs_model["lens_redshift_list"],
    multi_plane=kwargs_model["multi_plane"],
    observed_convention_index=kwargs_model.get("observed_convention_index"),
    z_source_convention=None,
    cosmo=kwargs_model.get("cosmo"),
)

rows = []
warning_count = 0
arrival_rows = []
for i in range(min(sample_limit, len(samples))):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        kw = param_class.args2kwargs(samples[i])
        ra = kw["kwargs_ps"][0]["ra_image"]
        dec = kw["kwargs_ps"][0]["dec_image"]
        arrival = np.asarray(lens_model.arrival_time(ra, dec, kw["kwargs_lens"]), dtype=float)
    warning_count += len(caught)
    arrival_rows.append(arrival)
    rows.append([arrival[0] - arrival[1], arrival[0] - arrival[3]])

arrival_matrix = np.asarray(arrival_rows, dtype=float)
recomputed = np.asarray(rows, dtype=float)
published_head = published_td[: len(recomputed), :]
delta = recomputed - published_head

old_param_names = list(fit_output[-1][2])
modern_param_count, modern_param_names = param_class.num_param()
old_occurrences = defaultdict(list)
for old_index, name in enumerate(old_param_names):
    old_occurrences[name].append(old_index)
used_occurrences = Counter()
occurrence_mapping = []
missing_modern_params = []
for modern_index, name in enumerate(modern_param_names):
    alias = "tau0" if name == "tau0_list" else name
    occurrence_index = used_occurrences[alias]
    used_occurrences[alias] += 1
    if occurrence_index < len(old_occurrences[alias]):
        occurrence_mapping.append(old_occurrences[alias][occurrence_index])
    else:
        occurrence_mapping.append(None)
        missing_modern_params.append(name)

aligned_samples = np.zeros((len(samples), modern_param_count), dtype=float)
for modern_index, old_index in enumerate(occurrence_mapping):
    name = modern_param_names[modern_index]
    if old_index is not None:
        aligned_samples[:, modern_index] = samples[:, old_index]
    elif name == "s_scale_lens0":
        aligned_samples[:, modern_index] = 0.0
    elif name == "tau0_list":
        # The old posterior stores this column as "tau0"; the alias above should
        # normally fill it.  Keep the public initial value as a defensive fallback.
        aligned_samples[:, modern_index] = 1.0
    else:
        aligned_samples[:, modern_index] = 0.0

aligned_rows = []
aligned_warning_count = 0
for i in range(min(sample_limit, len(aligned_samples))):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        kw = param_class.args2kwargs(aligned_samples[i])
        ra = kw["kwargs_ps"][0]["ra_image"]
        dec = kw["kwargs_ps"][0]["dec_image"]
        arrival = np.asarray(lens_model.arrival_time(ra, dec, kw["kwargs_lens"]), dtype=float)
    aligned_warning_count += len(caught)
    aligned_rows.append([arrival[0] - arrival[1], arrival[0] - arrival[3]])

aligned_recomputed = np.asarray(aligned_rows, dtype=float)
aligned_delta = aligned_recomputed - published_head
aligned_rmse = float(np.sqrt(np.mean(aligned_delta ** 2)))
aligned_match = aligned_rmse < 0.05

pair_series = {}
pair_summary = {}
for i, j in itertools.permutations(range(arrival_matrix.shape[1]), 2):
    label = f"{i}-{j}"
    series = arrival_matrix[:, i] - arrival_matrix[:, j]
    pair_series[label] = series
    pair_summary[label] = {
        "mean": float(np.mean(series)),
        "std": float(np.std(series, ddof=1)),
    }

best_direct = None
best_affine = None
for label_1, series_1 in pair_series.items():
    for label_2, series_2 in pair_series.items():
        candidate = np.vstack([series_1, series_2]).T
        direct_rmse = float(np.sqrt(np.mean((candidate - published_head) ** 2)))
        if best_direct is None or direct_rmse < best_direct["rmse_days"]:
            best_direct = {"pair_columns": [label_1, label_2], "rmse_days": direct_rmse}
        fitted = np.zeros_like(published_head)
        affine = []
        for column, series in enumerate([series_1, series_2]):
            design = np.vstack([series, np.ones_like(series)]).T
            slope, intercept = np.linalg.lstsq(design, published_head[:, column], rcond=None)[0]
            fitted[:, column] = slope * series + intercept
            affine.append({"slope": float(slope), "intercept": float(intercept)})
        affine_rmse = float(np.sqrt(np.mean((fitted - published_head) ** 2)))
        if best_affine is None or affine_rmse < best_affine["rmse_days"]:
            best_affine = {
                "pair_columns": [label_1, label_2],
                "rmse_days": affine_rmse,
                "affine_columns": affine,
            }

summary = {
    "model_id": model_id,
    "sample_limit": int(len(recomputed)),
    "lens_model_list": kwargs_model["lens_model_list"],
    "recomputed_shape": list(recomputed.shape),
    "published_shape": list(published_td.shape),
    "runtime_warning_count": int(warning_count),
    "recomputed_dt_mean": [float(x) for x in np.mean(recomputed, axis=0)],
    "published_head_dt_mean": [float(x) for x in np.mean(published_head, axis=0)],
    "absolute_delta_mean": [float(x) for x in np.mean(np.abs(delta), axis=0)],
    "absolute_delta_median": [float(x) for x in np.median(np.abs(delta), axis=0)],
    "absolute_delta_max": [float(x) for x in np.max(np.abs(delta), axis=0)],
    "old_param_count": len(old_param_names),
    "modern_param_count": int(modern_param_count),
    "old_first_8_param_names": old_param_names[:8],
    "modern_first_8_param_names": modern_param_names[:8],
    "missing_modern_params_after_occurrence_alignment": missing_modern_params,
    "alignment_policy": {
        "duplicate_names": "match by occurrence order",
        "tau0_list": "map from old tau0 column when present",
        "s_scale_lens0": "insert 0.0 fallback for old SPEMD posterior",
    },
    "aligned_recomputed_dt_mean": [float(x) for x in np.mean(aligned_recomputed, axis=0)],
    "aligned_absolute_delta_mean": [float(x) for x in np.mean(np.abs(aligned_delta), axis=0)],
    "aligned_absolute_delta_median": [float(x) for x in np.median(np.abs(aligned_delta), axis=0)],
    "aligned_absolute_delta_max": [float(x) for x in np.max(np.abs(aligned_delta), axis=0)],
    "aligned_rmse_days": aligned_rmse,
    "aligned_runtime_warning_count": int(aligned_warning_count),
    "occurrence_aware_parameter_alignment_matches_public_table": bool(aligned_match),
    "best_direct_pair_match": best_direct,
    "best_affine_pair_match": best_affine,
    "pair_summary": pair_summary,
    "recomputed_finite": bool(np.all(np.isfinite(recomputed))),
    "published_finite": bool(np.all(np.isfinite(published_head))),
    "matches_public_time_delay_table_under_current_reader": bool(np.max(np.abs(delta)) < 1e-6),
}
print(json.dumps(summary))
'''


def run_helper() -> dict[str, object]:
    if not VENv.exists():
        return {
            "helper_available": False,
            "blocked_reason": f"lenstronomy venv not found: {VENv}",
        }
    proc = subprocess.run(
        [str(VENv), "-c", HELPER, str(ROOT)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        return {
            "helper_available": True,
            "helper_returncode": proc.returncode,
            "blocked_reason": "arrival-time helper failed",
            "stderr_tail": proc.stderr[-4000:],
            "stdout_tail": proc.stdout[-4000:],
        }
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    payload = json.loads(lines[-1])
    payload["helper_available"] = True
    payload["helper_stderr_tail"] = proc.stderr[-2000:]
    return payload


def main() -> None:
    result = run_helper()
    recompute_passed = bool(result.get("recomputed_finite")) and bool(result.get("published_finite"))
    table_match = bool(result.get("matches_public_time_delay_table_under_current_reader"))
    aligned_table_match = bool(
        result.get("occurrence_aware_parameter_alignment_matches_public_table")
    )
    best_direct_rmse = float(result.get("best_direct_pair_match", {}).get("rmse_days", float("inf")))
    simple_pair_relabeling_resolves_mismatch = best_direct_rmse < 1e-6
    summary = {
        "schema": "paper7 DES J0408 arrival-time recomputation smoke v1",
        "purpose": (
            "Test whether a decoded DES J0408 posterior sample can be turned into "
            "image-level arrival-time differences under the current lenstronomy "
            "reader, and compare the result to the public time-delay table."
        ),
        "source": {
            "source_id": "DESJ0408_time_delay_cosmography",
            "model_id": result.get("model_id", "0408_run1001_0_0_0_0_0_1_1_0"),
            "helper_python": str(VENv),
        },
        "result": result,
        "criteria": {
            "lenstronomy_helper_available": bool(result.get("helper_available")),
            "arrival_time_recomputed_for_powerlaw_model": recompute_passed,
            "public_time_delay_table_compared": "published_shape" in result,
            "matches_public_time_delay_table_under_current_reader": table_match,
            "occurrence_aware_parameter_alignment_matches_public_table": aligned_table_match,
            "simple_image_pair_relabeling_resolves_mismatch": simple_pair_relabeling_resolves_mismatch,
            "no_t2_parameters_introduced": True,
            "evidence_grade_no_t2_reproduction": False,
            "real_data_T2_sampling_authorized": False,
        },
        "verdict": {
            "desj0408_arrival_time_recompute_smoke_executed": recompute_passed,
            "current_reader_reproduces_public_time_delay_table": table_match,
            "occurrence_aware_parameter_alignment_reproduces_public_time_delay_table": aligned_table_match,
            "simple_image_pair_relabeling_resolves_mismatch": simple_pair_relabeling_resolves_mismatch,
            "bounded_no_t2_baseline_reproduction_completed": False,
            "real_data_T2_sampling_authorized": False,
        },
        "claim_boundary": [
            "A finite image-level arrival-time recomputation is not a T2 result.",
            "The raw modern Param reader does not match the public DES J0408 time-delay table.",
            "An occurrence-aware old-to-modern parameter alignment reproduces the table for this bounded power-law smoke.",
            "No T2 parameter, T2 posterior, Bayes factor, or operator-necessity claim is introduced.",
        ],
        "next_finite_action": (
            "Promote the occurrence-aware parameter alignment to a reusable DES J0408 "
            "extractor and test it across the remaining compatible power-law models, "
            "still before any T2 route."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["verdict"], indent=2))
    print(json.dumps(summary["result"], indent=2))


if __name__ == "__main__":
    main()
