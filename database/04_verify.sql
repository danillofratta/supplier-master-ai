-- psql helper. Run from postgres database:
-- psql -U postgres -d postgres -f database\04_verify.sql

\connect supplier_db
SELECT current_database() AS database;
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

SELECT workflow_id, correlation_id, supplier_id, status
FROM supplier_onboarding_workflow
ORDER BY created_at DESC
LIMIT 10;

\connect sap_integration_db
SELECT current_database() AS database;
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

SELECT
    operation_id,
    message_id,
    correlation_id,
    workflow_id,
    supplier_id,
    status,
    attempts
FROM sap_sync_operations
ORDER BY created_at DESC
LIMIT 10;
