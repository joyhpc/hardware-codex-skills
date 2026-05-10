# Decision Record Template (v2 / schema_version 1, schema_kind: decision-record)

This template adds a YAML frontmatter envelope over the original `decision-record-template.md`. The frontmatter is the machine-readable interface for the meta-agent and lint; the body remains human-authored.

See `../../SCHEMA.md` for envelope reference and closed enumerations.

---

```yaml
---
schema_version: 1
schema_kind: decision-record
record_id: <YYYYMMDD>-<project-slug>-<component-slug>
project: <project-id>
revision: 1

status: draft
created_date: <YYYY-MM-DD>
review_date:
freeze_target_date:
maintainer:

supersedes: null
superseded_by: null

related_records: []
# Example:
#   - kind: selection-map
#     id: <YYYYMMDD>-<project>-<component>-selection-map
#     role: sidecar

evidence_freshness_window_days: 60

primary_candidate:
  pn:
  manufacturer:
  evidence_status: TBD-evidence

backup_candidates: []

freeze_blockers: []
# Example entry:
#   - id: fb-pcn-window
#     field: lifecycle
#     needed_evidence: pcn-or-vendor-roadmap-statement
#     owner: procurement
#     due_date: <YYYY-MM-DD>

external_validation_skills_needed: []
# Example entry:
#   - skill: si-channel-budget
#     reason: <why this skill is required to close a freeze blocker>

evidence_root:
risk_register:

last_lint_pass: null
---
```

# <Component> Selection Decision

## Decision Objective

State the exact freeze-grade choice being made.

## Requirement Baseline

Link the requirement file. Split into:

- Hard constraints:
- Changeable constraints:
- Acceptance criteria:

## Source Inventory

| Source ID | Type | Title / description | Date | Owner / path / URL | Trust level | Notes |
|---|---|---|---|---|---|---|
| S1 |  |  |  |  | primary |  |

## Candidate Classification

| Class | Candidate | Evidence pointer | Rationale |
|---|---|---|---|
| Primary |  |  |  |
| Backup |  |  |  |

## Evidence Matrix

| Field | Candidate | Requirement | Claimed value | Evidence source | Evidence date | Status | Notes |
|---|---|---|---|---|---|---|---|
| Interface / protocol |  |  |  |  |  | TBD-evidence |  |
| Lifecycle / EOL / PCN |  |  |  |  |  | TBD-evidence |  |

> **Body rules**:
> - `Status` cells must use `confirmed`, `TBD-evidence`, `conflict`, `N-A`, or `stale-evidence`. Lint rule **BD001** rejects others.
> - When both `Status` and `Evidence date` columns exist, lint rule **BD002** flags `confirmed` rows whose date is older than `evidence_freshness_window_days` before `created_date`.

## Risk Summary

Link the risk register. List unresolved high-impact risks; keep details external.

## Engineering Verification Gates

| Gate | Owner | Pass criteria | Artifact / link | Status |
|---|---|---|---|---|
|  |  |  |  | TBD-evidence |

> Status uses `pass`, `blocked`, `TBD-evidence`, or `N-A`.

## Decision

State what is selected, what is not, and what remains blocked. The frontmatter `status` is canonical; this section is the human-readable explanation.

## Freeze Blockers Narrative

For each `freeze_blockers[]` entry in the frontmatter, expand here. Keep IDs (`fb-*`) in sync.

## External Validation Handoff

For each `external_validation_skills_needed[]`, state expected artifact and which `freeze_blocker` it closes.

## Signoff

| Role | Name | Date | Notes |
|---|---|---|---|
| Engineering |  |  |  |
| Procurement |  |  |  |
| Project owner |  |  |  |

---

**Lint before commit:**

```bash
python tools/scripts/lint_record.py path/to/this/record.md --stamp
```
