import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_f814w_holdout_was_frozen_before_scoring():
    freeze = load(
        "data/derived/repro_results/"
        "tau_core_lensing_desj0408_crr_b_f814w_holdout_freeze_v1/summary.json"
    )
    assert freeze["heldout_image_values_read_by_freeze"] is False
    assert freeze["heldout_score_computed"] is False
    assert freeze["channel_effect_claim_allowed"] is False
    assert freeze["frozen_inputs"]["heldout_mask"]["active_pixels"] == 21115


def test_f814w_first_fold_is_negative_only_with_psf_nuisance_retained():
    score = load(
        "data/derived/repro_results/"
        "tau_core_lensing_desj0408_crr_b_f814w_holdout_score_v1/summary.json"
    )
    primary = score["primary_with_frozen_psf_uncertainty"]["reduced_chi2"]
    omitted = score["psf_uncertainty_omission_stress"]["reduced_chi2"]
    assert primary < 1.0
    assert omitted > 1.0
    assert score["channel_effect_candidate"] is False
    assert score["time_or_quantum_attribution_allowed"] is False
    assert score["status"] == "NEGATIVE_RESULT_PRESERVED"
