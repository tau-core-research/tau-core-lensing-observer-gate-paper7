import json
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper7_submission_source"
DATA = ROOT / "data/derived"
RESULTS = DATA / "repro_results"


def load_result(name: str) -> dict[str, object]:
    return json.loads((RESULTS / name / "summary.json").read_text(encoding="utf-8"))


def test_publication_files_exist():
    required = [
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "CITATION.cff",
        ROOT / "DATA_NOTICE.md",
        ROOT / "requirements.txt",
        SOURCE / "main.tex",
        SOURCE / "refs.bib",
        SOURCE / "main.pdf",
        SOURCE / "figures",
        ROOT / "figures",
        ROOT / "scripts/build_arxiv_source.py",
        ROOT / "scripts/reproduce.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_paper_source_is_scoped_and_formula_renderable():
    source = (SOURCE / "main.tex").read_text(encoding="utf-8")
    assert "Testing the Tau-Core Observer Principle" in source
    assert "No real-data T2 posterior was sampled" in source
    assert "epsilon_\\tau\\pi_i|\\Delta\\phi_i|" in source
    assert "Tau Core is proven" not in source
    assert "\\includegraphics" in source
    assert (SOURCE / "refs.bib").exists()


def test_paper_critical_verdicts_match_summary_artifacts():
    public_deep = load_result("tau_core_lensing_public_deep_repository_search_v0")
    method = load_result("tau_core_lensing_public_only_method_validation_v0")
    blind = load_result("tau_core_lensing_synthetic_blind_challenge_expansion_v0_quick")
    noise_mc = load_result("tau_core_lensing_noise_failure_monte_carlo_cached_v0")
    joint = load_result("tau_core_lensing_joint_stress_grid_cached_v0")
    he0435 = load_result("tau_core_lensing_he0435_public_repro_model_level_psf_correction_fit_v0")
    static_closure = load_result("tau_core_lensing_static_control_branch_closure_v0")

    assert public_deep["carried_forward_verdict"] == "NO_PUBLIC_EVIDENCE_GRADE_TIME_DELAY_MODEL_PRODUCTS_FOUND"
    assert public_deep["evidence_grade_target_found"] is False
    assert method["evidence_status"] == "METHOD_ONLY_NOT_REAL_DATA_EVIDENCE"
    assert abs(float(method["t2_best_epsilon_hat"]) - 0.0499193089) <= 1e-12
    assert blind["strict_identified_count"] == 4
    assert abs(float(blind["max_abs_epsilon_error"]) - 0.00038902503227167956) <= 1e-15
    assert abs(float(noise_mc["stable_noise_max"]) - 0.008) <= 1e-15
    assert noise_mc["transition_noise_min"] == 0.01
    assert joint["stable_count"] == 6
    assert joint["transition_count"] == 2
    assert he0435["carried_forward_verdict"] == "HE0435_PUBLIC_REPRO_PSF_POLICY_EDGE_SEEKING_OR_RESIDUAL_FAILS"
    assert he0435["selected_hard_bound_solution_count"] == 6
    assert static_closure["verdict"] == "STATIC_CONTROL_BRANCH_CLOSED"
    assert static_closure["sampling_status"] == "BLOCKED"


def test_derived_tables_exist():
    required = [
        DATA / "public_deep_repository_target_status.csv",
        DATA / "he0435_public_repro_model_level_psf_validation.csv",
        DATA / "hff_static_control_scorecard.csv",
        DATA / "static_control_null_stress_sweep.csv",
        DATA / "static_control_report_card_gates.csv",
        DATA / "static_control_systematic_template_sweep.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_arxiv_source_package_exists_and_is_source_only():
    archive_path = ROOT / "arxiv_submission_source.zip"
    assert archive_path.exists()
    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())
    assert "main.tex" in names
    assert "refs.bib" in names
    assert "main.pdf" not in names
    assert "figures/fig01_observer_principle_lensing_schematic.png" in names
    assert not any(name.endswith((".aux", ".log", ".out", ".toc", ".blg", ".bbl")) for name in names)


def test_reproduction_script_reports_completion():
    result = subprocess.run(
        ["python", "scripts/build_arxiv_source.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "arxiv_submission_source.zip" in result.stdout
