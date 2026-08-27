-- Run connected to the default postgres database with psql.
-- Example:
-- psql -U postgres -d postgres -f database\00_create_databases.sql

SELECT 'CREATE DATABASE supplier_db'
WHERE NOT EXISTS (
    SELECT 1 FROM pg_database WHERE datname = 'supplier_db'
)\gexec

SELECT 'CREATE DATABASE sap_integration_db'
WHERE NOT EXISTS (
    SELECT 1 FROM pg_database WHERE datname = 'sap_integration_db'
)\gexec

SELECT 'CREATE DATABASE supplier_agent_db'
WHERE NOT EXISTS (
    SELECT 1 FROM pg_database WHERE datname = 'supplier_agent_db'
)\gexec
