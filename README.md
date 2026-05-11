# hardware-codex-skills

Reusable Codex skills and schema tooling for hardware engineering workflows.

This repository is not a component database and does not store project records. It contains reusable method-level skills, record schemas, examples, and deterministic tooling that make hardware decisions easier to review, route, and hand off across agents.

## Repository Role

Hardware work often breaks at handoff boundaries: research says one thing, procurement has another source, design needs a freeze decision, and validation still has open artifacts. This repo gives those workflows a common shape:

1. A skill creates a record from project evidence.
2. The record exposes a YAML frontmatter envelope for machines.
3. The Markdown body remains readable for engineers.
4. Lint checks structure, status vocabulary, stale evidence dates, and empty-shell freeze patterns.
5. The DAG builder turns records and blockers into graph data for `hwpm`, dashboards, or a meta-agent.

Lint is a structural and anti-shell gate. It does not prove that a vendor claim, quote, PCN, SI margin, or validation artifact is true. Engineering truth still comes from dated sources, validation artifacts, and owner review.

## Current Skills

### `critical-component-selection`

Use for freeze-grade component decisions where a choice may enter schematic, BOM, pin assignment, layout, sourcing, lifecycle planning, or validation work.

Typical uses:

- critical component selection
- BOM freeze review
- EOL, PCN, or supplier substitute decision
- candidate part-number decision
- shortlist review
- vendor feedback against a requirement baseline
- selection evidence map
- procurement, supplier, FAE, leadership, or project-meeting brief

Do not use it for casual comparisons, learning questions, broad architecture sketches, or low-risk recommendations that do not require evidence reconciliation.

### `pin-assign-workbench`

Use for deliverable-grade pin/net assignment workflows where the expected output is an Excel/CSV workbook, schematic-order table, off-page connector list, or audit surface.

Typical uses:

- FPGA/SoC to memory or peripheral pin assignment workbook
- package ballout to schematic-symbol-order mapping
- OrCAD Capture, Cadence Capture CIS, or Allegro DE-HDL connector list generation
- schematic-order pin/net Excel or CSV output
- pin assignment audit against authoritative sources

Do not use it for simple pin lookups, package selection, broad schematic review, layout/SI advice, or FPGA constraint files unless the user also asks for a pin/net mapping artifact.

## Architecture

The repo has four layers:

```text
skill instructions
  -> Markdown records with YAML frontmatter
     -> lint_record.py
        -> build_blocker_dag.py
           -> hwpm / meta-agent / dashboard
```

### Layer 1: Skills

Skills define the workflow and evidence discipline. They should not include project facts, supplier claims, copied datasheet content, credentials, or real part-number decisions.

### Layer 2: Record Schema

[`SCHEMA.md`](./SCHEMA.md) defines the shared record contract. Current `schema_kind` values:

- `decision-record`: produced by `critical-component-selection`.
- `selection-map`: sidecar map for complex component selections.
- `pin-assign-workbench`: sidecar metadata for a pin assignment workbook.

Each record is a single Markdown file with:

- YAML frontmatter for identity, lifecycle state, routing, blockers, and graph links.
- Markdown body for source inventory, evidence matrix, gates, risks, rationale, and handoff notes.

### Layer 3: Lint

[`tools/scripts/lint_record.py`](./tools/scripts/lint_record.py) validates records.

It checks:

- required frontmatter fields
- schema version and kind
- closed status vocabularies
- cross-field consistency
- decision freeze blockers
- empty-shell `frozen` records
- body table status cells
- evidence aging and missing evidence dates
- JSON output for CI or agents

It does not parse datasheets, query suppliers, scrape PCNs, infer pin assignments, or make engineering judgments.

### Layer 4: DAG Builder

[`tools/scripts/build_blocker_dag.py`](./tools/scripts/build_blocker_dag.py) walks record directories and emits a graph of records, blockers, supersession links, and sidecar/source/derived links.

The DAG builder does not compute critical paths. CPM belongs in `hwpm`; this repo only emits clean input data.

## Closed Loop

```text
1. Skill workflow writes or updates a record from project evidence.
2. lint_record.py checks schema and structural consistency.
3. build_blocker_dag.py emits graph data.
4. hwpm / meta-agent / dashboard consumes the graph.
5. External validation skill or project owner produces an artifact.
6. Skill workflow updates the body evidence matrix and blockers.
7. lint_record.py re-validates before status advances.
8. build_blocker_dag.py rebuilds downstream graph state.
```

