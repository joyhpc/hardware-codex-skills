# hardware-codex-skills

Reusable Codex skills for hardware engineering workflows.

This repository contains **method-level AI skills**, not project records and not a component database. Its purpose is to make hardware work more repeatable when the same kind of engineering decision appears across projects.

## Why This Exists

Hardware decisions often fail in the handoff between research, procurement, design, and validation. A normal AI answer may recommend a part, but a real hardware freeze needs more:

- requirements split into hard constraints and changeable constraints
- candidate classes such as `Primary`, `Backup`, `Watchlist`, and `Rejected`
- evidence gaps that cannot be filled from model memory
- supplier, distributor, FAE, procurement, and tool-validation follow-up paths
- freeze blockers that are explicit enough for schematic, BOM, pinout, and PCB work

These skills turn that process into reusable structure.

## Current Skills

### `critical-component-selection`

Use this skill for freeze-grade component selection where the choice may enter schematic, BOM, pin assignment, layout, lifecycle planning, or engineering validation.

Typical triggers:

- critical component selection
- `关键物料选型`
- BOM freeze review
- EOL / PCN replacement
- candidate part-number decision
- supplier feedback versus requirement baseline
- selection evidence map / `选型证据地图`
- communication report / `选型报告` / `沟通报告`

Do not use it for casual comparisons, learning questions, or low-risk part recommendations.

### `pin-assign-workbench`

Use this skill only for deliverable-grade pin/net assignment workflows where an agent must produce or audit a concrete Excel, CSV, OrCAD Capture, Cadence Capture CIS, Allegro DE-HDL off-page connector list, schematic-symbol-order table, or similar pin/net artifact from authoritative sources.

Typical triggers:

- FPGA/SoC to memory or peripheral pin assignment workbook
- package ballout to schematic symbol mapping table
- OrCAD Capture, Capture CIS, or Allegro DE-HDL connector list generation
- schematic-order pin/net Excel or CSV output
- pin assignment audit against vendor rules and source evidence
- `pin assign 工作簿`, `引脚分配表`, `原理图顺序网名表`, `封装 ballout 映射`, `管脚映射审核`

Do not use it for simple one-off pin lookups, package selection, broad schematic review, layout/SI advice, FPGA toolchain constraint files such as QSF/XDC/LPF/SDC unless the user also asks for the Excel review surface, or when no pin/net deliverable is requested.

## Schema Layer and Closed-Loop Tooling

Skills in this repository produce Markdown records that share a common machine-readable contract defined in [`SCHEMA.md`](./SCHEMA.md). Three record kinds are currently registered:

- `decision-record` — produced by `critical-component-selection`
- `selection-map` — sidecar map produced by `critical-component-selection` for complex selections
- `pin-assign-workbench` — sidecar metadata for the .xlsx workbook produced by `pin-assign-workbench`

Each record is a single `.md` file with a YAML frontmatter envelope (identity, lifecycle, graph edges, routing) and a Markdown body (tables, narrative). The envelope is the interface other agents consume; the body is the authoring surface. This separation keeps the LLM's job to what only LLMs do well and pushes routing, filtering, and dependency tracking onto deterministic tooling.

Two scripts live at the repo root and operate across skills:

- **`tools/scripts/lint_record.py`** — validates the envelope, dispatches to kind-specific rules, scans body tables for closed-vocabulary status cells and stale evidence rows, and stamps `last_lint_pass` on success. Supports `--format json` for CI/agent consumption and `--strict-aging` to gate on evidence freshness.
- **`tools/scripts/build_blocker_dag.py`** — walks a directory of records, parses every valid frontmatter, and emits the cross-record graph as JSON or Mermaid. Output feeds `hwpm` CPM, dashboards, or any meta-agent doing route-and-wait orchestration.

These tools are not skills. They are repo-level developer tooling that enforces and consumes the schema contract.

The closed loop:

```text
1. Skill workflow (LLM)              writes Markdown record with frontmatter
2. lint_record.py --strict --stamp   gates on schema and consistency
3. build_blocker_dag.py              walks records, emits JSON
4. hwpm / meta-agent / dashboard     consume JSON, compute CPM, route tasks
5. external skill (si, emif, ...)    runs validation, produces artifact
6. Skill workflow updates body       evidence row goes confirmed
7. lint_record.py                    re-validates; if CR001 passes, status -> frozen
8. build_blocker_dag.py rebuilds     downstream tools see updated graph
```

