# Run the distributed messaging flow

This guide focuses on the Supplier → SAP request → SAP result integration path.

## 1. PostgreSQL

For Docker-based local development, start PostgreSQL and the core services with:

```powershell
docker compose up --build
```

Database bootstrap is consolidated in:

```text
database/init.sql
```

To align a manually managed local PostgreSQL instance:

```powershell
psql -U postgres -d postgres -f database\init.sql
```

To rebuild the Docker PostgreSQL volume from scratch:

```powershell
docker compose down -v
docker compose up --build
```

## 2. AWS SQS / DLQ topology

The application expects request/result queues and their DLQs:

```text
supplier-sap-sync-requests
supplier-sap-sync-requests-dlq
supplier-sap-sync-results
supplier-sap-sync-results-dlq
```

Create/reconcile the topology:

```powershell
python scripts\aws\setup_sqs.py
```

The setup script configures long polling, visibility timeout and a redrive policy with `maxReceiveCount=5`.

If you intentionally need to purge old local test messages during topology setup:

```powershell
$env:SQS_PURGE_EXISTING = 'true'
python scripts\aws\setup_sqs.py
```

Do not enable queue purging in a shared/production environment.

## 3. Processes in the flow

### Supplier Outbox publisher

```powershell
cd backend\worker-supplier-outbox
python -m worker_supplier_outbox.main
```

### SAP request consumer

```powershell
cd backend\consumer-sap
python -m consumer_sap.main
```

### SAP result Outbox publisher

```powershell
cd backend\worker-sap-outbox
python -m worker_sap_outbox.main
```

### Supplier SAP result consumer

```powershell
cd backend\consumer-supplier-sap-result
python -m consumer_supplier_sap_result.main
```

Docker Compose already starts these processes in the core stack.

## 4. Reliability behavior

### Supplier transaction

When onboarding is approved/allowed:

1. workflow moves to `syncing_to_sap`;
2. a `supplier.sap-sync.requested.v1` event is stored in the Supplier Outbox;
3. both changes commit in the local Supplier database transaction.

The Outbox worker later publishes the event. Publishing is at-least-once, so the consumer must tolerate duplicates.

### SAP request consumer

The SAP consumer:

1. validates/maps the integration event;
2. uses Inbox/message identity for duplicate protection;
3. persists SAP synchronization operation state;
4. calls the SAP gateway boundary;
5. stores a result event in the SAP Integration Outbox;
6. commits before deleting the SQS request message.

### Result path

The SAP Outbox worker publishes the result event. The Supplier result consumer uses its Inbox and updates the Supplier onboarding workflow to its final state.

## 5. Message envelope

Integration events carry:

- `message_id`;
- `correlation_id`;
- `event_type`;
- `version`;
- `occurred_at`;
- `payload`.

`message_id` identifies one event. `correlation_id` follows the end-to-end onboarding flow.

## 6. Retry and DLQ behavior

When a consumer fails before successful local commit:

1. the SQS message is not deleted;
2. it becomes visible after the visibility timeout;
3. Inbox/idempotency protects duplicate processing;
4. after repeated receives, the redrive policy moves it to the DLQ.

Operationally, DLQ replay should be a controlled action after the underlying error is understood.
