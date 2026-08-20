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
logger = configure_logging(
    "consumer-supplier-sap-result"
)
tracer = configure_tracing(
    "consumer-supplier-sap-result"
)
instrument_botocore()


async def run() -> None:
    engine = create_async_engine(
        require_env(
            "SUPPLIER_DATABASE_URL"
        ),
        pool_pre_ping=True,
    )
    instrument_sqlalchemy(engine)

    factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    uow = (
        SqlAlchemySupplierResultUnitOfWork(
            factory
        )
    )

    processor = SapResultMessageProcessor(
        complete_handler=(
            CompleteSapSyncHandler(uow)
        ),
        fail_handler=FailSapSyncHandler(
            uow
        ),
    )

    consumer = SqsConsumer(
        queue_url=os.getenv(
            "SQS_SAP_RESULT_QUEUE_URL"
        ),
        queue_name=os.getenv(
            "SQS_SAP_RESULT_QUEUE_NAME",
            "supplier-sap-sync-results",
        ),
        region_name=require_env(
            "AWS_REGION"
        ),
    )

    logger.info(
        "consumer started",
        extra={
            "component": "SqsConsumer"
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
                    body = (
                        SqsMessageMapper._parse(
                            message
                        )
                    )
                    token = set_correlation_id(
                        body.get(
                            "correlation_id"
                        )
                    )

                    with start_consumer_span(
                        tracer,
                        "sqs.consume supplier.sap-sync.result",
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
                            body["message_id"],
                        )
                        span.set_attribute(
                            "messaging.event_type",
                            body["event_type"],
                        )
                        span.set_attribute(
                            "app.correlation_id",
                            body[
                                "correlation_id"
                            ],
                        )

                        logger.info(
                            "SAP result received",
                            extra={
                                "component": (
                                    "SqsConsumer"
                                ),
                                "message_id": (
                                    body[
                                        "message_id"
                                    ]
                                ),
                                "event_type": (
                                    body[
                                        "event_type"
                                    ]
                                ),
                                "receive_count": (
                                    receive_count
                                ),
                            },
                        )

                        try:
                            await (
                                processor.process(
                                    message
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
                                "SAP result processed",
                                extra={
                                    "component": (
                                        "SapResultProcessor"
                                    ),
                                    "message_id": (
                                        body[
                                            "message_id"
                                        ]
                                    ),
                                    "event_type": (
                                        body[
                                            "event_type"
                                        ]
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
                        "SAP result processing failed",
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
