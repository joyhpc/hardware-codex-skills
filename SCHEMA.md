# Record Schema (v1)

This document defines the machine-readable contract shared across skills in this repository. Skills produce Markdown records with YAML frontmatter; the schema defines that envelope, the kind-specific extensions, and the lint/DAG behavior that makes records usable by downstream tools.

The loop is:

```text
skill output -> frontmatter envelope -> lint -> JSON -> DAG builder -> downstream tools
```

Downstream tools may include `hwpm`, a meta-agent, CI, or dashboards.

## Why A Schema Layer

A record has three audiences:

1. Author: LLM or engineer writes rationale and tradeoffs. Markdown is the right surface.
2. Reviewer: engineer scans candidates, evidence, risks, and blockers. Markdown tables are the right surface.
3. Downstream agent: machine filters, routes, and tracks dependencies. YAML/JSON is the right surface.

One representation cannot optimize for all three. The repository therefore uses a four-layer model.

## Four-Layer Model

```text
Record (.md)
|-- Layer 1: Frontmatter (YAML)
|   |-- universal envelope: identity, lifecycle, graph edges
|   |-- kind extension: routing and status fields
|   `-- consumed by lint, DAG builder, meta-agent, grep
|
`-- Layer 2: Body (Markdown)
    |-- source inventory, evidence matrix, gates, risks
    `-- rationale and handoff prose

Layer 3: Lint
|-- envelope rules (FM*, EN*)
|-- kind-specific rules (CR*, DR*, SM*, PA*)
|-- body table rules (BD*)
`-- human or JSON output

Layer 4: DAG Builder
|-- walks record directories
|-- builds record, blocker, related-record, and supersession graph
`-- emits JSON, summary, or Mermaid
```

Principle: frontmatter is for routing, body is for authoring, lint is for integrity, and the DAG builder is for cross-record reasoning.

Lint is not an engineering oracle. It catches structural drift and obvious empty-shell records; dated evidence and owner review still decide truth.

## Universal Envelope

Every record must include these fields before kind-specific validation runs:

```yaml
---
schema_version: 1
schema_kind: decision-record
record_id: 20260510-mainboard-r3-lpddr5-x16
project: mainboard-r3
revision: 1

status: selected-not-frozen
created_date: 2026-05-10
review_date: 2026-06-15
maintainer: example-owner

supersedes: null
superseded_by: null

related_records: []

evidence_freshness_window_days: 60
last_lint_pass: null
---
```

Required universal fields:

| Field | Rule |
|---|---|
| `schema_version` | Required integer. v1 is currently supported. |
| `schema_kind` | Required for new records. Missing value defaults to `decision-record` with warning `FM010`. |
| `record_id` | Required. Must match `YYYYMMDD-<lowercase-slug>`. |
| `project` | Required project identifier. |
| `revision` | Required integer. `revision > 1` requires `supersedes`. |
| `status` | Required. Enum depends on `schema_kind`. |
| `created_date` | Required ISO date. |

Optional universal fields:

| Field | Meaning |
|---|---|
| `review_date` | Next planned review date. Must not precede `created_date`. |
| `maintainer` | Record owner or maintainer. |
| `supersedes` | Prior record id replaced by this record. |
| `superseded_by` | Later record id that replaces this record. Required when `status: superseded`. |
| `related_records` | Cross-record graph links. |
| `evidence_freshness_window_days` | Record-level evidence aging window. Default is 60 days. |
| `last_lint_pass` | Optional audit stamp written by `--stamp` on a successful lint run. |

## Schema Kinds

### `decision-record`

Produced by `critical-component-selection`.

Purpose: freeze-grade component decision artifact.

Status enum:

```text
draft | shortlisted | selected-not-frozen | frozen | blocked | superseded
```

Kind extension:

```yaml
primary_candidate:
  pn: EXAMPLE-LPDDR5-X16-A
  manufacturer: example-corp
  evidence_status: confirmed

backup_candidates:
  - pn: EXAMPLE-LPDDR5-X16-B
    manufacturer: alt-corp
    evidence_status: TBD-evidence

freeze_blockers:
  - id: fb-pcn-window
    field: lifecycle
    needed_evidence: pcn-or-vendor-roadmap-statement
    owner: procurement
    due_date: 2026-05-25

external_validation_skills_needed:
  - skill: si-channel-budget
    reason: 6400mtps-channel-loss-margin

evidence_root: hardware-projects/prj/<project>/evidence/<component>/
risk_register: ./risks.md
```

Core rule: `status: frozen` requires no freeze blockers, no external validation still needed, and body evidence/gate tables that do not contain unresolved gate statuses.

### `selection-map`

Produced by `critical-component-selection`.

Purpose: sidecar navigation map for large selections with many candidate routes, source threads, or validation paths.

Status enum:

```text
active | stale | closed
```

Kind extension:

```yaml
decision_record: 20260510-mainboard-r3-lpddr5-x16
candidate_routes_count: 7
open_evidence_count: 3
tool_validation_open_count: 2
```

Selection map heuristic:

- expected when `len(freeze_blockers) >= 3`
- expected when `len(backup_candidates) >= 3`
- expected when body source inventory has 10 or more rows

Lint warning `SM010` fires when the heuristic recommends a map but no `selection-map` related record is referenced.

### `pin-assign-workbench`

Produced by `pin-assign-workbench`.

Purpose: sidecar metadata for the `.xlsx` workbook. The workbook is the primary deliverable; the Markdown sidecar exists so schema tools can route dependencies.

Status enum:

```text
draft | source-locked | mechanical-checked | reviewed | exported
```

Kind extension:

```yaml
workbook_path: ./mainboard-r3-fpga-mem-pinout.xlsx
schematic_target: orcad
mechanical_check_status: pass

