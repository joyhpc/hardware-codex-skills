# Evidence Matrix Template

Use this template to reconcile requirements, candidates, and evidence. Each row covers exactly one field for one candidate so evidence status cannot be blurred across candidates.

Reference sources by `Source ID` from `source-inventory-template.md` when possible.

Allowed `Status` values:

- `confirmed`: source exists and matches the requirement.
- `TBD-evidence`: no usable source yet.
- `conflict`: sources disagree or evidence contradicts the requirement.
- `stale-evidence`: source once supported the row, but is older than the decision record's `evidence_freshness_window_days` window or has been superseded.
- `N-A`: not applicable to this field, with a reason.

Every `confirmed` row must include `Evidence date`; lint rule **BD003** enforces this. If the decision owner has not set `evidence_freshness_window_days`, use the schema default of 60 days and keep freshness as `TBD-evidence` for facts that can change materially, such as price, stock, lead time, PCN/EOL state, lifecycle, and tool-version support.

| Field | Candidate | Requirement | Claimed value | Evidence source | Evidence date | Status | Notes |
|---|---|---|---|---|---|---|---|
| Interface / protocol |  |  |  |  |  | TBD-evidence |  |
| Capacity / width / rating |  |  |  |  |  | TBD-evidence |  |
| Package / footprint / pinout |  |  |  |  |  | TBD-evidence |  |
| Temperature / grade |  |  |  |  |  | TBD-evidence |  |
| Lifecycle / EOL / PCN |  |  |  |  |  | TBD-evidence |  |
| Toolchain or design support |  |  |  |  |  | TBD-evidence |  |
| Price / MOQ / MPQ / lead time |  |  |  |  |  | TBD-evidence |  |
| Second source / substitute path |  |  |  |  |  | TBD-evidence |  |
| Engineering validation artifact |  |  |  |  |  | TBD-evidence |  |

Add or remove rows only when the decision objective requires it. Keep the status vocabulary unchanged.
