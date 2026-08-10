# ADR 002: Unit of Work as the persistence transaction boundary

## Context

Supplier use cases need transactional consistency without coupling handlers to
SQLAlchemy, PostgreSQL, `AsyncSession`, `commit`, or `rollback`.

## Decision

Features depend on the `SupplierUnitOfWork` Protocol.

The Unit of Work exposes the repositories required by the use case and owns the
transaction boundary:

- `uow.suppliers` provides the `SupplierRepository` contract.
- `uow.commit()` makes the use-case changes durable.
- `uow.rollback()` reverts the active transaction.
- SQLAlchemy details remain inside infrastructure.

`SqlAlchemySupplierUnitOfWork` is the production PostgreSQL implementation.
`InMemorySupplierUnitOfWork` is used by unit tests.

## Consequences

### Benefits

- Handlers are independent from SQLAlchemy and PostgreSQL.
- A different persistence technology can implement the same Unit of Work and
  repository contracts.
- Multiple repository operations can participate in one transaction.
- Unit tests do not require a database.

### Trade-offs

- Adds one abstraction around persistence.
- Repository contracts must remain technology-agnostic.
- Database-specific optimizations stay in infrastructure and may require
  implementation-specific code.