source_records:
  - kind: decision-record
    id: 20260510-mainboard-r3-lpddr5-x16
    role: source

unresolved_source_conflicts: []
```

For v1, `source_records` is retained because existing examples and tools use it. Prefer also listing the same dependencies in `related_records` with `role: source` so the graph remains explicit. Future schema versions may collapse this duplication.

## Closed Vocabularies

Lint rejects values outside these enums.

| Vocabulary | Values |
|---|---|
| `evidence_status` | `confirmed`, `TBD-evidence`, `conflict`, `N-A`, `stale-evidence` |
| gate status in body tables | `pass`, `blocked`, `TBD-evidence`, `N-A` |
| `decision-record.status` | `draft`, `shortlisted`, `selected-not-frozen`, `frozen`, `blocked`, `superseded` |
| `selection-map.status` | `active`, `stale`, `closed` |
| `pin-assign-workbench.status` | `draft`, `source-locked`, `mechanical-checked`, `reviewed`, `exported` |
| `mechanical_check_status` | `pass`, `blocked`, `TBD-evidence`, `N-A` |
| `related_records[*].role` | `sidecar`, `source`, `derived`, `superseded` |
| `related_records[*].kind` | any registered `schema_kind` |

`stale-evidence` marks rows the author or reviewer has reclassified after evidence freshness review. Lint does not rewrite rows; it warns on old confirmed rows, or reports them as errors when `--strict-aging` is set.

## Cross-Record References

Records link through `related_records`:

```yaml
related_records:
  - kind: selection-map
    id: 20260510-mainboard-r3-lpddr5-selection-map
    role: sidecar
  - kind: pin-assign-workbench
    id: 20260520-mainboard-r3-lpddr5-pinout
    role: derived
```

Roles:

| Role | Meaning |
|---|---|
| `sidecar` | Referenced record is a detail artifact for this record. |
| `source` | This record depends on the referenced record. |
| `derived` | Referenced record was created from this one. |
| `superseded` | Legacy role. Prefer top-level `supersedes` / `superseded_by`. |

The DAG builder follows `related_records`, `supersedes`, `superseded_by`, and `freeze_blockers`.

## Evidence Aging

Rule `BD002` scans body tables whose headers include both `Status` and `Evidence date`.

Behavior:

- Default window is 60 days.
- Override per record with `evidence_freshness_window_days`.
- Confirmed rows older than the window emit warning by default.
- `--strict-aging` promotes stale confirmed evidence warnings to errors.
- Lint never mutates body table statuses.

Rule `BD003` rejects confirmed evidence rows with empty or invalid `Evidence date`.

## Lint Rules

Rule prefixes:

| Prefix | Scope |
|---|---|
| `FM` | Frontmatter envelope |
| `EN` | Envelope cross-field consistency |
| `CR` | Decision-record consistency |
| `DR` | Decision-record extension fields |
| `SM` | Selection-map fields and heuristics |
| `PA` | Pin-assign-workbench fields |
| `BD` | Body table vocabulary and evidence aging |

Selected rules:

| Rule | Level | Description |
|---|---|---|
| `FM001` | error | Required envelope field missing. |
| `FM002` | error | `record_id` does not match `YYYYMMDD-<slug>`. |
| `FM003` | error | `status` is outside the enum for this kind. |
| `FM005` | error | Date field is not ISO `YYYY-MM-DD`. |
| `FM010` | warning | `schema_kind` missing; defaults to `decision-record`. |
| `FM997` | error | Unknown `schema_kind`. |
| `FM999` | error | Unsupported `schema_version`. |
| `EN001` | error | `revision > 1` requires `supersedes`. |
| `EN002` | error | `review_date` precedes `created_date`. |
| `EN003` | error | `superseded_by` and `status: superseded` are inconsistent. |
| `EN010` | error | `related_records` is not a list of mappings. |
| `EN011` | error | Related record kind is unknown. |
| `EN012` | error | Related record id does not match id pattern. |
| `EN013` | error | Related record role is outside enum. |
| `CR001` | error | `status: frozen` but `freeze_blockers` is non-empty. |
| `CR002` | error | `status: selected-not-frozen` but `freeze_blockers` is empty. |
| `CR004` | error/warning | Blocker `due_date` is in the past; error for `selected-not-frozen`, warning for earlier non-frozen states. |
| `CR005` | error | `status: frozen` with non-empty `external_validation_skills_needed`. |
| `CR006` | error | `status: frozen` without minimum Source Inventory and passing gate evidence in body. |
| `CR007` | error | Body gate table has unresolved statuses but frontmatter has no `freeze_blockers`. |
| `CR008` | error | Confirmed primary candidate lacks a matching dated Evidence Matrix row. |
| `DR001` | error | Candidate `evidence_status` is outside enum. |
| `SM001` | error | `selection-map` missing `decision_record`. |
| `SM010` | warning | Selection map recommended by heuristic but not referenced. |
| `PA000` | error | `pin-assign-workbench` missing `workbook_path`. |
| `PA001` | error | `workbook_path` does not exist when checked with `--check-paths`. |
| `PA002` | error | `mechanical-checked` or later requires `mechanical_check_status: pass`. |
| `PA003` | error | `status: exported` with unresolved source conflicts. |
| `PA010` | error | Unsupported `schematic_target`. |
| `PA011` | error | `mechanical_check_status` is outside enum. |
| `PA020` | warning | Pin assignment sidecar has no `source_records`. |
| `BD001` | error | Body `Status` cell uses value outside allowed union. |
| `BD002` | warning | Confirmed evidence row date is older than freshness window. |
| `BD003` | error | Confirmed evidence row has empty or invalid `Evidence date`. |

## Lint CLI

```bash
# Human-readable output
python tools/scripts/lint_record.py path/to/record.md

