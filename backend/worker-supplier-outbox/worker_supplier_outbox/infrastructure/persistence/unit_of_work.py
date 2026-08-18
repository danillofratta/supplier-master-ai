from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from worker_supplier_outbox.infrastructure.persistence.repositories import PostgreSQLOutboxRepository

class SqlAlchemyOutboxUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session_factory
        self._session = None
    async def __aenter__(self):
        self._session = self._factory()
        self.outbox_messages = PostgreSQLOutboxRepository(self._session)
        return self
    async def __aexit__(self, exc_type, exc, tb):
        if self._session is None: return
        if exc_type: await self._session.rollback()
        await self._session.close()
        self._session = None
    async def commit(self): await self._session.commit()
    async def rollback(self): await self._session.rollback()

class InMemoryOutboxUnitOfWork:
    def __init__(self, repo) -> None:
        self.outbox_messages = repo
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): return None
    async def commit(self): return None
    async def rollback(self): return None
