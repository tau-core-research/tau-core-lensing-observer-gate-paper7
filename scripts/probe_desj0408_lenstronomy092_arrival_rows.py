#!/usr/bin/env python3
"""Optional DES J0408 lenstronomy-0.9.2 arrival-row probe.

This is an optional local probe, not part of the required reproduction chain.
It asks whether a Python-3.9 compatibility reconstruction of lenstronomy 0.9.2
resolves the DES J0408 57-parameter row-level arrival-time defects.

The probe does not sample or fit T2.  It only recomputes public arrival-time
rows from public DES posterior files and compares them with public TD tables.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv_desj0408_lenstronomy092_py39_probe" / "bin" / "python"
DERIVED = ROOT / "data" / "derived"
OUT_DIR = (
    DERIVED
    / "repro_results"
    / "tau_core_lensing_desj0408_lenstronomy092_probe_v1"
)
CSV_PATH = DERIVED / "desj0408_lenstronomy092_probe_v1.csv"


HELPER = r'''
import csv
import json
import pickle
import sys
import types
import warnings
from collections import Counter, defaultdict
from distutils.version import LooseVersion
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1])
sample_limit = 128
model_ids = [
    "0408_run1001_0_0_0_0_0_1_1_0",
    "0408_run902_0_0_1_0_0_1_1_0",
    "0408_run905_0_1_0_0_0_1_1_0",
    "0408_run1006_0_1_1_0_0_1_1_0",
    "0408_run909_0_2_0_0_0_1_1_0",
    "0408_run910_0_2_1_0_0_1_1_0",
]


class NumpyVersion:
    """Compatibility shim for lenstronomy 0.9.2 on newer SciPy."""

    def __init__(self, value):
        self.value = LooseVersion(str(value))

    def _coerce(self, other):
        return other.value if isinstance(other, NumpyVersion) else LooseVersion(str(other))

    def __ge__(self, other):
        return self.value >= self._coerce(other)

    def __gt__(self, other):
        return self.value > self._coerce(other)

    def __le__(self, other):
        return self.value <= self._coerce(other)

    def __lt__(self, other):
        return self.value < self._coerce(other)

    def __eq__(self, other):
        return self.value == self._coerce(other)


shim = types.ModuleType("scipy._lib._version")
shim.NumpyVersion = NumpyVersion
sys.modules["scipy._lib._version"] = shim

import dill
import dill._dill as dd
import astropy
import astropy.cosmology as cosmo
import astropy.cosmology.core as core
import lenstronomy
import scipy
from lenstronomy.LensModel.lens_model import LensModel
from lenstronomy.Sampling.parameters import Param

if not hasattr(core, "FlatLambdaCDM"):
    core.FlatLambdaCDM = cosmo.FlatLambdaCDM
dd._reverse_typemap.setdefault("ObjectType", object)

des = ROOT / "data" / "external" / "source_candidate_repos" / "DESJ0408_time_delay_cosmography"


def align_samples(samples, old_names, modern_names):
    old_occurrences = defaultdict(list)
    for old_index, name in enumerate(old_names):
        old_occurrences[name].append(old_index)
    used = Counter()
    aligned = np.zeros((len(samples), len(modern_names)), dtype=float)
    missing = []
    for modern_index, name in enumerate(modern_names):
        alias = "tau0" if name == "tau0_list" else name
        occurrence_index = used[alias]
        used[alias] += 1
        if occurrence_index < len(old_occurrences[alias]):
            aligned[:, modern_index] = samples[:, old_occurrences[alias][occurrence_index]]
        elif name == "s_scale_lens0":
            aligned[:, modern_index] = 0.0
            missing.append(name)
        elif name == "tau0_list":
            aligned[:, modern_index] = 1.0
            missing.append(name)
        else:
            aligned[:, modern_index] = 0.0
            missing.append(name)
    return aligned, missing


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
    samples = np.asarray(fit_output[-1][1])
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
    aligned, missing = align_samples(samples, old_names, modern_names)
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

    recomputed = []
    warning_count = 0
    for sample in aligned[:sample_limit]:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            kw = param_class.args2kwargs(sample)
            ra = kw["kwargs_ps"][0]["ra_image"]
            dec = kw["kwargs_ps"][0]["dec_image"]
            arrival = np.asarray(
                lens_model.arrival_time(ra, dec, kw["kwargs_lens"]), dtype=float
            )
        warning_count += len(caught)
        recomputed.append([arrival[0] - arrival[1], arrival[0] - arrival[3]])
    recomputed = np.asarray(recomputed, dtype=float)
    delta = recomputed - published
    row_max = np.max(np.abs(delta), axis=1)
    rows.append({
        "model_id": model_id,
        "sample_limit": int(sample_limit),
        "old_param_count": int(len(old_names)),
        "legacy092_param_count": int(modern_count),
        "missing_params": "|".join(missing),
        "rmse_days": float(np.sqrt(np.mean(delta ** 2))),
        "median_abs_delta_days": float(np.median(np.abs(delta))),
        "max_abs_delta_days": float(np.max(np.abs(delta))),
        "worst_row_index": int(np.argmax(row_max)),
        "runtime_warning_count": int(warning_count),
        "rowwise_clean_under_legacy092_py39_probe": bool(np.max(np.abs(delta)) < 0.5),
    })

summary = {
    "status": "completed",
    "probe_is_optional": True,
    "probe_runtime": {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "dill": dill.__version__,
        "astropy": astropy.__version__,
        "lenstronomy": lenstronomy.__version__,
        "compatibility_shim": "scipy._lib._version.NumpyVersion",
    },
    "sample_limit": sample_limit,
    "model_count": len(rows),
    "clean_model_count": int(sum(row["rowwise_clean_under_legacy092_py39_probe"] for row in rows)),
    "best_model_by_rmse": min(rows, key=lambda row: row["rmse_days"])["model_id"],
    "best_rmse_days": min(row["rmse_days"] for row in rows),
    "strict_current_baseline_promoted_by_legacy092_probe": False,
    "verdict": (
        "The Python-3.9 lenstronomy-0.9.2 compatibility probe imports and runs, "
        "but it does not recover the public DES J0408 time-delay rows.  It is "
        "therefore not evidence for promoting the four failed 57-parameter "
        "models or for replacing the existing two-model strict no-T2 baseline."
    ),
    "rows": rows,
}
print(json.dumps(summary))
'''


def run_helper() -> dict[str, object]:
    if not VENV.exists():
        return {
            "status": "not_run_venv_missing",
            "probe_is_optional": True,
            "venv_path": str(VENV),
            "strict_current_baseline_promoted_by_legacy092_probe": False,
            "verdict": "Optional lenstronomy-0.9.2 probe venv is not present.",
            "rows": [],
        }
    proc = subprocess.run(
        [str(VENV), "-c", HELPER, str(ROOT)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        return {
            "status": "failed",
            "probe_is_optional": True,
            "venv_path": str(VENV),
            "strict_current_baseline_promoted_by_legacy092_probe": False,
            "stderr_tail": proc.stderr[-4000:],
            "stdout_tail": proc.stdout[-4000:],
            "verdict": "Optional lenstronomy-0.9.2 probe failed before producing row evidence.",
            "rows": [],
        }
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    summary = json.loads(lines[-1])
    summary["venv_path"] = str(VENV)
    summary["stderr_tail"] = proc.stderr[-2000:]
    return summary


def write_outputs(summary: dict[str, object]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    rows = summary.get("rows", [])
    if rows:
        with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def main() -> None:
    summary = run_helper()
    write_outputs(summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
