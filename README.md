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

## What It Produces

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
└── critical-component-selection/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    └── references/
        ├── decision-record-template.md
        ├── communication-report-template.md
        ├── evidence-matrix-template.md
        ├── freeze-checklist-template.md
        ├── risk-register-template.md
        ├── selection-map-template.md
        └── source-inventory-template.md
```

## Repository Boundaries

Keep this repository clean and reusable:

- Put reusable workflow instructions and templates here.
- Put project decisions, supplier emails, datasheets, PCNs, quotes, and tool outputs in project repositories.
- Put component knowledge, design guides, and domain checklists in the hardware knowledge base.
- Put executable project-management automation in project tooling after repeated use proves the schema is stable.

Do not store project facts, supplier-specific claims, real part-number decisions, credentials, private customer data, or copied datasheet content in this repository.
