from datetime import UTC, datetime
from uuid import uuid4
import pytest
from worker_supplier_outbox.domain.entities.outbox_message import OutboxMessage
from worker_supplier_outbox.features.publish_outbox.command import PublishOutboxCommand
from worker_supplier_outbox.features.publish_outbox.handler import PublishOutboxHandler
from worker_supplier_outbox.infrastructure.persistence.repositories import InMemoryOutboxRepository
from worker_supplier_outbox.infrastructure.persistence.unit_of_work import InMemoryOutboxUnitOfWork

class FakePublisher:
    def __init__(self): self.messages=[]
    async def publish(self, **kwargs): self.messages.append(kwargs)

@pytest.mark.asyncio
async def test_publishes_pending_outbox_message():
    repo=InMemoryOutboxRepository()
    message=OutboxMessage(uuid4(),"supplier.sap-sync.requested.v1",'{"ok":true}',datetime.now(UTC))
    await repo.add(message)
    publisher=FakePublisher()
    result=await PublishOutboxHandler(InMemoryOutboxUnitOfWork(repo),publisher).handle(PublishOutboxCommand())
    assert result.published == 1
    assert result.failed == 0
    stored=await repo.get_by_id(message.message_id)
    assert stored.processed_at is not None
    assert stored.attempts == 1
