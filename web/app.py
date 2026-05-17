"""FastAPI entry point for the local hardware-codex-skills web app."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import bridge


WEB_DIR = Path(__file__).resolve().parent
STATIC_DIR = WEB_DIR / "static"

app = FastAPI(title="hardware-codex-skills local web")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


async def _read_uploads(files: list[UploadFile] | None) -> list[bridge.InputFile]:
    result: list[bridge.InputFile] = []
    for item in files or []:
        content = await item.read()
        if content:
            result.append(bridge.InputFile(name=item.filename or "upload.dat", content=content))
    return result


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "repo_root": str(bridge.REPO_ROOT),
    }


@app.post("/api/lint")
async def api_lint(
    files: Annotated[list[UploadFile] | None, File()] = None,
    record_text: Annotated[str, Form()] = "",
    server_paths: Annotated[str, Form()] = "",
    strict: Annotated[bool, Form()] = False,
    strict_aging: Annotated[bool, Form()] = False,
    check_paths: Annotated[bool, Form()] = False,
) -> dict:
    input_files = await _read_uploads(files)
    if record_text.strip():
        input_files.append(
            bridge.InputFile(name="pasted-record.md", content=record_text.encode("utf-8"))
        )
    return bridge.lint_records(
        files=input_files,
        paths=bridge.split_path_text(server_paths),
        strict=strict,
        strict_aging=strict_aging,
        check_paths=check_paths,
        output_format="json",
    )


@app.post("/api/dag")
async def api_dag(
    files: Annotated[list[UploadFile] | None, File()] = None,
    server_paths: Annotated[str, Form()] = "",
    output_format: Annotated[str, Form()] = "json",
    use_examples: Annotated[bool, Form()] = False,
) -> dict:
    if output_format not in {"json", "summary", "mermaid"}:
        output_format = "json"
    return bridge.build_dag(
        files=await _read_uploads(files),
        paths=bridge.split_path_text(server_paths),
        use_examples=use_examples,
        output_format=output_format,
    )


@app.post("/api/format-pin-workbook")
async def api_format_pin_workbook(
    workbook: Annotated[UploadFile | None, File()] = None,
    server_path: Annotated[str, Form()] = "",
    net_columns: Annotated[str, Form()] = "",
    pin_columns: Annotated[str, Form()] = "",
    skip_sheets: Annotated[str, Form()] = "",
) -> dict:
    input_workbook = None
    if workbook is not None:
        content = await workbook.read()
        if content:
            input_workbook = bridge.InputFile(
                name=workbook.filename or "input.xlsx",
                content=content,
            )
    server_paths = bridge.split_path_text(server_path)
    return bridge.format_pin_workbook(
        workbook=input_workbook,
        workbook_path=server_paths[0] if server_paths else None,
        net_columns=net_columns.strip() or None,
        pin_columns=pin_columns.strip() or None,
        skip_sheets=skip_sheets.strip() or None,
    )


@app.post("/api/doctor")
def api_doctor() -> dict:
    return bridge.run_doctor()
