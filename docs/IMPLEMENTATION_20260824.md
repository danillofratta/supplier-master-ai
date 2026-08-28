# Implementation snapshot — 2026-08-24

> Historical note: this file records the Agent/UI expansion delivered on 2026-08-24. For the current architecture and runtime instructions, use `README.md`, `docs/TECHNICAL_ARCHITECTURE.md` and `README-RUN-LOCAL.md`.

## Added in this snapshot

- FastAPI Agent API over the LangGraph runtime.
- React AI Agent page.
- Persistent conversation restoration through LangGraph PostgreSQL checkpoints.
- Web Human-in-the-Loop approval cards.
- Comprehensive supplier investigation capability.
- Agent model-provider factory for Bedrock, OpenAI and Gemini.
- Bedrock preserved as the default provider.
- Agent `.env.example` and frontend Agent API URL configuration.
- Business, technical and Agent/UI documentation.

## Preserved

- Existing real `.env` files were not deleted or replaced.
- Supplier UI and direct business-review experience remained available.
- Policy Ingest UI remained available.
- Supplier API RAG implementation remained Bedrock + Titan + OpenSearch.
- MCP, Gateway and event-driven SAP integration remained architectural boundaries.

## Consistency correction included

The MCP `ingest_supplier_policy` operation does not accept an LLM-supplied `confirmed` flag. Human approval for Agent-originated state changes is enforced by LangGraph Human-in-the-Loop middleware.

## Current follow-up status

Since this snapshot, project documentation has been consolidated and local database bootstrap is now represented by a single `database/init.sql` script. The current backend validation suite reports `56 passed`; Agent/MCP automated coverage remains a hardening item.
