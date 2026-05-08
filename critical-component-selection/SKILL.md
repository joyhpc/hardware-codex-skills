---
name: critical-component-selection
description: >-
  Use this skill when the user is making a freeze-grade component selection decision for hardware where the choice will be locked into schematic/BOM/pin assignment and at least two critical conditions apply: multi-year lifecycle/EOL/PCN/lead-time risk, toolchain verification such as EMIF/fitter/SI/PI/thermal, pinout/power/SI/thermal architecture impact, or vendor evidence that must be reconciled against requirements. Triggers include: 关键物料选型, BOM 冻结前评审, EOL/PCN 替代, 候选料号决策, 选型证据地图, selection map, 选型报告, 沟通报告, procurement brief, supplier inquiry, leadership brief, vendor 反馈与需求基线对账. Do NOT use for casual comparisons, learning questions, architecture sketches, or selections that do not require evidence reconciliation and freeze conditions.
---

# Critical Component Selection

## Purpose

Drive hardware component choices that are serious enough to freeze into schematic, BOM, pin assignment, or layout constraints. Treat the skill as a per-decision workflow, not a project database.

Keep project facts outside the skill. Use `CONTEXT_INDEX.md` when present, project folders such as `hardware-projects/prj/<project>/`, vendor files, datasheets, PCNs, and current email/procurement evidence as the source of truth.

## Entry Phase

Identify the current entry phase before producing output:

1. New requirement: create the requirement baseline first.
2. Vendor substitute or feedback: update candidates, evidence gaps, and risk deltas.
3. Existing shortlist: compare candidates, classify them, and recommend next action.
4. Pre-freeze review: run the freeze checklist and list blockers.
5. Post-decision update: update the decision record, risks, and review date.

Trim output to the active phase. Do not repeat all seven workflow steps when the user only needs an increment, but mention any missing prerequisite that blocks the phase.

## Evidence Rules

Never assert specific lifecycle, price, lead time, MOQ/MPQ, temperature grade, stock status, PCN/EOL status, tool support, or validation pass/fail from model memory.

For every concrete component fact, cite one of:

1. Datasheet section or table.
2. PCN/EOL number and date.
3. Vendor or distributor URL with access date.
4. Supplier email or message with date and sender.
5. Tool output file, report, or run date.
6. Project decision record or requirements file.

Mark unknown or unsupported fields exactly as `TBD-evidence`. Mark contradictions as `conflict`. Do not soften either state in prose.

## Workflow Checklist

1. Requirement baseline: identify hard constraints, changeable constraints, target lifetime, and acceptance criteria.
2. Source inventory: list source IDs before making component claims.
3. Hard-gate screen: reject candidates that fail non-negotiable constraints or lack required evidence.
4. Candidate evidence matrix: compare one field for one candidate per row using evidence status, not confidence language.
5. Candidate classification: assign each candidate to `Primary`, `Backup`, `Rejected`, or `Watchlist`.
6. Risk register: record supply, EOL, package/pinout, SI/PI/thermal, firmware/logic, cost, and substitute risks with mitigation owners.
7. Engineering verification gate: state this decision's required validation, owner, pass criteria, and output artifact; do not assume device-category-specific gates.
8. Decision and freeze path: recommend one next decision, list freeze blockers, and propose where to save the record.

## Selection Map Sidecar

Create a project-layer Selection Map when the selection has many datasheets, PCNs, overview files, supplier messages, or more candidate routes than can usefully fit in the decision record.

The map is not a catalog of every part number. It exists to help the next selection step by preserving:

1. Source navigation: where evidence lives and what conclusion it supports.
2. Candidate funnel: `Primary`, `Backup`, `Watchlist`, `Rejected`, and `Closed` routes at the useful family or route level.
3. Requirement coverage: which hard constraints are confirmed, conflicted, or still `TBD-evidence`.
4. Rejection rationale: why a route was excluded and what evidence would reopen it.
5. Evidence acquisition plan: who should ask the original vendor, distributor, FAE, procurement, internal owner, or tool/lab path for missing evidence.
6. Tool validation map: what engineering validation must produce before freeze.

Treat "ask the vendor/distributor/procurement" as an evidence-acquisition reminder only. Do not present a question as answered until a dated source with sender, channel, exact subject, and answer is available and cited in the evidence matrix.

