#!/usr/bin/env python3
"""Run the repository's local validation loop."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


CHECKS = [
    (
        "lint record tests",
        [sys.executable, "tools/tests/test_lint_record.py"],
    ),
    (
        "DAG builder tests",
        [sys.executable, "tools/tests/test_build_dag.py"],
    ),
    (
        "pin workbook formatter tests",
        [sys.executable, "pin-assign-workbench/tests/test_format_pin_workbook.py"],
    ),
    (
        "example record lint",
        [
            sys.executable,
            "tools/scripts/lint_record.py",
            "critical-component-selection/examples",
            "pin-assign-workbench/examples",
            "--format",
            "json",
        ],
    ),
    (
        "example DAG summary",
        [
            sys.executable,
            "tools/scripts/build_blocker_dag.py",
            "critical-component-selection/examples",
            "pin-assign-workbench/examples",
            "--format",
            "summary",
        ],
    ),
]


def run_check(name: str, command: list[str]) -> int:
    print(f"\n== {name} ==")
    print(" ".join(command))
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    if result.returncode == 0:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} (exit {result.returncode})")
    return result.returncode


def main() -> int:
    failures = []
    for name, command in CHECKS:
        rc = run_check(name, command)
        if rc != 0:
            failures.append(name)

    if failures:
        print("\nValidation failed:")
        for name in failures:
            print(f"- {name}")
        return 1

    print("\nAll validation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
