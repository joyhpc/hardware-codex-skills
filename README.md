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
- **Source Inventory**: the evidence list with trust boundaries.
- **Evidence Matrix**: one candidate-field per row, using `confirmed`, `TBD-evidence`, `conflict`, or `N-A`.
- **Risk Register**: supply, lifecycle, package, SI/PI/thermal, logic/toolchain, cost, and substitute risks with owners.
- **Freeze Checklist**: boolean pre-freeze gate review.
- **Selection Map**: a sidecar map for large investigations with source navigation, candidate funnel, rejection ledger, evidence acquisition plan, and tool-validation map.
- **Communication Report**: audience-specific report for leadership, procurement, supplier/FAE inquiry, or project meetings.

The most important rule: if lifecycle, price, lead time, MOQ, temperature grade, PCN/EOL state, stock, or validation status is not backed by a dated source, it must stay `TBD-evidence`.

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

Each top-level directory is one Codex skill:

```text
hardware-codex-skills/
├── README.md
├── critical-component-selection/
│   ├── SKILL.md
│   ├── agents/
│   │   └── openai.yaml
│   └── references/
│       ├── decision-record-template.md
│       ├── communication-report-template.md
│       ├── evidence-matrix-template.md
│       ├── freeze-checklist-template.md
│       ├── risk-register-template.md
│       ├── selection-map-template.md
│       └── source-inventory-template.md
└── pin-assign-workbench/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── assets/
    │   └── pin-assign-template.xlsx
    ├── references/
    │   ├── memory-interface-notes.md
    │   ├── schematic-output-patterns.md
    │   ├── source-policy.md
    │   ├── validation-checklist.md
    │   └── workbook-pattern.md
    └── scripts/
        └── format_pin_workbook.py
```

## Repository Boundaries

Keep this repository clean and reusable:

- Put reusable workflow instructions and templates here.
- Put project decisions, supplier emails, datasheets, PCNs, quotes, and tool outputs in project repositories.
- Put component knowledge, design guides, and domain checklists in the hardware knowledge base.
- Put executable project-management automation in project tooling after repeated use proves the schema is stable.

Do not store project facts, supplier-specific claims, real part-number decisions, credentials, private customer data, or copied datasheet content in this repository.