The LLM should work where ambiguity exists: synthesis, evidence reconciliation, rationale, and communication. Deterministic tooling should handle routing, filtering, dependency tracking, and structural gates.

## Skill Activation Policy

Keep new or experimental skills as repository assets first. Install a skill into `~/.codex/skills` only after repeated real tasks show that the trigger boundary is stable and valuable.

Graduation criteria:

1. Used successfully on at least 3 distinct real projects.
2. The `description` trigger boundary has been revised after observed missed triggers or false triggers.
3. Bundled scripts pass stress tests on known-good artifacts.
4. A second engineer or AI reviewer has audited the skill against repo anti-patterns.
5. At least one end-to-end output has been used in the real downstream tool without skill-induced rework.

Until then, prefer explicit invocation such as `Use critical-component-selection...` or `Use pin-assign-workbench...`.

## Repository Layout

```text
hardware-codex-skills/
|-- README.md
|-- SCHEMA.md
|-- tools/
|   |-- scripts/
|   |   |-- lint_record.py
|   |   `-- build_blocker_dag.py
|   `-- tests/
|       |-- test_lint_record.py
|       `-- test_build_dag.py
|-- critical-component-selection/
|   |-- SKILL.md
|   |-- agents/
|   |   `-- openai.yaml
|   |-- examples/
|   |   |-- example-decision-record.md
|   |   `-- example-selection-map.md
|   |-- references/
|   |   |-- communication-report-template.md
|   |   |-- decision-playbook.md
|   |   |-- decision-record-template.md
|   |   |-- evidence-matrix-template.md
|   |   |-- freeze-checklist-template.md
|   |   |-- risk-register-template.md
|   |   |-- selection-map-template.md
|   |   `-- source-inventory-template.md
|   `-- scripts/
|       `-- lint_decision_record.py
`-- pin-assign-workbench/
    |-- SKILL.md
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    |   `-- pin-assign-template.xlsx
    |-- examples/
    |   `-- example-pin-assign-record.md
    |-- references/
    |   |-- memory-interface-notes.md
    |   |-- pin-assign-record-template.md
    |   |-- schematic-output-patterns.md
    |   |-- source-policy.md
    |   |-- validation-checklist.md
    |   `-- workbook-pattern.md
    `-- scripts/
        `-- format_pin_workbook.py
```

`critical-component-selection/scripts/lint_decision_record.py` is an old-path compatibility shim. The canonical linter is `tools/scripts/lint_record.py`.

## Validation Commands

Lint records:

```bash
python tools/scripts/lint_record.py path/to/record.md
python tools/scripts/lint_record.py path/to/records/ --strict
python tools/scripts/lint_record.py path/to/records/ --format json
```

Build a graph:

```bash
python tools/scripts/build_blocker_dag.py path/to/records/ --format summary
python tools/scripts/build_blocker_dag.py path/to/records/ --format json > dag.json
python tools/scripts/build_blocker_dag.py path/to/records/ --format mermaid > dag.mmd
```

Run tests:

```bash
python tools/tests/test_lint_record.py
python tools/tests/test_build_dag.py
```

## Boundaries

Put reusable workflow instructions, schemas, templates, examples, and deterministic format/lint tools here.

Do not put these in this repo:

- real project decisions
- supplier emails
- datasheets or copied datasheet content
- PCNs, quotes, stock snapshots, or credentials
- customer-private information
- component knowledge base entries
- project-specific net names, pin tables, or CAD project files
- scripts that query suppliers, scrape PCNs, or infer engineering decisions

Project facts belong in project repositories. Component knowledge belongs in the hardware knowledge base. Project-management automation belongs in project tooling after repeated use proves the schema is stable.

## Development Direction

Near-term development should make the current contract more useful before adding new kinds:

1. Keep documentation synchronized with real files and actual tool behavior.
2. Extract shared schema parsing into `tools/scripts/schema_lib.py`.
3. Add reference resolution and cycle detection for cross-record graphs.
4. Dogfood `critical-component-selection` on real decisions and feed friction back into `decision-playbook.md`.
5. Decide whether `pin-assign-workbench` metadata should remain a Markdown sidecar or move into workbook `_Metadata`.

Do not add new `schema_kind` values until the current three have been used through real project cycles.
