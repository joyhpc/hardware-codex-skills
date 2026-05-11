"""Tests for tools/scripts/lint_record.py.

Run from repo root:

    python tools/tests/test_lint_record.py

Or with pytest:

    python -m pytest tools/tests/ -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT_DIR = REPO_ROOT / "tools" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import lint_record  # noqa: E402


def _rules(result):
    return {i.rule for i in result.issues}


# ============================================================
# Fixtures
# ============================================================

GOOD_DECISION = """---
schema_version: 1
schema_kind: decision-record
record_id: 20260510-test-component
project: test
revision: 1
status: selected-not-frozen
created_date: 2026-05-10
freeze_blockers:
  - id: fb-x
    field: lifecycle
    needed_evidence: pcn
    owner: procurement
    due_date: 2099-01-01
---

# Body

| Field | Status |
|---|---|
| lifecycle | TBD-evidence |
"""

GOOD_FROZEN_DECISION = """---
schema_version: 1
schema_kind: decision-record
record_id: 20260510-frozen-component
project: test
revision: 1
status: frozen
created_date: 2026-05-10
primary_candidate:
  pn: EXAMPLE-PN-A
  manufacturer: example
  evidence_status: confirmed
freeze_blockers: []
external_validation_skills_needed: []
---

# Body

## Hard Gate Screen

| Gate | Status |
|---|---|
| Exact orderable identity | pass |

## Source Inventory

| Source ID | Type | Title | Date | Path / URL | Trust level |
|---|---|---|---|---|---|
| S1 | datasheet | Example datasheet | 2026-05-09 | evidence/example.pdf | primary |

## Evidence Matrix

| Field | Candidate | Evidence source | Evidence date | Status |
|---|---|---|---|---|
| Exact orderable identity | EXAMPLE-PN-A | S1 | 2026-05-09 | confirmed |
"""

GOOD_SELECTION_MAP = """---
schema_version: 1
schema_kind: selection-map
record_id: 20260510-test-selection-map
project: test
revision: 1
status: active
created_date: 2026-05-10
decision_record: 20260510-test-component
related_records:
  - kind: decision-record
    id: 20260510-test-component
    role: sidecar
---

# Body
"""

GOOD_PIN_ASSIGN = """---
schema_version: 1
schema_kind: pin-assign-workbench
record_id: 20260520-test-pinout
project: test
revision: 1
status: draft
created_date: 2026-05-20
workbook_path: ./test.xlsx
schematic_target: orcad
mechanical_check_status: TBD-evidence
source_records:
  - kind: decision-record
    id: 20260510-test-component
    role: source
related_records:
  - kind: decision-record
    id: 20260510-test-component
    role: source
unresolved_source_conflicts: []
---

