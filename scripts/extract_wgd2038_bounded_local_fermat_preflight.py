#!/usr/bin/env python3
"""Extract a bounded local WGD2038 Fermat/parity preflight table.

This uses locally generated, explicitly non-converged WGD2038 diagnostic
outputs. It is a plumbing/extraction preflight only: it does not use the
published WGD posterior joblib payload, does not create a holdout score table,
and does not authorize T2 sampling.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RESULTS = DERIVED / "repro_results"
OUT_DIR = RESULTS / "tau_core_lensing_wgd2038_bounded_local_fermat_preflight_v1"
OUT_TABLE = DERIVED / "wgd2038_bounded_local_fermat_preflight_v1.csv"
WGD_TEMP = Path("/tmp/paper7_tdc_sources/WGD2038-4008/lenstronomy_modeling/temp")
VENV_PYTHON = ROOT / ".venv_wgd2038_repro" / "bin" / "python"

JOBS = [
    {
        "job_name": "tau_core_profile_freeze_v2_pemd_fastell_backend",
        "claim_level": "bounded_profile_freeze_v2_not_converged_posterior",
    },
    {
        "job_name": "tau_core_profile_freeze_v1_pemd_fastell_backend",
        "claim_level": "bounded_profile_freeze_v1_not_converged_posterior",
    },
    {
        "job_name": "tau_core_mcmc_diag120_cont3_cold_pemd_fastell_backend",
        "claim_level": "bounded_diag120_cont3_cold_not_converged_posterior",
    },
]


HELPER = r"""
import json
import joblib
import numpy as np
import sys
from pathlib import Path
from lenstronomy.LensModel.lens_model import LensModel

temp = Path(sys.argv[1])
jobs = json.loads(sys.argv[2])
all_rows = []
job_summaries = []
for job in jobs:
    job_name = job["job_name"]
    input_path = temp / (job_name + ".txt")
    output_path = temp / (job_name + "_out.txt")
    available = input_path.exists() and output_path.exists()
    job_summary = {
        "job_name": job_name,
        "claim_level": job["claim_level"],
        "input_path": str(input_path),
        "output_path": str(output_path),
        "input_present": input_path.exists(),
        "output_present": output_path.exists(),
        "extraction_success": False,
    }
    if not available:
        job_summaries.append(job_summary)
        continue
    try:
        input_ = joblib.load(open(input_path, "rb"))
        output_ = joblib.load(open(output_path, "rb"))
        kwargs_model = input_[2]
        kwargs_result = output_[1][0]
        kwargs_ps = kwargs_result["kwargs_ps"][0]
        ra = np.asarray(kwargs_ps["ra_image"], dtype=float)
        dec = np.asarray(kwargs_ps["dec_image"], dtype=float)
        lens_model = LensModel(
            lens_model_list=kwargs_model["lens_model_list"],
            z_lens=0.230,
            z_source=0.777,
            multi_plane=False,
        )
        fermat = np.asarray(
            lens_model.fermat_potential(ra, dec, kwargs_result["kwargs_lens"]),
            dtype=float,
        )
        f_xx, f_xy, f_yx, f_yy = lens_model.hessian(
            ra, dec, kwargs_result["kwargs_lens"]
        )
        det_a = (1 - f_xx) * (1 - f_yy) - f_xy * f_yx
        trace_a = (1 - f_xx) + (1 - f_yy)
        dphi_ab = float(fermat[1] - fermat[3])
        dphi_ac = float(fermat[1] - fermat[2])
        dphi_ad = float(fermat[1] - fermat[0])
        for i in range(len(ra)):
            if det_a[i] > 0 and trace_a[i] > 0:
                morse = "minimum"
            elif det_a[i] > 0 and trace_a[i] < 0:
                morse = "maximum"
            else:
                morse = "saddle"
            all_rows.append(
                {
                    "job_name": job_name,
                    "claim_level": job["claim_level"],
                    "image_order_index": int(i),
                    "image_label_contract_basis": ["D", "B", "C", "A"][i],
                    "ra_image": float(ra[i]),
                    "dec_image": float(dec[i]),
                    "fermat_potential": float(fermat[i]),
                    "jacobian_det": float(det_a[i]),
                    "jacobian_trace": float(trace_a[i]),
                    "parity_or_morse_type": morse,
                    "dphi_AB": dphi_ab,
                    "dphi_AC": dphi_ac,
                    "dphi_AD": dphi_ad,
                    "can_compute_no_t2_residual_vector": False,
                    "usable_for_des_frozen_score": False,
                }
            )
        job_summary.update(
            {
                "extraction_success": True,
                "image_count": int(len(ra)),
                "dphi_AB": dphi_ab,
                "dphi_AC": dphi_ac,
                "dphi_AD": dphi_ad,
                "lens_model_list": kwargs_model["lens_model_list"],
            }
        )
    except Exception as exc:
        job_summary["error"] = repr(exc)
    job_summaries.append(job_summary)

print(json.dumps({"rows": all_rows, "job_summaries": job_summaries}))
"""


def run_helper() -> dict[str, Any]:
    if not VENV_PYTHON.exists():
        return {
            "rows": [],
            "job_summaries": [],
            "helper_error": f"missing helper python: {VENV_PYTHON}",
        }
    proc = subprocess.run(
        [str(VENV_PYTHON), "-c", HELPER, str(WGD_TEMP), json.dumps(JOBS)],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        return {
            "rows": [],
            "job_summaries": [],
            "helper_error": proc.stderr.strip() or proc.stdout.strip(),
        }
    return json.loads(proc.stdout)


def main() -> None:
    helper = run_helper()
    rows = helper.get("rows", [])
    job_summaries = helper.get("job_summaries", [])
    successful_jobs = [job for job in job_summaries if job.get("extraction_success")]
    primary = next(
        (job for job in successful_jobs if job["job_name"] == JOBS[0]["job_name"]),
        successful_jobs[0] if successful_jobs else None,
    )

    summary = {
        "schema": "paper7 WGD2038 bounded local Fermat preflight v1",
        "purpose": (
            "Check whether the locally generated, non-converged WGD2038 diagnostic "
            "outputs can technically yield image positions, Fermat potentials, and "
            "Morse/parity labels."
        ),
        "sources": {
            "temp_dir": str(WGD_TEMP),
            "helper_python": str(VENV_PYTHON.relative_to(ROOT)) if VENV_PYTHON.exists() else str(VENV_PYTHON),
        },
        "job_summaries": job_summaries,
        "primary_job_summary": primary,
        "counts": {
            "candidate_job_count": len(JOBS),
            "successful_job_count": len(successful_jobs),
            "image_row_count": len(rows),
            "score_ready_row_count": sum(1 for row in rows if row["usable_for_des_frozen_score"]),
        },
        "verdict": {
            "wgd2038_bounded_local_fermat_preflight_created": True,
            "bounded_local_image_fermat_table_materialized": len(rows) > 0,
            "bounded_local_parity_labels_materialized": len(rows) > 0,
            "uses_converged_or_published_wgd_posterior": False,
            "can_apply_des_frozen_score_now": False,
            "real_data_T2_sampling_authorized": False,
            "claim_level": "local_extraction_preflight_not_holdout_score_not_time_shift_evidence",
        },
        "helper_error": helper.get("helper_error"),
        "rows": rows,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    if rows:
        with OUT_TABLE.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    else:
        OUT_TABLE.write_text("", encoding="utf-8")

    print(json.dumps(summary["verdict"], indent=2, sort_keys=True))
    print(json.dumps(summary["counts"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
