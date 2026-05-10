---
# THIS IS EXAMPLE DATA. Identifiers fictional.

schema_version: 1
schema_kind: selection-map
record_id: 20260510-mainboard-r3-lpddr5-selection-map
project: mainboard-r3
revision: 1

status: active
created_date: 2026-05-10
review_date: 2026-06-15
maintainer: example-engineer

supersedes: null
superseded_by: null

related_records:
  - kind: decision-record
    id: 20260510-mainboard-r3-lpddr5-x16
    role: sidecar

decision_record: 20260510-mainboard-r3-lpddr5-x16
candidate_routes_count: 5
open_evidence_count: 2
tool_validation_open_count: 3

last_lint_pass: null
---

# LPDDR5 Selection Map (Example)

> Sidecar navigation map for the LPDDR5 x16 selection. Schema kind: selection-map.

## Map Purpose

Help the next selection step by preserving:

1. Source navigation across 4 datasheets, 1 supplier email, and 1 fitter log.
2. Candidate funnel across 3 vendor families.
3. Requirement coverage status, including the unresolved PCN-window question.
4. Evidence acquisition plan for procurement and SI follow-up.

## Source Map

| Source ID | Source type | Title | Date | Path | Trust level | Candidate route | Supports | Status |
|---|---|---|---|---|---|---|---|---|
| S1 | datasheet | example-corp ds 1.4 | 2026-04-15 | evidence/lpddr5/example-corp-ds-1.4.pdf | primary | example-corp | EXAMPLE-LPDDR5-X16-A | active |
| S2 | vendor-email | example-corp lifecycle | 2026-04-22 | evidence/lpddr5/email-2026-04-22.eml | supplier | example-corp | lifecycle-claim | active |
| S3 | tool-output | fitter r3-mem-a | 2026-05-08 | evidence/lpddr5/fitter-r3-mem-a.log | primary | example-corp | EMIF timing | active |
| S4 | datasheet | alt-corp prelim ds | 2026-04-01 | evidence/lpddr5/alt-corp-ds-0.9.pdf | primary | alt-corp | EXAMPLE-LPDDR5-X16-B | active |

## Candidate Funnel

| Funnel class | Route | Representative PN | Why this level | Evidence pointer | Next action |
|---|---|---|---|---|---|
| Primary | example-corp x16 6400 | EXAMPLE-LPDDR5-X16-A | datasheet+fitter confirm | S1, S3 | obtain PCN-class lifecycle |
| Backup | alt-corp x16 6400 | EXAMPLE-LPDDR5-X16-B | preliminary ds only | S4 | request production rev |
| Rejected | third-corp x16 | EXAMPLE-LPDDR5-X16-C | grade unconfirmed | (web only) | reopen if industrial grade documented |

## Requirement Coverage Map

| Requirement | Primary route | Backup route | Evidence pointer | Status | Freeze impact |
|---|---|---|---|---|---|
| LPDDR5 x16 6400 MT/s | confirmed | TBD-evidence | S1, S4 | confirmed | none |
| 200-ball FBGA std | confirmed | TBD-evidence | S1 | confirmed | none |
| Industrial grade | confirmed | TBD-evidence | S1 | confirmed | none |
| 5y supply from freeze | conflict | TBD-evidence | S2 | conflict | blocks freeze |
| Fitter ≥10% margin | confirmed | TBD-evidence | S3 | confirmed | none |
| SI <6 dB at Nyquist | TBD-evidence | TBD-evidence | (none) | TBD-evidence | blocks freeze |

## Open Evidence Ledger

| Evidence gap | Affects | Best route | Format needed | Owner | Due | Status |
|---|---|---|---|---|---|---|
| PCN-class lifecycle commitment | primary | example-corp authorized distributor | dated PCN or quote with EOL clause | procurement | 2026-05-25 | TBD-evidence |
| IBIS-AMI channel sim | primary | internal SI tool | report under evidence/lpddr5/ | si-engineer | 2026-06-10 | TBD-evidence |

## Tool Validation Map

| Validation | Inputs | Tool | Owner | Pass criteria | Artifact | Status |
|---|---|---|---|---|---|---|
| EMIF fitter | RTL + constraints | vendor fitter | digital | ≥10% margin | S3 | pass |
| IBIS-AMI channel | stackup + IBIS | SI tool | si-engineer | <6 dB; eye open | (pending) | TBD-evidence |
| Power integrity | decap network | PI tool | pi-engineer | Z-target | (pending) | TBD-evidence |
