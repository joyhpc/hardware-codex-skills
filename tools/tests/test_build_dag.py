"""Tests for tools/scripts/build_blocker_dag.py.

Exercises:
- Walking a directory of records
- Parsing all three kinds
- Edge construction (related_records, supersedes, superseded_by)
- Edge deduplication
- Mermaid output
- JSON shape
- Real example files in the repo
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from textwrap import dedent

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT_DIR = REPO_ROOT / "tools" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import build_blocker_dag as dag_mod  # noqa: E402


# ============================================================
# Helpers
# ============================================================

def write_record(dir_path: Path, name: str, content: str) -> Path:
    p = dir_path / name
    p.write_text(dedent(content).strip() + "\n", encoding="utf-8")
    return p


# ============================================================
# Single-record parsing
# ============================================================

def test_parse_decision_record_extracts_tasks():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        write_record(d, "a.md", """
            ---
            schema_version: 1
            schema_kind: decision-record
            record_id: 20260510-a-comp
            project: a
            revision: 1
            status: selected-not-frozen
            created_date: 2026-05-10
            freeze_blockers:
              - id: fb-1
                field: lifecycle
                needed_evidence: pcn
                owner: procurement
                due_date: 2026-06-01
              - id: fb-2
                field: si
                needed_evidence: ibis
                owner: si
                due_date: 2026-06-15
            external_validation_skills_needed:
              - skill: si-channel-budget
                reason: 6400-margin
            ---

            body
        """)
        result = dag_mod.parse_record(d / "a.md")
        assert not isinstance(result, str), result
        m, edges = result
        assert m.id == "20260510-a-comp"
        assert m.schema_kind == "decision-record"
        assert len(m.tasks) == 2
        assert m.tasks[0]["id"] == "fb-1"
        assert len(m.external_dependencies) == 1
        assert m.external_dependencies[0]["skill"] == "si-channel-budget"


def test_parse_selection_map_no_tasks():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        write_record(d, "m.md", """
            ---
            schema_version: 1
            schema_kind: selection-map
            record_id: 20260510-a-map
            project: a
            revision: 1
            status: active
            created_date: 2026-05-10
            decision_record: 20260510-a-comp
            related_records:
              - kind: decision-record
                id: 20260510-a-comp
                role: sidecar
            ---
            body
        """)
        result = dag_mod.parse_record(d / "m.md")
        assert not isinstance(result, str)
        m, edges = result
        assert m.tasks == []
        assert any(e.kind == "sidecar" for e in edges)


def test_parse_skips_records_without_frontmatter():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "x.md").write_text("just markdown, no frontmatter")
        result = dag_mod.parse_record(d / "x.md")
        assert isinstance(result, str)
        assert "frontmatter" in result.lower()


# ============================================================
# DAG building
# ============================================================

def _build_three_record_set(d: Path) -> None:
    """A decision record + its selection map + a downstream pin-assign."""
    write_record(d, "decision.md", """
        ---
        schema_version: 1
        schema_kind: decision-record
        record_id: 20260510-test-comp
        project: test
        revision: 1
        status: selected-not-frozen
        created_date: 2026-05-10
        related_records:
          - kind: selection-map
            id: 20260510-test-map
            role: sidecar
          - kind: pin-assign-workbench
            id: 20260520-test-pinout
            role: derived
        freeze_blockers:
          - id: fb-1
            field: lifecycle
            needed_evidence: pcn
            owner: procurement
            due_date: 2099-01-01
        ---
        body
    """)
    write_record(d, "map.md", """
        ---
        schema_version: 1
        schema_kind: selection-map
        record_id: 20260510-test-map
        project: test
        revision: 1
        status: active
        created_date: 2026-05-10
        decision_record: 20260510-test-comp
        related_records:
          - kind: decision-record
            id: 20260510-test-comp
            role: sidecar
        ---
        body
    """)
    write_record(d, "pinout.md", """
        ---
        schema_version: 1
        schema_kind: pin-assign-workbench
        record_id: 20260520-test-pinout
        project: test
        revision: 1
        status: draft
        created_date: 2026-05-20
        workbook_path: ./test.xlsx
        related_records:
          - kind: decision-record
            id: 20260510-test-comp
            role: source
        source_records:
          - kind: decision-record
            id: 20260510-test-comp
            role: source
        ---
        body
    """)


def test_build_dag_three_records():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        _build_three_record_set(d)
        result = dag_mod.build_dag([d])
    assert result["schema_version"] == 1
    assert result["kind"] == "blocker-dag"
    assert len(result["milestones"]) == 3
    kinds = {m["schema_kind"] for m in result["milestones"]}
    assert kinds == {"decision-record", "selection-map", "pin-assign-workbench"}
    # No errors
    assert result["errors"] == []
    # No unresolved targets (all referenced IDs are in scope)
    assert result["unresolved_edge_targets"] == []


def test_dag_edges_are_deduplicated():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        _build_three_record_set(d)
        result = dag_mod.build_dag([d])
    keys = [(e["from"], e["to"], e["kind"]) for e in result["edges"]]
    assert len(keys) == len(set(keys))


def test_dag_supersedes_edge():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        write_record(d, "old.md", """
            ---
            schema_version: 1
            schema_kind: decision-record
            record_id: 20260101-old-comp
            project: test
            revision: 1
            status: superseded
            superseded_by: 20260510-new-comp
            created_date: 2026-01-01
            ---
            body
        """)
        write_record(d, "new.md", """
            ---
            schema_version: 1
            schema_kind: decision-record
            record_id: 20260510-new-comp
            project: test
            revision: 2
            status: selected-not-frozen
            created_date: 2026-05-10
            supersedes: 20260101-old-comp
            freeze_blockers:
              - id: fb-1
                field: si
                needed_evidence: ibis
                owner: si
                due_date: 2099-01-01
            ---
            body
        """)
        result = dag_mod.build_dag([d])
    edge_kinds = {e["kind"] for e in result["edges"]}
    assert "supersedes" in edge_kinds or "superseded_by" in edge_kinds


def test_dag_unresolved_target_reported():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        write_record(d, "a.md", """
            ---
            schema_version: 1
            schema_kind: decision-record
            record_id: 20260510-a-comp
            project: test
            revision: 1
            status: selected-not-frozen
            created_date: 2026-05-10
            related_records:
              - kind: decision-record
                id: 20260101-missing-comp
                role: source
            freeze_blockers:
              - id: fb-1
                field: si
                needed_evidence: ibis
                owner: si
                due_date: 2099-01-01
            ---
            body
        """)
        result = dag_mod.build_dag([d])
    assert len(result["unresolved_edge_targets"]) == 1
    assert result["unresolved_edge_targets"][0]["to"] == "20260101-missing-comp"


# ============================================================
# Mermaid output
# ============================================================

def test_mermaid_output_contains_nodes():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        _build_three_record_set(d)
        result = dag_mod.build_dag([d])
    mermaid = dag_mod.to_mermaid(result)
    assert "graph TD" in mermaid
    assert "n_20260510_test_comp" in mermaid
    assert "n_20260510_test_map" in mermaid
    assert "n_20260520_test_pinout" in mermaid
    assert "sidecar" in mermaid
    assert "derived" in mermaid


# ============================================================
# Summary output
# ============================================================

def test_summary_output_groups_by_kind_and_status():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        _build_three_record_set(d)
        result = dag_mod.build_dag([d])
    summary = dag_mod.to_summary(result)
    assert "Records: 3" in summary
    assert "decision-record: 1" in summary
    assert "selection-map: 1" in summary
    assert "pin-assign-workbench: 1" in summary
    assert "Open freeze blockers" in summary


# ============================================================
# Real repo example files
# ============================================================

def test_dag_builds_from_real_examples():
    examples_dirs = [
        REPO_ROOT / "critical-component-selection" / "examples",
        REPO_ROOT / "pin-assign-workbench" / "examples",
    ]
    existing = [d for d in examples_dirs if d.exists()]
    if not existing:
        return
    result = dag_mod.build_dag(existing)
    assert result["errors"] == [], (
        "DAG build errors:\n"
        + "\n".join(f"  {e['path']}: {e['message']}" for e in result["errors"])
    )
    assert len(result["milestones"]) >= 3
    # Cross-skill linkage: pin-assign should reference the decision record
    pin_records = [m for m in result["milestones"]
                   if m["schema_kind"] == "pin-assign-workbench"]
    if pin_records:
        # there must be at least one edge from pin-assign to a decision-record
        pin_id = pin_records[0]["id"]
        cross_edges = [e for e in result["edges"]
                       if e["from"] == pin_id and e["kind"] == "source"]
        assert cross_edges, "pin-assign-workbench has no source edges"


def test_dag_json_serializes():
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        _build_three_record_set(d)
        result = dag_mod.build_dag([d])
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    re_parsed = json.loads(serialized)
    assert re_parsed["kind"] == "blocker-dag"


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