# Body
"""


# ============================================================
# Universal envelope (FM*, EN*)
# ============================================================

def test_decision_record_happy_path():
    r = lint_record.lint_text(GOOD_DECISION)
    assert not r.errors, f"unexpected errors: {[i.rule for i in r.errors]}"


def test_selection_map_happy_path():
    r = lint_record.lint_text(GOOD_SELECTION_MAP)
    assert not r.errors, f"unexpected errors: {[i.rule for i in r.errors]}"


def test_pin_assign_happy_path():
    r = lint_record.lint_text(GOOD_PIN_ASSIGN)
    assert not r.errors, f"unexpected errors: {[i.rule for i in r.errors]}"


def test_missing_schema_version():
    text = GOOD_DECISION.replace("schema_version: 1\n", "")
    r = lint_record.lint_text(text)
    assert "FM001" in _rules(r)


def test_unsupported_schema_version():
    text = GOOD_DECISION.replace("schema_version: 1", "schema_version: 99")
    r = lint_record.lint_text(text)
    assert "FM999" in _rules(r)


def test_missing_schema_kind_warns_not_errors():
    text = GOOD_DECISION.replace("schema_kind: decision-record\n", "")
    r = lint_record.lint_text(text)
    assert "FM010" in _rules(r)
    # default to decision-record, so the rest should still pass as decision-record
    fm010 = [i for i in r.issues if i.rule == "FM010"][0]
    assert fm010.level == "warning"


def test_unknown_schema_kind_errors():
    text = GOOD_DECISION.replace("schema_kind: decision-record",
                                  "schema_kind: not-a-real-kind")
    r = lint_record.lint_text(text)
    assert "FM997" in _rules(r)


def test_bad_record_id_pattern():
    text = GOOD_DECISION.replace("20260510-test-component", "BadID-2026")
    r = lint_record.lint_text(text)
    assert "FM002" in _rules(r)


def test_bad_status_for_kind():
    text = GOOD_DECISION.replace("status: selected-not-frozen",
                                  "status: active")  # active is selection-map status
    r = lint_record.lint_text(text)
    assert "FM003" in _rules(r)


def test_bad_date_format():
    text = GOOD_DECISION.replace("created_date: 2026-05-10",
                                  "created_date: 05/10/2026")
    r = lint_record.lint_text(text)
    assert "FM005" in _rules(r)


def test_review_before_created_fails():
    text = GOOD_DECISION.replace(
        "created_date: 2026-05-10",
        "created_date: 2026-05-10\nreview_date: 2026-01-01",
    )
    r = lint_record.lint_text(text)
    assert "EN002" in _rules(r)


def test_revision_gt_1_needs_supersedes():
    text = GOOD_DECISION.replace("revision: 1", "revision: 2")
    r = lint_record.lint_text(text)
    assert "EN001" in _rules(r)


def test_superseded_by_without_status_superseded():
    text = GOOD_DECISION.replace(
        "superseded_by: null" if "superseded_by" in GOOD_DECISION else "supersedes: null",
        "superseded_by: 20260101-old-record",
    ) if "supersedes:" in GOOD_DECISION else (
        GOOD_DECISION.replace(
            "freeze_blockers:",
            "superseded_by: 20260101-old-record\nfreeze_blockers:",
        )
    )
    r = lint_record.lint_text(text)
    assert "EN003" in _rules(r)


def test_status_superseded_without_pointer():
    text = GOOD_DECISION.replace("status: selected-not-frozen",
                                  "status: superseded")
    r = lint_record.lint_text(text)
    assert "EN003" in _rules(r)


def test_related_records_bad_kind():
    text = GOOD_DECISION.replace(
        "freeze_blockers:",
        "related_records:\n  - kind: bogus\n    id: 20260510-x\n    role: sidecar\nfreeze_blockers:",
    )
    r = lint_record.lint_text(text)
    assert "EN011" in _rules(r)


def test_related_records_bad_role():
    text = GOOD_DECISION.replace(
        "freeze_blockers:",
        "related_records:\n  - kind: decision-record\n    id: 20260510-x\n    role: friend\nfreeze_blockers:",
    )
    r = lint_record.lint_text(text)
    assert "EN013" in _rules(r)


# ============================================================
# decision-record (CR*, DR*)
# ============================================================

def test_frozen_with_blockers_fails():
    text = GOOD_DECISION.replace("status: selected-not-frozen", "status: frozen")
    r = lint_record.lint_text(text)
    assert "CR001" in _rules(r)


def test_selected_not_frozen_no_blockers_errors():
    text = """---
schema_version: 1
schema_kind: decision-record
record_id: 20260510-test-x
project: test
revision: 1
status: selected-not-frozen
created_date: 2026-05-10
freeze_blockers: []
---
body
"""
    r = lint_record.lint_text(text)
    assert "CR002" in _rules(r)
    fm = [i for i in r.issues if i.rule == "CR002"][0]
    assert fm.level == "error"


def test_past_blocker_due_errors_on_selected_not_frozen():
    text = GOOD_DECISION.replace("due_date: 2099-01-01", "due_date: 2020-01-01")
    r = lint_record.lint_text(text)
    assert "CR004" in _rules(r)
    cr004 = [i for i in r.issues if i.rule == "CR004"][0]
    assert cr004.level == "error"


def test_bad_evidence_status_in_candidate():
    text = GOOD_DECISION.replace(
        "freeze_blockers:",
        "primary_candidate:\n  pn: X\n  evidence_status: probably\nfreeze_blockers:",
    )
    r = lint_record.lint_text(text)
    assert "DR001" in _rules(r)


def test_stale_evidence_is_valid_enum_token():
    text = GOOD_DECISION.replace(
        "freeze_blockers:",
        "primary_candidate:\n  pn: X\n  evidence_status: stale-evidence\nfreeze_blockers:",
    )
    r = lint_record.lint_text(text)
    assert "DR001" not in _rules(r)


def test_frozen_happy_path_has_structural_body():
    r = lint_record.lint_text(GOOD_FROZEN_DECISION)
    assert not r.errors, f"unexpected errors: {[i.rule for i in r.errors]}"


def test_frozen_with_external_validation_fails():
    text = GOOD_FROZEN_DECISION.replace(
        "external_validation_skills_needed: []",
        "external_validation_skills_needed:\n  - skill: si-channel-budget\n    reason: close-si",
    )
    r = lint_record.lint_text(text)
    assert "CR005" in _rules(r)


def test_frozen_without_source_or_gate_body_fails():
    text = """---
