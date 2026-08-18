import asyncio
import os

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
from consumer_sap.shared.logging import configure_logging
from consumer_sap.shared.observability import configure_tracing


load_dotenv()
logger = configure_logging("consumer-sap")
tracer = configure_tracing("consumer-sap")


async def run() -> None:
    engine = create_async_engine(
        os.environ["SAP_INTEGRATION_DATABASE_URL"],
        pool_pre_ping=True,
    )
    factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    handler = SyncSupplierHandler(
        unit_of_work=SqlAlchemySapIntegrationUnitOfWork(
            factory
        ),
        sap_gateway=FakeSapGateway(),
    )

    consumer = SqsConsumer(
        queue_url=os.environ[
            "SQS_SAP_REQUEST_QUEUE_URL"
        ],
        region_name=os.environ["AWS_REGION"],
    )

    logger.info(
        "consumer started",
        extra={"sap_adapter": "fake"},
    )

    try:
        while True:
            messages = await consumer.receive_messages()

            for message in messages:
                receive_count = (
                    message.get("Attributes", {})
                    .get("ApproximateReceiveCount")
                )

                try:
                    command = (
                        SqsMessageMapper
                        .to_sync_supplier_command(message)
                    )

                    with tracer.start_as_current_span(
                        "process supplier.sap-sync.requested.v1"
                    ) as span:
                        span.set_attribute(
                            "messaging.message.id",
                            str(command.message_id),
                        )
                        span.set_attribute(
                            "app.correlation_id",
                            str(command.correlation_id),
                        )
                        span.set_attribute(
                            "app.workflow_id",
                            str(command.workflow_id),
                        )
                        span.set_attribute(
                            "app.supplier_id",
                            str(command.supplier_id),
                        )

                        logger.info(
                            "SAP sync request received",
                            extra={
                                "message_id": str(
                                    command.message_id
                                ),
                                "correlation_id": str(
                                    command.correlation_id
                                ),
                                "workflow_id": str(
                                    command.workflow_id
                                ),
                                "supplier_id": str(
                                    command.supplier_id
                                ),
                                "receive_count": receive_count,
                            },
                        )

                        result = await handler.handle(command)

                        await consumer.delete_message(
                            message["ReceiptHandle"]
                        )

                        logger.info(
                            "SAP sync request processed",
                            extra={
                                "message_id": str(
                                    command.message_id
                                ),
                                "correlation_id": str(
                                    command.correlation_id
                                ),
                                "workflow_id": str(
                                    command.workflow_id
                                ),
                                "supplier_id": str(
                                    command.supplier_id
                                ),
                                "duplicate": result is None,
                                "business_partner_id": (
                                    None
                                    if result is None
                                    else result.business_partner_id
                                ),
                            },
                        )
                except Exception:
                    logger.exception(
                        "SAP sync request failed",
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
