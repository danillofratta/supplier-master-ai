# Database bootstrap

The `database/` folder now has a **single SQL bootstrap/alignment script**:

```text
database/init.sql
```

It replaces the previous numbered create/schema/upgrade/verify scripts and the `database/init/` subfolder.

## What `init.sql` manages

The script:

1. creates `supplier_db`, `sap_integration_db` and `supplier_agent_db` when missing;
2. creates/alignment-checks the Supplier schema;
3. creates/alignment-checks the SAP Integration schema;
4. includes durable onboarding idempotency (`idempotency_key` + unique/partial indexes);
5. includes `correlation_id`, Inbox/Outbox `attempts` and current status constraints;
6. returns a small verification summary at the end.

` supplier_agent_db` intentionally has no business tables in this script. LangGraph creates and evolves its checkpoint tables at Agent API startup through `AsyncPostgresSaver.setup()`.

## Docker bootstrap

`docker-compose.yml` mounts the file as a PostgreSQL initialization script:

```text
./database/init.sql:/docker-entrypoint-initdb.d/001-init.sql:ro
```

PostgreSQL executes files under `/docker-entrypoint-initdb.d` only when its data directory is initialized for the first time.

To rebuild the local databases from scratch:

```powershell
docker compose down -v
docker compose up --build
```

## Manual local alignment

Because `init.sql` uses `psql` meta-commands such as `\connect` and `\gexec`, run it through `psql`:

```powershell
psql -U postgres -d postgres -f database\init.sql
```

The DDL is written to tolerate re-execution for the current local/reference schema, including backfills for columns added by earlier project versions.

## Production note

The consolidated script is a bootstrap/reference convenience. It is **not a replacement for controlled production migrations**. Application migrations such as the onboarding-idempotency migration remain useful for upgrading deployed environments with explicit change control.

## Ownership

- `supplier_db`: Supplier bounded context.
- `sap_integration_db`: SAP Integration bounded context.
- `supplier_agent_db`: LangGraph runtime/checkpoint state.

There are no cross-database foreign keys. Communication between Supplier and SAP Integration occurs through versioned integration events.