## Communication Reports

Create a report when the user needs to communicate the selection state to leadership, procurement, suppliers, FAEs, or a project meeting.

Reports are derived artifacts. They must point back to the decision record, selection map, or evidence matrix and must not introduce new facts. Always keep the current decision strength visible, such as `selected-not-frozen`, `frozen`, or `blocked`.

Choose the report audience before writing:

1. Leadership brief: emphasize decision ask, business impact, top options, top blockers, and deadline.
2. Procurement brief: emphasize exact evidence gaps, supplier questions, required answer format, owners, and dates.
3. Supplier / FAE inquiry: ask only the external-safe questions needed to close evidence gaps; avoid internal rankings, cost targets, competitor details, and unapproved architecture disclosure.
4. Project meeting brief: emphasize current status, decisions needed, blockers, owners, and next review.

Do not paste the full evidence matrix into a report unless explicitly requested. Use the smallest evidence summary that supports the communication goal.

Use hardware freeze semantics:

1. `draft`: still shaping requirements or candidates.
2. `shortlisted`: candidates are identified but no primary decision exists.
3. `selected-not-frozen`: primary candidate chosen for engineering/procurement work, but freeze blockers remain.
4. `frozen`: approved for schematic/BOM/pin/layout freeze with all non-N-A gates passed.
5. `blocked`: cannot proceed without named evidence or architecture change.
6. `superseded`: replaced by a later decision record.

If any hard constraint lacks evidence, the strongest allowed status is `selected-not-frozen`, never `frozen`.

## Output Behavior

Default to phase-trimmed output. Include only the sections needed for the current entry phase, plus `Evidence Gaps`, `Recommendation`, and `Next Actions` when applicable.

Use the full formal schema only when the user asks to create a decision record, run a freeze review, or save a project artifact.

Use a Selection Map sidecar when the user asks for a map, when the evidence set is too large for the decision record, or when future agents need a navigation artifact to continue the selection.

Use a Communication Report when the user asks for a report, meeting brief, leadership update, procurement action note, supplier inquiry, or FAE question list derived from the selection.

Full formal schema:

1. `Decision Objective`
2. `Entry Phase`
3. `Source Inventory`
4. `Requirement Baseline`
5. `Candidate Classification`
6. `Evidence Matrix`
7. `Evidence Gaps`
8. `Risk Register`
9. `Engineering Verification Gates`
10. `Recommendation`
11. `Freeze Checklist`
12. `Record Location`
13. `Next Actions`

## Workspace Interface

When working inside an existing workspace:

1. Read `CONTEXT_INDEX.md` first if it exists and the project/component is ambiguous.
2. Search project evidence before browsing the web. Browse only when current vendor, lifecycle, PCN, price, stock, standard, or tool support facts may have changed.
3. Suggest saving the final decision to `hardware-projects/prj/<project>/decisions/<YYYYMMDD>-<component>-selection.md` or the closest existing project decision folder.
4. Suggest adding a pointer to `CONTEXT_INDEX.md` after the decision record exists.
5. Do not store real project facts, vendor-specific cheatsheets, or concrete part numbers in this skill.

## References

Load only the template needed for the active phase:

1. `references/source-inventory-template.md` for source IDs and source trust boundaries.
2. `references/evidence-matrix-template.md` for candidate evidence comparison.
3. `references/risk-register-template.md` for structured risk capture.
4. `references/decision-record-template.md` for the final selection record.
5. `references/freeze-checklist-template.md` for pre-freeze gate review.
6. `references/selection-map-template.md` for large evidence sets, candidate funnels, rejection ledgers, evidence acquisition reminders, and tool-validation navigation.
7. `references/communication-report-template.md` for leadership, procurement, supplier/FAE, and project-meeting reports derived from the selection artifacts.

## Anti-Patterns

Do not include in this skill:

1. Real project data or real part-number examples.
2. Vendor-specific lifecycle claims.
3. Domain cheatsheets such as DDR pinout rules, PMIC compensation recipes, or connector SI tables.
4. Scripts that parse datasheets, query suppliers, or scrape PCNs; those belong in project tooling after repeated use proves the schema is stable.
