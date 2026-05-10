---
# THIS IS EXAMPLE DATA. Identifiers fictional.

schema_version: 1
schema_kind: pin-assign-workbench
record_id: 20260520-mainboard-r3-fpga-mem-pinout
project: mainboard-r3
revision: 1

status: source-locked
created_date: 2026-05-20
review_date: 2026-06-20
maintainer: example-engineer

supersedes: null
superseded_by: null

related_records:
  - kind: decision-record
    id: 20260510-mainboard-r3-lpddr5-x16
    role: source
  - kind: decision-record
    id: 20260420-mainboard-r3-fpga
    role: source

workbook_path: ./mainboard-r3-fpga-mem-pinout.xlsx
schematic_target: orcad
mechanical_check_status: TBD-evidence

source_records:
  - kind: decision-record
    id: 20260510-mainboard-r3-lpddr5-x16
    role: source
  - kind: decision-record
    id: 20260420-mainboard-r3-fpga
    role: source

unresolved_source_conflicts: []

last_lint_pass: null
---

# FPGA ↔ LPDDR5 Pin Assignment Workbook (Example)

> Markdown sidecar for the .xlsx workbook. The .xlsx is the deliverable; this file carries envelope and handoff notes.

## Scope

Pin/net assignment between the FPGA selected in `20260420-mainboard-r3-fpga` and the LPDDR5 device selected in `20260510-mainboard-r3-lpddr5-x16`. The workbook covers byte-lane assignment, ZQ/RZQ, control group routing, off-page connector lists, and mechanical checks.

## Source Inventory

| Source ID | Type | Title | Date | Path | Trust level |
|---|---|---|---|---|---|
| S1 | decision-record | LPDDR5 selection | 2026-05-10 | ../decisions/20260510-mainboard-r3-lpddr5-x16.md | primary |
| S2 | decision-record | FPGA selection | 2026-04-20 | ../decisions/20260420-mainboard-r3-fpga.md | primary |
| S3 | datasheet | FPGA pinout package XYZ | 2026-04-15 | evidence/fpga/pinout-xyz.pdf | primary |
| S4 | datasheet | LPDDR5 ballout 200-FBGA | 2026-04-15 | evidence/lpddr5/ballout-200fbga.pdf | primary |

## Workbook Structure

The .xlsx contains the following sheets, in order:

1. `Source_Inventory` — mirrors the table above, plus access dates and digests.
2. `Raw_Pinout` — vendor-original pinout for FPGA package XYZ.
3. `Raw_Ballout` — vendor-original ballout for LPDDR5 200-FBGA.
4. `Placement_Rules` — byte-lane swap policy, address/control group rules.
5. `Schematic_Order` — rows ordered to match the OrCAD symbol order, not vendor datasheet order.
6. `Final_Pin_Net` — canonical pin/net assignment.
7. `Mechanical_Checks` — duplicate net review, blank pin/net mismatches.
8. `Change_Log` — all edits since `created_date` with reason and source.

## Mechanical Checks

| Check | Status |
|---|---|
| Duplicate nets | TBD-evidence |
| Duplicate pins | TBD-evidence |
| Blank pin/net mismatches | TBD-evidence |
| Unresolved source conflicts | pass |

When all checks reach `pass`, advance frontmatter `mechanical_check_status: pass` and `status: mechanical-checked`.

## Handoff Notes

- Byte-lane swap is permitted on lanes 0/1; lanes 2/3 are constrained by FPGA physical bank assignment per S3.
- ZQ/RZQ resistor placement under FAE confirmation (open question).
- NC and RFU pins handled per pin-assign-workbench `references/memory-interface-notes.md`.

## Outstanding Questions

- FAE confirmation needed for ZQ resistor value at 6400 MT/s.
- SI engineer to confirm whether trace-length matching tolerances differ between byte-lane 0 and 1 after layout pass.
