from typing import Protocol
from uuid import UUID

from api_supplier.domain.entities.outbox.outbox_message import OutboxMessage


class OutboxRepository(Protocol):
    async def add(
        self,
        message: OutboxMessage,
    ) -> None:
        ...

    async def get_pending_messages(
        self,
        *,
        limit: int = 100,
    ) -> tuple[OutboxMessage, ...]:
        ...

    async def update(
        self,
        message: OutboxMessage,
    ) -> None:
        ...

    async def get_by_id(
        self,
        message_id: UUID,
    ) -> OutboxMessage | None:
        ...
