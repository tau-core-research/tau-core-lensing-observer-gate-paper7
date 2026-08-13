from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_desj0408_full24_md1_f1_rank.py"
SUMMARY = ROOT / "data/derived/repro_results/tau_core_lensing_desj0408_full24_md1_f1_rank_v1/summary.json"


def load_module():
    spec = importlib.util.spec_from_file_location("md1_rank", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_span_audit_distinguishes_rank_one_and_rank_two():
    module = load_module()
    rank_one = np.array([[0.0, 0.0], [1.0, 2.0], [2.0, 4.0], [3.0, 6.0]])
    rank_two = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    assert module.span_audit(rank_one)["strict_rank"] == 1
    assert module.span_audit(rank_one)["orthogonal_complement_dimension"] == 1
    assert module.span_audit(rank_two)["strict_rank"] == 2
    assert module.span_audit(rank_two)["orthogonal_complement_dimension"] == 0


def test_frozen_public_artifact_preserves_no_go_claim_boundary():
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert payload["source_manifest"]["posterior_file_count"] == 24
    assert payload["source_manifest"]["total_samples"] == 240000
    assert payload["freeze_policy"]["uses_observed_delays_to_select_models_or_basis"] is False
    assert payload["freeze_policy"]["fits_or_samples_t2_or_tau_amplitude"] is False
    assert payload["rank_verdict"]["empirical_no_t2_nuisance_rank"] == 2
    assert payload["rank_verdict"]["covariance_whitened_no_t2_nuisance_rank"] == 2
    assert payload["rank_verdict"]["remaining_delay_only_f1_dimension"] == 0
    assert payload["rank_verdict"]["nuisance_residualized_f1_row_constructed"] is False
    assert payload["rank_verdict"]["practical_weak_direction_present_at_5pct"] is True
    assert payload["rank_verdict"]["practical_weak_direction_is_detection"] is False
    assert payload["verdict"] == "DESJ0408_DELAY_ONLY_STRUCTURAL_F1_NO_GO_WITH_PRACTICAL_WEAK_DIRECTION"
