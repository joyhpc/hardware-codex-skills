# Validation Checklist

Run this before delivery.

## Source Completeness

- Every mapping has a source: pinout, placement rule, package ballout, schematic order, or user instruction.
- Source sheet includes title, revision/date, path/URL, and table/figure/section.
- Non-authoritative references are labeled as examples or cross-checks.
- `Pin_Net_Output` rows with any pin/net content have non-empty `Source IDs`.
- Unknown cells are marked exactly as `TBD-source`; source contradictions are marked exactly as `conflict`.

## Mapping Integrity

- All user-requested package pins exist in the official pinout.
- All official pinout pins used by the output resolve to the intended bank/package.
- All logical signals required by the selected topology appear exactly as expected.
- Optional signals are marked with their condition, such as rank-dependent CS pins.
- Local-only and FPGA-only nets are not mixed with peripheral package pins.

## Schematic Order

- Output order matches the user's CAD symbol order.
- Left/right/top/bottom sides are preserved.
- Any corrections to user-pasted pin order are highlighted and listed.
- Blank rows are intentional and documented.

## Net Names

- Net names are CAD-safe and consistent.
- Duplicate net names are either intentional/shared with `Intentional Duplicate Marker = Y` or flagged.
- Bus syntax is avoided unless the user explicitly asks for it.
- Prefixes distinguish repeated devices.

## Package and Topology

- Package option matches the selected part number and topology.
- x32 vs 2ch x16 vs x64 is explicitly checked.
- Package ballout is not borrowed from a different protocol, package code, or memory generation.
- Any package not recommended for the current design is marked as reference-only.

## Delivery

- Workbook includes `Sources`, `Checks`, generated `Mechanical_Checks`, `Review_Notes`, and `Change_Log`.
- Copy/paste helper files are generated when requested.
- Final response states what was generated, what was validated, and what still needs tool/FAE/layout confirmation.
