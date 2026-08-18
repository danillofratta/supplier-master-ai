from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from consumer_sap.infrastructure.persistence.sqlalchemy.repositories import PostgreSQLInboxRepository, PostgreSQLOperationRepository, PostgreSQLOutboxRepository

class SqlAlchemySapIntegrationUnitOfWork:
    def __init__(self, factory: async_sessionmaker[AsyncSession]): self._factory=factory; self._session=None
    async def __aenter__(self):
        self._session=self._factory()
        self.inbox=PostgreSQLInboxRepository(self._session)
        self.operations=PostgreSQLOperationRepository(self._session)
        self.outbox_messages=PostgreSQLOutboxRepository(self._session)
        return self
    async def __aexit__(self, exc_type, exc, tb):
        if self._session is None: return
        if exc_type: await self._session.rollback()
        await self._session.close(); self._session=None
    async def commit(self): await self._session.commit()
    async def rollback(self): await self._session.rollback()
