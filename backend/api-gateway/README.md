# API Gateway

Public edge service for the Supplier Master application.

## Responsibilities

- exposes the public `/api/v1/*` routes;
- hides internal service URLs from the frontend;
- creates or propagates `X-Correlation-ID`;
- propagates `Authorization` for future JWT enforcement;
- centralizes downstream timeouts and `503/504` errors;
- provides liveness and readiness endpoints;
- configures frontend CORS.

## Local run

Start `api-supplier` on port 8001:

```cmd
cd backend\api-supplier
python -m uvicorn api_supplier.main:app --reload --port 8001
```

Then start the gateway on port 8000:

```cmd
cd backend\api-gateway
python -m pip install -e .
python -m uvicorn api_gateway.main:app --reload --port 8000
```

Frontend base URL:

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
```

Health:

```text
GET /health
GET /health/live
GET /health/ready
```

`/health/ready` returns 503 when `api-supplier` cannot be reached.
