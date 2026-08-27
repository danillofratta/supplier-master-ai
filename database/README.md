# PostgreSQL scripts

These files are the only database bootstrap/upgrade scripts required by the
project.

## New local environment

```cmd
psql -U postgres -d postgres -f database\00_create_databases.sql
psql -U postgres -d supplier_db -f database\01_supplier_db.sql
psql -U postgres -d sap_integration_db -f database\02_sap_integration_db.sql
```

## Existing local environment

If the databases were created using an older project ZIP, run:

```cmd
psql -U postgres -d postgres -f database\03_upgrade_existing.sql
```

## Verify

```cmd
psql -U postgres -d postgres -f database\04_verify.sql
```

Database ownership:

- `supplier_db`: API Supplier + Supplier Outbox worker + SAP result consumer.
- `sap_integration_db`: SAP consumer + SAP Outbox worker.
- `supplier_agent_db`: LangGraph checkpoints for Agent conversations and HITL interrupts. LangGraph creates its internal tables with `checkpointer.setup()`.
- No cross-database foreign keys are used.