Steps 2-4 and 7-8 require no LLM. The LLM is constrained to steps 1 and 6, where its strengths actually pay off. See [`SCHEMA.md`](./SCHEMA.md) for the full rule reference, JSON output shapes, and DAG schema.

## Skill Activation Policy

This repository may contain more reusable methods than should be active in a given Codex runtime. Keep new or experimental skills as repository assets first. Install a skill into `~/.codex/skills` only after repeated real tasks show that its trigger boundary is stable and valuable.

Prefer explicit prompts such as `Use pin-assign-workbench...` during incubation. This avoids loading too many hardware workflows by default and reduces routing mistakes.

### Graduation Criteria

A skill graduates from repo asset to default-installed only after all of:

1. Used successfully on at least 3 distinct real projects by the maintainer.
2. The frontmatter `description` has been revised at least once based on observed mis-triggers or missed triggers.
3. All scripts pass a stress test on a known-good real workbook with zero false positives in `Mechanical_Checks`.
4. A second engineer or AI reviewer has audited the skill against this repo's anti-patterns.
5. At least one end-to-end run has produced a workbook that was actually pasted into OrCAD Capture, Cadence Capture CIS, or Allegro DE-HDL and reviewed without skill-induced rework.

Until all criteria pass, prefer explicit invocation: `Use pin-assign-workbench ...`

### Domain Notes Carve-Out

`critical-component-selection` is a project-agnostic selection workflow and should not include domain cheatsheets. Deliverable-production skills such as `pin-assign-workbench` may include narrow domain notes only when the final artifact would otherwise be ambiguous, such as DDR/LPDDR topology distinctions, shared nets, ZQ/RZQ, NC, and RFU handling. Those notes are prompts to verify current vendor documents, not authoritative pinout data.

## What `critical-component-selection` Produces

The skill is designed to produce decision artifacts, not prose-only advice.

Common outputs:

- **Decision Record**: the current decision, candidate classification, risk summary, freeze blockers, and next actions.
- **Hard-Gate Screen**: early pass/block review of orderable identity, package, lifecycle, commercial, toolchain, validation, and substitute gates before ranking.
- **Source Inventory**: the evidence list with trust boundaries.
- **Evidence Matrix**: one candidate-field per row, using `confirmed`, `TBD-evidence`, `conflict`, or `N-A`.
- **Risk Register**: supply, lifecycle, package, SI/PI/thermal, logic/toolchain, cost, and substitute risks with owners.
- **Freeze Checklist**: boolean pre-freeze gate review.
- **Selection Map**: a sidecar map for large investigations with source navigation, candidate funnel, rejection ledger, evidence acquisition plan, and tool-validation map.
- **Communication Report**: audience-specific report for leadership, procurement, supplier/FAE inquiry, or project meetings.

The practical rule: first decide whether the candidate can freeze, then explain why. If lifecycle, price, lead time, MOQ, temperature grade, PCN/EOL state, stock, or validation status is not backed by a dated source, it must stay `TBD-evidence` and cannot support `frozen`.

## What `pin-assign-workbench` Produces

The skill is designed to produce reviewable CAD-facing artifacts, not memory-only pin tables.

Common outputs:

- **Pin/Net Workbook**: source inventory, raw pinout, placement rules, package ballout, schematic order, final pin/net output, checks, and change log.
- **Schematic-Order Table**: rows ordered to match the actual OrCAD/Allegro symbol, not just vendor datasheet order.
- **Off-Page Connector Lists**: grouped by byte lane, control group, local-only, FPGA-only, power/ground, NC, and RFU where applicable.
- **Mechanical Checks**: duplicate net review, duplicate pin review, blank pin/net mismatches, and unresolved source conflicts.
- **Handoff Notes**: assumptions, source IDs, and items requiring FAE, fitter, SI/PI, or layout confirmation.

## Quick Start For Humans

Install a skill by symlinking it into the Codex runtime skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -sfn "$(pwd)/critical-component-selection" \
  "${CODEX_HOME:-$HOME/.codex}/skills/critical-component-selection"
```

Then ask Codex with a task like:

```text
Use critical-component-selection for this LPDDR5 selection. Create a decision record and selection map from the current project evidence.
```

or:

```text
这个是关键物料选型。请按 freeze-grade component selection 做候选分类、证据缺口、风险登记和冻结条件。
```

To create a communication report:

```text
基于当前选型记录，生成一份给采购推进供应商确认的沟通报告。
```

Install `pin-assign-workbench` only after it has proven useful enough for default discovery.
During incubation, prefer explicit prompts:

```text
Use pin-assign-workbench to create a schematic-order pin/net workbook from these FPGA pinout, memory ballout, and OrCAD symbol-order files.
```

To install it:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -sfn "$(pwd)/pin-assign-workbench" \
  "${CODEX_HOME:-$HOME/.codex}/skills/pin-assign-workbench"
```

