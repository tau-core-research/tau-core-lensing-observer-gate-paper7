#!/usr/bin/env python3
"""Build the Paper 7 arXiv-oriented LaTeX source package."""

from __future__ import annotations

import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper7_submission_source"
ZIP_PATH = ROOT / "arxiv_submission_source.zip"
EXCLUDED_SUFFIXES = {".aux", ".log", ".out", ".toc", ".blg", ".bbl", ".synctex.gz"}


def should_include(path: Path) -> bool:
    if path.name == "main.pdf":
        return False
    if any(str(path).endswith(suffix) for suffix in EXCLUDED_SUFFIXES):
        return False
    return path.is_file()


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(SOURCE.rglob("*")):
            if should_include(path):
                archive.write(path, path.relative_to(SOURCE).as_posix())
    print(f"wrote {ZIP_PATH}")


if __name__ == "__main__":
    main()
