# Source Policy

## Priority Order

1. **User-provided files**
   - Local Excel, PDF, schematic exports, FAE emails, design notes, and project constraints.
   - Treat these as highest priority for project intent and schematic symbol order.

2. **Local project or knowledge-base files**
   - Search local files before the web with `rg --files` and `rg`.
   - Look for exact part numbers, package codes, document IDs, table names, signal names, and prior pin assignments.

3. **Vendor official documents**
   - Use FPGA/SoC, memory, connector, PMIC, retimer, or peripheral vendor documents as authoritative for pinout, ballout, package dimensions, electrical rules, timing, SI/PI, and layout constraints.

4. **Authorized distributor pages**
   - Use DigiKey, Mouser, LCSC, Arrow, Avnet, and similar sources for part discovery, orderable MPNs, and availability.
   - Do not use distributor fields as the sole authority for pin mapping, ballout, or package dimensions.

5. **Open-source hardware and reference designs**
   - Use as cross-checks, examples, or schematic patterns.
   - Mark as non-authoritative unless the user explicitly accepts that design as the basis.

6. **Forums and generic web pages**
   - Use only as search leads. Do not cite as final authority for pin/net assignments.

## Local Search

- Search local files before browsing.
- Prefer exact identifiers:
  - part number: `A5EC052A`, `MT62F1G32D4`
  - package code: `B32A`, `DR`, `DS`, `EK`
  - document ID: `817467`
  - table/figure name: `LPDDR5 Pin Placement`, `Ball Assignments`
  - signal: `DQ0_A`, `CA0_B`, `RZQ`
- Extract PDF text when tables are selectable.
- Use visual inspection for PDF figures or rotated tables that text extraction mangles.
- If a figure/table was visually read, record that in `Sources` or `Review_Notes`.

## Web Search

- Browse when local files lack required data, the data may be stale, or the user asks for current availability/recommendations.
- Prefer vendor domains and official document portals.
- Record URL, title, revision/date, and exact section/table/figure.

## Conflict Handling

- If two sources disagree on pin number, package code, topology, or ballout, stop and show the conflict.
- Do not resolve source conflicts by intuition.
- If the user wants a provisional output, mark disputed cells exactly as `conflict` and add a `Requires Confirmation` note.
- If a required source cannot be found, mark the unsupported cell exactly as `TBD-source`.
