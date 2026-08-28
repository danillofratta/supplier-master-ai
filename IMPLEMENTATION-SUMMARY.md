# Current implementation summary

This document summarizes the current repository state. It is not a changelog; dated implementation notes remain under `docs/` for historical context.

## Implemented application flow

- Supplier creation, listing and detail views.
- RAG-based supplier analysis using Titan embeddings, OpenSearch and Amazon Bedrock.
- Policy ingestion API and React screen.
- Governed onboarding workflow with deterministic decision rules.
- Explicit human review decision endpoint (`approve` / `reject`).
- Durable onboarding idempotency and concurrency protection.
- Transactional Supplier Outbox and asynchronous SAP request publication.
- Idempotent SAP consumer with its own persistence boundary and fake SAP adapter.
- Transactional SAP result Outbox and asynchronous result publication.
- Supplier result consumer that completes/fails the persisted workflow.
- React polling for long-running SAP synchronization.

## Agent layer

- FastAPI Agent API.
- LangGraph/LangChain runtime with PostgreSQL checkpoints.
- MCP tools/resources as the business capability boundary.
- Persistent Agent threads and conversation restoration.
- LangGraph Human-in-the-Loop interrupts for state-changing tools.
- Runtime-generated idempotency key for onboarding calls.
- Composite read-only `investigate_supplier` capability.
- Bedrock as the default Agent provider, with optional OpenAI/Gemini adapters.

## Runtime and platform

- React + TypeScript frontend.
- PostgreSQL 16 with separate Supplier, SAP Integration and Agent databases.
- Single database bootstrap script: `database/init.sql`.
- AWS SQS request/result queues and DLQs.
- Structured JSON logging, correlation IDs and OpenTelemetry integration.
- Jaeger + OpenTelemetry Collector in Docker Compose.

## Local runtime note

`docker compose up --build` starts the core application, databases, workers/consumers, frontend and observability stack. MCP (`:8010`) and Agent API (`:8011`) are currently launched as local Python processes; see `README-RUN-LOCAL.md`.

## Validation

The current automated backend suites for Gateway, Supplier API, consumers and workers run successfully:

```text
56 passed
```

`agent-supplier` and `mcp-supplier` do not yet have equivalent automated test suites and remain a documented hardening area.
