# ADR 001: Deterministic workflow with AI-ssisted decisions

## Context

Supplier onboarding includes financial, compliance and operational risks. A fully autonomous agent would make the process hardes to test, audit and control.

## Decision

The application will use a deterministic workflow to control supplier onboarding.

AI will be used for:
- document interpretation
- policy retrieval
- risk recommendation
- missing information detection

Business rules will control:
- workflow transitions
- approval requiments
- SAP updates
- retries
- idempotency
- audit record

# Consequences

## Benefits

- Better auditability
- Predictable execution
- Easir testing
- Human approval for critical actions
- Lower risck of unauthorized AI action

## Trade-offs

- Less autonomy
- More workflow code
- Additional orchestration complexity
