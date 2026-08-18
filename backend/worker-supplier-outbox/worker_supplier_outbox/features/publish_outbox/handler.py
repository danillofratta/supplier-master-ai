from datetime import UTC, datetime
from worker_supplier_outbox.features.publish_outbox.command import PublishOutboxCommand
from worker_supplier_outbox.features.publish_outbox.result import PublishOutboxResult
from worker_supplier_outbox.features.publish_outbox.message_publisher import MessagePublisher
from worker_supplier_outbox.shared.unit_of_work import OutboxUnitOfWork

class PublishOutboxHandler:
    def __init__(self, unit_of_work: OutboxUnitOfWork, publisher: MessagePublisher) -> None:
        self._uow = unit_of_work
        self._publisher = publisher

    async def handle(self, command: PublishOutboxCommand) -> PublishOutboxResult:
        async with self._uow as uow:
            messages = await uow.outbox_messages.get_pending(limit=command.limit)

        published = failed = 0
        for message in messages:
            try:
                await self._publisher.publish(
                    event_type=message.event_type,
                    payload=message.payload,
                    message_id=str(message.message_id),
                )
                async with self._uow as uow:
                    stored = await uow.outbox_messages.get_by_id(message.message_id)
                    if stored is None:
                        continue
                    stored.register_attempt()
                    stored.mark_processed(datetime.now(UTC))
                    await uow.outbox_messages.update(stored)
                    await uow.commit()
                published += 1
            except Exception:
                async with self._uow as uow:
                    stored = await uow.outbox_messages.get_by_id(message.message_id)
                    if stored is not None:
                        stored.register_attempt()
                        await uow.outbox_messages.update(stored)
                        await uow.commit()
                failed += 1

        return PublishOutboxResult(published=published, failed=failed)