Until that symlink exists, it remains a repository asset rather than a default runtime skill.

To uninstall it from the runtime skill list:

```bash
unlink "${CODEX_HOME:-$HOME/.codex}/skills/pin-assign-workbench"
```

## Quick Start For AI Agents

When a task matches a skill:

1. Open that skill's `SKILL.md`.
2. Load only the referenced template needed for the current phase.
3. Read project evidence first; browse only for current vendor, lifecycle, PCN, price, stock, standards, or tool-support facts that may have changed.
4. Save real decision artifacts in the project repository, not in this skills repo.
5. Keep unsupported facts as `TBD-evidence`.

For `critical-component-selection`, project artifacts usually belong under a project decision folder such as:

```text
hardware-projects/prj/<project>/decisions/
```

or the closest existing revision decision folder.

## Repository Layout

The repo has two top-level skills plus repo-level schema documentation and tooling:

```text
hardware-codex-skills/
├── README.md
├── SCHEMA.md                                     # Multi-kind schema contract (v1)
├── tools/                                        # Repo-level tooling, not a skill
│   ├── scripts/
│   │   ├── lint_record.py                        # Unified multi-kind lint
│   │   └── build_blocker_dag.py                  # Cross-record DAG builder
│   └── tests/
│       ├── test_lint_record.py
│       └── test_build_dag.py
├── critical-component-selection/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── examples/
│   │   ├── example-decision-record.md            # schema_kind: decision-record
│   │   └── example-selection-map.md              # schema_kind: selection-map
│   └── references/
│       ├── decision-record-template.md           # legacy v1 (no envelope)
│       ├── decision-record-template-v2.md        # current (with envelope)
│       ├── selection-map-template.md             # legacy v1
│       ├── selection-map-template-v2.md          # current
│       ├── communication-report-template.md
│       ├── evidence-matrix-template.md
│       ├── freeze-checklist-template.md
│       ├── risk-register-template.md
│       └── source-inventory-template.md
└── pin-assign-workbench/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/
    │   └── pin-assign-template.xlsx
    ├── examples/
    │   └── example-pin-assign-record.md          # schema_kind: pin-assign-workbench
    ├── references/
    │   ├── pin-assign-record-template.md         # markdown sidecar template
    │   ├── memory-interface-notes.md
    │   ├── schematic-output-patterns.md
    │   ├── source-policy.md
    │   ├── validation-checklist.md
    │   └── workbook-pattern.md
    └── scripts/
        └── format_pin_workbook.py
```

## Validating and Graphing Records

After a skill produces a record, validate it before commit:

```bash
# Lint a single record (human-readable output)
python tools/scripts/lint_record.py \
  hardware-projects/prj/<project>/decisions/<record>.md --stamp

# Strict mode for CI: warnings become errors
python tools/scripts/lint_record.py \
  hardware-projects/prj/<project>/decisions/<record>.md --strict

# JSON output for meta-agent or dashboards
python tools/scripts/lint_record.py \
  hardware-projects/prj/<project>/decisions/*.md --format json
```

Build the cross-record graph for `hwpm` or a project dashboard:

```bash
# Summary view
python tools/scripts/build_blocker_dag.py \
  hardware-projects/prj/<project>/decisions/ --format summary

# JSON for hwpm or other consumers
python tools/scripts/build_blocker_dag.py \
  hardware-projects/prj/<project>/decisions/ --format json > dag.json

# Mermaid for human review
python tools/scripts/build_blocker_dag.py \
  hardware-projects/prj/<project>/decisions/ --format mermaid > dag.mmd
```

Tests live under `tools/tests/`:

```bash
python tools/tests/test_lint_record.py
python tools/tests/test_build_dag.py
```

## Repository Boundaries

Keep this repository clean and reusable:

- Put reusable workflow instructions and templates here.
- Put project decisions, supplier emails, datasheets, PCNs, quotes, and tool outputs in project repositories.
- Put component knowledge, design guides, and domain checklists in the hardware knowledge base.
- Put executable project-management automation in project tooling after repeated use proves the schema is stable.

Do not store project facts, supplier-specific claims, real part-number decisions, credentials, private customer data, or copied datasheet content in this repository.
