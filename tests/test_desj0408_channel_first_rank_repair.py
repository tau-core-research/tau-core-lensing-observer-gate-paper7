from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "data/derived/repro_results/tau_core_lensing_desj0408_channel_first_rank_repair_v1/summary.json"
CRR_A = ROOT / "data/derived/repro_results/tau_core_lensing_desj0408_crr_a_kinematic_conditioned_rank_v1/summary.json"


def test_channel_first_atlas_has_two_valid_and_one_forbidden_route():
    payload = json.loads(ATLAS.read_text(encoding="utf-8"))
    assert payload["source_manifest"]["delay_posterior_count"] == 24
    assert payload["source_manifest"]["velocity_dispersion_product_count"] == 480
    assert len(payload["source_manifest"]["imaging"]) == 3
    assert payload["priority"] == ["CRR-A", "CRR-B"]
    assert payload["routes"][2]["role"] == "forbidden_false_rank_repair"


def test_kinematic_conditioning_preserves_negative_rank_repair_result():
    payload = json.loads(CRR_A.read_text(encoding="utf-8"))
    assert payload["freeze_policy"]["uses_observed_delay_values_for_conditioning"] is False
    assert payload["freeze_policy"]["fits_or_classifies_time_quantum_other_channel_origin"] is False
    assert payload["source_counts"]["delay_samples"] == 240000
    assert payload["rank_repair"]["exact_delay_nuisance_rank_reduced"] is False
    assert payload["rank_repair"]["practical_5pct_rank_reduced"] is False
    assert payload["verdict"] == "CRR_A_KINEMATIC_CONDITIONING_DOES_NOT_REPAIR_DELAY_RANK"
