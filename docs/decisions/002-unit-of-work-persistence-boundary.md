# ADR 002: Unit of Work as the persistence transaction boundary

## Status

Accepted.

## Context

Supplier use cases need transactional consistency without coupling application handlers to SQLAlchemy, PostgreSQL, `AsyncSession`, `commit()` or `rollback()` details.

The architecture also needs one local transaction to persist related business state and Transactional Outbox records where required.

## Decision

Application features depend on Unit of Work protocols rather than concrete SQLAlchemy sessions.

For the Supplier context, a Unit of Work exposes repositories required by a use case and owns transaction completion:

- repository access is exposed through technology-agnostic contracts;
- `commit()` makes use-case changes durable;
- `rollback()` reverts the active transaction;
- SQLAlchemy details remain in infrastructure.

`SqlAlchemySupplierUnitOfWork` is the PostgreSQL implementation. In-memory implementations support focused unit tests.

The same principle is used by messaging/integration services with context-specific Unit of Work implementations rather than sharing Supplier persistence internals.

## Consequences

### Benefits

- handlers remain independent from SQLAlchemy/PostgreSQL APIs;
- multiple repository changes can participate in one local transaction;
- Outbox creation can share the business transaction;
- test doubles can run without a database;
- bounded contexts keep independent persistence implementations.

### Trade-offs

- one more abstraction in the application layer;
- repository/Unit of Work contracts must remain technology-agnostic;
- database-specific optimizations stay inside infrastructure and can require implementation-specific code.
