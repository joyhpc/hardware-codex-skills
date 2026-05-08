# Communication Report Template

Use this template to produce a concise report from an existing component selection decision record, selection map, evidence matrix, risk register, or freeze checklist.

The report is a communication artifact, not a new evidence source. Do not introduce new component facts. Keep unsupported facts as `TBD-evidence`, conflicts as `conflict`, and current decision strength visible.

## Report Type

Choose one audience before writing:

| Type | Audience | Optimize for | Avoid |
|---|---|---|---|
| Leadership brief | Leadership / project owner | Decision ask, business impact, options, top blockers, deadline | Long evidence tables, low-level datasheet details |
| Procurement brief | Procurement / sourcing | Exact supplier questions, answer format, owner, due date | Ambiguous asks, engineering-only detail without procurement action |
| Supplier / FAE inquiry | Original vendor, authorized distributor, FAE | External-safe technical and commercial questions that close evidence gaps | Internal rankings, competitor details, unapproved cost targets, sensitive architecture |
| Project meeting brief | Cross-functional project meeting | Status, decisions needed, blockers, owners, next review | Repeating the full decision record |

## Metadata

| Field | Value |
|---|---|
| Project |  |
| Component / function |  |
| Report type | leadership / procurement / supplier-fae / project-meeting |
| Audience |  |
| Report date |  |
| Related decision record |  |
| Related selection map |  |
| Related evidence matrix / freeze checklist |  |
| Report status | draft / ready-to-send / blocked-needs-source / superseded |

## Common Report Structure

Use these sections unless the audience-specific shape below is better.

1. `Purpose`
2. `Current Decision State`
3. `Recommendation / Decision Ask`
4. `Candidate Or Route Summary`
5. `Evidence Status`
6. `Top Risks Or Blockers`
7. `Actions Needed`
8. `Source Links`

## Leadership Brief Shape

Use this when the report is for leadership or project-owner decision making.

```markdown
# <Component> Selection Leadership Brief

## Purpose

## Current State

## Decision Needed

## Recommendation

## Options

| Option | What it means | Benefit | Cost / risk | Decision status |
|---|---|---|---|---|

## Top Blockers

| Blocker | Impact | Owner | Needed by |
|---|---|---|---|

## Next Actions

| Owner | Action | Due date |
|---|---|---|

## Source Links
```

## Procurement Brief Shape

Use this when the report is for internal sourcing work.

```markdown
# <Component> Procurement Action Brief

## Purpose

## Current Candidate Routes

| Route | Current class | Evidence status | Procurement action |
|---|---|---|---|

## Evidence To Obtain

| Evidence gap | Supplier / channel | Exact question | Required answer format | Due date |
|---|---|---|---|---|

## Do Not Use / Do Not Freeze

## Source Links
```

## Supplier / FAE Inquiry Shape

Use this when the report may be sent outside the company. Keep it short, factual, and external-safe.

```markdown
# <Component> Supplier / FAE Inquiry

## Context

## Candidate Part Or Route

## Questions

| Topic | Question | Required answer format |
|---|---|---|

## Requested Attachments Or Links

## Project Timing
```

Rules for external reports:

- Ask only what is needed to close evidence gaps.
- Include exact part numbers only when necessary for the supplier to answer.
- Do not include internal candidate ranking unless intentionally approved.
- Do not disclose competitor routes, internal cost targets, unresolved architecture concerns, or customer-sensitive details unless the project owner approves.

## Project Meeting Brief Shape

Use this for recurring project status or cross-functional meetings.

```markdown
# <Component> Selection Project Meeting Brief

## Status

## Decisions Needed This Meeting

| Decision | Owner | Needed because | Consequence if not decided |
|---|---|---|---|

## Blockers

| Blocker | Owner | Current status | Next evidence |
|---|---|---|---|

## Action Items

| Owner | Action | Output | Due date |
|---|---|---|---|

## Source Links
```

## Quality Rules

- Every report must cite or link the decision artifact it is derived from.
- The report must say whether the component is `draft`, `shortlisted`, `selected-not-frozen`, `frozen`, `blocked`, or `superseded`.
- If the report asks someone to obtain evidence, specify the required answer format.
- Use exact dates for action deadlines and review dates.
- Keep audience-specific reports short; link to the selection map for detail instead of copying it.
