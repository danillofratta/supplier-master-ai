# Implementation package — 2026-08-24

This update adds the application-facing Agent layer without removing the existing Supplier, RAG, policy-ingest, onboarding or messaging behavior.

## Added

- FastAPI Agent API over the existing LangGraph runtime.
- React AI Agent page.
- Persistent conversation restore through LangGraph PostgreSQL checkpoints.
- Web Human-in-the-Loop approval cards.
- Dedicated comprehensive supplier investigation tool and endpoint.
- Agent model-provider factory for Bedrock, OpenAI and Gemini.
- Bedrock remains the default provider.
- Agent `.env.example` and frontend Agent API environment variable.
- Business, technical and Agent/UI documentation.

## Preserved

- Existing `.env` files are not deleted or replaced.
- Existing Supplier UI and direct review experience remain available.
- Existing Policy Ingest frontend remains available.
- Existing Supplier API RAG implementation remains on Bedrock + Titan + OpenSearch.
- Existing MCP, Gateway and event-driven SAP flow remain the system boundaries.

## Small consistency correction

The MCP `ingest_supplier_policy` tool no longer accepts an LLM-supplied `confirmed` boolean. Human approval is enforced by LangGraph HITL, consistent with the other state-changing Agent operations.

## Deleted files

None.
