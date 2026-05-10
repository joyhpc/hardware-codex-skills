---
name: pin-assign-workbench
description: >-
  Use only when the user requests a deliverable-grade pin/net assignment artifact in Excel/CSV form for OrCAD Capture, Cadence Capture CIS, or Allegro DE-HDL schematic drawing, including FPGA/SoC-to-memory or peripheral pin assignment workbooks, package ballout to schematic-symbol-order mapping tables, off-page connector lists for batch paste, and pin assignment audits against vendor official sources. Triggers include: pin assign 工作簿, 引脚分配表, 原理图顺序网名表, OrCAD off-page connector 表, 封装 ballout 映射, 管脚映射审核, schematic-order pin/net workbook, ballout-to-symbol mapping. Do NOT use for casual pin lookups, single datasheet questions, component or package selection, layout/SI/PI advice, FPGA toolchain constraint files such as QSF/XDC/LPF/SDC unless the user also asks for the Excel review surface, or requests without a concrete pin/net deliverable.
---

# Pin Assign Workbench

## Core Rule

Never produce final pin/net tables from memory alone. Identify the authoritative source for every mapping, preserve schematic-symbol order, and emit a reviewable Excel workbook with sources, assumptions, validation checks, and unresolved conflicts.

Use Excel as the primary review surface unless the user explicitly asks for another format.

## Evidence Rules

Never assert FPGA pin/ball, package ball, bank, signal type, I/O standard, voltage rail, direction, or NC/RFU status from model memory.

For every row in `Pin_Net_Output`, cite a `Source ID` that resolves to one of:

- Vendor official document, section/table/figure, with revision/date.
- User-provided file path, version, and date received.
- FAE/vendor message with sender, date, and subject.
- Tool report such as Quartus EMIF, Vivado I/O planner, or fitter output with run date.

Mark unknown or unsupported cells exactly as `TBD-source`. Mark contradictions between sources exactly as `conflict`. Do not soften either state in prose.

If no sources are provided and none can be located, refuse to produce a final `Pin_Net_Output`; return only `Inputs`, `Sources`, and the required document list.

## Activation Boundary

Use this skill only when the expected output is a concrete pin/net deliverable: an Excel workbook, CSV, OrCAD Capture or Allegro DE-HDL off-page connector list, schematic-symbol-order table, or audit report. Prefer explicit user invocation while this skill is still being proven. Do not use it for package selection, simple datasheet lookup, broad schematic review, SI/layout advice, FPGA IP configuration discussion, or QSF/XDC/LPF/SDC generation unless the user also asks for a pin/net mapping artifact.

## Source Gap Gate

Before building `Pin_Net_Output`, perform a source gap review from the user's stated target and available files. Identify which required source classes are present, missing, stale, or conflicting:

- FPGA/SoC package pinout and bank/package pin numbers.
- FPGA/IP placement, lane, byte, polarity, swap, or topology rules needed for the interface.
- Peripheral, connector, module, or memory package pinout/ballout.
- Schematic symbol order or CAD-exported pin list.
- Project constraints such as voltage bank, device instance naming, net prefix, and CAD paste format.

Search user-provided files and local knowledge bases first. Browse only for missing, stale, or conflicting source classes, and prefer vendor official documents. If a required source class remains missing, list it in `Required Documents`, mark affected cells `TBD-source`, and do not present the final table as complete.

## Workflow

1. **Set the target.** Capture device part/package, interface topology, package option, CAD tool, schematic symbol order, desired net naming, and output format.
2. **Gather sources.** Follow `references/source-policy.md`. Search user-provided files and local knowledge bases before web search. Use vendor official documents for final pinout/ballout/electrical claims.
3. **Review source gaps.** Apply the Source Gap Gate. Decide whether local evidence is sufficient or whether official documents must be found online before final mapping.
4. **Build the mapping chain.** Keep logical rules separate from package pins:
   - logical signal or IP rule
   - internal placement index or lane
   - FPGA/SoC package pin or ball
   - peripheral package pin or ball
   - schematic net name
5. **Align to schematic order.** Use the user's OrCAD/Allegro symbol order as the output order. Do not default to datasheet order when the user is drawing a schematic.
6. **Classify nets.** Separate data groups, clocks/strobes, address/control, reset, local-only pins, FPGA-only pins, power/ground, NC, and RFU.
7. **Generate Excel.** Use `references/workbook-pattern.md` for sheet structure. Use `assets/pin-assign-template.xlsx` when starting a new workbook.
8. **Validate.** Apply `references/validation-checklist.md`. Use `scripts/format_pin_workbook.py` only for deterministic formatting/checking; do not let scripts make engineering judgments.
9. **Create the schema sidecar when the workbook is a project artifact.** Use `references/pin-assign-record-template.md` to write a Markdown sidecar with `schema_kind: pin-assign-workbench`, `workbook_path`, `source_records`, and `related_records` so the repo-level schema tools can route dependencies.
10. **Explain the result.** Add a source/workflow note in the workbook and summarize assumptions, conflicts, and required FAE/Quartus/SI/layout confirmations.

## Source Discipline

- Stop and surface conflicts between sources. Do not silently choose one.
- Distributor pages may identify part numbers and availability, but they are not authoritative for ballout or pin assignment.
- Open-source schematics are cross-checks or examples unless the user explicitly accepts them as a design basis.
- If a PDF figure cannot be reliably extracted, mark that section as manually/visually verified.

## Common Outputs

- FPGA/SoC symbol-order pin/net table.
- Peripheral package pin/net table.
- Off-page connector lists grouped by byte lane, control group, local-only, and FPGA-only signals.
- Review workbook with `Sources`, `Assumptions`, `Checks`, and `Change_Log`.
- Markdown sidecar record with `schema_kind: pin-assign-workbench` for the workbook when downstream agents need routeable metadata.
- Short explanation suitable for FAE, schematic review, and layout handoff.

## References

- Read `references/source-policy.md` before searching for documents or citing sources.
- Read `references/workbook-pattern.md` before creating or restructuring Excel outputs.
- Read `references/schematic-output-patterns.md` when producing OrCAD Capture, Capture CIS, or Allegro DE-HDL connector tables.
- Read `references/validation-checklist.md` before final delivery.
- Read `references/memory-interface-notes.md` for DDR/LPDDR-specific traps such as x32 vs 2ch x16, shared/T-line nets, ZQ, RZQ, REFCLK, NC, and RFU.
- Read `references/pin-assign-record-template.md` and repo-root `../SCHEMA.md` when saving a routeable workbook sidecar record.

## Bundled Tools

- `assets/pin-assign-template.xlsx`: starter workbook with recommended sheet names.
- `scripts/format_pin_workbook.py`: styles a workbook and creates a mechanical check sheet for duplicate nets, blank pin/net mismatches, and duplicate pins.
- `../tools/scripts/lint_record.py`: validates the Markdown workbook sidecar when one is created. It does not infer pin assignments or inspect workbook contents.

## Anti-Patterns

Do not include in this skill:

1. Real project ballout/pinout tables, net naming conventions, or symbol files.
2. Vendor- or part-specific cheatsheets beyond the limited DDR/LPDDR notes in `references/memory-interface-notes.md`, which exists only because correct deliverables for memory interfaces require topology disambiguation.
3. Scripts that infer pin assignments, choose topologies, or call external APIs. Scripts here only style workbooks and emit mechanical checks.
4. OrCAD project files (`.opj`, `.dsn`, `.olb`) or Allegro DE-HDL design files.
5. Project-specific net prefix tables, such as `LP5_U0_`; those belong in the project repository, not this skill.