schema_version: 1
schema_kind: decision-record
record_id: 20260510-empty-frozen
project: test
revision: 1
status: frozen
created_date: 2026-05-10
freeze_blockers: []
external_validation_skills_needed: []
---

# Empty body
"""
    r = lint_record.lint_text(text)
    assert "CR006" in _rules(r)


def test_body_blocked_gate_requires_frontmatter_blocker():
    text = """---
schema_version: 1
schema_kind: decision-record
record_id: 20260510-blocked-gate
project: test
revision: 1
status: selected-not-frozen
created_date: 2026-05-10
freeze_blockers: []
---

## Hard Gate Screen

| Gate | Status |
|---|---|
| Lifecycle / PCN / EOL | blocked |
"""
    r = lint_record.lint_text(text)
    assert "CR007" in _rules(r)


def test_confirmed_primary_requires_evidence_matrix_row():
    text = GOOD_FROZEN_DECISION.replace("EXAMPLE-PN-A | S1", "OTHER-PN | S1")
    r = lint_record.lint_text(text)
    assert "CR008" in _rules(r)


# ============================================================
# selection-map (SM*)
# ============================================================

def test_selection_map_missing_decision_record():
    text = GOOD_SELECTION_MAP.replace("decision_record: 20260510-test-component\n", "")
    r = lint_record.lint_text(text)
    assert "SM001" in _rules(r)


def test_selection_map_heuristic_warns_on_complex_decision():
    text = """---
schema_version: 1
schema_kind: decision-record
record_id: 20260510-complex-decision
project: test
revision: 1
status: selected-not-frozen
created_date: 2026-05-10
freeze_blockers:
  - id: fb-1
    field: lifecycle
    needed_evidence: x
    owner: a
    due_date: 2099-01-01
  - id: fb-2
    field: si
    needed_evidence: y
    owner: b
    due_date: 2099-01-01
  - id: fb-3
    field: pi
    needed_evidence: z
    owner: c
    due_date: 2099-01-01
---
body
"""
    r = lint_record.lint_text(text)
    assert "SM010" in _rules(r)


def test_selection_map_heuristic_quiet_when_map_present():
    text = """---
schema_version: 1
schema_kind: decision-record
record_id: 20260510-complex-decision
project: test
revision: 1
status: selected-not-frozen
created_date: 2026-05-10
related_records:
  - kind: selection-map
    id: 20260510-complex-decision-map
    role: sidecar
freeze_blockers:
  - id: fb-1
    field: lifecycle
    needed_evidence: x
    owner: a
    due_date: 2099-01-01
  - id: fb-2
    field: si
    needed_evidence: y
    owner: b
    due_date: 2099-01-01
  - id: fb-3
    field: pi
    needed_evidence: z
    owner: c
    due_date: 2099-01-01
---
body
"""
    r = lint_record.lint_text(text)
    assert "SM010" not in _rules(r)


# ============================================================
# pin-assign-workbench (PA*)
# ============================================================

def test_pin_assign_missing_workbook_path():
    text = GOOD_PIN_ASSIGN.replace("workbook_path: ./test.xlsx\n", "")
    r = lint_record.lint_text(text)
    assert "PA000" in _rules(r)


def test_pin_assign_bad_schematic_target():
    text = GOOD_PIN_ASSIGN.replace("schematic_target: orcad",
                                    "schematic_target: kicad")
    r = lint_record.lint_text(text)
    assert "PA010" in _rules(r)


def test_pin_assign_mechanical_status_conflict():
    text = GOOD_PIN_ASSIGN.replace("status: draft", "status: mechanical-checked")
    # mech_check_status is still TBD-evidence
    r = lint_record.lint_text(text)
    assert "PA002" in _rules(r)


def test_pin_assign_exported_with_conflicts():
    text = GOOD_PIN_ASSIGN.replace(
        "status: draft", "status: exported"
    ).replace(
        "mechanical_check_status: TBD-evidence", "mechanical_check_status: pass"
    ).replace(
        "unresolved_source_conflicts: []",
        "unresolved_source_conflicts:\n  - some-conflict",
    )
    r = lint_record.lint_text(text)
    assert "PA003" in _rules(r)


# ============================================================
# Body rules (BD*)
# ============================================================

def test_bad_status_in_body_table_fails():
    bad = GOOD_DECISION.replace("TBD-evidence", "kinda-confirmed")
    r = lint_record.lint_text(bad)
    assert "BD001" in _rules(r)


def test_evidence_aging_warning():
    text = """---
