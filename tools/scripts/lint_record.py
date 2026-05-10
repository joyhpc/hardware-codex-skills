#!/usr/bin/env python3
"""Lint records produced by skills in this repository.

Validates schema_version=1 records of any registered schema_kind:
    - decision-record
    - selection-map
    - pin-assign-workbench

See ../SCHEMA.md for the full rule reference.

Exit codes:
    0  all checks pass (warnings allowed unless --strict)
    1  lint violations
    2  file or parse error, or unsupported schema_version
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Iterable

try:
    import yaml
except ImportError:
    sys.stderr.write("error: PyYAML required. pip install pyyaml\n")
    sys.exit(2)


# ============================================================
# Schema constants (mirror SCHEMA.md)
# ============================================================

SUPPORTED_SCHEMA_VERSIONS = {1}

DECISION_RECORD = "decision-record"
SELECTION_MAP = "selection-map"
PIN_ASSIGN = "pin-assign-workbench"

SUPPORTED_KINDS = {DECISION_RECORD, SELECTION_MAP, PIN_ASSIGN}

# Status enums per kind
STATUS_BY_KIND = {
    DECISION_RECORD: {
        "draft", "shortlisted", "selected-not-frozen",
        "frozen", "blocked", "superseded",
    },
    SELECTION_MAP: {"active", "stale", "closed"},
    PIN_ASSIGN: {"draft", "source-locked", "mechanical-checked",
                 "reviewed", "exported"},
}

EVIDENCE_STATUS = {
    "confirmed", "TBD-evidence", "conflict", "N-A", "stale-evidence",
}
GATE_STATUS = {"pass", "blocked", "TBD-evidence", "N-A"}
MECH_CHECK_STATUS = {"pass", "blocked", "TBD-evidence", "N-A"}

ALL_BODY_STATUS_TOKENS = (
    EVIDENCE_STATUS
    | GATE_STATUS
    | STATUS_BY_KIND[DECISION_RECORD]
    | STATUS_BY_KIND[SELECTION_MAP]
    | STATUS_BY_KIND[PIN_ASSIGN]
)

RELATED_RECORD_ROLES = {"sidecar", "source", "derived", "superseded"}

UNIVERSAL_REQUIRED = (
    "schema_version", "record_id", "project", "revision",
    "status", "created_date",
)

DECISION_RECORD_ID_RE = re.compile(r"^\d{8}-[a-z0-9][a-z0-9-]*$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

DEFAULT_EVIDENCE_FRESHNESS_DAYS = 60


# ============================================================
# Result types
# ============================================================

@dataclass
class LintIssue:
    level: str          # "error" | "warning"
    rule: str
    location: str
    message: str


@dataclass
class LintResult:
    path: str = ""
    schema_kind: str | None = None
    record_id: str | None = None
    issues: list[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[LintIssue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> list[LintIssue]:
        return [i for i in self.issues if i.level == "warning"]

    def add(self, level: str, rule: str, location: str, message: str) -> None:
        self.issues.append(LintIssue(level, rule, location, message))


# ============================================================
# Parsing
# ============================================================

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)", re.DOTALL)


def split_frontmatter(text: str) -> tuple[dict, str] | None:
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


def _parse_iso_date(value: object) -> dt.date | None:
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str) and ISO_DATE_RE.match(value):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


# ============================================================
# Backward compatibility for record_id / decision_id
# ============================================================

def get_record_id(meta: dict) -> str | None:
    """Universal accessor; legacy decision_id supported on decision-record kind."""
    rid = meta.get("record_id")
    if rid:
        return rid
    if meta.get("schema_kind", DECISION_RECORD) == DECISION_RECORD:
        return meta.get("decision_id")
    return None


# ============================================================
# Universal envelope rules (FM*, EN*)
# ============================================================

def check_schema_version(meta: dict, r: LintResult) -> bool:
    v = meta.get("schema_version")
    if v is None:
        r.add("error", "FM001", "frontmatter:schema_version",
              "missing required field: schema_version")
        return False
    if v not in SUPPORTED_SCHEMA_VERSIONS:
        r.add("error", "FM999", "frontmatter:schema_version",
              f"unsupported schema_version={v}; "
              f"supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)}")
        return False
    return True


def check_schema_kind(meta: dict, r: LintResult) -> str:
    kind = meta.get("schema_kind")
    if kind is None:
        r.add("warning", "FM010", "frontmatter:schema_kind",
              f"schema_kind not set; defaulting to '{DECISION_RECORD}'")
        return DECISION_RECORD
    if kind not in SUPPORTED_KINDS:
        r.add("error", "FM997", "frontmatter:schema_kind",
              f"unknown schema_kind '{kind}'; supported: {sorted(SUPPORTED_KINDS)}")
        return ""
    return kind


def check_envelope_required(meta: dict, r: LintResult) -> None:
    # record_id check tolerates legacy decision_id
    rid = get_record_id(meta)
    if rid is None:
        r.add("error", "FM001", "frontmatter:record_id",
              "missing required field: record_id")

    for f in UNIVERSAL_REQUIRED:
        if f == "record_id":
            continue  # handled above with legacy fallback
        if f not in meta:
            r.add("error", "FM001", f"frontmatter:{f}",
                  f"missing required field: {f}")


def check_record_id_pattern(meta: dict, r: LintResult) -> None:
    rid = get_record_id(meta)
    if rid is None:
        return
    if not DECISION_RECORD_ID_RE.match(str(rid)):
        r.add("error", "FM002", "frontmatter:record_id",
              f"record_id '{rid}' must match YYYYMMDD-<lowercase-slug>")


def check_kind_status_enum(meta: dict, kind: str, r: LintResult) -> None:
    status = meta.get("status")
    if status is None:
        return
    allowed = STATUS_BY_KIND.get(kind, set())
    if status not in allowed:
        r.add("error", "FM003", "frontmatter:status",
              f"status '{status}' not in {sorted(allowed)} for kind '{kind}'")


def check_envelope_dates(meta: dict, r: LintResult) -> None:
    for k in ("created_date", "review_date", "freeze_target_date"):
        v = meta.get(k)
        if v is None:
            continue
        if _parse_iso_date(v) is None:
            r.add("error", "FM005", f"frontmatter:{k}",
                  f"{k}='{v}' must be ISO date YYYY-MM-DD")


def check_envelope_consistency(meta: dict, r: LintResult) -> None:
    """EN* rules: cross-field envelope consistency."""
    rev = meta.get("revision")
    sup = meta.get("supersedes")
    sup_by = meta.get("superseded_by")
    status = meta.get("status")

    if isinstance(rev, int) and rev > 1 and not sup:
        r.add("error", "EN001", "frontmatter:supersedes",
              f"revision={rev} requires supersedes to be non-null")

    created = _parse_iso_date(meta.get("created_date"))
    review = _parse_iso_date(meta.get("review_date"))
    if created and review and review < created:
        r.add("error", "EN002", "frontmatter:review_date",
              f"review_date {review} precedes created_date {created}")

    if sup_by and status != "superseded":
        r.add("error", "EN003", "frontmatter:superseded_by",
              f"superseded_by set but status='{status}' (expected 'superseded')")
    if status == "superseded" and not sup_by:
        r.add("error", "EN003", "frontmatter:superseded_by",
              "status=superseded requires superseded_by")


def check_related_records(meta: dict, r: LintResult) -> None:
    rels = meta.get("related_records") or []
    if not isinstance(rels, list):
        r.add("error", "EN010", "frontmatter:related_records",
              "related_records must be a list")
        return
    for i, rel in enumerate(rels):
        if not isinstance(rel, dict):
            r.add("error", "EN010", f"frontmatter:related_records[{i}]",
                  "must be a mapping with kind/id/role")
            continue
        kind = rel.get("kind")
        rid = rel.get("id")
        role = rel.get("role")
        if kind not in SUPPORTED_KINDS:
            r.add("error", "EN011", f"frontmatter:related_records[{i}].kind",
                  f"kind '{kind}' not in {sorted(SUPPORTED_KINDS)}")
        if not rid or not DECISION_RECORD_ID_RE.match(str(rid)):
            r.add("error", "EN012", f"frontmatter:related_records[{i}].id",
                  f"id '{rid}' must match YYYYMMDD-<slug>")
        if role not in RELATED_RECORD_ROLES:
            r.add("error", "EN013", f"frontmatter:related_records[{i}].role",
                  f"role '{role}' not in {sorted(RELATED_RECORD_ROLES)}")


# ============================================================
# decision-record validator (CR*, DR*)
# ============================================================

def validate_decision_record(meta: dict, body: str, r: LintResult) -> None:
    _check_evidence_status_in_candidates(meta, r)
    _check_decision_status_consistency(meta, r)
    _check_blocker_due_dates(meta, r)


def _check_evidence_status_in_candidates(meta: dict, r: LintResult) -> None:
    pri = meta.get("primary_candidate") or {}
    if isinstance(pri, dict):
        es = pri.get("evidence_status")
        if es is not None and es not in EVIDENCE_STATUS:
            r.add("error", "DR001",
                  "frontmatter:primary_candidate.evidence_status",
                  f"evidence_status '{es}' not in {sorted(EVIDENCE_STATUS)}")
    backups = meta.get("backup_candidates") or []
    if isinstance(backups, list):
        for i, c in enumerate(backups):
            if not isinstance(c, dict):
                continue
            es = c.get("evidence_status")
            if es is not None and es not in EVIDENCE_STATUS:
                r.add("error", "DR001",
                      f"frontmatter:backup_candidates[{i}].evidence_status",
                      f"evidence_status '{es}' not in {sorted(EVIDENCE_STATUS)}")


def _check_decision_status_consistency(meta: dict, r: LintResult) -> None:
    status = meta.get("status")
    blockers = meta.get("freeze_blockers") or []

    if status == "frozen" and blockers:
        r.add("error", "CR001", "frontmatter:status",
              f"status=frozen requires empty freeze_blockers; "
              f"{len(blockers)} blocker(s) present")
    if status == "selected-not-frozen" and not blockers:
        r.add("warning", "CR002", "frontmatter:status",
              "status=selected-not-frozen with no freeze_blockers — "
              "consider promoting to frozen or adding blockers")


def _check_blocker_due_dates(meta: dict, r: LintResult) -> None:
    today = dt.date.today()
    blockers = meta.get("freeze_blockers") or []
    if not isinstance(blockers, list):
        return
    status = meta.get("status")
    if status == "frozen":
        return
    for i, b in enumerate(blockers):
        if not isinstance(b, dict):
            continue
        due = _parse_iso_date(b.get("due_date"))
        if due and due < today:
            r.add("warning", "CR004",
                  f"frontmatter:freeze_blockers[{i}].due_date",
                  f"due_date {due} is in the past")


# ============================================================
# selection-map validator (SM*)
# ============================================================

def validate_selection_map(meta: dict, body: str, r: LintResult) -> None:
    if "decision_record" not in meta or not meta["decision_record"]:
        r.add("error", "SM001", "frontmatter:decision_record",
              "selection-map requires decision_record reference (record_id)")
    else:
        dr = meta["decision_record"]
        if not DECISION_RECORD_ID_RE.match(str(dr)):
            r.add("error", "SM001", "frontmatter:decision_record",
                  f"decision_record '{dr}' must match YYYYMMDD-<slug>")


def check_selection_map_heuristic(decision_meta: dict, r: LintResult) -> None:
    """SM010: warn when a decision-record probably needs a selection map."""
    blockers = len(decision_meta.get("freeze_blockers") or [])
    backups = len(decision_meta.get("backup_candidates") or [])
    if blockers >= 3 or backups >= 3:
        rels = decision_meta.get("related_records") or []
        has_map = any(
            isinstance(rel, dict) and rel.get("kind") == SELECTION_MAP
            for rel in rels
        )
        if not has_map:
            r.add("warning", "SM010", "frontmatter:related_records",
                  f"complexity heuristic ({blockers} blockers, {backups} backups) "
                  f"recommends a selection-map sidecar; none referenced")


# ============================================================
# pin-assign-workbench validator (PA*)
# ============================================================

def validate_pin_assign(meta: dict, body: str, r: LintResult,
                         check_paths: bool = False,
                         base_dir: Path | None = None) -> None:
    workbook = meta.get("workbook_path")
    if not workbook:
        r.add("error", "PA000", "frontmatter:workbook_path",
              "pin-assign-workbench requires workbook_path")
    elif check_paths and base_dir is not None:
        wb_path = (base_dir / workbook).resolve()
        if not wb_path.exists():
            r.add("error", "PA001", "frontmatter:workbook_path",
                  f"workbook_path does not exist: {wb_path}")

    sched_target = meta.get("schematic_target")
    allowed_targets = {"orcad", "cadence-cis", "allegro-de-hdl"}
    if sched_target and sched_target not in allowed_targets:
        r.add("error", "PA010", "frontmatter:schematic_target",
              f"schematic_target '{sched_target}' not in {sorted(allowed_targets)}")

    mech = meta.get("mechanical_check_status")
    if mech is not None and mech not in MECH_CHECK_STATUS:
        r.add("error", "PA011", "frontmatter:mechanical_check_status",
              f"mechanical_check_status '{mech}' not in {sorted(MECH_CHECK_STATUS)}")

    status = meta.get("status")
    if status in ("mechanical-checked", "reviewed", "exported"):
        if mech != "pass":
            r.add("error", "PA002", "frontmatter:mechanical_check_status",
                  f"status='{status}' requires mechanical_check_status=pass; got '{mech}'")

    conflicts = meta.get("unresolved_source_conflicts") or []
    if status == "exported" and conflicts:
        r.add("error", "PA003", "frontmatter:unresolved_source_conflicts",
              f"status=exported requires empty unresolved_source_conflicts; "
              f"{len(conflicts)} present")

    src_recs = meta.get("source_records") or []
    if not src_recs:
        r.add("warning", "PA020", "frontmatter:source_records",
              "pin-assign-workbench has no source_records; "
              "downstream traceability is reduced")


# ============================================================
# Body table scanners (BD*)
# ============================================================

TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|[\s\-:|]+\|\s*$")


def _split_row(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def _iter_tables(body: str) -> Iterable[tuple[int, list[str], list[tuple[int, list[str]]]]]:
    """Yield (start_line, header_cells, [(line_no, row_cells), ...])."""
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        if (TABLE_ROW_RE.match(lines[i])
                and i + 1 < len(lines)
                and TABLE_SEP_RE.match(lines[i + 1])):
            header = _split_row(lines[i])
            j = i + 2
            rows: list[tuple[int, list[str]]] = []
            while (j < len(lines)
                   and TABLE_ROW_RE.match(lines[j])
                   and not TABLE_SEP_RE.match(lines[j])):
                rows.append((j + 1, _split_row(lines[j])))
                j += 1
            yield i + 1, header, rows
            i = j
        else:
            i += 1


def _column_index(header: list[str], name: str) -> int | None:
    for idx, cell in enumerate(header):
        if cell.lower() == name.lower():
            return idx
    return None


def scan_body_status_columns(body: str, r: LintResult) -> None:
    """BD001: status cells must use the closed enum union."""
    for _hdr_line, header, rows in _iter_tables(body):
        status_idx = _column_index(header, "status")
        if status_idx is None:
            continue
        for line_no, cells in rows:
            if status_idx >= len(cells):
                continue
            val = cells[status_idx]
            if val and val not in ALL_BODY_STATUS_TOKENS:
                r.add("error", "BD001", f"line:{line_no}",
                      f"status cell '{val}' not in any allowed enum")


def scan_body_evidence_aging(body: str, meta: dict, r: LintResult,
                              strict_aging: bool = False) -> None:
    """BD002: confirmed evidence rows older than the freshness window."""
    window_days = meta.get(
        "evidence_freshness_window_days",
        DEFAULT_EVIDENCE_FRESHNESS_DAYS,
    )
    if not isinstance(window_days, int) or window_days <= 0:
        return

    created = _parse_iso_date(meta.get("created_date"))
    if created is None:
        return
    cutoff = created - dt.timedelta(days=window_days)

    for _hdr_line, header, rows in _iter_tables(body):
        status_idx = _column_index(header, "status")
        date_idx = _column_index(header, "evidence date")
        if status_idx is None or date_idx is None:
            continue
        for line_no, cells in rows:
            if status_idx >= len(cells) or date_idx >= len(cells):
                continue
            status = cells[status_idx]
            ev_date = _parse_iso_date(cells[date_idx])
            if status == "confirmed" and ev_date and ev_date < cutoff:
                age = (created - ev_date).days
                level = "error" if strict_aging else "warning"
                r.add(level, "BD002", f"line:{line_no}",
                      f"confirmed evidence dated {ev_date} is {age} days old "
                      f"(window={window_days}); consider re-verification "
                      f"or mark as stale-evidence")


# ============================================================
# Main lint flow
# ============================================================

def lint_text(text: str, *, strict_aging: bool = False,
              check_paths: bool = False,
              base_dir: Path | None = None) -> LintResult:
    r = LintResult()
    parsed = split_frontmatter(text)
    if parsed is None:
        r.add("error", "FM000", "file",
              "no valid YAML frontmatter found between leading --- markers")
        return r
    meta, body = parsed

    if not check_schema_version(meta, r):
        return r

    kind = check_schema_kind(meta, r)
    if not kind:
        return r
    r.schema_kind = kind
    r.record_id = get_record_id(meta)

    check_envelope_required(meta, r)
    check_record_id_pattern(meta, r)
    check_kind_status_enum(meta, kind, r)
    check_envelope_dates(meta, r)
    check_envelope_consistency(meta, r)
    check_related_records(meta, r)

    # Kind-specific
    if kind == DECISION_RECORD:
        validate_decision_record(meta, body, r)
        check_selection_map_heuristic(meta, r)
    elif kind == SELECTION_MAP:
        validate_selection_map(meta, body, r)
    elif kind == PIN_ASSIGN:
        validate_pin_assign(meta, body, r,
                            check_paths=check_paths, base_dir=base_dir)

    # Body scanners (universal)
    scan_body_status_columns(body, r)
    scan_body_evidence_aging(body, meta, r, strict_aging=strict_aging)

    return r


# ============================================================
# Stamp on success
# ============================================================

def stamp_lint_pass(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    parsed = split_frontmatter(text)
    if parsed is None:
        return
    meta, body = parsed
    meta["last_lint_pass"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    new_fm = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True)
    path.write_text(f"---\n{new_fm}---\n{body}", encoding="utf-8")


# ============================================================
# Output formatters
# ============================================================

def format_human(path: Path, result: LintResult, ok: bool, stamped: bool) -> str:
    lines = []
    for issue in result.issues:
        lines.append(
            f"{path}:{issue.location} [{issue.rule}] {issue.level}: {issue.message}"
        )
    suffix = " (stamped)" if stamped else ""
    if ok:
        lines.append(f"{path}: OK{suffix}")
    return "\n".join(lines)


def format_json_payload(file_results: list[tuple[Path, LintResult, bool]],
                         exit_code: int) -> dict:
    return {
        "schema_version": 1,
        "files": [
            {
                "path": str(p),
                "schema_kind": r.schema_kind,
                "record_id": r.record_id,
                "ok": ok,
                "issues": [asdict(i) for i in r.issues],
            }
            for p, r, ok in file_results
        ],
        "exit_code": exit_code,
    }


# ============================================================
# CLI driver
# ============================================================

def expand_paths(paths: Iterable[Path]) -> list[Path]:
    expanded: list[Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(sorted(path.rglob("*.md")))
        else:
            expanded.append(path)
    return expanded


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", type=Path,
                    help="record files to lint")
    ap.add_argument("--stamp", action="store_true",
                    help="update last_lint_pass on success")
    ap.add_argument("--strict", action="store_true",
                    help="treat all warnings as errors")
    ap.add_argument("--strict-aging", action="store_true",
                    help="treat BD002 evidence-aging warnings as errors")
    ap.add_argument("--check-paths", action="store_true",
                    help="verify referenced files exist (e.g. workbook_path)")
    ap.add_argument("--format", choices=("human", "json"),
                    default="human", help="output format")
    args = ap.parse_args(argv)

    file_results: list[tuple[Path, LintResult, bool]] = []
    parse_failures = 0
    error_count = 0

    for path in expand_paths(args.paths):
        if not path.exists():
            if args.format == "human":
                print(f"{path}: file not found", file=sys.stderr)
            parse_failures += 1
            r = LintResult(path=str(path))
            r.add("error", "FM998", "file", "file not found")
            file_results.append((path, r, False))
            continue

        text = path.read_text(encoding="utf-8")
        result = lint_text(
            text,
            strict_aging=args.strict_aging,
            check_paths=args.check_paths,
            base_dir=path.parent,
        )
        result.path = str(path)

        had_errors = bool(result.errors)
        had_warnings = bool(result.warnings)
        effective_fail = had_errors or (args.strict and had_warnings)

        ok = not effective_fail
        stamped = False
        if ok and args.stamp:
            stamp_lint_pass(path)
            stamped = True

        if not ok:
            error_count += 1

        if args.format == "human":
            print(format_human(path, result, ok, stamped))

        file_results.append((path, result, ok))

    if parse_failures:
        exit_code = 2
    elif error_count:
        exit_code = 1
    else:
        exit_code = 0

    if args.format == "json":
        print(json.dumps(format_json_payload(file_results, exit_code),
                         indent=2, ensure_ascii=False))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
