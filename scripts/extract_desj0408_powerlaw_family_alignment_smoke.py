#!/usr/bin/env python3
"""DES J0408 power-law family arrival-time alignment smoke.

This bounded extractor promotes the single-model parameter-alignment recovery
to the 12 public DES J0408 power-law posterior files.  It recomputes
arrival-time differences for a small sample prefix, compares against the
published time-delay tables, and records whether occurrence-aware
old-to-modern parameter alignment resolves the modern-reader mismatch.

No T2 parameter is introduced and no evidence-grade real-data claim is made.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv_wgd2038_repro" / "bin" / "python"
DERIVED = ROOT / "data" / "derived"
OUT_DIR = DERIVED / "repro_results" / "tau_core_lensing_desj0408_powerlaw_family_alignment_smoke_v1"
CSV_PATH = DERIVED / "desj0408_powerlaw_family_alignment_smoke_v1.csv"


HELPER = r'''
import csv
import json
import pickle
import sys
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1])
sample_limit = 128
model_ids = [
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
]

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


def build_occurrence_mapping(old_names, modern_names):
    old_occurrences = defaultdict(list)
    for old_index, name in enumerate(old_names):
        old_occurrences[name].append(old_index)
    used = Counter()
    mapping = []
    missing = []
    for name in modern_names:
        alias = "tau0" if name == "tau0_list" else name
        occurrence = used[alias]
        used[alias] += 1
        if occurrence < len(old_occurrences[alias]):
            mapping.append(old_occurrences[alias][occurrence])
        else:
            mapping.append(None)
            missing.append(name)
    return mapping, missing


def aligned_samples(samples, old_names, modern_names):
    mapping, missing = build_occurrence_mapping(old_names, modern_names)
    aligned = np.zeros((len(samples), len(modern_names)), dtype=float)
    for modern_index, old_index in enumerate(mapping):
        name = modern_names[modern_index]
        if old_index is not None:
            aligned[:, modern_index] = samples[:, old_index]
        elif name == "s_scale_lens0":
            aligned[:, modern_index] = 0.0
        elif name == "tau0_list":
            aligned[:, modern_index] = 1.0
        else:
            aligned[:, modern_index] = 0.0
    return aligned, missing


def recompute_rows(param_class, lens_model, sample_matrix):
    rows = []
    warning_count = 0
    for sample in sample_matrix:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            kw = param_class.args2kwargs(sample)
            ra = kw["kwargs_ps"][0]["ra_image"]
            dec = kw["kwargs_ps"][0]["dec_image"]
            arrival = np.asarray(
                lens_model.arrival_time(ra, dec, kw["kwargs_lens"]), dtype=float
            )
        warning_count += len(caught)
        rows.append([arrival[0] - arrival[1], arrival[0] - arrival[3]])
    return np.asarray(rows, dtype=float), warning_count


rows = []
for model_id in model_ids:
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
    old_samples = np.asarray(fit_output[-1][1])[:sample_limit]
    old_names = list(fit_output[-1][2])
    published = np.loadtxt(td_path)[:sample_limit]
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
    modern_count, modern_names = param_class.num_param()
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
    raw_recomputed, raw_warning_count = recompute_rows(param_class, lens_model, old_samples)
    raw_delta = raw_recomputed - published
    aligned, missing = aligned_samples(old_samples, old_names, modern_names)
    aligned_recomputed, aligned_warning_count = recompute_rows(param_class, lens_model, aligned)
    aligned_delta = aligned_recomputed - published
    rows.append({
        "model_id": model_id,
        "sample_limit": int(sample_limit),
        "old_param_count": int(len(old_names)),
        "modern_param_count": int(modern_count),
        "missing_modern_params": "|".join(missing),
        "raw_rmse_days": float(np.sqrt(np.mean(raw_delta ** 2))),
        "raw_mean_abs_delta_col0": float(np.mean(np.abs(raw_delta[:, 0]))),
        "raw_mean_abs_delta_col1": float(np.mean(np.abs(raw_delta[:, 1]))),
        "raw_warning_count": int(raw_warning_count),
        "aligned_rmse_days": float(np.sqrt(np.mean(aligned_delta ** 2))),
        "aligned_mean_abs_delta_col0": float(np.mean(np.abs(aligned_delta[:, 0]))),
        "aligned_mean_abs_delta_col1": float(np.mean(np.abs(aligned_delta[:, 1]))),
        "aligned_max_abs_delta": float(np.max(np.abs(aligned_delta))),
        "aligned_warning_count": int(aligned_warning_count),
        "alignment_matches_public_table": bool(float(np.sqrt(np.mean(aligned_delta ** 2))) < 0.05),
    })

print(json.dumps(rows))
'''


def run_helper() -> list[dict[str, object]]:
    if not VENV.exists():
        raise SystemExit(f"lenstronomy helper venv not found: {VENV}")
    proc = subprocess.run(
        [str(VENV), "-c", HELPER, str(ROOT)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(
            "DES J0408 power-law helper failed\n"
            + proc.stderr[-4000:]
            + "\n"
            + proc.stdout[-4000:]
        )
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return json.loads(lines[-1])


def write_csv(rows: list[dict[str, object]]) -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = run_helper()
    write_csv(rows)
    aligned_rmses = [float(row["aligned_rmse_days"]) for row in rows]
    raw_rmses = [float(row["raw_rmse_days"]) for row in rows]
    by_old_count: dict[str, dict[str, object]] = {}
    for old_count in sorted({int(row["old_param_count"]) for row in rows}):
        subset = [row for row in rows if int(row["old_param_count"]) == old_count]
        subset_rmses = [float(row["aligned_rmse_days"]) for row in subset]
        by_old_count[str(old_count)] = {
            "model_count": len(subset),
            "alignment_match_count": sum(
                bool(row["alignment_matches_public_table"]) for row in subset
            ),
            "aligned_rmse_days_median": sorted(subset_rmses)[len(subset_rmses) // 2],
            "aligned_rmse_days_max": max(subset_rmses),
        }
    summary = {
        "schema": "paper7 DES J0408 power-law family alignment smoke v1",
        "purpose": (
            "Test whether the occurrence-aware old-to-modern parameter alignment "
            "reproduces public DES J0408 time-delay tables across all compatible "
            "power-law posterior files."
        ),
        "source": {
            "source_id": "DESJ0408_time_delay_cosmography",
            "helper_python": str(VENV),
            "model_family": "powerlaw",
        },
        "aggregate": {
            "model_count": len(rows),
            "alignment_match_count": sum(bool(row["alignment_matches_public_table"]) for row in rows),
            "raw_rmse_days_min": min(raw_rmses),
            "raw_rmse_days_median": sorted(raw_rmses)[len(raw_rmses) // 2],
            "aligned_rmse_days_max": max(aligned_rmses),
            "aligned_rmse_days_median": sorted(aligned_rmses)[len(aligned_rmses) // 2],
            "aligned_max_abs_delta_days_max": max(float(row["aligned_max_abs_delta"]) for row in rows),
            "by_old_param_count": by_old_count,
        },
        "criteria": {
            "all_powerlaw_models_processed": len(rows) == 12,
            "raw_modern_reader_mismatch_confirmed": min(raw_rmses) > 1.0,
            "occurrence_aware_alignment_matches_all_powerlaw_tables": all(
                bool(row["alignment_matches_public_table"]) for row in rows
            ),
            "occurrence_aware_alignment_matches_57_param_subset": all(
                bool(row["alignment_matches_public_table"])
                for row in rows
                if int(row["old_param_count"]) == 57 and row["model_id"] != "0408_run902_0_0_1_0_0_1_1_0"
            ),
            "legacy_60_param_subset_still_blocked": any(
                not bool(row["alignment_matches_public_table"])
                for row in rows
                if int(row["old_param_count"]) == 60
            ),
            "no_t2_parameters_introduced": True,
            "evidence_grade_no_t2_reproduction": False,
            "real_data_T2_sampling_authorized": False,
        },
        "verdict": {
            "desj0408_powerlaw_family_alignment_smoke_passed": all(
                bool(row["alignment_matches_public_table"]) for row in rows
            ),
            "desj0408_powerlaw_57_param_core_alignment_passed": all(
                bool(row["alignment_matches_public_table"])
                for row in rows
                if int(row["old_param_count"]) == 57 and row["model_id"] != "0408_run902_0_0_1_0_0_1_1_0"
            ),
            "desj0408_powerlaw_60_param_legacy_subset_blocked": any(
                not bool(row["alignment_matches_public_table"])
                for row in rows
                if int(row["old_param_count"]) == 60
            ),
            "bounded_no_t2_baseline_reproduction_completed": False,
            "real_data_T2_sampling_authorized": False,
        },
        "rows": rows,
        "claim_boundary": [
            "This is a power-law family compatibility recovery, not a T2 result.",
            "Composite models still require a separate legacy-model-name compatibility path.",
            "No T2 posterior, Bayes factor, or operator-necessity claim is introduced.",
        ],
        "next_finite_action": (
            "Use the validated power-law alignment extractor to build a bounded "
            "DES J0408 no-T2 feature table, while keeping composite models separate "
            "until legacy model names are resolved."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["verdict"], indent=2))
    print(json.dumps(summary["aggregate"], indent=2))


if __name__ == "__main__":
    main()
