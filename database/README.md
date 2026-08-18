# PostgreSQL bootstrap

## 1. Create the two databases

From PowerShell:

```powershell
psql -U postgres -d postgres -f 00_create_databases.sql
```

## 2. Create Supplier tables

```powershell
psql -U postgres -d supplier_db -f 01_supplier_db.sql
```

## 3. Create SAP Integration tables

```powershell
psql -U postgres -d sap_integration_db -f 02_sap_integration_db.sql
```

## 4. Verify

```powershell
psql -U postgres -d supplier_db -f 03_verify.sql
psql -U postgres -d sap_integration_db -f 03_verify.sql
```

Expected ownership:

- `supplier_db`: `suppliers`, `supplier_onboarding_workflow`, `outbox_messages`, `inbox_messages`.
- `sap_integration_db`: `inbox_messages`, `sap_sync_operations`, `outbox_messages`.

The two bounded contexts do not use cross-database foreign keys.
