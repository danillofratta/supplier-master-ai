# ADR 001: Deterministic workflow with AI-assisted decisions

## Status

Accepted.

## Context

Supplier onboarding carries compliance, financial and operational risk. A fully autonomous Agent that can interpret policy and directly execute ERP actions would be difficult to test, audit and constrain.

The system still benefits from AI for document interpretation and contextual risk analysis, but those probabilistic outputs should not become the transaction authority.

## Decision

Supplier onboarding is controlled by a deterministic, persisted application workflow.

AI is used for:

- policy/document interpretation;
- RAG-grounded risk recommendation;
- missing-information detection;
- contextual summaries and investigation assistance.

Deterministic application/domain logic controls:

- workflow transitions;
- whether business human review is required;
- onboarding idempotency and concurrency invariants;
- creation of SAP synchronization integration events;
- retry/error state semantics;
- persistence boundaries.

When the LangGraph Agent proposes a state-changing tool, a separate Agent Human-in-the-Loop control must approve execution before the MCP capability is invoked.

## Consequences

### Benefits

- predictable workflow execution;
- stronger auditability and explainability;
- easier automated testing of business rules;
- explicit human control for critical/uncertain actions;
- lower risk of unauthorized model-driven side effects;
- clearer separation between AI recommendation and business authority.

### Trade-offs

- less Agent autonomy;
- additional workflow/orchestration code;
- more explicit state management;
- two approval concepts must be understood: business review and Agent tool approval.
