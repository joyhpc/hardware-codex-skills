---
# THIS IS EXAMPLE DATA. Part numbers, dates, and identifiers are fictional.

schema_version: 1
schema_kind: decision-record
record_id: 20260510-mainboard-r3-lpddr5-x16
project: mainboard-r3
revision: 1

status: selected-not-frozen
created_date: 2026-05-10
review_date: 2026-06-15
freeze_target_date: 2026-07-01
maintainer: example-engineer

supersedes: null
superseded_by: null

related_records:
  - kind: selection-map
    id: 20260510-mainboard-r3-lpddr5-selection-map
    role: sidecar
  - kind: pin-assign-workbench
    id: 20260520-mainboard-r3-fpga-mem-pinout
    role: derived

evidence_freshness_window_days: 60

primary_candidate:
  pn: EXAMPLE-LPDDR5-X16-A
  manufacturer: example-corp
  evidence_status: confirmed

backup_candidates:
  - pn: EXAMPLE-LPDDR5-X16-B
    manufacturer: alt-corp
    evidence_status: TBD-evidence

freeze_blockers:
  - id: fb-pcn-window
    field: lifecycle
    needed_evidence: pcn-or-vendor-roadmap-statement
    owner: procurement
    due_date: 2026-05-25
  - id: fb-si-validation
    field: si
    needed_evidence: ibis-am-channel-simulation
    owner: si-engineer
    due_date: 2026-06-10

external_validation_skills_needed:
  - skill: emif-timing-analysis
    reason: lpddr5-x16-on-fpga-fitter-margin
  - skill: si-channel-budget
    reason: 6400mtps-channel-loss-margin-vs-eye-mask

evidence_root: hardware-projects/prj/mainboard-r3/evidence/lpddr5/
risk_register: ./20260510-mainboard-r3-lpddr5-x16-risks.md

last_lint_pass: null
---

# LPDDR5 x16 Selection Decision (Example)

> Worked example for schema v1 / kind=decision-record. All identifiers fictional.

## Decision Objective

Select the LPDDR5 x16 device for mainboard revision 3, main-memory channel A. The choice locks footprint, byte-lane assignment, and EMIF fitter input.

## Requirement Baseline

Link: `hardware-projects/prj/mainboard-r3/requirements/main-memory-r3.md`

- Hard constraints:
  - LPDDR5 x16, 6400 MT/s minimum
  - 200-ball FBGA, vendor-standard ballout
  - Industrial temperature grade
  - Minimum 5-year supply window from freeze date
- Changeable constraints:
  - Density: 8 Gb preferred, 16 Gb acceptable if cost-neutral
- Acceptance criteria:
  - EMIF fitter passes timing at 6400 MT/s with ≥10% margin
  - SI channel loss < 6 dB at Nyquist
  - Two compliant second-source candidates

## Hard Gate Screen

| Gate | Requirement / pass condition | Candidate impact | Evidence pointer | Status | Owner / next action |
|---|---|---|---|---|---|
| Exact orderable identity | Exact order code and package are confirmed | Primary can remain selected | S1 | pass | hardware-owner / keep source current |
| Package / footprint / pinout | 200-ball FBGA standard ballout is confirmed | Primary can proceed to pin workbench | S1 | pass | hardware-owner / link pin workbook |
| Lifecycle / PCN / EOL | 5-year supply window from freeze date | Primary cannot freeze | S2 | blocked | procurement / obtain formal PCN window |
| Commercial availability | Sample and production terms are dated | Procurement can sample, not production freeze | S2 | TBD-evidence | procurement / obtain quote |
| Toolchain / firmware / logic support | EMIF/fitter timing pass exists | Primary can proceed to SI validation | S3 | pass | digital / rerun if topology changes |
| SI / PI / thermal / mechanical risk | Channel simulation and board-level checks pass | Primary cannot freeze |  | TBD-evidence | si-engineer / run SI artifact |
| Substitute path | At least one backup route remains actionable | Backup remains watch item | S4 | TBD-evidence | hardware-owner / close backup evidence |

## Source Inventory

| Source ID | Type | Title | Date | Path / URL | Trust level | Notes |
|---|---|---|---|---|---|---|
| S1 | datasheet | EXAMPLE-LPDDR5-X16-A datasheet rev 1.4 | 2026-04-15 | evidence/lpddr5/example-corp-ds-1.4.pdf | primary |  |
| S2 | vendor-email | example-corp lifecycle confirmation | 2026-04-22 | evidence/lpddr5/email-2026-04-22.eml | supplier | Roadmap, not PCN |
| S3 | tool-output | Fitter run r3-mem-a | 2026-05-08 | evidence/lpddr5/fitter-r3-mem-a.log | primary | 12% margin at 6400 MT/s |
| S4 | datasheet | EXAMPLE-LPDDR5-X16-B preliminary | 2026-04-01 | evidence/lpddr5/alt-corp-ds-0.9.pdf | primary | Preliminary |

