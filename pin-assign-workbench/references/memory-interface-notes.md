# Memory Interface Notes

Use this reference for DDR/LPDDR-style work. It is not a substitute for the current vendor documents.

## Topology Traps

- `x32` and `2ch x16` are not automatically interchangeable.
- A vendor IP table may use `Pin Index` for FPGA internal I/O bank positions, not package ball numbers.
- A memory package ball name such as `DQ0_A` is not the same thing as FPGA `DQ0` unless the topology mapping says so.
- A single x32 memory package can expose channel A and channel B pins. FPGA nets may map `DQ0-DQ15` to channel A and `DQ16-DQ31` to channel B.

## Shared Signals

For LPDDR x32 topologies, address/control and clock nets can intentionally connect to both A and B channel balls:

- CA
- CK
- WCK
- CS
- RESET, depending on package and IP

Repeated off-page connector names for these signals are expected when drawing the memory page.

## ZQ, RZQ, and Reference Clocks

- Memory `ZQ` is a memory calibration resistor net, usually local to the memory supply.
- FPGA `RZQ`, OCT, or calibration pins are FPGA-side calibration resources and are not memory ZQ.
- FPGA PLL or EMIF reference clocks are FPGA/IP clocks, not memory package pins unless the memory datasheet explicitly defines such pins.

## NC and RFU

- NC usually remains unconnected.
- RFU must follow the vendor datasheet. If unclear, mark as requiring confirmation.
- Do not use unused memory-interface lane pins as GPIO unless the FPGA/IP/user guide explicitly permits it and the fitting tool confirms it.

## Package Selection Notes

- Verify protocol generation: LPDDR5 is not LPDDR5X unless explicitly selected and supported.
- Verify die organization, width, rank, and capacity against the part number.
- Package with more balls is not automatically better. Consider supply, pitch, escape routing, assembly process, reliability, and available reference designs.
- If package ballout comes from a reference schematic, cross-check against the vendor package figure before final output.
