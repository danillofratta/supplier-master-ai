from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from worker_sap_outbox.domain.entities.outbox_message import (
    OutboxMessage,
)
from worker_sap_outbox.infrastructure.persistence.sqlalchemy.models import (
    OutboxMessageModel,
)


class PostgreSQLOutboxRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_pending(
        self,
        *,
        limit: int = 100,
    ) -> tuple[OutboxMessage, ...]:
        result = await self._session.execute(
            select(OutboxMessageModel)
            .where(
                OutboxMessageModel.processed_at.is_(None)
            )
            .order_by(
                OutboxMessageModel.created_at
            )
            .limit(limit)
        )

        return tuple(
            self._to_domain(model)
            for model in result.scalars().all()
        )

    async def get_by_id(
        self,
        message_id: UUID,
    ) -> OutboxMessage | None:
        model = await self._session.get(
            OutboxMessageModel,
            message_id,
        )

        if model is None:
            return None

        return self._to_domain(model)

    async def update(
        self,
        message: OutboxMessage,
    ) -> None:
        model = await self._session.get(
            OutboxMessageModel,
            message.message_id,
        )

        if model is None:
            return

        model.processed_at = message.processed_at
        model.attempts = message.attempts

    @staticmethod
    def _to_domain(
        model: OutboxMessageModel,
    ) -> OutboxMessage:
        return OutboxMessage(
            message_id=model.message_id,
            event_type=model.event_type,
            payload=model.payload,
            created_at=model.created_at,
            processed_at=model.processed_at,
            attempts=model.attempts or 0,
        )
