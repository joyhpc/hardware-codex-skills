# Selection Map Template (v2 / schema_version 1, schema_kind: selection-map)

Schema-aware version of `selection-map-template.md`. Use this as a sidecar artifact when a decision involves many sources, candidate routes, or supplier threads.

See `../../SCHEMA.md` for envelope reference.

---

```yaml
---
schema_version: 1
schema_kind: selection-map
record_id: <YYYYMMDD>-<project>-<component>-selection-map
project: <project-id>
revision: 1

status: active
created_date: <YYYY-MM-DD>
review_date:
maintainer:

supersedes: null
superseded_by: null

related_records:
  - kind: decision-record
    id: <decision_record_id>
    role: sidecar

decision_record: <decision_record_id>
candidate_routes_count: 0
open_evidence_count: 0
tool_validation_open_count: 0

last_lint_pass: null
---
```

# <Component> Selection Map

## Map Purpose

State how this map helps the next selection step. Tie it to evidence navigation, candidate filtering, missing evidence, and freeze blockers.

## Source Map

| Source ID | Source type | Title | Date | Path / URL | Trust level | Candidate route | Supports | Map state |
|---|---|---|---|---|---|---|---|---|
| S1 |  |  |  |  | primary |  |  | active |

> `Map state` may use local workflow values such as `active`, `superseded`, `rejected`, or `stale`. Do not name this column `Status`; the repo linter reserves exact `Status` columns for the closed schema vocabularies in `SCHEMA.md`.

## Candidate Funnel

| Funnel class | Route / family | Representative PN | Why this level | Evidence pointer | Next action |
|---|---|---|---|---|---|
| Primary |  |  |  |  |  |
| Backup |  |  |  |  |  |
| Watchlist |  |  |  |  |  |
| Rejected |  |  |  |  |  |

## Requirement Coverage Map

| Requirement / gate | Primary route | Backup route | Evidence pointer | Status | Freeze impact |
|---|---|---|---|---|---|
|  |  |  |  | TBD-evidence |  |

## Rejection Ledger

| Route | Rejection reason | Evidence pointer | Reopen condition | Owner |
|---|---|---|---|---|
|  |  |  |  |  |

## Open Evidence Ledger

| Evidence gap | Affects gate | Best route | Format needed | Owner | Due | Status |
|---|---|---|---|---|---|---|
|  |  |  | datasheet table / PCN / vendor email / quote / tool report |  |  | TBD-evidence |

## Evidence Acquisition Plan

| Evidence gap | Best channel | Who asks | Question | Required answer format | Acquisition state |
|---|---|---|---|---|---|
|  |  |  |  |  | to-ask |

> `Acquisition state` may use `to-ask`, `asked`, `answered`, `stale`, `blocked`, or `N-A`. Do not name this column `Status` unless every value is in the linter's closed `Status` vocabulary.

## Tool Validation Map

| Validation | Inputs | Tool / method | Owner | Pass criteria | Output artifact | Status |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  | TBD-evidence |

## Update Rules

- Promote a route only when the evidence matrix can cite the required source.
- Demote or reject a route when new evidence conflicts with a hard constraint.
- Mark a source `stale` when its date, PCN state, pricing, lead time, stock, or tool version may no longer support the decision.
