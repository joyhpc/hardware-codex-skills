#!/usr/bin/env python3
"""Build a cross-record blocker DAG from a directory of records.

Walks the given paths, parses every Markdown record with valid frontmatter,
and emits the cross-record graph as JSON or Mermaid.

Output is consumed by hwpm CPM, dashboards, and the meta-agent. CPM-style
critical path computation belongs in hwpm; this builder produces the input
data only.

This builder intentionally does not call lint_text(); lint is a gate, while the
DAG builder is a reporter that should preserve partial graph visibility when a
record has a parseable envelope.

Exit codes:
    0  graph built; warnings allowed
    1  one or more records failed to parse
    2  no records found at the given paths
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

# Reuse the shared schema envelope parser + constants.
THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
import schema_lib  # noqa: E402


@dataclass
class Milestone:
    id: str
    schema_kind: str
    project: str | None
    status: str | None
    revision: int | None
    created_date: str | None
    review_date: str | None
    freeze_target_date: str | None
    maintainer: str | None
    path: str
    tasks: list[dict] = field(default_factory=list)
    external_dependencies: list[dict] = field(default_factory=list)


@dataclass
class Edge:
    from_: str
    to: str
    kind: str        # supersedes | superseded_by | sidecar | source | derived

    def to_dict(self) -> dict:
        return {"from": self.from_, "to": self.to, "kind": self.kind}


@dataclass
class BuildError:
    path: str
    message: str


def _iter_record_files(paths: list[Path]) -> Iterable[Path]:
    for p in paths:
        if p.is_file() and p.suffix == ".md":
            yield p
        elif p.is_dir():
            for f in sorted(p.rglob("*.md")):
                yield f


def _coerce_str(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, dt.date):
        return value.isoformat()
    return str(value)


def parse_record(path: Path) -> tuple[Milestone, list[Edge]] | str:
    """Return (milestone, edges) or an error message string."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return f"read error: {e}"

    parsed = schema_lib.split_frontmatter(text)
    if parsed is None:
        return "no valid frontmatter"
    meta, _body = parsed

    # Skip records with unsupported schema_version
    sv = meta.get("schema_version")
    if sv not in schema_lib.SUPPORTED_SCHEMA_VERSIONS:
        return f"unsupported schema_version: {sv}"

    rid = schema_lib.get_record_id(meta)
    if not rid:
        return "missing record_id"

    kind = meta.get("schema_kind", schema_lib.DECISION_RECORD)

    milestone = Milestone(
        id=rid,
        schema_kind=kind,
        project=meta.get("project"),
        status=meta.get("status"),
        revision=meta.get("revision"),
        created_date=_coerce_str(meta.get("created_date")),
        review_date=_coerce_str(meta.get("review_date")),
        freeze_target_date=_coerce_str(meta.get("freeze_target_date")),
        maintainer=meta.get("maintainer"),
        path=str(path),
    )

    # Tasks (freeze blockers) — only meaningful on decision-record
    if kind == schema_lib.DECISION_RECORD:
        for b in (meta.get("freeze_blockers") or []):
            if isinstance(b, dict):
                milestone.tasks.append({
                    "id": b.get("id"),
                    "owner": b.get("owner"),
                    "due_date": _coerce_str(b.get("due_date")),
                    "field": b.get("field"),
                    "needed_evidence": b.get("needed_evidence"),
                })
        for d in (meta.get("external_validation_skills_needed") or []):
            if isinstance(d, dict):
                milestone.external_dependencies.append({
                    "skill": d.get("skill"),
                    "reason": d.get("reason"),
                })

    # Edges
    edges: list[Edge] = []
    sup = meta.get("supersedes")
    if sup:
        edges.append(Edge(from_=str(sup), to=rid, kind="supersedes"))
    sup_by = meta.get("superseded_by")
    if sup_by:
        edges.append(Edge(from_=rid, to=str(sup_by), kind="superseded_by"))

    for rel in (meta.get("related_records") or []):
        if not isinstance(rel, dict):
            continue
        target = rel.get("id")
        role = rel.get("role")
        if not target or not role:
            continue
        edges.append(Edge(from_=rid, to=str(target), kind=str(role)))

    return milestone, edges


