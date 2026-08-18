from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from worker_supplier_outbox.domain.entities.outbox_message import OutboxMessage
from worker_supplier_outbox.infrastructure.persistence.sqlalchemy.models import OutboxMessageModel

def _to_domain(m: OutboxMessageModel) -> OutboxMessage:
    return OutboxMessage(m.message_id, m.event_type, m.payload, m.created_at, m.processed_at, m.attempts)

class PostgreSQLOutboxRepository:
    def __init__(self, session: AsyncSession) -> None: self._session = session
    async def get_pending(self, *, limit: int = 100) -> tuple[OutboxMessage, ...]:
        result = await self._session.execute(
            select(OutboxMessageModel)
            .where(OutboxMessageModel.processed_at.is_(None))
            .order_by(OutboxMessageModel.created_at)
            .limit(limit)
        )
        return tuple(_to_domain(x) for x in result.scalars().all())
    async def get_by_id(self, message_id: UUID) -> OutboxMessage | None:
        m = await self._session.get(OutboxMessageModel, message_id)
        return None if m is None else _to_domain(m)
    async def update(self, message: OutboxMessage) -> None:
        m = await self._session.get(OutboxMessageModel, message.message_id)
        if m is None: return
        m.processed_at = message.processed_at
        m.attempts = message.attempts

class InMemoryOutboxRepository:
    def __init__(self) -> None: self.items = {}
    async def get_pending(self, *, limit: int = 100):
        return tuple(x for x in self.items.values() if x.processed_at is None)[:limit]
    async def get_by_id(self, message_id): return self.items.get(message_id)
    async def update(self, message): self.items[message.message_id] = message
    async def add(self, message): self.items[message.message_id] = message
