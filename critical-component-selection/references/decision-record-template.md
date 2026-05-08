# Decision Record Template

Use this for the project-layer decision artifact. Do not save real project facts inside the skill.

## Metadata

| Field | Value |
|---|---|
| Project |  |
| Component / function |  |
| Decision date |  |
| Decision owner |  |
| Review date |  |
| Record status | draft / shortlisted / selected-not-frozen / frozen / blocked / superseded |

## Decision Objective

State the exact freeze-grade choice being made.

## Requirement Baseline

Link the requirement file, message, or project record. Split requirements into:

- Hard constraints:
- Changeable constraints:
- Acceptance criteria:

## Candidate Classification

| Class | Candidate | Evidence pointer | Rationale |
|---|---|---|---|
| Primary |  |  |  |
| Backup |  |  |  |
| Rejected |  |  |  |
| Watchlist |  |  |  |

## Evidence Summary

Link the source inventory and evidence matrix. List only decision-changing facts.

## Risk Summary

Link the risk register and list unresolved high-impact risks.

## Engineering Verification Gates

| Gate | Owner | Pass criteria | Artifact / link | Status |
|---|---|---|---|---|
|  |  |  |  | TBD-evidence |

## Decision

State what is selected now, what is not selected, and what remains blocked before freeze.

Allowed decision strengths:

- `selected-not-frozen`: primary candidate can proceed to procurement and engineering validation, but at least one freeze gate is open.
- `frozen`: schematic/BOM/pin/layout freeze is allowed because all non-N-A freeze gates passed.
- `blocked`: no candidate can proceed without named missing evidence or an architecture change.

## Signoff

| Role | Name | Date | Notes |
|---|---|---|---|
| Engineering |  |  |  |
| Procurement |  |  |  |
| Project owner |  |  |  |
