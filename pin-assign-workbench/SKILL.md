---
name: pin-assign-workbench
description: Use only for deliverable-grade hardware pin/net assignment workbooks when the user asks to create or audit Excel/CSV/OrCAD/Allegro pin-net tables from authoritative pinouts, package ballouts, placement rules, and schematic symbol order. Do not use for casual pin lookups, component selection, layout/SI advice, or questions without a pin/net deliverable.
---

# Pin Assign Workbench

## Core Rule

Never produce final pin/net tables from memory alone. Identify the authoritative source for every mapping, preserve schematic-symbol order, and emit a reviewable Excel workbook with sources, assumptions, validation checks, and unresolved conflicts.

## Activation Boundary

Use this skill only when the expected output is a concrete pin/net deliverable: an Excel workbook, CSV, OrCAD/Allegro off-page connector list, schematic-symbol-order table, or audit report. Prefer explicit user invocation while this skill is still being proven. Do not use it for package selection, simple datasheet lookup, broad schematic review, SI/layout advice, or FPGA IP configuration discussion unless the user also asks for a pin/net mapping artifact.

## Workflow

1. **Set the target.** Capture device part/package, interface topology, package option, CAD tool, schematic symbol order, desired net naming, and output format.
2. **Gather sources.** Follow `references/source-policy.md`. Search user-provided files and local knowledge bases before web search. Use vendor official documents for final pinout/ballout/electrical claims.
3. **Build the mapping chain.** Keep logical rules separate from package pins:
   - logical signal or IP rule
   - internal placement index or lane
   - FPGA/SoC package pin or ball
   - peripheral package pin or ball
   - schematic net name
4. **Align to schematic order.** Use the user's OrCAD/Allegro symbol order as the output order. Do not default to datasheet order when the user is drawing a schematic.
5. **Classify nets.** Separate data groups, clocks/strobes, address/control, reset, local-only pins, FPGA-only pins, power/ground, NC, and RFU.
6. **Generate Excel.** Use `references/workbook-pattern.md` for sheet structure. Use `assets/pin-assign-template.xlsx` when starting a new workbook.
7. **Validate.** Apply `references/validation-checklist.md`. Use `scripts/format_pin_workbook.py` only for deterministic formatting/checking; do not let scripts make engineering judgments.
8. **Explain the result.** Add a source/workflow note in the workbook and summarize assumptions, conflicts, and required FAE/Quartus/SI/layout confirmations.

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
- Short explanation suitable for FAE, schematic review, and layout handoff.

## References

- Read `references/source-policy.md` before searching for documents or citing sources.
- Read `references/workbook-pattern.md` before creating or restructuring Excel outputs.
- Read `references/schematic-output-patterns.md` when producing OrCAD/Allegro off-page connector tables.
- Read `references/validation-checklist.md` before final delivery.
- Read `references/memory-interface-notes.md` for DDR/LPDDR-specific traps such as x32 vs 2ch x16, shared/T-line nets, ZQ, RZQ, REFCLK, NC, and RFU.

## Bundled Tools

- `assets/pin-assign-template.xlsx`: starter workbook with recommended sheet names.
- `scripts/format_pin_workbook.py`: styles a workbook and creates a mechanical check sheet for duplicate nets, blank pin/net mismatches, and duplicate pins.
