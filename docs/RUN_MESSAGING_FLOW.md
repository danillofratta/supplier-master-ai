# Run the distributed messaging flow

## 1. PostgreSQL

Start PostgreSQL:

```cmd
docker compose up -d
```

For a new environment:

```cmd
psql -U postgres -d postgres -f database\00_create_databases.sql
psql -U postgres -d supplier_db -f database\01_supplier_db.sql
psql -U postgres -d sap_integration_db -f database\02_sap_integration_db.sql
```

For databases created from an older project ZIP:

```cmd
psql -U postgres -d postgres -f database\03_upgrade_existing.sql
```

Verify:

```cmd
psql -U postgres -d postgres -f database\04_verify.sql
```

## 2. AWS SQS / DLQ

The application expects:

```text
supplier-sap-sync-requests
supplier-sap-sync-requests-dlq
supplier-sap-sync-results
supplier-sap-sync-results-dlq
```

To create or reconcile the topology:

```cmd
python scripts\aws\setup_sqs.py
```

The script configures long polling, a 60-second visibility timeout and
`maxReceiveCount=5`.

Because this version introduces a new standard event envelope, old local
test messages should be removed once. To purge the four queues during
setup:

```cmd
set SQS_PURGE_EXISTING=true
python scripts\\aws\\setup_sqs.py
```

## 3. Run the messaging processes

Supplier Outbox:

```cmd
cd backend\worker-supplier-outbox
python -m worker_supplier_outbox.main
```

SAP request consumer:

```cmd
cd backend\consumer-sap
python -m consumer_sap.main
```

SAP result Outbox:

```cmd
cd backend\worker-sap-outbox
python -m worker_sap_outbox.main
```

Supplier SAP result consumer:

```cmd
cd backend\consumer-supplier-sap-result
python -m consumer_supplier_sap_result.main
```

## Reliability behavior

Messages are deleted from SQS only after local persistence commits.

If a consumer fails:

1. the message is not deleted;
2. SQS makes it visible again after the visibility timeout;
3. Inbox/idempotency protects against duplicate side effects;
4. after repeated failures the SQS redrive policy sends it to the DLQ.

All new integration events carry:

- `message_id`: unique message identity;
- `correlation_id`: end-to-end flow identity;
- `event_type`;
- `version`;
- `occurred_at`;
- `payload`.

The same `correlation_id` is propagated from Supplier onboarding through SAP
request and SAP result messages. Runtime processes emit structured JSON logs
containing those identifiers.
