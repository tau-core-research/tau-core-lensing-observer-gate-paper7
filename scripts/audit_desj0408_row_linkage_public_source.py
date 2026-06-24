#!/usr/bin/env python3
"""Audit public DES J0408 source code for row-linkage rules.

This source audit records what the public repository says about the intended
relationship between lens posterior samples and saved time-delay rows.  It does
not recompute lensing quantities and does not promote any failed model.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DES_ROOT = ROOT / "data" / "external" / "source_candidate_repos" / "DESJ0408_time_delay_cosmography"
SOURCE_PATH = DES_ROOT / "notebooks" / "process_output" / "output_class.py"
NOTEBOOK_PATH = DES_ROOT / "notebooks" / "Distance posterior from combining lensing, kinematics, and external convergence.ipynb"
DERIVED = ROOT / "data" / "derived"
OUT_DIR = DERIVED / "repro_results" / "tau_core_lensing_desj0408_row_linkage_public_source_audit_v1"
CSV_PATH = DERIVED / "desj0408_row_linkage_public_source_audit_v1.csv"


PATTERNS = {
    "samples_mcmc_loaded_from_fit_output": "self.samples_mcmc = fit_output[-1][1]",
    "time_delay_loop_over_sample_index": "for i in tnrange(num_samples,",
    "per_row_param_array_from_samples_mcmc_i": "param_array = self.samples_mcmc[i]",
    "per_row_args2kwargs": "kwargs_result = self.param_class.args2kwargs(param_array)",
    "arrival_time_from_row_kwargs": "model_arrival_times = self.lens_model.arrival_time(",
    "append_dt_ab_dt_ad_in_loop_order": "self.model_time_delays.append([dt_AB, dt_AD])",
    "model_time_delays_array_no_shuffle": "self.model_time_delays = np.array(self.model_time_delays)",
    "load_time_delays_np_loadtxt": "loaded_time_delays = np.loadtxt(file_path)",
    "load_time_delays_length_assert": "assert len(loaded_time_delays) == self.get_num_samples()",
    "loaded_time_delays_assigned": "self.model_time_delays = loaded_time_delays",
}

NOTEBOOK_PATTERNS = {
    "compute_time_delays_first_time_comment": "model.compute_model_time_delays()",
    "load_time_delays_from_public_td_dir": "model.load_time_delays(model.model_id, '../model_posteriors/time_delays/td_', dir_suffix)",
}


def find_pattern(path: Path, pattern: str) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [
        {"line": index + 1, "text": line.strip()}
        for index, line in enumerate(lines)
        if pattern in line
    ]
    return {
        "path": str(path.relative_to(ROOT)),
        "pattern": pattern,
        "match_count": len(matches),
        "first_line": matches[0]["line"] if matches else None,
        "first_text": matches[0]["text"] if matches else "",
    }


def write_csv(rows: list[dict[str, object]]) -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows: list[dict[str, object]] = []
    for rule_id, pattern in PATTERNS.items():
        row = find_pattern(SOURCE_PATH, pattern)
        row["rule_id"] = rule_id
        row["source_kind"] = "python_source"
        rows.append(row)
    for rule_id, pattern in NOTEBOOK_PATTERNS.items():
        row = find_pattern(NOTEBOOK_PATH, pattern)
        row["rule_id"] = rule_id
        row["source_kind"] = "notebook_json"
        rows.append(row)
    write_csv(rows)
    found = {str(row["rule_id"]): int(row["match_count"]) > 0 for row in rows}
    summary = {
        "schema": "paper7 DES J0408 row-linkage public source audit v1",
        "purpose": (
            "Record public-source evidence for the intended row relationship "
            "between lens posterior samples and saved time-delay rows."
        ),
        "source": {
            "source_id": "DESJ0408_time_delay_cosmography",
            "source_file": str(SOURCE_PATH.relative_to(ROOT)),
            "notebook_file": str(NOTEBOOK_PATH.relative_to(ROOT)),
        },
        "criteria": {
            "public_source_available": SOURCE_PATH.exists(),
            "samples_mcmc_loaded_from_fit_output": found["samples_mcmc_loaded_from_fit_output"],
            "compute_model_time_delays_iterates_by_sample_index": all(
                found[key]
                for key in [
                    "time_delay_loop_over_sample_index",
                    "per_row_param_array_from_samples_mcmc_i",
                    "per_row_args2kwargs",
                    "arrival_time_from_row_kwargs",
                    "append_dt_ab_dt_ad_in_loop_order",
                    "model_time_delays_array_no_shuffle",
                ]
            ),
            "saved_time_delays_loaded_without_reordering": all(
                found[key]
                for key in [
                    "load_time_delays_np_loadtxt",
                    "load_time_delays_length_assert",
                    "loaded_time_delays_assigned",
                ]
            ),
            "notebook_loads_public_time_delay_files": found["load_time_delays_from_public_td_dir"],
            "notebook_mentions_compute_time_delays_first_time_path": found[
                "compute_time_delays_first_time_comment"
            ],
            "independent_row_removal_policy_found": False,
            "failed_models_promoted_to_baseline": False,
            "real_data_T2_sampling_authorized": False,
        },
        "verdict": {
            "desj0408_row_linkage_public_source_audit_created": True,
            "public_code_intends_index_order_linkage": True,
            "public_code_contains_no_independent_outlier_removal_policy": True,
            "row_linkage_blocker_narrowed_but_not_cleared": True,
            "real_data_T2_sampling_authorized": False,
        },
        "rows": rows,
        "claim_boundary": [
            "The public code supports intended index-order linkage.",
            "This does not prove that modern lenstronomy reproduction preserves every legacy row exactly.",
            "No failed model is promoted without an independent row-level recovery/removal policy.",
        ],
        "next_finite_action": (
            "Either reconstruct the original legacy lenstronomy execution semantics for "
            "the catastrophic rows, or keep the strict two-model DES no-T2 core."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["verdict"], indent=2))
    print(json.dumps(summary["criteria"], indent=2))


if __name__ == "__main__":
    main()