schema_version: 1
schema_kind: decision-record
record_id: 20260510-aging-test
project: test
revision: 1
status: selected-not-frozen
created_date: 2026-05-10
evidence_freshness_window_days: 30
freeze_blockers:
  - id: fb-x
    field: lifecycle
    needed_evidence: pcn
    owner: a
    due_date: 2099-01-01
---

# Body

| Field | Evidence date | Status |
|---|---|---|
| lifecycle | 2025-01-01 | confirmed |
"""
    r = lint_record.lint_text(text)
    assert "BD002" in _rules(r)
    bd002 = [i for i in r.issues if i.rule == "BD002"][0]
    assert bd002.level == "warning"


def test_evidence_aging_strict_promotes_to_error():
    text = """---
schema_version: 1
schema_kind: decision-record
record_id: 20260510-aging-test
project: test
revision: 1
status: selected-not-frozen
created_date: 2026-05-10
evidence_freshness_window_days: 30
freeze_blockers:
  - id: fb-x
    field: lifecycle
    needed_evidence: pcn
    owner: a
    due_date: 2099-01-01
---

# Body

| Field | Evidence date | Status |
|---|---|---|
| lifecycle | 2025-01-01 | confirmed |
"""
    r = lint_record.lint_text(text, strict_aging=True)
    bd002 = [i for i in r.issues if i.rule == "BD002"]
    assert bd002 and bd002[0].level == "error"


def test_evidence_aging_quiet_when_within_window():
    text = """---
schema_version: 1
schema_kind: decision-record
record_id: 20260510-aging-test
project: test
revision: 1
status: selected-not-frozen
created_date: 2026-05-10
evidence_freshness_window_days: 60
freeze_blockers:
  - id: fb-x
    field: lifecycle
    needed_evidence: pcn
    owner: a
    due_date: 2099-01-01
---

# Body

| Field | Evidence date | Status |
|---|---|---|
| lifecycle | 2026-04-15 | confirmed |
"""
    r = lint_record.lint_text(text)
    assert "BD002" not in _rules(r)


def test_confirmed_evidence_with_blank_date_fails():
    text = """---
schema_version: 1
schema_kind: decision-record
record_id: 20260510-blank-date
project: test
revision: 1
status: selected-not-frozen
created_date: 2026-05-10
freeze_blockers:
  - id: fb-x
    field: lifecycle
    needed_evidence: pcn
    owner: a
    due_date: 2099-01-01
---

# Body

| Field | Evidence date | Status |
|---|---|---|
| lifecycle |  | confirmed |
"""
    r = lint_record.lint_text(text)
    assert "BD003" in _rules(r)


# ============================================================
# JSON output format
# ============================================================

def test_json_output_shape():
    import io
    from contextlib import redirect_stdout

    # Use the example record
    example = REPO_ROOT / "critical-component-selection" / "examples" / \
              "example-decision-record.md"
    if not example.exists():
        return
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = lint_record.main([str(example), "--format", "json"])
    payload = json.loads(buf.getvalue())
    assert payload["schema_version"] == 1
    assert isinstance(payload["files"], list)
    assert payload["files"][0]["schema_kind"] == "decision-record"
    assert "issues" in payload["files"][0]
    assert payload["exit_code"] == rc


# ============================================================
# All example files lint clean
# ============================================================

def test_all_examples_lint_clean():
    examples = [
        REPO_ROOT / "critical-component-selection" / "examples" /
        "example-decision-record.md",
        REPO_ROOT / "critical-component-selection" / "examples" /
        "example-selection-map.md",
        REPO_ROOT / "pin-assign-workbench" / "examples" /
        "example-pin-assign-record.md",
    ]
    for ex in examples:
        if not ex.exists():
            continue
        r = lint_record.lint_text(ex.read_text(encoding="utf-8"))
        assert not r.errors, (
            f"{ex.name} has lint errors:\n"
            + "\n".join(f"  {i.rule} {i.level}: {i.message}" for i in r.errors)
        )


# ============================================================
# Standalone runner
# ============================================================

def _main():
    g = globals()
    tests = [(n, f) for n, f in g.items()
             if n.startswith("test_") and callable(f)]
    fails = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as e:
            fails += 1
            print(f"FAIL  {name}: {e}")
        except Exception as e:
            fails += 1
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - fails}/{len(tests)} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_main())
