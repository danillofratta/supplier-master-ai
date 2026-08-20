import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from consumer_sap.features.sync_supplier.handler import (
    SyncSupplierHandler,
)
from consumer_sap.infrastructure.integrations.sap.fake_sap_gateway import (
    FakeSapGateway,
)
from consumer_sap.infrastructure.messaging.sqs_consumer import (
    SqsConsumer,
)
from consumer_sap.infrastructure.messaging.sqs_message_mapper import (
    SqsMessageMapper,
)
from consumer_sap.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemySapIntegrationUnitOfWork,
)
from consumer_sap.shared.logging import (
    configure_logging,
)
from consumer_sap.shared.observability import (
    configure_tracing,
    instrument_botocore,
    instrument_sqlalchemy,
    record_exception,
    reset_correlation_id,
    set_correlation_id,
    start_consumer_span,
)


def load_environment() -> None:
    service_root = (
        Path(__file__).resolve().parent.parent
    )
    load_dotenv(service_root / ".env")
    load_dotenv(
        service_root / ".env.example"
    )


def require_env(
    name: str,
) -> str:
    value = os.getenv(name)
    if value:
        return value

    raise RuntimeError(
        f"Missing required environment variable '{name}'. "
        "Create a .env file or populate the service .env.example values."
    )


load_environment()
logger = configure_logging("consumer-sap")
tracer = configure_tracing("consumer-sap")
instrument_botocore()


async def run() -> None:
    engine = create_async_engine(
        require_env(
            "SAP_INTEGRATION_DATABASE_URL"
        ),
        pool_pre_ping=True,
    )
    instrument_sqlalchemy(engine)

    factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    handler = SyncSupplierHandler(
        unit_of_work=(
            SqlAlchemySapIntegrationUnitOfWork(
                factory
            )
        ),
        sap_gateway=FakeSapGateway(),
    )

    consumer = SqsConsumer(
        queue_url=os.getenv(
            "SQS_SAP_REQUEST_QUEUE_URL"
        ),
        queue_name=os.getenv(
            "SQS_SAP_REQUEST_QUEUE_NAME",
            "supplier-sap-sync-requests",
        ),
        region_name=require_env(
            "AWS_REGION"
        ),
    )

    logger.info(
        "consumer started",
        extra={
            "component": "SqsConsumer",
            "sap_adapter": "fake",
        },
    )

    try:
        while True:
            messages = (
                await consumer.receive_messages()
            )

            for message in messages:
                receive_count = (
                    message.get(
                        "Attributes",
                        {},
                    ).get(
                        "ApproximateReceiveCount"
                    )
                )

                token = None

                try:
                    command = (
                        SqsMessageMapper
                        .to_sync_supplier_command(
                            message
                        )
                    )

                    token = set_correlation_id(
                        str(
                            command.correlation_id
                        )
                    )

                    with start_consumer_span(
                        tracer,
                        "sqs.consume supplier.sap-sync.requested.v1",
                        message,
                    ) as span:
                        span.set_attribute(
                            "messaging.system",
                            "aws.sqs",
                        )
                        span.set_attribute(
                            "messaging.operation",
                            "process",
                        )
                        span.set_attribute(
                            "messaging.message.id",
                            str(
                                command.message_id
                            ),
                        )
                        span.set_attribute(
                            "app.correlation_id",
                            str(
                                command.correlation_id
                            ),
                        )
                        span.set_attribute(
                            "app.workflow_id",
                            str(
                                command.workflow_id
                            ),
                        )
                        span.set_attribute(
                            "app.supplier_id",
                            str(
                                command.supplier_id
                            ),
                        )

                        logger.info(
                            "SAP sync request received",
                            extra={
                                "component": (
                                    "SqsConsumer"
                                ),
                                "message_id": str(
                                    command.message_id
                                ),
                                "workflow_id": str(
                                    command.workflow_id
                                ),
                                "supplier_id": str(
                                    command.supplier_id
                                ),
                                "receive_count": (
                                    receive_count
                                ),
                            },
                        )

                        try:
                            result = (
                                await handler.handle(
                                    command
                                )
                            )

                            await (
                                consumer.delete_message(
                                    message[
                                        "ReceiptHandle"
                                    ]
                                )
                            )

                            logger.info(
                                "SAP sync request processed",
                                extra={
                                    "component": (
                                        "SyncSupplier"
                                    ),
                                    "message_id": str(
                                        command.message_id
                                    ),
                                    "workflow_id": str(
                                        command.workflow_id
                                    ),
                                    "supplier_id": str(
                                        command.supplier_id
                                    ),
                                    "duplicate": (
                                        result is None
                                    ),
                                    "business_partner_id": (
                                        None
                                        if result is None
                                        else result
                                        .business_partner_id
                                    ),
                                },
                            )
                        except Exception as exc:
                            record_exception(
                                span,
                                exc,
                            )
                            raise

                except Exception:
                    logger.exception(
                        "SAP sync request failed",
                        extra={
                            "component": (
                                "SqsConsumer"
                            ),
                            "sqs_message_id": (
                                message.get(
                                    "MessageId"
                                )
                            ),
                            "receive_count": (
                                receive_count
                            ),
                        },
                    )
                finally:
                    if token is not None:
                        reset_correlation_id(
                            token
                        )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