# Directory scan
python tools/scripts/lint_record.py path/to/records/

# JSON for CI or agents
python tools/scripts/lint_record.py path/to/records/ --format json

# Treat warnings as failures
python tools/scripts/lint_record.py path/to/records/ --strict

# Treat stale confirmed evidence as failure
python tools/scripts/lint_record.py path/to/records/ --strict-aging

# Verify referenced paths where supported, such as workbook_path
python tools/scripts/lint_record.py path/to/record.md --check-paths

# Stamp last_lint_pass on success
python tools/scripts/lint_record.py path/to/record.md --stamp
```

JSON output shape:

```json
{
  "schema_version": 1,
  "files": [
    {
      "path": "path/to/record.md",
      "schema_kind": "decision-record",
      "record_id": "20260510-mainboard-r3-lpddr5-x16",
      "ok": false,
      "issues": [
        {
          "rule": "CR001",
          "level": "error",
          "location": "frontmatter:status",
          "message": "status=frozen requires empty freeze_blockers; 2 blocker(s) present"
        }
      ]
    }
  ],
  "exit_code": 1
}
```

## DAG Builder

`tools/scripts/build_blocker_dag.py` walks records and emits graph data.

```bash
python tools/scripts/build_blocker_dag.py hardware-projects/prj/mainboard-r3/decisions/ --format summary
python tools/scripts/build_blocker_dag.py hardware-projects/prj/mainboard-r3/decisions/ --format json > dag.json
python tools/scripts/build_blocker_dag.py hardware-projects/prj/mainboard-r3/decisions/ --format mermaid > dag.mmd
```

JSON shape:

```json
{
  "schema_version": 1,
  "kind": "blocker-dag",
  "generated_at": "2026-05-10T14:32:00+08:00",
  "scope": "hardware-projects/prj/mainboard-r3/decisions",
  "milestones": [
    {
      "id": "20260510-mainboard-r3-lpddr5-x16",
      "schema_kind": "decision-record",
      "project": "mainboard-r3",
      "status": "selected-not-frozen",
      "freeze_target_date": "2026-07-01",
      "tasks": [
        {
          "id": "fb-pcn-window",
          "owner": "procurement",
          "due_date": "2026-05-25",
          "field": "lifecycle"
        }
      ],
      "external_dependencies": [
        {
          "skill": "si-channel-budget",
          "reason": "6400mtps-channel-loss-margin"
        }
      ]
    }
  ],
  "edges": [
    {
      "from": "20260510-mainboard-r3-lpddr5-x16",
      "to": "20260520-mainboard-r3-lpddr5-pinout",
      "kind": "derived"
    }
  ],
  "unresolved_edge_targets": [],
  "errors": []
}
```

CPM critical-path computation belongs outside this repo, typically in `hwpm`.

## Versioning

`schema_version: 1` covers:

- universal envelope
- three current schema kinds
- body status vocabulary scanning
- evidence aging
- cross-record graph output

Breaking changes must increment `schema_version` and should include a migration script under `tools/scripts/migrate_v<N>_to_v<N+1>.py`.

Unknown schema versions fail early with exit code 2 so CI can route to migration instead of treating the record as a normal content failure.

## Composition With Meta-Agent

The intended division of labor:

```text
LLM skill:
  - collect and reconcile evidence
  - write/update record body
  - explain rationale and next actions

lint:
  - reject malformed schema
  - reject invalid status vocabulary
  - reject obvious empty-shell freeze patterns

DAG builder:
  - expose records, blockers, supersession, and related artifacts as graph data

meta-agent / hwpm:
  - route work
  - compute project scheduling
  - wait on blockers and validation artifacts
```

This keeps LLMs at ambiguity boundaries and puts machine-checkable behavior in deterministic tools.
