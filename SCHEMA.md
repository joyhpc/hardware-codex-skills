# Record Schema (v1)

This document defines the **machine-readable contract** shared across all skills in this repository. Each skill produces Markdown records with a YAML frontmatter envelope; this schema specifies the envelope, the per-kind extensions, and the lint that gates them.

The goal is a closed loop: skill output → frontmatter envelope → lint → JSON → DAG builder → downstream tools (`hwpm`, meta-agent, dashboards).

## Table of Contents

- [Why a Schema Layer](#why-a-schema-layer)
- [Three-Layer Model](#three-layer-model)
- [Universal Envelope](#universal-envelope)
- [Schema Kinds](#schema-kinds)
- [Closed Vocabularies](#closed-vocabularies)
- [Cross-Record References](#cross-record-references)
- [Evidence Aging](#evidence-aging)
- [Lint Rules](#lint-rules)
- [Lint Output Formats](#lint-output-formats)
- [DAG Builder](#dag-builder)
- [Versioning](#versioning)
- [Composition With Meta-Agent](#composition-with-meta-agent)

## Why a Schema Layer

A skill record serves three audiences with conflicting needs:

1. **Author** (LLM or engineer) writes narrative reasoning — Markdown is right.
2. **Reviewer** (engineer) scans tables, candidate classes, and freeze blockers — Markdown tables are right.
3. **Downstream agent** (machine) filters, routes, and tracks dependencies — YAML/JSON is right.

A single representation cannot satisfy all three. The fix is layered representation in one file with clear ownership per layer.

## Three-Layer Model

```
┌──────────────────────────────────────────────────────────┐
│  Record (single .md file)                                │
│                                                          │
│   Layer 1: Frontmatter (YAML)                            │
│     - envelope: identity, lifecycle, graph edges         │
│     - kind extension: kind-specific routing fields       │
│     - consumed by: meta-agent, lint, DAG builder, grep   │
│                                                          │
│   Layer 2: Body (Markdown)                               │
│     - tables (candidates, evidence, risks, gates)        │
│     - rationale prose                                    │
│     - authored by: skill workflow                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
                       │
                       ▼
   Layer 3: Lint (validation gate)
     - envelope rules           (FM*, EN*)
     - kind-specific rules      (DR*, SM*, PA*)
     - cross-field consistency  (CR*)
     - body table vocabulary    (BD*)
     - emits human or JSON output
     - stamps `last_lint_pass` on success
                       │
                       ▼
   Layer 4: DAG Builder (cross-record graph)
     - walks record dirs
     - builds milestone/task graph from blockers + supersedes + related_records
     - outputs JSON consumable by hwpm CPM, dashboards, meta-agent
```

Principle: **frontmatter is for routing, body is for authoring, lint is for integrity, DAG builder is for cross-record reasoning.** Each layer has one job.

## Universal Envelope

Every record, regardless of kind, must include these fields. The lint validates the envelope before dispatching to kind-specific rules.

```yaml
---
schema_version: 1                            # required, integer
schema_kind: decision-record                 # required, see "Schema Kinds"
record_id: 20260510-mainboard-r3-lpddr5-x16  # required, YYYYMMDD-<lowercase-slug>
project: mainboard-r3                        # required
revision: 1                                  # required, integer >= 1

status: selected-not-frozen                  # required, enum is kind-specific
created_date: 2026-05-10                     # required, ISO date
review_date: 2026-06-15                      # optional
maintainer: pure                             # optional

# Decision history graph
supersedes: null                             # record_id of older version, or null
superseded_by: null                          # set when status=superseded

# Cross-record links
related_records: []                          # see "Cross-Record References"

# Evidence policy (optional, kind-aware default)
evidence_freshness_window_days: 60           # body evidence rows older than this raise BD002

# Audit
last_lint_pass: null                         # set by `lint --stamp`
---
```

**Backward compatibility**: when `schema_kind` is absent, lint defaults to `decision-record` and emits warning `FM010`. New records must set `schema_kind` explicitly.

## Schema Kinds

Three kinds are currently defined. Each kind has its own status enum, required extension fields, and body table rules.

| `schema_kind` | Skill | Purpose |
|---|---|---|
| `decision-record` | `critical-component-selection` | Freeze-grade component decision artifact |
| `selection-map` | `critical-component-selection` | Sidecar navigation map for large selections |
| `pin-assign-workbench` | `pin-assign-workbench` | Sidecar metadata + handoff for the .xlsx workbook |

### `decision-record`

Status enum: `draft | shortlisted | selected-not-frozen | frozen | blocked | superseded`

Extension fields:

```yaml
primary_candidate:
  pn: EXAMPLE-LPDDR5-X16-A
  manufacturer: example-corp
  evidence_status: confirmed                 # closed enum, see below

backup_candidates: []

freeze_blockers:                             # empty iff status=frozen
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

### `selection-map`

Sidecar artifact when a decision involves many sources, candidate routes, or supplier threads. Always paired 1:1 with a decision record via `related_records`.

Status enum: `active | stale | closed`

Extension fields:

```yaml
decision_record: 20260510-mainboard-r3-lpddr5-x16   # required reference
candidate_routes_count: 7                            # informational
open_evidence_count: 3                               # decremented as evidence arrives
tool_validation_open_count: 2                       # decremented as artifacts produced
```

A selection map is **expected** when any of:

1. `len(freeze_blockers) >= 3` on the decision record, OR
2. `len(backup_candidates) >= 3` on the decision record, OR
3. The body source inventory has 10+ rows.

Lint warning `SM010` fires if the heuristic recommends a map but `related_records` does not point to one.

### `pin-assign-workbench`

Markdown sidecar carrying envelope metadata and handoff notes for the actual `.xlsx` workbook. The workbook itself is the deliverable; this file is what the schema layer can validate.

Status enum: `draft | source-locked | mechanical-checked | reviewed | exported`

Extension fields:

```yaml
workbook_path: ./mainboard-r3-fpga-mem-pinout.xlsx   # required, relative
schematic_target: orcad                              # orcad | cadence-cis | allegro-de-hdl
mechanical_check_status: pass                        # pass | blocked | TBD-evidence | N-A

source_records:                                      # decision records this workbook implements
  - kind: decision-record
    id: 20260510-mainboard-r3-lpddr5-x16
    role: source
  - kind: decision-record
    id: 20260420-mainboard-r3-fpga
    role: source

unresolved_source_conflicts: []                      # empty for status=mechanical-checked or beyond
```

## Closed Vocabularies

These are enforced exactly. Lint rejects any value outside the listed set.

| Vocabulary | Values |
|---|---|
| `evidence_status` (per-field evidence rows) | `confirmed`, `TBD-evidence`, `conflict`, `N-A`, `stale-evidence` |
| `gate_status` (freeze checklist gates) | `pass`, `blocked`, `TBD-evidence`, `N-A` |
| `decision-record.status` | `draft`, `shortlisted`, `selected-not-frozen`, `frozen`, `blocked`, `superseded` |
| `selection-map.status` | `active`, `stale`, `closed` |
| `pin-assign-workbench.status` | `draft`, `source-locked`, `mechanical-checked`, `reviewed`, `exported` |
| `mechanical_check_status` | `pass`, `blocked`, `TBD-evidence`, `N-A` |
| `related_records[*].role` | `sidecar`, `source`, `derived`, `superseded` |
| `related_records[*].kind` | any registered `schema_kind` |

`stale-evidence` is added to evidence_status to mark rows that the record author has reclassified after evidence freshness review. The lint scanner does not rewrite records; it warns on stale confirmed rows, or reports them as errors when `--strict-aging` is set.

## Cross-Record References

Records link to each other through `related_records`. Each entry is `(kind, id, role)`:

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

- `sidecar`: 1:1 detail artifact (selection map ↔ decision record).
- `source`: this record depends on the referenced one (pin workbook depends on multiple decisions).
- `derived`: the referenced record was created from this one.
- `superseded`: kept for legacy reference; canonical chain is `supersedes`/`superseded_by`.

The DAG builder follows `related_records`, `supersedes`, `superseded_by`, and `freeze_blockers` to build the cross-record graph.

## Evidence Aging

Lint rule **BD002** scans body evidence-matrix tables and compares the `Evidence date` cell against `created_date - evidence_freshness_window_days`. Behavior:

- Default window: 60 days.
- Settable per-record via frontmatter `evidence_freshness_window_days`.
- Confirmed rows past the window emit warning by default.
- `--strict-aging` flag promotes the warning to an error.
- Lint never mutates body table statuses; changing `confirmed` to `stale-evidence` is an explicit author/reviewer action.

Evidence dates are scanned only in tables whose header includes both `Status` and `Evidence date` columns.

## Lint Rules

Rules grouped by code prefix:

| Prefix | Scope |
|---|---|
| `FM` | Frontmatter envelope (universal across kinds) |
| `EN` | Envelope cross-field consistency |
| `CR` | Decision-record specific consistency |
| `DR` | Decision-record extension validation |
| `SM` | Selection-map extension and consistency |
| `PA` | Pin-assign-workbench extension and consistency |
| `BD` | Body table vocabulary and aging |

Selected rules:

| Rule | Level | Description |
|---|---|---|
| FM001 | error | Required envelope field missing |
| FM002 | error | `record_id` does not match `YYYYMMDD-<slug>` |
| FM010 | warning | `schema_kind` not set; defaulting to `decision-record` |
| FM999 | error | Unsupported `schema_version` |
| EN001 | error | `revision > 1` requires `supersedes` non-null |
| EN002 | error | `review_date` precedes `created_date` |
| EN003 | error | `superseded_by` set but `status != superseded` (or vice versa) |
| CR001 | error | `status: frozen` but `freeze_blockers` non-empty |
| CR002 | error | `status: selected-not-frozen` with empty `freeze_blockers` |
| CR004 | error/warning | `freeze_blocker.due_date` in the past; error for `selected-not-frozen`, warning for earlier non-frozen states |
| CR005 | error | `status: frozen` with non-empty `external_validation_skills_needed` |
| CR006 | error | `status: frozen` without minimum Source Inventory and passing gate evidence in body tables |
| CR007 | error | Body gate table has unresolved statuses but frontmatter has no `freeze_blockers` |
| CR008 | error | `primary_candidate.evidence_status: confirmed` without a matching dated Evidence Matrix row |
| DR001 | error | `evidence_status` not in closed enum |
| SM001 | error | `selection-map` missing `decision_record` reference |
| SM010 | warning | Selection map heuristic recommends one, none referenced |
| PA001 | error | `workbook_path` does not exist (when checked with `--check-paths`) |
| PA002 | error | `status: mechanical-checked` requires `mechanical_check_status: pass` |
| PA003 | error | `status: exported` with non-empty `unresolved_source_conflicts` |
| BD001 | error | Status cell uses value outside allowed enum union |
| BD002 | warning | Evidence row date older than `evidence_freshness_window_days` |
| BD003 | error | Confirmed evidence row has an empty or invalid `Evidence date` |

## Lint Output Formats

```bash
# Human-readable (default)
python tools/scripts/lint_record.py path/to/record.md

# Machine-readable JSON for CI / meta-agent
python tools/scripts/lint_record.py path/to/record.md --format json

# Strict mode: warnings become errors
python tools/scripts/lint_record.py path/to/record.md --strict

# Strict aging: BD002 warnings become errors; records are not rewritten
python tools/scripts/lint_record.py path/to/record.md --strict-aging

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
        {"rule": "CR001", "level": "error",
         "location": "frontmatter:status",
         "message": "status=frozen requires empty freeze_blockers; 2 blocker(s) present"}
      ]
    }
  ],
  "exit_code": 1
}
```

## DAG Builder

`tools/scripts/build_blocker_dag.py` walks a directory, parses every record with valid frontmatter, and builds the cross-record graph for downstream consumption.

```bash
# Walk a project's decisions and emit JSON
python tools/scripts/build_blocker_dag.py hardware-projects/prj/mainboard-r3/decisions/ \
    --format json > mainboard-r3-dag.json

# Mermaid for human review
python tools/scripts/build_blocker_dag.py hardware-projects/prj/mainboard-r3/decisions/ \
    --format mermaid > mainboard-r3-dag.mmd
```

JSON shape (DAG schema_version 1):

```json
{
  "schema_version": 1,
  "kind": "blocker-dag",
  "generated_at": "2026-05-10T14:32:00+08:00",
  "scope": "hardware-projects/prj/mainboard-r3/decisions/",
  "milestones": [
    {
      "id": "20260510-mainboard-r3-lpddr5-x16",
      "schema_kind": "decision-record",
      "project": "mainboard-r3",
      "status": "selected-not-frozen",
      "freeze_target_date": "2026-07-01",
      "tasks": [
        {"id": "fb-pcn-window", "owner": "procurement",
         "due_date": "2026-05-25", "field": "lifecycle"}
      ],
      "external_dependencies": [
        {"skill": "si-channel-budget", "reason": "6400mtps-channel-loss-margin"}
      ]
    }
  ],
  "edges": [
    {"from": "20260510-mainboard-r3-lpddr5-x16",
     "to": "20260520-mainboard-r3-lpddr5-pinout",
     "kind": "derived"},
    {"from": "20260510-mainboard-r3-lpddr5-x16",
     "to": "20260510-mainboard-r3-lpddr5-selection-map",
     "kind": "sidecar"}
  ],
  "errors": []
}
```

The CPM critical-path computation belongs in `hwpm`; this builder produces the input data only.

## Versioning

`schema_version: 1` covers the universal envelope, all three kinds, evidence aging, and cross-record refs as documented here. Future breaking changes increment the version and require a migration script under `tools/scripts/migrate_v<N>_to_v<N+1>.py`.

The lint validates `schema_version` first; unknown versions exit code 2 (parse failure) so CI routes to the migration step rather than treating it as a content failure.

## Composition With Meta-Agent

The closed loop:

```
1. Skill workflow (LLM)              writes Markdown record with frontmatter
2. lint_record.py --strict --stamp   gates on schema and consistency
3. build_blocker_dag.py              walks records, emits JSON
4. hwpm / meta-agent / dashboard     consume JSON, compute CPM, route tasks
5. external skill (si, emif, ...)    runs validation, produces artifact
6. Skill workflow updates body       evidence row goes confirmed
7. lint_record.py                    re-validates structure before status -> frozen
8. build_blocker_dag.py rebuilds     downstream tools see updated graph
```

Steps 2-4 and 7-8 require no LLM. The LLM is constrained to steps 1 and 6, where its strengths (synthesis, narrative, judgment under ambiguity) actually pay off. Routing, filtering, dependency tracking, and structural freeze checks are deterministic; engineering truth still comes from dated evidence and owner review.

This is the architectural payoff: the schema turns each skill into an addressable node in a DAG, and the meta-agent becomes a graph walker rather than an LLM-in-the-loop traffic cop.
