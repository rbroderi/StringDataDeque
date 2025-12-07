"""Cross-platform helper for running toml-sort on all project TOML files."""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
from collections.abc import Sequence

_EXCLUDED_DIRS = {".venv", ".tox"}


def _discover_files() -> list[str]:
    root = pathlib.Path()
    files: list[str] = []
    for path in root.rglob("*.toml"):
        if _EXCLUDED_DIRS.intersection(path.parts):
            continue
        files.append(str(path))
    files.sort()
    return files


def _run_tomlsort(extra_args: Sequence[str]) -> int:
    """Invoke ``toml-sort`` with the provided arguments."""
    cmd = ["toml-sort", *extra_args]
    completed = subprocess.run(cmd, check=False)  # noqa: S603
    return completed.returncode


def main() -> int:
    """Parse CLI args and run ``toml-sort`` in check or in-place mode."""
    parser = argparse.ArgumentParser(description="Run toml-sort across the repo")
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Apply changes in place instead of running in --check mode.",
    )
    args = parser.parse_args()

    files = _discover_files()
    if not files:
        return 0

    mode = ["-i"] if args.in_place else ["--check"]
    return _run_tomlsort([*mode, *files])


if __name__ == "__main__":
    sys.exit(main())
