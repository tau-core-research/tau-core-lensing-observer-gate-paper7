#!/usr/bin/env python3
"""One-command reproduction check for the Paper 7 public package."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper7_submission_source"


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    print("$ " + " ".join(cmd) + f"  # cwd={cwd}")
    subprocess.run(cmd, cwd=cwd, check=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if shutil.which("tectonic") is None:
        raise SystemExit("tectonic is required to compile paper7_submission_source/main.tex")
    run(["tectonic", "main.tex"], cwd=SOURCE)
    run([sys.executable, "scripts/build_arxiv_source.py"])
    run([sys.executable, "-m", "pytest", "-q"])
    pdf = SOURCE / "main.pdf"
    print(f"paper7_pdf_sha256: {sha256(pdf)}")
    print("PAPER7_LENSING_OBSERVER_GATE_REPRODUCTION_COMPLETE")


if __name__ == "__main__":
    main()
