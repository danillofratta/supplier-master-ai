from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_supplier.domain.entities.outbox.outbox_message import OutboxMessage
from api_supplier.infrastructure.persistence.sqlalchemy.mappers.outbox_message_mapper import (
    OutboxMessageMapper,
)
from api_supplier.infrastructure.persistence.sqlalchemy.models.outbox_message_model import (
    OutboxMessageModel,
)


class PostgreSQLOutboxRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def add(
        self,
        message: OutboxMessage,
    ) -> None:
        self._session.add(
            OutboxMessageMapper.to_model(message)
        )

    async def get_pending_messages(
        self,
        *,
        limit: int = 100,
    ) -> tuple[OutboxMessage, ...]:
        result = await self._session.execute(
            select(OutboxMessageModel)
            .where(OutboxMessageModel.processed_at.is_(None))
            .order_by(OutboxMessageModel.created_at)
            .limit(limit)
        )
        return tuple(
            OutboxMessageMapper.to_domain(model)
            for model in result.scalars().all()
        )

    async def update(
        self,
        message: OutboxMessage,
    ) -> None:
        model = await self._session.get(
            OutboxMessageModel,
            message.message_id,
        )
        if model is None:
            self._session.add(
                OutboxMessageMapper.to_model(message)
            )
            return

        model.processed_at = message.processed_at
        model.attempts = message.attempts

    async def get_by_id(
        self,
        message_id: UUID,
    ) -> OutboxMessage | None:
        model = await self._session.get(
            OutboxMessageModel,
            message_id,
        )
        return (
            None
            if model is None
            else OutboxMessageMapper.to_domain(model)
        )


class InMemoryOutboxRepository:
    def __init__(self) -> None:
        self._messages: dict[UUID, OutboxMessage] = {}

    async def add(
        self,
        message: OutboxMessage,
    ) -> None:
        self._messages[message.message_id] = message

    async def get_pending_messages(
        self,
        *,
        limit: int = 100,
    ) -> tuple[OutboxMessage, ...]:
        pending = [
            message
            for message in self._messages.values()
            if message.processed_at is None
        ]
        pending.sort(key=lambda message: message.created_at)
        return tuple(pending[:limit])

    async def update(
        self,
        message: OutboxMessage,
    ) -> None:
        self._messages[message.message_id] = message

    async def get_by_id(
        self,
        message_id: UUID,
    ) -> OutboxMessage | None:
        return self._messages.get(message_id)
