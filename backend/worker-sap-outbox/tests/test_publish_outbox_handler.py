from datetime import UTC, datetime
from uuid import uuid4

import pytest

from worker_sap_outbox.domain.entities.outbox_message import (
    OutboxMessage,
)
from worker_sap_outbox.features.publish_outbox.command import (
    PublishOutboxCommand,
)
from worker_sap_outbox.features.publish_outbox.handler import (
    PublishOutboxHandler,
)


class InMemoryRepository:
    def __init__(self) -> None:
        self.items = {}

    async def get_pending(self, *, limit: int = 100):
        return tuple(
            message
            for message in self.items.values()
            if message.processed_at is None
        )[:limit]

    async def get_by_id(self, message_id):
        return self.items.get(message_id)

    async def update(self, message):
        self.items[message.message_id] = message


class InMemoryUow:
    def __init__(self, repository) -> None:
        self.outbox_messages = repository

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return None

    async def commit(self):
        return None

    async def rollback(self):
        return None


class FakePublisher:
    def __init__(self) -> None:
        self.messages = []

    async def publish(self, **kwargs) -> None:
        self.messages.append(kwargs)


@pytest.mark.asyncio
async def test_publishes_and_marks_sap_outbox_processed() -> None:
    repository = InMemoryRepository()
    message = OutboxMessage(
        message_id=uuid4(),
        event_type="supplier.sap-sync.completed.v1",
        payload='{"ok":true}',
        created_at=datetime.now(UTC),
    )
    repository.items[message.message_id] = message

    publisher = FakePublisher()

    result = await PublishOutboxHandler(
        InMemoryUow(repository),
        publisher,
    ).handle(PublishOutboxCommand(limit=10))

    assert result.published == 1
    assert result.failed == 0
    assert len(publisher.messages) == 1
    assert message.processed_at is not None
    assert message.attempts == 1
