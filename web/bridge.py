"""Thin web adapters over the repository's existing deterministic tools.

This module deliberately delegates core behavior to the existing command-line
scripts. It only handles temporary files, subprocess execution, and response
shaping for the local web app.
"""

from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


WEB_DIR = Path(__file__).resolve().parent
REPO_ROOT = WEB_DIR.parent

LINT_SCRIPT = REPO_ROOT / "tools" / "scripts" / "lint_record.py"
DAG_SCRIPT = REPO_ROOT / "tools" / "scripts" / "build_blocker_dag.py"
DOCTOR_SCRIPT = REPO_ROOT / "tools" / "scripts" / "doctor.py"
PIN_FORMATTER_SCRIPT = (
    REPO_ROOT / "pin-assign-workbench" / "scripts" / "format_pin_workbook.py"
)

EXAMPLE_RECORD_DIRS = [
    REPO_ROOT / "critical-component-selection" / "examples",
    REPO_ROOT / "pin-assign-workbench" / "examples",
]


@dataclass(frozen=True)
class InputFile:
    name: str
    content: bytes


def split_path_text(value: str | None) -> list[Path]:
    if not value:
        return []
    raw_items = re.split(r"[\r\n,]+", value)
    paths = []
    for item in raw_items:
        item = item.strip().strip('"')
        if item:
            paths.append(Path(item))
    return paths


def _safe_filename(name: str, fallback: str) -> str:
    stem = Path(name or fallback).name
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._")
    return stem or fallback


def _write_input_files(directory: Path, files: Iterable[InputFile]) -> list[Path]:
    written: list[Path] = []
    used: set[str] = set()
    for index, item in enumerate(files, start=1):
        name = _safe_filename(item.name, f"input-{index}.dat")
        if name in used:
            path_obj = Path(name)
            name = f"{path_obj.stem}-{index}{path_obj.suffix}"
        used.add(name)
        path = directory / name
        path.write_bytes(item.content)
        written.append(path)
    return written


def _display_command(command: list[str]) -> list[str]:
    result = []
    for part in command:
        try:
            path = Path(part)
        except TypeError:
            result.append(part)
            continue
        if path.is_absolute():
            try:
                result.append(str(path.relative_to(REPO_ROOT)))
            except ValueError:
                result.append(str(path))
        else:
            result.append(part)
    return result


def _run(command: list[str], *, timeout_seconds: int = 120) -> dict:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout_seconds,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "exit_code": 124,
            "stdout": exc.stdout or "",
            "stderr": (exc.stderr or "") + f"\nTimed out after {timeout_seconds}s.",
            "command": _display_command(command),
        }

    return {
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "command": _display_command(command),
    }


def _with_json_payload(result: dict) -> dict:
    payload = None
    if result["stdout"].strip():
        try:
            payload = json.loads(result["stdout"])
        except json.JSONDecodeError:
            payload = None
    result["json"] = payload
    return result


def lint_records(
    *,
    files: list[InputFile] | None = None,
    paths: list[Path] | None = None,
    strict: bool = False,
    strict_aging: bool = False,
    check_paths: bool = False,
    output_format: str = "json",
) -> dict:
    files = files or []
    paths = paths or []
    if not files and not paths:
        return {
            "exit_code": 2,
            "stdout": "",
            "stderr": "Provide at least one record file, pasted record, or server path.",
            "command": [],
            "json": None,
        }

    with tempfile.TemporaryDirectory(prefix="hardware-web-lint-") as tmp:
        tmp_path = Path(tmp)
        input_paths = _write_input_files(tmp_path, files) + paths
        command = [
            sys.executable,
            str(LINT_SCRIPT),
            *[str(path) for path in input_paths],
            "--format",
            output_format,
        ]
        if strict:
            command.append("--strict")
        if strict_aging:
            command.append("--strict-aging")
        if check_paths:
            command.append("--check-paths")
        result = _run(command)

    return _with_json_payload(result) if output_format == "json" else result


def build_dag(
    *,
    files: list[InputFile] | None = None,
    paths: list[Path] | None = None,
    use_examples: bool = False,
    output_format: str = "json",
) -> dict:
    files = files or []
    paths = paths or []
    if use_examples:
        paths = [*paths, *EXAMPLE_RECORD_DIRS]
    if not files and not paths:
        return {
            "exit_code": 2,
            "stdout": "",
            "stderr": "Provide record files, server paths, or choose example records.",
            "command": [],
            "json": None,
        }

    with tempfile.TemporaryDirectory(prefix="hardware-web-dag-") as tmp:
        tmp_path = Path(tmp)
        temp_files = _write_input_files(tmp_path, files)
        dag_paths = paths
        if temp_files:
            dag_paths = [tmp_path, *dag_paths]
        command = [
            sys.executable,
            str(DAG_SCRIPT),
            *[str(path) for path in dag_paths],
            "--format",
            output_format,
        ]
        result = _run(command)

    return _with_json_payload(result) if output_format == "json" else result


def format_pin_workbook(
    *,
    workbook: InputFile | None = None,
    workbook_path: Path | None = None,
    net_columns: str | None = None,
    pin_columns: str | None = None,
    skip_sheets: str | None = None,
) -> dict:
    if workbook is None and workbook_path is None:
        return {
            "exit_code": 2,
            "stdout": "",
            "stderr": "Provide a workbook upload or server path.",
            "command": [],
            "filename": None,
            "content_base64": None,
        }

    with tempfile.TemporaryDirectory(prefix="hardware-web-workbook-") as tmp:
        tmp_path = Path(tmp)
        if workbook is not None:
            input_name = _safe_filename(workbook.name, "input.xlsx")
            input_path = tmp_path / input_name
            input_path.write_bytes(workbook.content)
        else:
            input_path = workbook_path
            input_name = Path(str(workbook_path)).name

        output_name = f"{Path(input_name).stem}-formatted.xlsx"
        output_path = tmp_path / output_name
        command = [
            sys.executable,
            str(PIN_FORMATTER_SCRIPT),
            str(input_path),
            str(output_path),
        ]
        if net_columns:
            command.extend(["--net-columns", net_columns])
        if pin_columns:
            command.extend(["--pin-columns", pin_columns])
        if skip_sheets:
            command.extend(["--skip-sheets", skip_sheets])

        result = _run(command)
        if result["exit_code"] == 0 and output_path.exists():
            result["filename"] = output_name
            result["content_base64"] = base64.b64encode(output_path.read_bytes()).decode(
                "ascii"
            )
        else:
            result["filename"] = None
            result["content_base64"] = None
        return result


def run_doctor() -> dict:
    command = [sys.executable, str(DOCTOR_SCRIPT)]
    return _run(command, timeout_seconds=240)
