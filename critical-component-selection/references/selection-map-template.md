# Selection Map Template

Use this as a project-layer navigation artifact when a selection involves many source files, candidate routes, supplier messages, or validation paths. The map supports the decision record; it is not a replacement for the evidence matrix, risk register, or freeze checklist.

Do not list every discovered part number by default. Group low-value variants into candidate routes or families, and include exact part numbers only when they affect the decision, need supplier follow-up, or define a validation input.

## Metadata

| Field | Value |
|---|---|
| Project |  |
| Component / function |  |
| Map date |  |
| Related decision record |  |
| Map owner |  |
| Review date |  |

## Map Purpose

State how this map helps the next selection step. Keep it tied to evidence navigation, candidate filtering, missing evidence, and freeze blockers.

## Source Map

| Source ID | Source type | Title / description | Date | Path / URL / owner | Trust level | Candidate route | Supports which conclusion | Status |
|---|---|---|---|---|---|---|---|---|
| S1 | datasheet / PCN / email / tool / project / secondary |  |  |  | primary / supplier / project / secondary |  |  | active / superseded / rejected / stale |

## Candidate Funnel

| Funnel class | Route / family / exact candidate | Representative exact PN if needed | Why this level is enough | Evidence pointer | Next action |
|---|---|---|---|---|---|
| Primary |  |  |  |  |  |
| Backup |  |  |  |  |  |
| Watchlist |  |  |  |  |  |
| Rejected |  |  |  |  |  |
| Closed |  |  |  |  |  |

## Requirement Coverage Map

Allowed status values: `confirmed`, `TBD-evidence`, `conflict`, `N-A`.

| Requirement / gate | Primary route status | Backup / watchlist status | Evidence pointer | Status | Freeze impact |
|---|---|---|---|---|---|
|  |  |  |  | TBD-evidence |  |

## Rejection Ledger

| Route / candidate | Rejection reason | Evidence pointer | Reopen condition | Owner |
|---|---|---|---|---|
|  |  |  |  |  |

## Open Evidence Ledger

| Evidence gap | Affects gate | Current best route | Needed evidence format | Owner | Due / review date | Status |
|---|---|---|---|---|---|---|
|  |  |  | datasheet table / PCN / vendor email / quote / tool report / project signoff |  |  | TBD-evidence |

## Evidence Acquisition Plan

Use this only as a reminder for how to obtain evidence. Questions are not evidence until answered by a dated source with sender, channel, exact subject, and answer.

Allowed status values: `to-ask`, `asked`, `answered`, `stale`, `blocked`, `N-A`.

| Evidence gap | Best channel | Who asks | Question to ask | Required answer format | Status |
|---|---|---|---|---|---|
|  | original vendor / authorized distributor / FAE / procurement / internal owner / tool-lab |  |  | dated email / official URL / datasheet table / PCN / quote / tool artifact / signoff | to-ask |

## Tool Validation Map

| Validation item | Inputs | Tool / method | Owner | Pass criteria | Output artifact | Status |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  | TBD-evidence |

## Update Rules

- Promote a route only when the evidence matrix can cite the required source.
- Demote or reject a route when new evidence conflicts with a hard constraint.
- Mark a source `stale` when its date, PCN state, pricing, lead time, stock, or tool version may no longer support the decision.
- Keep raw supplier emails, datasheets, PCNs, and tool artifacts outside the skill and inside the project evidence store.
