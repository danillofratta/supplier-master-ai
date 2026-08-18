# Running the distributed SAP messaging flow

## Databases

Supplier bounded context:

```text
supplier_db
```

SAP Integration bounded context:

```text
sap_integration_db
```

Apply the final schema alignment once:

```cmd
psql -U postgres -d sap_integration_db -f database\05_finalize_messaging_schema.sql
psql -U postgres -d supplier_db -f database\06_supplier_inbox_schema.sql
```

## AWS SQS queues

```text
supplier-sap-sync-requests
supplier-sap-sync-results
```

Their DLQs remain configured in AWS.

## Processes

Open a terminal for each process.

### Supplier Outbox Worker

```cmd
cd backend\worker-supplier-outbox
python -m worker_supplier_outbox.main
```

Reads `supplier_db.outbox_messages` and publishes request events to
` supplier-sap-sync-requests`.

### SAP Consumer

```cmd
cd backend\consumer-sap
python -m consumer_sap.main
```

Consumes request events, uses the SAP Integration database, executes the
current Fake SAP adapter, and atomically persists:

- `sap_sync_operations`
- `inbox_messages`
- SAP result `outbox_messages`

### SAP Outbox Worker

```cmd
cd backend\worker-sap-outbox
python -m worker_sap_outbox.main
```

Reads `sap_integration_db.outbox_messages` and publishes result events to
`supplier-sap-sync-results`.

### Supplier SAP Result Consumer

```cmd
cd backend\consumer-supplier-sap-result
python -m consumer_supplier_sap_result.main
```

Consumes SAP results, uses `supplier_db.inbox_messages` for idempotency,
and changes the onboarding workflow from `syncing_to_sap` to `completed`
or `failed`.

## End-to-end flow

```text
api-supplier
    |
supplier_db + transactional outbox
    |
worker-supplier-outbox
    |
supplier-sap-sync-requests (SQS)
    |
consumer-sap
    |
sap_integration_db
    |-- inbox_messages
    |-- sap_sync_operations
    `-- outbox_messages
    |
worker-sap-outbox
    |
supplier-sap-sync-results (SQS)
    |
consumer-supplier-sap-result
    |
supplier_db
    |
workflow COMPLETED / FAILED
```

SQS messages are deleted only after the relevant database transaction
commits successfully. Failed messages are left in SQS for retry and eventual
DLQ handling. Duplicate processing is protected with Inbox/idempotency data.
