# Decision Playbook

Use this playbook when the task is a shortlist review, supplier substitute,
pre-freeze review, blocked decision, or any selection where the user expects a
real recommendation instead of a blank template.

This is a decision discipline, not a component database. Do not add part-specific,
tool-specific, or topology-specific facts here.

## Review Posture

Act like a freeze reviewer:

1. Protect hard constraints before optimizing preferences.
2. Separate what is proven from what is only claimed.
3. Reject or block candidates early when evidence cannot support freeze.
4. Keep every open blocker addressable by owner, evidence format, and date.
5. Recommend the next decision, not a vague research plan.

Never make the answer sound more certain than the evidence.

## Fast Triage

Before comparing candidates, establish these six facts:

| Question | Why it matters | If unknown |
|---|---|---|
| What decision is being frozen? | Prevents broad research drift. | Status cannot exceed `draft`. |
| What are the hard constraints? | Defines rejection rules. | Create requirement baseline first. |
| Which facts can change over time? | Drives evidence aging. | Mark as `TBD-evidence` or `stale-evidence`. |
| Which sources are authoritative? | Prevents supplier/distributor overreach. | Build source inventory first. |
| What validation artifacts gate freeze? | Routes to domain skills/tools. | Add external validation blocker. |
| Who owns each blocker? | Makes the record actionable. | Do not call it handoff-ready. |

## Hard-Gate Screen

Run hard gates before ranking. A candidate with an unresolved hard gate may be
investigated, but it cannot be `frozen`.

| Gate type | Required evidence | Failure effect |
|---|---|---|
| Requirement fit | Requirement record plus candidate evidence | Reject or block. |
| Exact orderable identity | Datasheet/orderable PN/project record | Keep as `TBD-evidence`; do not freeze. |
| Package / footprint / pinout | Official pin/package data or checked CAD/library artifact | Reject, block, or route to CAD validation. |
| Lifecycle / PCN / EOL | PCN/EOL notice, official lifecycle source, or accepted owner signoff | Block freeze. |
| Commercial availability | Quote, distributor/vendor page, procurement email, or project sourcing record with date | Block production freeze. |
| Toolchain / firmware / logic support | Tool report, owner signoff, or project artifact | Block engineering freeze. |
| SI / PI / thermal / mechanical risk | Decision-specific validation artifact or explicit risk acceptance | Block or route to domain validation. |
| Substitute path | Backup candidate or explicit risk acceptance | Keep risk open if absent. |

## Candidate Elimination

Use this order:

1. Remove candidates that violate hard constraints with cited evidence.
2. Mark candidates with unresolved hard constraints as `Watchlist` or `blocked`; do not rank them as `Primary` unless the record remains `selected-not-frozen`.
3. Promote `Primary` only when it has the strongest evidence path to freeze, not merely the best apparent specification.
4. Keep `Backup` candidates only if their evidence path is actionable.
5. Record every rejection with the evidence that would reopen it.

Do not use "best", "safer", or "preferred" without naming the evidence field that
made the difference.

## Evidence Authority

Use the source inventory trust boundary:

| Source class | Good for | Not enough for |
|---|---|---|
| `primary` | Datasheet facts, PCN/EOL, tool/lab pass, approved project requirements | None, if current and relevant. |
| `supplier` | Clarifying availability, roadmap, substitute claims, quote details | Freeze authority unless owner accepts it. |
| `project` | Requirements, accepted risk, prior decisions, internal validation | Vendor facts unless it cites a source. |
| `secondary` | Discovery and cross-checking | Freeze decisions. |

When sources conflict, the row status is `conflict`. Do not resolve conflicts in
prose without a stronger dated source or owner acceptance.

## Status Decision Tree

Use this exact decision logic:

| Situation | Maximum status |
|---|---|
| Requirements or candidate set still being shaped | `draft` |
| Candidates exist but no primary path is selected | `shortlisted` |
| Primary path chosen, but any hard gate is open | `selected-not-frozen` |
| Evidence blocks all usable paths or requires architecture change | `blocked` |
| All non-`N-A` hard gates pass and blockers are closed | `frozen` |
| Later record replaces this one | `superseded` |

If any hard constraint is `TBD-evidence`, `conflict`, or `stale-evidence`, do not
use `frozen`.

## Domain Validation Dispatch

This skill owns the decision record and freeze gates. It does not perform
device-category analysis. When the objective implies category-specific checks,
add `external_validation_skills_needed` and a freeze blocker.

