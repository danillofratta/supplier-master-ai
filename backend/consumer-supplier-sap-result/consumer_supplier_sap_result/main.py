import asyncio
import os

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
from consumer_supplier_sap_result.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemySupplierResultUnitOfWork,
)


load_dotenv()


async def run() -> None:
    engine = create_async_engine(
        os.environ["SUPPLIER_DATABASE_URL"],
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    uow = SqlAlchemySupplierResultUnitOfWork(
        session_factory
    )

    processor = SapResultMessageProcessor(
        complete_handler=CompleteSapSyncHandler(uow),
        fail_handler=FailSapSyncHandler(uow),
    )

    consumer = SqsConsumer(
        queue_url=os.environ[
            "SQS_SAP_RESULT_QUEUE_URL"
        ],
        region_name=os.environ["AWS_REGION"],
    )

    print("consumer-supplier-sap-result started")

    try:
        while True:
            messages = await consumer.receive_messages()

            for message in messages:
                try:
                    await processor.process(message)

                    # ACK only after database commit/idempotency succeeds.
                    await consumer.delete_message(
                        message["ReceiptHandle"]
                    )

                    print(
                        "SAP result processed:",
                        message["MessageId"],
                    )
                except Exception as exc:
                    # Do not delete. Visibility timeout + DLQ policy handle retry.
                    print(
                        "SAP result processing failed:",
                        message.get("MessageId"),
                        str(exc),
                    )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
