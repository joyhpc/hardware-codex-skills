#!/usr/bin/env python3
"""Shared schema parsing helpers for hardware-codex-skills records.

This module holds the small protocol surface shared by linting and DAG
reporting. Keep lint policy, body-table scanning, and kind-specific checks in
the callers so this file remains a schema envelope helper rather than a second
linter.
"""

from __future__ import annotations

import datetime as dt
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("error: PyYAML required. pip install pyyaml\n")
    sys.exit(2)


SUPPORTED_SCHEMA_VERSIONS = {1}

DECISION_RECORD = "decision-record"
SELECTION_MAP = "selection-map"
PIN_ASSIGN = "pin-assign-workbench"

SUPPORTED_KINDS = {DECISION_RECORD, SELECTION_MAP, PIN_ASSIGN}

RELATED_RECORD_ROLES = {"sidecar", "source", "derived", "superseded"}

DECISION_RECORD_ID_RE = re.compile(r"^\d{8}-[a-z0-9][a-z0-9-]*$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)", re.DOTALL)


def split_frontmatter(text: str) -> tuple[dict, str] | None:
    text = text.lstrip("\ufeff")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    if not isinstance(meta, dict):
        return None
    return meta, m.group(2)


def parse_iso_date(value: object) -> dt.date | None:
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str) and ISO_DATE_RE.match(value):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def get_record_id(meta: dict) -> str | None:
    """Universal accessor; legacy decision_id supported on decision-record kind."""
    rid = meta.get("record_id")
    if rid:
        return rid
    if meta.get("schema_kind", DECISION_RECORD) == DECISION_RECORD:
        return meta.get("decision_id")
    return None
