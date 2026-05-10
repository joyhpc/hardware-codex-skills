# Schematic Output Patterns

## CAD-Oriented Ordering

When the user is drawing a schematic, output order should match the schematic symbol, not the vendor datasheet.

Capture:

- symbol side: left, right, top, bottom
- visible order: top-to-bottom or left-to-right
- package pin number shown in the symbol
- any hidden or multi-section symbol pins

If the user's pasted symbol order conflicts with the official pinout, preserve the official pinout in the final table and add a corrections sheet.

## OrCAD Off-Page Connectors

For OrCAD Capture:

- Use one net name per connector `Name` property.
- Generate one-column plain text lists for Property Editor paste.
- Generate grouped lists by signal class so connector columns stay tidy.
- Leave non-connected or unused pins blank. Do not create off-page connectors for them.
- Use separate lists for local-only and FPGA-only nets.

Recommended group columns:

- data byte lane or data group
- data mask/inversion
- read/write strobes
- address/control
- clock/reference clock
- reset
- local-only resistor/calibration nets
- power/ground/NC/RFU if the user wants full package sheets

## Repeated Nets

Repeated net names are acceptable when the topology requires them, for example:

- LPDDR x32 CA/CK/WCK/CS T-line connections to channel A and channel B balls.
- Shared reset pins.
- Strap or reference networks connected to multiple pins.

Mark repeated nets as intentional. Unexpected duplicate nets should go to `Checks`.

## Local-Only and Device-Only Nets

Keep these out of the wrong schematic page:

- memory `ZQ`: local resistor to memory supply, not FPGA
- FPGA `RZQ` or OCT calibration: FPGA-only resistor, not memory ZQ
- PLL/reference clocks: FPGA/IP clocks unless a memory package pin explicitly exists
- NC/RFU: do not connect unless the vendor datasheet says otherwise

## Copy/Paste Deliverables

When useful, emit:

- `.xlsx` workbook for review
- `.tsv` pin/net files
- `.txt` one-column net lists
- a short note explaining the paste order and blank rows