def build_dag(paths: list[Path]) -> dict:
    milestones: list[Milestone] = []
    edges: list[Edge] = []
    errors: list[BuildError] = []

    for p in _iter_record_files(paths):
        result = parse_record(p)
        if isinstance(result, str):
            errors.append(BuildError(path=str(p), message=result))
            continue
        m, e = result
        milestones.append(m)
        edges.extend(e)

    # Deduplicate edges
    seen: set[tuple[str, str, str]] = set()
    unique_edges: list[Edge] = []
    for e in edges:
        key = (e.from_, e.to, e.kind)
        if key in seen:
            continue
        seen.add(key)
        unique_edges.append(e)

    # Detect dangling edge targets (warnings, not errors)
    known_ids = {m.id for m in milestones}
    dangling = [
        {"from": e.from_, "to": e.to, "kind": e.kind}
        for e in unique_edges
        if e.to not in known_ids and e.from_ not in known_ids
    ]
    # More useful: edges where target is unknown but source is known
    unresolved_targets = [
        {"from": e.from_, "to": e.to, "kind": e.kind}
        for e in unique_edges
        if e.to not in known_ids and e.from_ in known_ids
    ]

    return {
        "schema_version": 1,
        "kind": "blocker-dag",
        "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "scope": [str(p) for p in paths],
        "milestones": [_milestone_to_dict(m) for m in milestones],
        "edges": [e.to_dict() for e in unique_edges],
        "unresolved_edge_targets": unresolved_targets,
        "errors": [asdict(e) for e in errors],
    }


def _milestone_to_dict(m: Milestone) -> dict:
    d = asdict(m)
    return d


# ============================================================
# Mermaid output
# ============================================================

def _mermaid_node_id(record_id: str) -> str:
    """Mermaid node identifiers cannot contain hyphens at the start, etc.
    We sanitize and use a quoted label for display.
    """
    return "n_" + record_id.replace("-", "_")


def to_mermaid(dag: dict) -> str:
    lines = ["graph TD"]
    for m in dag["milestones"]:
        nid = _mermaid_node_id(m["id"])
        status = m.get("status") or "?"
        kind_short = {
            "decision-record": "DR",
            "selection-map": "SM",
            "pin-assign-workbench": "PA",
        }.get(m["schema_kind"], m["schema_kind"])
        label = f"{kind_short}: {m['id']}<br/>status: {status}"
        if m.get("tasks"):
            label += f"<br/>blockers: {len(m['tasks'])}"
        lines.append(f'    {nid}["{label}"]')

    edge_style = {
        "supersedes": "-.->|supersedes|",
        "superseded_by": "-.->|superseded_by|",
        "sidecar": "-->|sidecar|",
        "source": "-->|source|",
        "derived": "-->|derived|",
    }
    known_ids = {m["id"] for m in dag["milestones"]}
    for e in dag["edges"]:
        if e["from"] not in known_ids or e["to"] not in known_ids:
            continue
        from_id = _mermaid_node_id(e["from"])
        to_id = _mermaid_node_id(e["to"])
        arrow = edge_style.get(e["kind"], "-->")
        lines.append(f"    {from_id} {arrow} {to_id}")

    return "\n".join(lines)


# ============================================================
# Summary text output
# ============================================================

def to_summary(dag: dict) -> str:
    lines = []
    lines.append(f"Records: {len(dag['milestones'])}")
    lines.append(f"Edges: {len(dag['edges'])}")
    if dag["errors"]:
        lines.append(f"Parse errors: {len(dag['errors'])}")
        for e in dag["errors"]:
            lines.append(f"  {e['path']}: {e['message']}")
    if dag["unresolved_edge_targets"]:
        lines.append(f"Unresolved edge targets: {len(dag['unresolved_edge_targets'])}")
        for u in dag["unresolved_edge_targets"]:
            lines.append(f"  {u['from']} --[{u['kind']}]--> {u['to']} (target not in scope)")

    by_status: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    open_blockers = 0
    for m in dag["milestones"]:
        by_status[m.get("status") or "?"] = by_status.get(m.get("status") or "?", 0) + 1
        by_kind[m["schema_kind"]] = by_kind.get(m["schema_kind"], 0) + 1
        open_blockers += len(m.get("tasks") or [])

    lines.append("")
    lines.append("By kind:")
    for k, n in sorted(by_kind.items()):
        lines.append(f"  {k}: {n}")
    lines.append("By status:")
    for k, n in sorted(by_status.items()):
        lines.append(f"  {k}: {n}")
    lines.append(f"Open freeze blockers (decision-record): {open_blockers}")

    return "\n".join(lines)


# ============================================================
# CLI driver
# ============================================================

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", type=Path,
                    help="record files or directories to walk")
    ap.add_argument("--format", choices=("json", "mermaid", "summary"),
                    default="json", help="output format")
    args = ap.parse_args(argv)

    dag = build_dag(args.paths)

    if not dag["milestones"] and not dag["errors"]:
        sys.stderr.write("warning: no records found at the given paths\n")
        return 2

    if args.format == "json":
        print(json.dumps(dag, indent=2, ensure_ascii=False))
    elif args.format == "mermaid":
        print(to_mermaid(dag))
    else:  # summary
        print(to_summary(dag))

    return 1 if dag["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
