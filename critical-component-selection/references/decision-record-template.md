# Decision Record Template (v2 / schema_version 1, schema_kind: decision-record)

This template adds a YAML frontmatter envelope over the original `decision-record-template.md`. The frontmatter is the machine-readable interface for the meta-agent and lint; the body remains the human review surface.

See `../../SCHEMA.md` for envelope reference and closed enumerations. See `decision-playbook.md` for practical hard-gate and freeze-review rules.

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

## Hard Gate Screen

Screen hard gates before ranking candidates. A candidate with an unresolved hard gate can be investigated, but cannot be `frozen`.

| Gate | Requirement / pass condition | Candidate impact | Evidence pointer | Status | Owner / next action |
|---|---|---|---|---|---|
| Exact orderable identity |  |  |  | TBD-evidence |  |
| Package / footprint / pinout |  |  |  | TBD-evidence |  |
| Lifecycle / PCN / EOL |  |  |  | TBD-evidence |  |
| Commercial availability |  |  |  | TBD-evidence |  |
| Toolchain / firmware / logic support |  |  |  | TBD-evidence |  |
| SI / PI / thermal / mechanical risk |  |  |  | TBD-evidence |  |
| Substitute path |  |  |  | TBD-evidence |  |

> Status uses `pass`, `blocked`, `TBD-evidence`, or `N-A`. If a gate is `blocked` or `TBD-evidence`, keep or create a matching `freeze_blockers[]` entry in frontmatter.

## Source Inventory

| Source ID | Type | Title / description | Date | Owner / path / URL | Trust level | Notes |
|---|---|---|---|---|---|---|
| S1 |  |  |  |  | primary |  |

## Candidate Classification

| Class | Candidate | Evidence pointer | Rationale |
|---|---|---|---|
| Primary |  |  |  |
| Backup |  |  |  |
| Watchlist |  |  |  |
| Rejected |  |  |  |
| Closed |  |  |  |

## Rejection Ledger

Record why a route was excluded and what evidence would reopen it.

| Candidate / route | Rejection or demotion reason | Evidence pointer | Reopen condition | Owner |
|---|---|---|---|---|
|  |  |  |  |  |

## Evidence Matrix

| Field | Candidate | Requirement | Claimed value | Evidence source | Evidence date | Status | Notes |
|---|---|---|---|---|---|---|---|
| Interface / protocol |  |  |  |  |  | TBD-evidence |  |
| Lifecycle / EOL / PCN |  |  |  |  |  | TBD-evidence |  |

> **Body rules**:
> - `Status` cells must use `confirmed`, `TBD-evidence`, `conflict`, `N-A`, or `stale-evidence`. Lint rule **BD001** rejects others.
> - When both `Status` and `Evidence date` columns exist, lint rule **BD002** flags `confirmed` rows whose date is older than `evidence_freshness_window_days` before `created_date`.
> - Confirmed evidence rows must carry a non-empty ISO `Evidence date`; lint rule **BD003** rejects blank or invalid dates.
> - If `primary_candidate.evidence_status` is `confirmed`, at least one row for that PN must have `Status=confirmed`, an `Evidence source`, and a valid `Evidence date`; lint rule **CR008** rejects empty-shell confirmation.

## Risk Summary

Link the risk register. List unresolved high-impact risks; keep details external.

## Engineering Verification Gates

| Gate | Owner | Pass criteria | Artifact / link | Status |
|---|---|---|---|---|
|  |  |  |  | TBD-evidence |

> Status uses `pass`, `blocked`, `TBD-evidence`, or `N-A`.

## Decision

State what is selected, what is not, and what remains blocked. Start with one of: `freeze`, `do not freeze`, `stay selected-not-frozen`, `block`, or `supersede`. The frontmatter `status` is canonical; this section is the human-readable explanation.

## Freeze Blockers Narrative

For each `freeze_blockers[]` entry in the frontmatter, expand here. Keep IDs (`fb-*`) in sync.

## External Validation Handoff

For each `external_validation_skills_needed[]`, state expected artifact and which `freeze_blocker` it closes.

For `status: frozen`, `external_validation_skills_needed` must be empty, `freeze_blockers` must be empty, Source Inventory must contain at least one row, and hard/verification gate tables must not contain unresolved gate statuses.

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
