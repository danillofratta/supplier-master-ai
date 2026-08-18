# Supplier Master AI

Microservice-oriented monorepo. Each deployable has its own Python package,
dependencies and tests.

```text
backend/
├── api-supplier/
├── worker-supplier-outbox/
├── consumer-sap/
└── consumer-supplier-sap-result/

contracts/
docs/
```

## Database ownership

`api-supplier`, `worker-supplier-outbox`, and
`consumer-supplier-sap-result` belong to the Supplier bounded context and
operate on `supplier_db`.

`consumer-sap` owns a separate `sap_integration_db`. It never reads or writes
`Supplier` tables.

### supplier_db
- suppliers
- supplier_onboarding_workflow
- outbox_messages
- inbox_messages (for inbound integration results)

### sap_integration_db
- inbox_messages
- sap_sync_operations
- outbox_messages

The services communicate through versioned integration events, not shared
domain entities or cross-service database access.
