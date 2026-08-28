# API Gateway

Public edge service for the Supplier Master application.

## Responsibilities

- exposes public `/api/v1/*` routes;
- hides the internal Supplier API URL from browser clients;
- creates or propagates `X-Correlation-ID`;
- propagates `Authorization` for future downstream enforcement;
- centralizes downstream timeout and `503/504` handling;
- provides liveness/readiness endpoints;
- configures frontend CORS.

The Gateway is intentionally thin: Supplier business rules remain in `api-supplier`.

## Local run

Start Supplier API on port `8001`, then Gateway on `8000`:

```powershell
cd backend\api-supplier
python -m uvicorn api_supplier.main:app --reload --port 8001
```

```powershell
cd backend\api-gateway
python -m pip install -e .
python -m uvicorn api_gateway.main:app --reload --port 8000
```

Browser/frontend base URL:

```text
http://localhost:8000/api
```

## Public routes

```text
GET  /api/v1/suppliers
POST /api/v1/suppliers
GET  /api/v1/suppliers/{supplier_id}
POST /api/v1/suppliers/{supplier_id}/analysis
GET  /api/v1/suppliers/{supplier_id}/onboarding
POST /api/v1/suppliers/{supplier_id}/onboarding
POST /api/v1/suppliers/{supplier_id}/onboarding/review-decision
POST /api/v1/policies/ingest
```

## Health

```text
GET /health
GET /health/live
GET /health/ready
```

`/health/ready` returns `503` when the downstream Supplier API cannot be reached.

## Correlation and errors

`X-Correlation-ID` is accepted from a caller when present or generated at the edge when missing, then propagated downstream. It is a business/operational correlation aid and is distinct from OpenTelemetry `trace_id`.
