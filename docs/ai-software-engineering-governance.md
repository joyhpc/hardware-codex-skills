# AI Software Engineering Governance Closed Loop

This note records an AI software engineering governance model for systems that place model capability inside runtime workflows.

The core premise is:

```text
A model is an incompletely predictable compute unit that can be constrained by engineering governance.
```

The goal is not to make model behavior absolutely deterministic. The goal is to make model behavior bounded, reviewable, recoverable, and auditable when it is used inside a real software system.

This document is intentionally written as a governance checklist. Each section includes a local closed-loop verification block so a maintainer can inspect whether the governance claim has been turned into an operational control.

Tracking issue: https://github.com/joyhpc/hardware-codex-skills/issues/1

## Scope

This repository contains reusable Codex skills, schemas, examples, and deterministic tools for hardware engineering workflows. The governance model below does not store project facts or private engineering evidence in this repository. It defines how AI-enabled workflows should be designed before they are trusted as system capability.

The model applies to:

- Codex skills that load context, transform evidence, or prepare engineering records.
- Agent workflows that call tools or produce handoff artifacts.
- Deterministic scripts that validate AI-authored records.
- Future integrations that route AI output into dashboards, project tooling, or hardware project management systems.

The model does not make the model an engineering oracle. Evidence, dated sources, validation artifacts, and owner review still decide engineering truth.

## 1. Responsibility Model

### Governance Goal

AI governance starts with ownership. A system cannot be governed only by prompts, schemas, and evals. It also needs named responsibility for business intent, data quality, tool authority, release risk, and human review.

### Engineering Mechanism

Every AI runtime workflow should identify these roles before it can move from experiment to trusted operation:

| Role | Owns | Must be able to answer |
|---|---|---|
| Product Owner | Business goal, user value, acceptable workflow risk | Why should this workflow use AI, and what failure is unacceptable? |
| AI System Owner | Model orchestration, prompt contracts, runtime state, fallback behavior | Which model path ran, under which policy, and how can it be replayed? |
| Data Owner | Context sources, retrieval scope, memory policy, freshness | Which facts were eligible for use, and which sources were excluded? |
| Tool Owner | Tool authorization, parameters, side effects, rollback or compensation | What can the model ask this tool to do, and what can it never do? |
| Risk and Compliance Owner | Audit, privacy, security, regulatory or customer constraints | Which outputs require human review or stronger retention? |
| Human Reviewer | High-risk confirmation, dispute resolution, release approval | What evidence was reviewed before the system acted? |

For this repository, role ownership should be reflected in skill documentation, schema fields, or release notes before a workflow is treated as stable. For example, a skill that creates a freeze-grade hardware record should name who maintains the record, what evidence root is allowed, and which deterministic checks gate status advancement.

### Closed-Loop Verification

Verification question:

```text
Can a reviewer identify who owns intent, data, model behavior, tools, risk, and final approval?
```

Pass conditions:

- The workflow has at least one named maintainer or owner field.
- Data sources and excluded source classes are documented.
- Tool authority is separated from model instruction.
- High-risk outputs have a human reviewer or approval gate.
- Incident triage can assign the failure to product intent, context, prompt, model behavior, tool policy, or review failure.

Failure handling:

- If no owner exists, keep the workflow experimental.
- If the tool owner is unclear, disable write tools or require manual execution.
- If review authority is unclear, block status advancement or downstream automation.

## 2. Risk Classification

### Governance Goal

Model capability should not be governed as one uniform object. Risk depends on what the model can see, decide, and change. A low-risk summarizer and a production-writing agent require different controls.

### Engineering Mechanism

Use levels L0 through L5 to classify AI runtime capability:

| Level | Capability | Typical permission | Required governance |
|---|---|---|---|
| L0 | Offline generation with no external data and no side effects | Draft text only | Basic prompt contract and manual review |
| L1 | Read-only retrieval and summarization | Search or read approved context | Source citation, freshness check, output uncertainty |
| L2 | Advice or recommendation for human execution | Produce suggested action | Human confirmation, rationale, evidence separation |
| L3 | Low-risk tool calls | Bounded read tools or reversible local transforms | Tool schema, parameter validation, audit log |
| L4 | Business action or write operation | Create, update, notify, route, or mutate records | Approval gate, idempotency, rollback or compensation, replay |
| L5 | Rights, safety, financial, legal, medical, employment, or production-critical impact | Strongly restricted or disabled by default | Formal risk review, strong human oversight, red-team tests, incident runbook |

Risk level must be promoted when any of these are true:

- The workflow can modify persistent state.
- The workflow can contact another person or external system.
- The workflow uses private, regulated, customer, supplier, or security-sensitive data.
- The output may affect cost, schedule, safety, legal exposure, sourcing decisions, or design freeze.
- The model can choose tools dynamically rather than following a fixed path.

### Closed-Loop Verification

Verification question:

```text
Is the workflow's risk level explicit, and do its controls match that level?
```

Pass conditions:

- The workflow is assigned L0 through L5.
- Tool permissions do not exceed the assigned level.
- Human approval appears before irreversible or high-impact action.
- Evals include at least one test for risk-level promotion triggers.
- Logs preserve enough state to prove which level was active during execution.

Failure handling:

- If the level is unknown, default to L2 at most and require human execution.
- If the system performs writes without L4 controls, disable the write path.
- If the system touches L5 domains, require explicit risk owner approval before runtime use.

## 3. Lifecycle Governance

### Governance Goal

AI software governance is not only runtime monitoring. It covers the full lifecycle of requirements, design, development, testing, release, operations, and post-incident learning.

### Engineering Mechanism

Treat these artifacts as versioned system assets:

- Model version and provider configuration.
- Prompt, instruction, and skill version.
- Context loading policy and retrieval filters.
- Tool manifests and authorization rules.
- Output schemas and validation rules.
- Eval sets, red-team cases, and regression fixtures.
- Release notes, rollback criteria, and incident reports.

Lifecycle gates:

| Phase | Required governance question |
|---|---|
| Requirements | Is AI necessary, and what non-AI fallback exists? |
| Design | What are the input boundary, risk level, data boundary, tool boundary, and human gates? |
| Development | Are prompts, schemas, tools, and context policies versioned and reviewable? |
| Testing | Do evals cover normal cases, ambiguous input, stale context, conflicting evidence, injection, and tool refusal? |
| Release | Is there a rollout plan, limit, rollback path, and owner on call? |
| Operation | Are latency, cost, refusal, tool failures, drift, and user overrides observable? |
| Review | Are incidents converted into new evals, policy changes, or documentation changes? |

For this repository, deterministic scripts such as linters and DAG builders are part of the lifecycle gate. They do not prove truth, but they prevent unstable or empty-shell AI output from quietly becoming downstream state.

### Closed-Loop Verification

Verification question:

```text
Can a maintainer reconstruct how a model capability changed from requirement to release?
```

Pass conditions:

- Prompt or skill changes are reviewed like code.
- Test fixtures include AI-specific failure modes.
- Release notes identify any change to model, prompt, context, tool, or schema behavior.
- Operational metrics include failure, timeout, refusal, cost, and human override signals.
- Incidents produce durable changes, not only one-time explanations.

Failure handling:

- If an AI path lacks regression coverage, keep it behind manual review.
- If a provider or model change is untracked, freeze promotion until evals are rerun.
- If a production incident cannot be replayed, treat audit logging as a release blocker.

## 4. Evidence Governance

### Governance Goal

AI output must separate what is known, what is remembered, what is inferred, and what is recommended. Without evidence boundaries, a model can turn stale memory into current fact or turn a plausible inference into a decision.

### Engineering Mechanism

Use explicit evidence categories in prompts, records, and downstream output:

| Category | Meaning | Required handling |
|---|---|---|
| fact | Directly supported by an eligible source | Include source and timestamp |
| historical | Previously true or previously observed | Mark the time period and require freshness review |
| inference | Derived from facts, but not directly stated | Link to supporting facts and label as inference |
| assumption | Needed to proceed but not verified | Make visible and block high-risk automation |
| recommendation | Suggested action | Include rationale and approval requirement |
| uncertainty | Known unknown, ambiguity, conflict, or missing data | Preserve in output and route to owner |

Minimum evidence envelope for high-value outputs:

```yaml
claim_type: fact | historical | inference | assumption | recommendation | uncertainty
claim: concise statement
source: source id, file path, URL, tool result id, or reviewer note
source_timestamp: YYYY-MM-DD or null
observed_at: YYYY-MM-DDTHH:MM:SSZ
confidence_basis: source-backed | tool-backed | reviewer-backed | model-inferred
review_required: true | false
```

In this repository, the existing record schema already supports evidence freshness windows, evidence dates, status vocabularies, blockers, and linter checks. AI governance should build on those fields instead of replacing them with free-form prose.

### Closed-Loop Verification

Verification question:

```text
Can each important claim be traced to a source, a timestamp, and a claim type?
```

Pass conditions:

- Facts have source identifiers and evidence dates.
- Inferences are not phrased as confirmed facts.
- Assumptions are visible and cannot silently unblock high-risk status.
- Conflicting evidence stays in the record until an owner resolves it.
- Stale evidence is either refreshed or reclassified.

Failure handling:

- If source and timestamp are missing, mark the claim as assumption or uncertainty.
- If a model asserts unsupported facts, add a regression example.
- If evidence conflicts, block downstream write action until resolution is recorded.

## 5. Tool Governance

### Governance Goal

The highest operational risk is often not that a model says the wrong thing. It is that a model does the wrong thing through a tool. Tool access must therefore be a governed capability, not a prompt-level permission.

### Engineering Mechanism

Model runtimes should request tool actions through a policy layer. The policy layer decides whether the request is allowed, needs approval, or must be denied.

Tool classes:

| Class | Example | Default stance |
|---|---|---|
| Read-only local | Read repo files, inspect generated artifacts | Allowed within workspace policy |
| Read-only remote | Fetch issue, PR, documentation, supplier source | Allowed with source and privacy controls |
| Local transform | Format workbook, run linter, build graph | Allowed when input and output paths are bounded |
| External write | Create issue, comment, notify, update ticket | Approval or explicit user request required |
| Persistent business write | Change status, release artifact, mutate production record | L4 controls required |
| High-impact action | Financial, safety, legal, production, or rights-affecting change | L5 review required |

Each tool should have:

- A purpose statement.
- Allowed input ranges.
- Denied input ranges.
- Side-effect classification.
- Idempotency or duplicate-detection behavior.
- Rollback or compensation plan for writes.
- Audit fields for requester, model path, parameters, result, and time.

Tool results must not become truth automatically. The system should distinguish tool output, model interpretation, and verified conclusion.

### Closed-Loop Verification

Verification question:

```text
Can a reviewer prove that a tool call was authorized, bounded, auditable, and recoverable?
```

Pass conditions:

- Write tools require explicit user request or approval.
- Parameter validation runs before execution.
- Tool call logs include intent, parameters, result, actor, model path, and timestamp.
- Duplicate writes are detected or harmless.
- A rollback, compensation, or manual repair path exists for meaningful side effects.

Failure handling:

- If authorization cannot be proven, revoke the tool from autonomous use.
- If parameters are not bounded, move the tool behind human confirmation.
- If a side effect cannot be repaired, require pre-execution approval and stronger logging.

## 6. AI Runtime Security

### Governance Goal

AI runtime security must handle attacks that target instructions, context, memory, tools, and output interpretation. The system must assume that untrusted text can attempt to steer the model.

### Engineering Mechanism

Primary attack surfaces and controls:

| Attack surface | Risk | Control |
|---|---|---|
| Prompt injection | Untrusted text overrides system policy | Separate trusted instructions from retrieved content and ignore tool-like commands inside data |
| RAG contamination | Retrieved document contains malicious or stale instructions | Source allowlist, freshness checks, content labeling, retrieval quarantine |
| Tool misuse | Model calls a tool outside intent | Policy layer, tool schemas, approval gates, denied parameter ranges |
| Data exfiltration | Model leaks secrets or private context | Secret scanning, least-context loading, output filters, access scopes |
| Memory poisoning | Prior conversation or stored memory corrupts future behavior | Memory provenance, expiration, review, and delete paths |
| Cross-tenant leakage | Context from one user or project reaches another | Tenant isolation, access checks, context partitioning |
| Model or provider drift | Behavior changes without code changes | Version pinning where possible, eval reruns, release notes |
| Output manipulation | Model convinces a user to perform unsafe action | High-risk warnings, human review, source-backed recommendations |

Security design should preserve the difference between instructions and evidence:

```text
System policy is instruction.
User goal is request.
Retrieved content is evidence or untrusted data.
Tool output is observation.
Model text is interpretation until verified.
```

### Closed-Loop Verification

Verification question:

```text
Does the workflow resist hostile or stale context while preserving useful evidence?
```

Pass conditions:

- Retrieved content cannot define tool permissions.
- Untrusted text is labeled and scoped.
- Secrets and credentials are excluded from context.
- Injection and exfiltration cases appear in eval or manual test fixtures.
- Context boundaries can be audited after a failure.

Failure handling:

- If untrusted content can change instructions, isolate retrieval and block tool use.
- If secrets can enter context, remove the source and add scanning.
- If memory cannot be traced or deleted, do not use memory for high-risk workflows.

## 7. Cost, Latency, and Degradation Governance

### Governance Goal

An AI system is not governed if its cost, latency, retries, and fallback behavior are unknown. Runtime limits are part of the product contract.

### Engineering Mechanism

