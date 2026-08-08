# Supplier Master AI

FastAPI portfolio project for supplier onboarding, deterministic workflow control, Amazon Bedrock analysis, and enterprise integration patterns.

## Architecture

```text
API request/response (Pydantic)
        ↓
Vertical slice command + handler
        ↓
Application ports and immutable results
        ↓
Domain entities and rules
        ↓
Infrastructure adapters (repository, Amazon Bedrock)
```

The API response model is used only at the HTTP boundary. The analysis handler works with `SupplierAnalysisResult`, while the Bedrock adapter validates untrusted model output with an infrastructure Pydantic model before mapping it to the application result.

## Installation

Run commands from the repository root.

### API without AWS SDK

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .\backend
uvicorn backend.app.main:app --reload
```

The create-supplier endpoint and automated API tests do not require `boto3`.

### API with Amazon Bedrock

```powershell
pip install -e ".\backend[ai]"
```

Configure `.env` using `backend/.env.example`, and configure AWS credentials through the standard AWS credential chain.

### Development and tests

```powershell
pip install -e ".\backend[all]"
pytest .\backend\tests -q
```

### Manual Bedrock smoke test

```powershell
python -m backend.scripts_test_bedrock_analysis
```

This command invokes the real provider and may incur AWS charges.

## Composition root

Dependencies are composed in `backend/app/bootstrap/dependencies.py`. The Bedrock adapter is imported lazily only when the analysis dependency is resolved. Therefore, importing and starting the API does not require `boto3`; invoking the analysis endpoint requires the `ai` extra and `BEDROCK_MODEL_ID`.
