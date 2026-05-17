# Repository Architecture

This document is the architectural entry point for `hardware-codex-skills`.
It describes what lives in the repository, how the pieces interact, and which
files are authoritative when documentation and behavior disagree.

## Purpose

The repository packages reusable hardware-engineering workflows for Codex. It
does not hold project facts. Its job is to turn ambiguous, evidence-heavy work
into reviewable artifacts with stable machine-readable envelopes.

The core loop is:

```text
Project evidence
  -> Codex skill instructions
     -> Markdown record with YAML frontmatter
        -> record linter
           -> blocker DAG builder
              -> downstream project tools or meta-agents
```

The model handles ambiguity: synthesis, evidence reconciliation, rationale, and
communication. Deterministic tools handle structure: schema parsing, vocabulary
checks, stale-evidence warnings, workbook mechanics, and graph extraction.

## Source Of Truth

Use this precedence order when maintaining the repository:

| Question | Authoritative file |
|---|---|
| What does the linter actually reject or warn about? | `tools/scripts/lint_record.py` |
| How is frontmatter parsed and which schema kinds exist? | `tools/scripts/schema_lib.py` |
| What graph edges and JSON fields are emitted? | `tools/scripts/build_blocker_dag.py` |
| What does the pin workbook formatter inspect or generate? | `pin-assign-workbench/scripts/format_pin_workbook.py` |
| What should humans write in records? | `SCHEMA.md` plus the relevant skill template |
| What is the repo-level orientation? | `README.md` and this document |

`SCHEMA.md` is the human-facing contract and should mirror the code. If a code
change alters behavior, update `SCHEMA.md`, the relevant templates, and examples
in the same change.

## Layers

### 1. Skills

Skill directories define reusable workflows:

- `critical-component-selection/`
- `pin-assign-workbench/`

Each skill contains:

- `SKILL.md`: trigger boundary, workflow, evidence rules, output behavior, and
  anti-patterns.
- `references/`: templates and local guidance loaded only when needed.
- `examples/`: fictional, lint-clean examples.
- Optional `assets/`, `scripts/`, `tests/`, and `agents/` support files.

Skills must not contain real project decisions, supplier-private data, vendor
claims copied from datasheets, or project-specific pin/net tables.

### 2. Records

A project record is Markdown with YAML frontmatter. The frontmatter is for
machines; the body is for engineers.

Current record kinds:

| `schema_kind` | Role |
|---|---|
| `decision-record` | Component decision with candidates, blockers, validation needs, and freeze state. |
| `selection-map` | Sidecar map for large evidence sets or complex candidate funnels. |
| `pin-assign-workbench` | Sidecar metadata for a pin assignment workbook. |

Records are normally saved in project repositories, not here. The examples in
this repository are fictional fixtures and documentation aids.

### 3. Lint

`tools/scripts/lint_record.py` validates schema v1 records. It checks:

- required universal fields
- schema kind and status vocabularies
- cross-field consistency
- decision freeze blockers and frozen-record readiness
- pin-workbook sidecar consistency
- body tables with a column named exactly `Status`
- confirmed evidence rows with `Evidence date`
- evidence aging relative to `created_date`

Important implementation detail: the body table scanner treats any column named
`Status` as a closed-vocabulary column. If a template needs a local workflow
state such as `to-ask`, `answered`, or `rejected`, the column should be named
something else, such as `Acquisition state` or `Map state`.

### 4. DAG Builder

`tools/scripts/build_blocker_dag.py` reports graph structure from records with
parseable frontmatter. It intentionally does not call the linter. This keeps
partial graph visibility available even when one record has content-level lint
issues.

The DAG builder emits:

- `milestones`: one entry per parsed record.
- `tasks`: freeze blockers from `decision-record` records.
- `external_dependencies`: entries from `external_validation_skills_needed`.
- `edges`: `related_records`, `supersedes`, and `superseded_by` links.
- `unresolved_edge_targets`: outgoing edges whose target record is not in the
  scanned scope.
- `errors`: files that could not be parsed as records.

Critical-path math and scheduling belong downstream, usually in `hwpm` or a
project-management agent.

### 5. Pin Workbook Formatter

`pin-assign-workbench/scripts/format_pin_workbook.py` is a mechanical formatter
and checker for existing workbooks. It:

- styles worksheets
- freezes header panes
- infers pin, net, source, and intentional-duplicate columns from headers
- flags duplicate nets, duplicate pins, missing sources, source review markers,
  and blank pin/net mismatches
- deletes and regenerates `Mechanical_Checks`

It does not infer pin assignments, choose topologies, resolve source conflicts,
or inspect the Markdown sidecar.

## Data Flow

```text
User/project files
  -> skill reads evidence and references
     -> skill writes or updates a project artifact
        -> linter validates record structure
           -> DAG builder extracts graph state
              -> downstream tool routes blockers or displays state
```

For `critical-component-selection`, the main artifact is a `decision-record`.
Complex selections may add a `selection-map`. The linter has a narrow heuristic:
it warns when a decision record has at least three freeze blockers or at least
three backup candidates and no `selection-map` sidecar is referenced. The skill
may recommend a map for broader human reasons such as many sources, routes, or
supplier threads.

For `pin-assign-workbench`, the workbook is the deliverable. The Markdown
sidecar exists so schema tools can route dependencies and track source records.

## Record Link Semantics

Use `related_records` for graph links:

| Role | Meaning |
|---|---|
| `source` | Current record depends on the referenced record. |
| `derived` | Referenced record was created from the current record. |
| `sidecar` | Referenced record is a supporting sidecar. |
| `superseded` | Legacy relation; prefer top-level `supersedes` and `superseded_by`. |

Supersession is represented with top-level fields:

- `supersedes`: prior record id replaced by this record.
- `superseded_by`: later record id that replaces this record.

## Validation Loop

Run this before considering repository changes complete:

```bash
python tools/scripts/doctor.py
```

The doctor script runs:

- linter tests
- DAG builder tests
- pin workbook formatter tests
- example record lint
- example DAG summary

The example DAG currently reports one unresolved target by design: the pin
assignment sidecar references a fictional FPGA decision record outside the
example scope.

## Extension Rules

Add a new workflow only after the existing schema kinds are insufficient in real
project use. A mature addition should include:

- a skill directory with `SKILL.md`
- templates under `references/`
- fictional examples under `examples/`
- deterministic validation or formatting scripts when useful
- tests for scripts and record examples
- `SCHEMA.md` updates for any new `schema_kind`, fields, statuses, or rules
- `docs/architecture.md` and `README.md` updates when architecture changes

Do not add deterministic scripts that make engineering judgments, scrape
suppliers, query private systems, or infer hardware decisions. Scripts in this
repository should only parse, validate, format, or report structure.