Each workflow should define budgets:

| Budget | Example control |
|---|---|
| Context budget | Maximum source count, maximum token window, source prioritization |
| Reasoning budget | Maximum planning steps or model rounds |
| Tool budget | Maximum tool calls, denied recursive tool loops |
| Cost budget | Per-request, per-user, per-workflow, or per-day caps |
| Latency budget | Timeout per model call, per tool call, and whole workflow |
| Retry budget | Retry count, backoff, retryable errors, non-retryable errors |
| Degradation budget | Smaller model, narrower context, read-only mode, manual handoff |

Fallback should be explicit:

- If retrieval fails, produce a source-missing response instead of inventing context.
- If a tool times out, preserve state and report the recovery point.
- If the model exceeds budget, summarize current state and request approval before continuing.
- If validation fails, return structured errors rather than silently rewriting the answer until it looks acceptable.

### Closed-Loop Verification

Verification question:

```text
Can the system stop, degrade, or recover without losing the audit trail?
```

Pass conditions:

- Budgets are documented for context, tools, retries, cost, and latency.
- Timeout behavior is deterministic.
- Partial progress is recorded with recovery points.
- Degraded output is labeled as degraded.
- A cost or retry spike can be attributed to a workflow and model path.

Failure handling:

- If no budget exists, cap tool loops and require manual continuation.
- If timeout loses state, add step recording before enabling long-running tasks.
- If degraded output is indistinguishable from normal output, block automated downstream use.

## 8. Governance Architecture

### Governance Goal

The architecture must surround the model with input boundaries, context management, tool policy, validation, state, and audit. The model is important, but it is not the whole system.

### Engineering Mechanism

Reference architecture:

```text
User goal
  -> input gateway
     - identity
     - permission
     - intent
     - risk classification
  -> context layer
     - facts
     - history
     - evidence
     - memory
     - access filters
  -> task orchestration layer
     - plan
     - steps
     - state
     - recovery point
  -> model reasoning layer
     - prompt contract
     - model version
     - policy
     - output schema
  -> tool governance layer
     - authorization
     - parameter validation
     - approval
     - side-effect control
  -> validation layer
     - schema
     - facts
     - business rules
     - conflicts
  -> output layer
     - result
     - evidence
     - uncertainty
     - required human action
  -> observation and audit layer
     - logs
     - replay
     - eval updates
     - incident review
```

Runtime state should record:

- Session id and workflow id.
- Risk level and active policy.
- Model and prompt version.
- Context source ids and timestamps.
- Tool call intent, parameters, and result.
- Validation result and errors.
- Human approvals or overrides.
- Final output and downstream write ids.

### Closed-Loop Verification

Verification question:

```text
Can an incident be replayed from user goal to final output and downstream side effect?
```

Pass conditions:

- Each runtime layer has a clear responsibility.
- Model reasoning is separated from tool execution.
- Validation runs after model output and before high-impact writes.
- Logs preserve enough information to reproduce the decision path.
- Audit records include both successful and refused actions.

Failure handling:

- If model output cannot be separated from tool execution, insert a policy boundary.
- If validation is post-hoc only, move it before side effects.
- If audit records are final-answer-only, add step and tool logs.

## 9. Overall Acceptance

### Governance Goal

The system is governed only when model capability can be scheduled, constrained, validated, recovered, audited, and improved over time.

### Engineering Mechanism

Overall acceptance checklist:

- Input boundaries are explicit.
- Facts, history, inference, assumption, recommendation, and uncertainty are separated.
- Runtime state has recovery points.
- Tools have authorization and side-effect boundaries.
- Output is schema-checked or template-checked where the downstream contract requires it.
- Errors can be replayed.
- Decisions can flow across phases without losing evidence.
- Cost, timeout, safety, and degradation are part of the main design.
- Evals and incidents feed back into prompts, policies, tools, and documentation.

Governance conclusion:

```text
When an organization can classify, authorize, evaluate, release, monitor, audit, and improve model capability, that capability has entered software engineering governance.
```

### Closed-Loop Verification

Verification question:

```text
Does the workflow have enough structure to keep useful model uncertainty inside controlled engineering boundaries?
```

Pass conditions:

- The risk level determines tool access and review gates.
- Evidence determines what can be stated as fact.
- Validation determines what can flow downstream.
- Runtime state determines what can be recovered.
- Audit records determine what can be learned after failure.

Failure handling:

- If the workflow cannot be replayed, do not automate downstream effects.
- If validation is weaker than the risk level, demote the workflow or strengthen controls.
- If ownership is unclear, keep the capability experimental until responsibility is assigned.
