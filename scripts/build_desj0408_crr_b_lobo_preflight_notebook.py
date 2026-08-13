#!/usr/bin/env python3
"""Build leakage-guarded DES J0408 leave-one-band-out preflight notebooks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography/notebooks/DESJ0408 Multiband Image Modeling.ipynb"
OUT = ROOT / "data/derived/repro_results/tau_core_lensing_desj0408_crr_b_lobo_preflight_v1"
FOLDS = {
    "F814W": [False, True, True],
    "F475X": [True, False, True],
    "F160W": [True, True, False],
}


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"expected exactly one occurrence of {old!r}, found {count}")
    return text.replace(old, new)


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for heldout, compute in FOLDS.items():
        notebook = json.loads(json.dumps(source))
        notebook["cells"] = notebook["cells"][:35]

        for cell in notebook["cells"]:
            if cell.get("cell_type") == "code":
                cell_text = "".join(cell.get("source", []))
                cell_text = cell_text.replace("../data/alpha_s_distribution.npy", "../data/alpha_s_distribution")
                public_data = (
                    "/Volumes/EXTERNAL/Research/Tau Core/tau-core-lensing-observer-gate-paper7/"
                    "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography/data/"
                )
                cell_text = cell_text.replace("../data/", public_data)
                cell_text = cell_text.replace(
                    "                         'check_matched_source_position': False,\n",
                    "",
                )
                cell_text = cell_text.replace(
                    "                   'psf_error_map': psf_error_map,\n",
                    "                   # psf_error_map is profiled separately in the endpoint audit.\n",
                )
                cell_text = cell_text.replace(
                    "cwd = os.getcwd()\nbase_path, _ = os.path.split(cwd)",
                    "base_path = "
                    "'/Volumes/EXTERNAL/Research/Tau Core/tau-core-lensing-observer-gate-paper7/"
                    "data/external/source_candidate_repos/DESJ0408_time_delay_cosmography'\n"
                    "cwd = os.path.join(base_path, 'notebooks')",
                )
                cell["source"] = cell_text.splitlines(keepends=True)

        imports = "".join(notebook["cells"][3]["source"])
        imports = imports.replace("from paperfig import *\nset_fontscale(2)\n", "import matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\nimport seaborn as sns\ncmap = 'viridis'\nmsh_cmap = 'coolwarm'\n")
        notebook["cells"][3]["source"] = imports.splitlines(keepends=True)

        model = "".join(notebook["cells"][30]["source"])
        model = replace_once(
            model,
            "with open('known_solution.pickle', 'rb') as f:\n"
            "    kwargs_result_old = pickle.load(f)\n"
            "    \n"
            "initiate_from_old_result = kwargs_result_old # or None",
            "initiate_from_old_result = None # leakage guard: no full-three-band initialization",
        )
        model = replace_once(model, "reconstruct_psf = True", "reconstruct_psf = False")
        model = replace_once(model, "psf_iteration = True", "psf_iteration = False")
        model = replace_once(model, "n_p_short = 30", "n_p_short = 4")
        model = replace_once(model, "n_i_short = 20", "n_i_short = 1")
        model = replace_once(
            model,
            "    fitting_kwargs_list = []\n    # fix F160W band and first only fit the UVIS bands",
            "    fitting_kwargs_list = []\n"
            "    if not reconstruct_psf:\n"
            "        # Leakage-safe geometry preflight on the enabled training bands only.\n"
            "        fitting_kwargs_list.append(['PSO', {'sigma_scale': 1., 'n_particles': n_p, "
            "'n_iterations': n_i, 'threadCount': 1}])\n"
            "    # fix F160W band and first only fit the UVIS bands",
        )
        band_switch = "'bands_compute': [True, True, True]"
        if model.count(band_switch) != 2:
            raise ValueError(f"expected two band-switch branches, found {model.count(band_switch)}")
        model = model.replace(band_switch, f"'bands_compute': {compute}")
        notebook["cells"][30]["source"] = model.splitlines(keepends=True)

        cluster = "".join(notebook["cells"][32]["source"])
        cluster = replace_once(cluster, "if True:", "if False:")
        notebook["cells"][32]["source"] = cluster.splitlines(keepends=True)

        local = "".join(notebook["cells"][34]["source"])
        local = replace_once(local, "job_name = 'test'", f"job_name = 'tau_core_crr_b_lobo_{heldout.lower()}_preflight'")
        local = local.replace("subgrid_res=3,", "subgrid_res=1,")
        local += f"\nprint('CRR_B_LOBO_PREFLIGHT_COMPLETE heldout={heldout} bands_compute={compute}')\n"
        notebook["cells"][34]["source"] = local.splitlines(keepends=True)

        for cell in notebook["cells"]:
            if cell.get("cell_type") == "code":
                cell["execution_count"] = None
                cell["outputs"] = []

        path = OUT / f"desj0408_crr_b_lobo_{heldout.lower()}_preflight.ipynb"
        path.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
        manifest.append({
            "heldout_band": heldout,
            "bands_compute": compute,
            "notebook": str(path.relative_to(ROOT)),
            "full_three_band_initialization_allowed": False,
            "heldout_psf_optimization_allowed": False,
            "bounded_pso_particles": 4,
            "bounded_pso_iterations": 1,
        })

    payload = {
        "schema": "paper7 DES J0408 CRR-B LOBO preflight notebook manifest v1",
        "source_notebook": str(SOURCE.relative_to(ROOT)),
        "folds": manifest,
        "preflight_only": True,
        "heldout_pixels_opened_by_builder": False,
        "channel_effect_test_authorized": False,
        "verdict": "CRR_B_THREE_LEAKAGE_GUARDED_PREFLIGHT_NOTEBOOKS_BUILT",
    }
    (OUT / "manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(payload["verdict"])


if __name__ == "__main__":
    main()
