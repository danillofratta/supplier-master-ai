-- Run connected to the default "postgres" database.
-- CREATE DATABASE cannot run inside a transaction block.

SELECT 'CREATE DATABASE supplier_db'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'supplier_db'
)\gexec

SELECT 'CREATE DATABASE sap_integration_db'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'sap_integration_db'
)\gexec
