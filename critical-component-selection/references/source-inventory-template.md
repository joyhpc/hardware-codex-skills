# Source Inventory Template

Use this before building the evidence matrix. The source inventory gives short source IDs so the matrix stays readable and makes trust boundaries explicit.

Trust level values:

- `primary`: official datasheet, official PCN/EOL notice, tool output, or approved project record.
- `supplier`: vendor, distributor, or procurement communication that must still be reconciled with primary evidence.
- `project`: internal project notes, meeting records, handoff files, or daily logs.
- `secondary`: web catalog, aggregator, or non-authoritative summary.

| Source ID | Type | Title / description | Date | Owner / path / URL | Trust level | Notes |
|---|---|---|---|---|---|---|
| S1 |  |  |  |  | primary |  |
| S2 |  |  |  |  | supplier |  |
| S3 |  |  |  |  | project |  |

Rules:

- Use `Source ID` values in evidence matrix rows.
- Do not treat supplier or secondary sources as lifecycle/freeze authority unless the decision owner explicitly accepts that evidence class.
- Mark source conflicts as `conflict` in the evidence matrix rather than hiding them in notes.
- If a source is older than the decision record's `evidence_freshness_window_days` window for a fact that can change, keep the source listed but mark affected evidence rows as `stale-evidence`.
