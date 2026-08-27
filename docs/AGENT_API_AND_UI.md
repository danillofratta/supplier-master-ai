# Agent API and Web UI

## Purpose

The Agent API turns the existing CLI LangGraph proof of concept into an application capability consumable by the React frontend.

It preserves the same guarantees already proven in the CLI:

- Bedrock tool calling;
- MCP capability boundary;
- PostgreSQL LangGraph checkpoints;
- persistent threads;
- Human-in-the-Loop interrupts;
- human approval before state-changing MCP tools;
- application-generated idempotency keys.

## Local configuration

The repository keeps the real `backend/agent-supplier/.env` untouched. A new `.env.example` documents the supported variables.

Minimum Bedrock configuration:

```env
AGENT_AI_PROVIDER=bedrock
AWS_REGION=us-east-2
BEDROCK_MODEL_ID=openai.gpt-oss-120b-1:0
SUPPLIER_MCP_URL=http://127.0.0.1:8010/mcp
LANGGRAPH_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/supplier_agent_db
AGENT_API_HOST=127.0.0.1
AGENT_API_PORT=8011
```

Frontend:

```env
VITE_API_URL=http://localhost:8000/api
VITE_AGENT_API_URL=http://localhost:8011/api
```

## Install Agent dependencies

```powershell
cd backend\agent-supplier
python -m pip install -e .
```

Optional providers:

```powershell
python -m pip install -e ".[openai]"
python -m pip install -e ".[gemini]"
# or both
python -m pip install -e ".[providers]"
```

## Run order

A practical local order is:

1. PostgreSQL / OpenSearch dependencies;
2. Supplier API (`:8001`);
3. API Gateway (`:8000`);
4. MCP Supplier server (`:8010`);
5. Agent API (`:8011`);
6. React frontend (`:5173`).

Run the Agent API on Windows with:

```powershell
cd backend\agent-supplier
python -m supplier_agent.api_main
```

`api_main` configures the Windows selector event loop required by async Psycopg and then starts Uvicorn.

## React experience

The sidebar now includes **AI Agent**.

The page provides:

- persistent Agent thread ID;
- multi-turn chat;
- full supplier investigation shortcut;
- automatic restoration of persisted conversation state;
- pending-action cards;
- approve/reject controls;
- optional reviewer note;
- a visible list of agent capabilities.

Supplier Details also includes **Investigate with Agent**, which opens the Agent page with the supplier UUID pre-filled.

## HITL request lifecycle

```text
React
  ↓ POST message
Agent API
  ↓
LangGraph
  ↓ tool request
HumanInTheLoopMiddleware
  ↓
PostgreSQL checkpoint
  ↓
Agent API returns pending_approval
  ↓
React renders approval card
  ↓ approve/reject
Agent API
  ↓ Command(resume=...)
LangGraph continues
```

The UI does not manufacture `confirmed=true`. The approval decision is represented by LangGraph resume semantics.

## Provider selection

### Bedrock (default)

```env
AGENT_AI_PROVIDER=bedrock
AWS_REGION=us-east-2
BEDROCK_MODEL_ID=openai.gpt-oss-120b-1:0
```

### OpenAI

Install the optional dependency and configure:

```env
AGENT_AI_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=...
```

### Gemini

Install the optional dependency and configure:

```env
AGENT_AI_PROVIDER=gemini
GOOGLE_API_KEY=...
GEMINI_MODEL=...
```

Provider modules are imported lazily. This is intentional: the Bedrock installation remains the default and does not require OpenAI/Gemini packages.