## Candidate Classification

| Class | Candidate | Evidence pointer | Rationale |
|---|---|---|---|
| Primary | EXAMPLE-LPDDR5-X16-A | S1, S2, S3 | Datasheet confirmed, fitter pass, vendor lifecycle statement |
| Backup | EXAMPLE-LPDDR5-X16-B | S4 | Preliminary datasheet, no SI run, no PCN window |
| Rejected | EXAMPLE-LPDDR5-X16-C | (web catalog) | Industrial grade not confirmed in any primary source |

## Rejection Ledger

| Candidate / route | Rejection or demotion reason | Evidence pointer | Reopen condition | Owner |
|---|---|---|---|---|
| EXAMPLE-LPDDR5-X16-C | Industrial grade not confirmed by primary evidence | Web catalog only | Official datasheet/order-code evidence confirms grade and package | hardware-owner |
| EXAMPLE-LPDDR5-X16-B | Kept as backup because datasheet is preliminary and lifecycle evidence is open | S4 | Production datasheet and lifecycle evidence arrive | procurement |

## Evidence Matrix

| Field | Candidate | Requirement | Claimed value | Evidence source | Evidence date | Status | Notes |
|---|---|---|---|---|---|---|---|
| Interface / protocol | EXAMPLE-LPDDR5-X16-A | LPDDR5 x16 6400 MT/s | LPDDR5 x16 6400 MT/s | S1 §1.2 | 2026-04-15 | confirmed |  |
| Package / ballout | EXAMPLE-LPDDR5-X16-A | 200-ball FBGA std | 200-ball FBGA std | S1 §11 | 2026-04-15 | confirmed |  |
| Temperature grade | EXAMPLE-LPDDR5-X16-A | Industrial | Industrial | S1 §1.3 | 2026-04-15 | confirmed |  |
| Lifecycle / PCN | EXAMPLE-LPDDR5-X16-A | 5y supply from freeze | 7y per roadmap | S2 | 2026-04-22 | conflict | Supplier email lacks PCN authority |
| Fitter timing | EXAMPLE-LPDDR5-X16-A | ≥10% margin at 6400 | 12% margin | S3 | 2026-05-08 | confirmed |  |
| SI channel margin | EXAMPLE-LPDDR5-X16-A | <6 dB at Nyquist | TBD |  |  | TBD-evidence | Awaits IBIS-AMI |
| Lifecycle / PCN | EXAMPLE-LPDDR5-X16-B | 5y supply from freeze | TBD |  |  | TBD-evidence |  |
| Interface / protocol | EXAMPLE-LPDDR5-X16-B | LPDDR5 x16 6400 MT/s | LPDDR5 x16 6400 MT/s (prelim) | S4 §1.1 | 2026-04-01 | TBD-evidence | Preliminary |

## Risk Summary

Full register: `./20260510-mainboard-r3-lpddr5-x16-risks.md`

Top unresolved risks:

- Lifecycle / PCN: roadmap-only commitment for primary; needs PCN-class statement.
- SI / PI: channel simulation pending; eye-mask margin unknown.

## Engineering Verification Gates

| Gate | Owner | Pass criteria | Artifact / link | Status |
|---|---|---|---|---|
| Fitter timing 6400 MT/s | digital | ≥10% margin | S3 | pass |
| IBIS-AMI channel sim | si-engineer | <6 dB loss; eye open | (pending) | TBD-evidence |
| Power integrity | pi-engineer | Z-target met | (pending) | TBD-evidence |
| Thermal under stress | thermal | Tj <85 °C | (pending) | TBD-evidence |

## Decision

Do not freeze; stay `selected-not-frozen`.

`EXAMPLE-LPDDR5-X16-A` is **primary**. Procurement may proceed with sample qualification. Cannot advance to `frozen` until both `fb-pcn-window` and `fb-si-validation` close.

`EXAMPLE-LPDDR5-X16-B` remains backup pending preliminary-to-production datasheet promotion.

## Freeze Blockers Narrative

- **fb-pcn-window** (lifecycle): The vendor roadmap email (S2) is supplier-trust-level evidence and does not carry lifecycle-freeze authority. Procurement to obtain a formal PCN window or distributor end-of-life commitment. Due 2026-05-25.
- **fb-si-validation** (si): IBIS-AMI channel simulation against current PCB stackup, eye-mask check at 6400 MT/s. Owner: si-engineer. Due 2026-06-10.

## External Validation Handoff

- `emif-timing-analysis`: produces fitter-margin report. Already passed once (S3); rerun required if PCB topology changes.
- `si-channel-budget`: produces IBIS-AMI artifact that closes `fb-si-validation`.

## Signoff

| Role | Name | Date | Notes |
|---|---|---|---|
| Engineering |  |  |  |
| Procurement |  |  |  |
| Project owner |  |  |  |
