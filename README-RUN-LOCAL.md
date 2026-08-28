# Run Supplier Master AI locally

This guide reflects the current repository runtime. The **core distributed stack** runs in Docker Compose. MCP and the LangGraph Agent API are currently started as local Python processes.

## 1. Prerequisites

- Docker Desktop / Docker Compose.
- Python 3.11+ for MCP and Agent local processes.
- AWS credentials/profile with access to the configured Bedrock model, Titan embeddings, OpenSearch Serverless and SQS queues.
- Existing project `.env` files for local development. Real `.env` files are not committed.

## 2. Configure Docker-facing SQS values

From the repository root:

```powershell
Copy-Item .env.docker.example .env.docker
```

Set the request/result SQS queue URLs in `.env.docker`.

The Supplier API continues to use its existing local environment configuration for Bedrock/OpenSearch. Do not replace working `.env` files with example files.

## 3. Database bootstrap

PostgreSQL mounts a single bootstrap file:

```text
database/init.sql
```

On a new PostgreSQL volume, it creates:

- `supplier_db`;
- `sap_integration_db`;
- `supplier_agent_db`;
- Supplier and SAP Integration schemas/indexes/constraints.

LangGraph creates its checkpoint tables in `supplier_agent_db` when the Agent API starts (`AsyncPostgresSaver.setup()`).

## 4. Start the core stack

```powershell
docker compose up --build
```

This starts:

- PostgreSQL;
- Supplier API;
- API Gateway;
- Supplier Outbox Worker;
- SAP Consumer;
- SAP Outbox Worker;
- Supplier SAP Result Consumer;
- React frontend;
- OpenTelemetry Collector;
- Jaeger.

Core endpoints:

| Component | URL |
|---|---|
| Frontend | `http://localhost:5173` |
| API Gateway | `http://localhost:8000` |
| Supplier API docs | `http://localhost:8001/docs` |
| Jaeger | `http://localhost:16686` |
| PostgreSQL | `localhost:5432` |

## 5. Start MCP

The current MCP server entry point is `supplier_mcp.server`.

```powershell
cd backend\mcp-supplier
python -m pip install -e .
python -m supplier_mcp.server
```

Expected endpoint:

```text
http://127.0.0.1:8010/mcp
```

The current MCP server is local-development oriented and calls the Gateway at `http://localhost:8000`.

## 6. Start the Agent API

Copy/configure the Agent example only if you do not already have a working local `.env`:

```powershell
cd backend\agent-supplier
python -m pip install -e .
python -m supplier_agent.api_main
```

Minimum Bedrock settings are documented in `backend/agent-supplier/.env.example`.

Expected Agent API:

```text
http://127.0.0.1:8011
```

The Windows-specific `api_main` entry point configures the selector event loop required by async Psycopg before starting Uvicorn.

## 7. Demo flow

1. Open `http://localhost:5173`.
2. In **Policy Ingest**, ingest at least one supplier onboarding policy.
3. Create a supplier.
4. Open Supplier Details.
5. Optionally run **AI Analysis** to inspect the RAG/LLM recommendation without starting the workflow.
6. Start onboarding.
7. If business rules require review, approve or reject the persisted onboarding review.
8. When approved/automatic, the Supplier API writes the SAP request event to its Transactional Outbox.
9. `worker-supplier-outbox` publishes the request to SQS.
10. `consumer-sap` processes it through the fake SAP adapter and persists a SAP result Outbox event.
11. `worker-sap-outbox` publishes the result.
12. `consumer-supplier-sap-result` completes/fails the Supplier workflow.
13. The frontend polls active synchronization and displays the final result.
14. With MCP + Agent running, open **AI Agent** or use **Investigate with Agent** from Supplier Details.

## 8. Reset or align local PostgreSQL

Docker initialization runs only when the PostgreSQL volume is first created.

To recreate the development databases from scratch:

```powershell
docker compose down -v
docker compose up --build
```

To manually re-run the consolidated alignment script against an existing local PostgreSQL instance:

```powershell
psql -U postgres -d postgres -f database\init.sql
```

Review this command before using it against any non-local environment. Production schema evolution should use controlled migrations rather than a bootstrap script.

## 9. Run automated backend tests

From the repository root, make the six tested service packages importable and use pytest importlib mode to avoid duplicate test-module names:

```powershell
$env:PYTHONPATH = @(
  "$PWD\backend\api-gateway",
  "$PWD\backend\api-supplier",
  "$PWD\backend\consumer-sap",
  "$PWD\backend\consumer-supplier-sap-result",
  "$PWD\backend\worker-sap-outbox",
  "$PWD\backend\worker-supplier-outbox"
) -join ';'

python -m pytest --import-mode=importlib `
  backend/api-gateway/tests `
  backend/api-supplier/tests `
  backend/consumer-sap/tests `
  backend/consumer-supplier-sap-result/tests `
  backend/worker-sap-outbox/tests `
  backend/worker-supplier-outbox/tests -q
```

Current validated result:

```text
56 passed
```
