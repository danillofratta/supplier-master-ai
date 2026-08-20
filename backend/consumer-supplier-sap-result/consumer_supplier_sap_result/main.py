import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from consumer_supplier_sap_result.features.complete_sap_sync.handler import (
    CompleteSapSyncHandler,
)
from consumer_supplier_sap_result.features.fail_sap_sync.handler import (
    FailSapSyncHandler,
)
from consumer_supplier_sap_result.features.process_sap_result.processor import (
    SapResultMessageProcessor,
)
from consumer_supplier_sap_result.infrastructure.messaging.sqs_consumer import (
    SqsConsumer,
)
from consumer_supplier_sap_result.infrastructure.messaging.sqs_message_mapper import (
    SqsMessageMapper,
)
from consumer_supplier_sap_result.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemySupplierResultUnitOfWork,
)
from consumer_supplier_sap_result.shared.logging import (
    configure_logging,
)
from consumer_supplier_sap_result.shared.observability import (
    configure_tracing,
)


def load_environment() -> None:
    service_root = Path(__file__).resolve().parent.parent
    load_dotenv(service_root / ".env")
    load_dotenv(service_root / ".env.example")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(
        f"Missing required environment variable '{name}'. "
        "Create a .env file or populate the service .env.example values."
    )


load_environment()
logger = configure_logging(
    "consumer-supplier-sap-result"
)
tracer = configure_tracing(
    "consumer-supplier-sap-result"
)


async def run() -> None:
    engine = create_async_engine(
        require_env("SUPPLIER_DATABASE_URL"),
        pool_pre_ping=True,
    )
    factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    uow = SqlAlchemySupplierResultUnitOfWork(factory)

    processor = SapResultMessageProcessor(
        complete_handler=CompleteSapSyncHandler(uow),
        fail_handler=FailSapSyncHandler(uow),
    )

    consumer = SqsConsumer(
        queue_url=os.getenv(
            "SQS_SAP_RESULT_QUEUE_URL"
        ),
        queue_name=os.getenv(
            "SQS_SAP_RESULT_QUEUE_NAME",
            "supplier-sap-sync-results",
        ),
        region_name=require_env("AWS_REGION"),
    )

    logger.info("consumer started")

    try:
        while True:
            messages = await consumer.receive_messages()

            for message in messages:
                receive_count = (
                    message.get("Attributes", {})
                    .get("ApproximateReceiveCount")
                )
                try:
                    body = SqsMessageMapper._parse(message)

                    with tracer.start_as_current_span(
                        "process SAP result"
                    ) as span:
                        span.set_attribute(
                            "messaging.message.id",
                            body["message_id"],
                        )
                        span.set_attribute(
                            "app.correlation_id",
                            body["correlation_id"],
                        )
                        span.set_attribute(
                            "messaging.event_type",
                            body["event_type"],
                        )

                        logger.info(
                            "SAP result received",
                            extra={
                                "message_id": body[
                                    "message_id"
                                ],
                                "correlation_id": body[
                                    "correlation_id"
                                ],
                                "event_type": body[
                                    "event_type"
                                ],
                                "receive_count": receive_count,
                            },
                        )

                        await processor.process(message)
                        await consumer.delete_message(
                            message["ReceiptHandle"]
                        )

                        logger.info(
                            "SAP result processed",
                            extra={
                                "message_id": body[
                                    "message_id"
                                ],
                                "correlation_id": body[
                                    "correlation_id"
                                ],
                                "event_type": body[
                                    "event_type"
                                ],
                            },
                        )
                except Exception:
                    logger.exception(
                        "SAP result processing failed",
                        extra={
                            "sqs_message_id": message.get(
                                "MessageId"
                            ),
                            "receive_count": receive_count,
                        },
                    )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
