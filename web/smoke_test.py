"""Smoke tests for the optional web adapter layer.

Run from the repository root:

    python web/smoke_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

import bridge
import run as web_run
from app import app


def _assert_ok(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"{name} failed. {detail}".strip())
    print(f"PASS {name}")


def main() -> int:
    client = TestClient(app)

    health = client.get("/api/health")
    _assert_ok("health endpoint", health.status_code == 200, health.text)
    _assert_ok("health payload", health.json().get("ok") is True)

    example = bridge.REPO_ROOT / "critical-component-selection" / "examples" / (
        "example-decision-record.md"
    )
    lint_result = bridge.lint_records(
        files=[
            bridge.InputFile(
                name=example.name,
                content=example.read_bytes(),
            )
        ],
        output_format="json",
    )
    _assert_ok("lint bridge", lint_result["exit_code"] == 0, lint_result["stderr"])
    _assert_ok("lint json payload", lint_result["json"] is not None)

    lint_response = client.post(
        "/api/lint",
        data={"record_text": example.read_text(encoding="utf-8")},
    )
    _assert_ok("lint endpoint", lint_response.status_code == 200, lint_response.text)
    _assert_ok("lint endpoint exit", lint_response.json()["exit_code"] == 0)

    dag_result = bridge.build_dag(use_examples=True, output_format="json")
    _assert_ok("dag bridge", dag_result["exit_code"] == 0, dag_result["stderr"])
    _assert_ok("dag json payload", dag_result["json"] is not None)

    dag_response = client.post(
        "/api/dag",
        data={"use_examples": "true", "output_format": "json"},
    )
    _assert_ok("dag endpoint", dag_response.status_code == 200, dag_response.text)
    _assert_ok("dag endpoint exit", dag_response.json()["exit_code"] == 0)

    workbook = bridge.REPO_ROOT / "pin-assign-workbench" / "assets" / (
        "pin-assign-template.xlsx"
    )
    workbook_result = bridge.format_pin_workbook(
        workbook=bridge.InputFile(
            name=workbook.name,
            content=workbook.read_bytes(),
        )
    )
    _assert_ok(
        "workbook bridge",
        workbook_result["exit_code"] == 0,
        workbook_result["stderr"],
    )
    _assert_ok("workbook output", bool(workbook_result["content_base64"]))

    workbook_response = client.post(
        "/api/format-pin-workbook",
        files={
            "workbook": (
                workbook.name,
                workbook.read_bytes(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    _assert_ok(
        "workbook endpoint",
        workbook_response.status_code == 200,
        workbook_response.text,
    )
    _assert_ok("workbook endpoint exit", workbook_response.json()["exit_code"] == 0)
    _assert_ok("workbook endpoint output", bool(workbook_response.json()["content_base64"]))

    port = web_run.find_available_port()
    _assert_ok("port picker", isinstance(port, int) and port >= web_run.DEFAULT_PORT)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