| Decision area | Typical external validation artifact | Blocker field examples |
|---|---|---|
| DDR / LPDDR / memory interface | Controller/IP report, timing/fitter report, SI/layout review | `toolchain-validation`, `si`, `pinout` |
| FPGA / SoC selection | Tool support report, package/pin planning artifact, firmware/logic owner signoff | `toolchain`, `pinout`, `firmware-logic` |
| Power MOSFET / load switch / hot-plug path | SOA/thermal/lab artifact, switching stress review, protection review | `thermal`, `soa`, `transient` |
| PMIC / regulator / power tree | Sequencing review, stability/layout review, load/transient validation | `power-sequence`, `stability`, `layout` |
| Clock / oscillator / timing source | Jitter/timing budget, tool timing signoff, availability evidence | `timing`, `jitter`, `toolchain` |
| Connector / cable / module | Mechanical fit, mating lifecycle, SI/current/thermal review | `mechanical`, `si`, `lifecycle` |
| Sensor / AFE / precision component | Accuracy budget, calibration path, firmware/driver owner signoff | `accuracy`, `calibration`, `firmware` |
| Safety / isolation / high-voltage item | Standards/compliance evidence and review artifact | `compliance`, `safety`, `layout` |

The artifact names above are routing hints, not proof. The evidence matrix must
cite the dated output before a blocker can close.

## Supplier Substitute Review

When the input is a vendor or procurement substitute:

1. Identify what changed: exact PN, package, grade, lifecycle, commercial terms, firmware/tool support, or validation state.
2. Compare against the original requirement baseline, not against the previous candidate's marketing summary.
3. Treat supplier claims as `supplier` evidence until reconciled with primary evidence or accepted by the owner.
4. Record deltas as candidate rows and risk rows.
5. Recommend one of: accept for validation, request evidence, reject, or block.

## Pre-Freeze Review

A pre-freeze answer must include:

1. Current `status`.
2. Hard gates that are `pass`.
3. Hard gates still `blocked`, `TBD-evidence`, `conflict`, or `stale-evidence`.
4. Freeze blockers with owner, needed evidence, and date.
5. External validation artifacts still needed.
6. A single recommendation: freeze, stay selected-not-frozen, block, or supersede.

If the user asks "can we freeze?", answer yes/no first, then list blockers.

## Practical Red Flags

Escalate or block when you see any of these:

1. Exact orderable PN is unclear.
2. Datasheet family matches, but package/grade/order code is not proven.
3. Lifecycle evidence is only a distributor listing or old supplier message.
4. Lead time, price, stock, or quote evidence has no date.
5. Candidate is pin-compatible but CAD/library/package evidence is absent.
6. Tool support is assumed from a related family instead of a dated report.
7. Validation pass/fail is described verbally but no artifact is linked.
8. Backup candidate exists only as a name with no evidence path.
9. Supplier substitute changes firmware, logic, SI/PI/thermal, or layout risk without owner signoff.
10. Communication report adds facts not present in the decision artifacts.

## Evidence Acquisition

Turn every evidence gap into a precise ask:

| Gap type | Ask for | Required answer format |
|---|---|---|
| Lifecycle / PCN | Current lifecycle, PCN/EOL state, roadmap statement | Official URL, PCN/EOL ID, or dated vendor/FAE response |
| Commercial terms | Price, MOQ/MPQ, lead time, allocation risk | Dated quote, distributor page, or procurement record |
| Package / pinout | Exact package/order-code compatibility | Datasheet table, CAD/library check, or project artifact |
| Toolchain | Supported device/package/configuration | Dated tool report or owner signoff |
| Validation | Pass/fail and limits | Tool/lab/SI/thermal report path and run date |

Do not treat the question itself as evidence.

## Output Shortcuts

For practical work, prefer these compact outputs:

| User asks | Output shape |
|---|---|
| "Review this shortlist" | Hard gates, candidate classification, evidence gaps, recommendation. |
| "Can we freeze?" | Yes/no, blocker table, required artifacts, next review date. |
| "Supplier suggests substitute" | Delta table, evidence authority, accept/reject/block recommendation. |
| "Make procurement ask" | Evidence gap table and external-safe supplier questions. |
| "Update decision" | Changed fields, status impact, blocker changes, lint reminder. |

The useful answer is the one that lets the next owner act without guessing.
