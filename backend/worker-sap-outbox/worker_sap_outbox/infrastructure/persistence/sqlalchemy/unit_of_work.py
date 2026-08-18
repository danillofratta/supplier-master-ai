from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from worker_sap_outbox.infrastructure.persistence.sqlalchemy.repositories.outbox_repository import (
    PostgreSQLOutboxRepository,
)


class SqlAlchemySapOutboxUnitOfWork:
    def __init__(
        self,
        session_factory: async_sessionmaker[
            AsyncSession
        ],
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self):
        self._session = self._session_factory()

        self.outbox_messages = (
            PostgreSQLOutboxRepository(
                self._session
            )
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
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()