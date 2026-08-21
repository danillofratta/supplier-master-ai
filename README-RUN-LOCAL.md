# Run the complete Supplier Master AI locally

## 1. AWS prerequisites
The Docker stack uses your existing AWS Bedrock, OpenSearch Serverless and two SQS queues. It does not replace or modify model/OpenSearch configuration.

Make sure the AWS profile used locally can access Bedrock, OpenSearch and SQS.

## 2. Docker environment
From this folder:

```cmd
copy .env.docker.example .env.docker
```

Edit only the two SQS queue URLs in `.env.docker`.

The existing `api-supplier/.env` is reused for Bedrock/OpenSearch configuration.

## 3. Start everything

```cmd
docker compose up --build
```

Endpoints:
- Frontend: http://localhost:5173
- Gateway: http://localhost:8000
- Supplier API docs: http://localhost:8001/docs
- Jaeger traces: http://localhost:16686
- PostgreSQL: localhost:5432

## 4. Demo flow
1. Open **Policy Ingest** and ingest at least one supplier onboarding policy.
2. Create a supplier.
3. Open supplier details.
4. Optional: use **Run AI Analysis** to inspect the decision only.
5. Click **Start AI Onboarding** for the real workflow.
6. If AI/deterministic rules require human review, approve/reject in the UI.
7. Approval creates the transactional Outbox event.
8. `worker-supplier-outbox` publishes it to the request SQS queue.
9. `consumer-sap` processes it through the current Fake SAP adapter and writes the SAP result Outbox event.
10. `worker-sap-outbox` publishes the result event.
11. `consumer-supplier-sap-result` updates the supplier onboarding workflow.
12. The frontend polls while SAP sync is active and displays the final `completed` state and Business Partner ID.

## Reset local PostgreSQL
The initialization SQL runs only when the PostgreSQL volume is created. To recreate both databases from scratch:

```cmd
docker compose down -v
docker compose up --build
```
