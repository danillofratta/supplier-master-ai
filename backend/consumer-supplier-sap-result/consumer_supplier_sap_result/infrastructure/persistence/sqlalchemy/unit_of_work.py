from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from consumer_supplier_sap_result.infrastructure.persistence.sqlalchemy.repositories import (
    PostgreSQLInboxRepository,
    PostgreSQLWorkflowRepository,
)


class SqlAlchemySupplierResultUnitOfWork:
    def __init__(
        self,
        factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._factory = factory
        self._session: AsyncSession | None = None

    async def __aenter__(self):
        self._session = self._factory()
        self.workflows = PostgreSQLWorkflowRepository(
            self._session
        )
        self.inbox = PostgreSQLInboxRepository(
            self._session
        )
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:
        if self._session is None:
            return

        try:
            if exc_type is not None:
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("Unit of Work is not active.")
        await self._session.commit()

    async def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("Unit of Work is not active.")
        await self._session.rollback()
