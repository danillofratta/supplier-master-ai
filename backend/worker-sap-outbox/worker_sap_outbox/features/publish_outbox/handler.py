import json
import logging
from datetime import UTC, datetime
from time import perf_counter

from worker_sap_outbox.features.publish_outbox.command import (
    PublishOutboxCommand,
)
from worker_sap_outbox.features.publish_outbox.message_publisher import (
    MessagePublisher,
)
from worker_sap_outbox.features.publish_outbox.result import (
    PublishOutboxResult,
)
from worker_sap_outbox.shared.observability import (
    get_tracer,
    record_exception,
    reset_correlation_id,
    set_correlation_id,
    start_producer_span,
)
from worker_sap_outbox.shared.unit_of_work import (
    SapOutboxUnitOfWork,
)


logger = logging.getLogger(__name__)
tracer = get_tracer(
    "worker-sap-outbox"
)


class PublishOutboxHandler:
    def __init__(
        self,
        unit_of_work: SapOutboxUnitOfWork,
        publisher: MessagePublisher,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._publisher = publisher

    async def handle(
        self,
        command: PublishOutboxCommand,
    ) -> PublishOutboxResult:
        async with self._unit_of_work as uow:
            messages = (
                await uow.outbox_messages
                .get_pending(
                    limit=command.limit
                )
            )

        published = 0
        failed = 0

        for message in messages:
            correlation_id = (
                self._correlation_id(
                    message.payload
                )
            )
            token = set_correlation_id(
                correlation_id
            )
            started = perf_counter()
            span = None

            try:
                with start_producer_span(
                    tracer,
                    "sqs.publish supplier.sap-sync.result",
                ) as span:
                    span.set_attribute(
                        "messaging.system",
                        "aws.sqs",
                    )
                    span.set_attribute(
                        "messaging.message.id",
                        str(message.message_id),
                    )
                    span.set_attribute(
                        "messaging.event_type",
                        message.event_type,
                    )

                    logger.info(
                        "outbox message publish started",
                        extra={
                            "component": (
                                "SapOutbox"
                            ),
                            "message_id": str(
                                message.message_id
                            ),
                            "event_type": (
                                message.event_type
                            ),
                        },
                    )

                    await self._publisher.publish(
                        event_type=(
                            message.event_type
                        ),
                        payload=message.payload,
                        message_id=str(
                            message.message_id
                        ),
                    )

                    async with self._unit_of_work as uow:
                        stored = (
                            await uow
                            .outbox_messages
                            .get_by_id(
                                message.message_id
                            )
                        )

                        if stored is None:
                            continue

                        stored.register_attempt()
                        stored.mark_processed(
                            datetime.now(UTC)
                        )
                        await (
                            uow.outbox_messages
                            .update(stored)
                        )
                        await uow.commit()

                    published += 1

                    logger.info(
                        "outbox message published",
                        extra={
                            "component": (
                                "SapOutbox"
                            ),
                            "message_id": str(
                                message.message_id
                            ),
                            "event_type": (
                                message.event_type
                            ),
                            "duration_ms": round(
                                (
                                    perf_counter()
                                    - started
                                )
                                * 1000,
                                2,
                            ),
                        },
                    )

            except Exception as exc:
                record_exception(span, exc)

                logger.exception(
                    "outbox message publish failed",
                    extra={
                        "component": (
                            "SapOutbox"
                        ),
                        "message_id": str(
                            message.message_id
                        ),
                        "event_type": (
                            message.event_type
                        ),
                        "duration_ms": round(
                            (
                                perf_counter()
                                - started
                            )
                            * 1000,
                            2,
                        ),
                    },
                )

                async with self._unit_of_work as uow:
                    stored = (
                        await uow
                        .outbox_messages
                        .get_by_id(
                            message.message_id
                        )
                    )
                    if stored is not None:
                        stored.register_attempt()
                        await (
                            uow.outbox_messages
                            .update(stored)
                        )
                        await uow.commit()

                failed += 1

            finally:
                reset_correlation_id(token)

        return PublishOutboxResult(
            published=published,
            failed=failed,
        )

    @staticmethod
    def _correlation_id(
        payload: str,
    ) -> str | None:
        try:
            value = json.loads(
                payload
            ).get("correlation_id")
            return (
                str(value)
                if value
                else None
            )
        except (
            TypeError,
            ValueError,
        ):
            return None
